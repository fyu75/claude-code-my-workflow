"""
21_rating_outcomes_rich.py

Richer set of rating outcomes to handle SDC's sparse rating coverage (~80% NR):

  A. Avg rating (lower = better) on the **rated-only** subsample — clean within-rated comparison
  B. **Per-agency** ATTs (Moody / S&P / Fitch) — different agencies, different coverage
  C. **Extensive margin** — share of par with any agency rating (vs NR)
  D. **AAA share** — share of par rated AAA / Aaa
  E. **Investment-grade share** — share of par rated ≥ BBB- / Baa3

These let us separate (i) "rating quality conditional on being rated" from (ii) "are
DC counties more likely to seek a public rating at all?"

Outputs:
  data/derived/rating_outcomes_results.md
  data/derived/figures/fig_rating_outcomes.png

Run: python3 scripts/python/21_rating_outcomes_rich.py
"""

import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from differences import ATTgt
from pathlib import Path
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

ROOT = Path(__file__).resolve().parents[2]
RATINGS  = ROOT / 'data/sdc_muni/sdc_municipals/ratings.sas7bdat'
DEALS    = ROOT / 'data/sdc_muni/sdc_municipals/deals_data.sas7bdat'
MATURITY = ROOT / 'data/sdc_muni/sdc_municipals/maturity.sas7bdat'
ISS_MAP  = ROOT / 'data/derived/sdc_issuer_county_full_v3.csv'
PNL      = ROOT / 'data/derived/county_year_panel_v3.csv'
TAX_SHARE= ROOT / 'data/derived/dc_tax_share_distribution.csv'

OUT_MD   = ROOT / 'data/derived/rating_outcomes_results.md'
OUT_FIG  = ROOT / 'data/derived/figures'

TIER_A = {'District','City, Town Vlg','Local Authority','County/Parish'}
THRESHOLD = 1.0

RATING_MAP = {
    'Aaa':1,'Aa1':2,'Aa2':3,'Aa3':4,'A1':5,'A2':6,'A3':7,
    'Baa1':8,'Baa2':9,'Baa3':10,'Ba1':11,'Ba2':12,'Ba3':13,
    'B1':14,'B2':15,'B3':16,'Caa1':17,'Caa2':18,'Caa3':19,'Ca':20,'C':21,
    'AAA':1,'AA+':2,'AA':3,'AA-':4,'A+':5,'A':6,'A-':7,
    'BBB+':8,'BBB':9,'BBB-':10,'BB+':11,'BB':12,'BB-':13,
    'B+':14,'B':15,'B-':16,'CCC+':17,'CCC':18,'CCC-':19,'CC':20,'D':22,
    'Aa':3,'Ba':12,'Baa':9,
}
def map_rate(x):
    if pd.isna(x): return np.nan
    s = str(x).strip()
    if s in ('NR','WR','',' '): return np.nan
    return RATING_MAP.get(s, np.nan)

def cs_run(d, y, cohort='cohort'):
    sub = d[[y,cohort]].dropna(subset=[y])
    if len(sub)<100 or sub[cohort].notna().sum()<5: return None
    try:
        est = ATTgt(data=sub, cohort_column=cohort, anticipation=0)
        est.fit(formula=y, n_jobs=1)
        s = est.aggregate('simple')
        return float(s.iloc[0,0]), float(s.iloc[0,1]), len(sub), est.aggregate('event').reset_index()
    except Exception as e:
        print(f'  {y} failed: {e}')
        return None

def main():
    print('1. Building deal-level rating aggregates...')
    r = pd.read_sas(RATINGS, encoding='latin-1')
    r['mn'] = r['MOODY_RATING'].map(map_rate)
    r['sn'] = r['SP_RATING'].map(map_rate)
    r['fn'] = r['FITCHRATING1'].map(map_rate)
    r['any_rated']  = (r[['mn','sn','fn']].notna().any(axis=1)).astype(int)
    r['avg_rating'] = r[['mn','sn','fn']].mean(axis=1)
    # Best (lowest) rating across agencies
    r['best_rating']= r[['mn','sn','fn']].min(axis=1)
    # Tags for category outcomes
    r['is_aaa']     = (r['best_rating']==1).astype(int)
    r['is_ig']      = ((r['best_rating']<=10) & r['best_rating'].notna()).astype(int)

    # Need tranche par from maturity file
    print('2. Joining tranche par from maturity file...')
    t = pd.read_sas(MATURITY, encoding='latin-1')[['MASTER_DEAL_NO','MUNITRANCHE','AMTMATY']]
    t['amt'] = pd.to_numeric(t['AMTMATY'], errors='coerce')
    tr = t.merge(r[['MASTER_DEAL_NO','MUNITRANCHE','any_rated','avg_rating','best_rating','is_aaa','is_ig','mn','sn','fn']],
                  on=['MASTER_DEAL_NO','MUNITRANCHE'], how='left')
    tr = tr[tr['amt']>0].copy()

    print(f'   tranches: {len(tr):,}; with any rating: {tr["any_rated"].sum():,} ({100*tr["any_rated"].mean():.0f}%)')

    # Deal-level par-weighted
    print('3. Deal-level aggregates...')
    grp = tr.groupby('MASTER_DEAL_NO')
    deal = grp.agg(
        par_total=('amt','sum'),
        # extensive — share of par with ANY rating
        par_any_rated=('amt', lambda s: s[tr.loc[s.index,'any_rated']==1].sum()),
        # rated subsample: par-weighted average rating where rating exists
        rated_par_avg=('avg_rating', lambda s: (s.dropna() * tr.loc[s.dropna().index,'amt']).sum()),
        rated_par=('avg_rating', lambda s: tr.loc[s.dropna().index,'amt'].sum()),
        # category shares
        par_aaa=('amt', lambda s: s[tr.loc[s.index,'is_aaa']==1].sum()),
        par_ig=('amt', lambda s: s[tr.loc[s.index,'is_ig']==1].sum()),
        # per-agency rated par (best-rating proxy)
        moody_par=('mn', lambda s: (s.dropna() * tr.loc[s.dropna().index,'amt']).sum()),
        moody_par_n=('mn', lambda s: tr.loc[s.dropna().index,'amt'].sum()),
        sp_par=('sn', lambda s: (s.dropna() * tr.loc[s.dropna().index,'amt']).sum()),
        sp_par_n=('sn', lambda s: tr.loc[s.dropna().index,'amt'].sum()),
    ).reset_index()
    deal['share_rated']     = deal['par_any_rated'] / deal['par_total'].replace(0,np.nan)
    deal['rated_avg_rating']= deal['rated_par_avg'] / deal['rated_par'].replace(0,np.nan)
    deal['share_aaa']       = deal['par_aaa']  / deal['par_total'].replace(0,np.nan)
    deal['share_ig']        = deal['par_ig']   / deal['par_total'].replace(0,np.nan)
    deal['moody_avg']       = deal['moody_par']/ deal['moody_par_n'].replace(0,np.nan)
    deal['sp_avg']          = deal['sp_par']   / deal['sp_par_n'].replace(0,np.nan)
    deal = deal[['MASTER_DEAL_NO','share_rated','rated_avg_rating','share_aaa','share_ig','moody_avg','sp_avg']]
    print(f'   deals: {len(deal):,}')

    # =================================================================
    # 4. Join + aggregate to county-year + run CS DiD
    # =================================================================
    print('4. Joining deals + issuer FIPS + aggregating to county-year...')
    iss = pd.read_csv(ISS_MAP, dtype={'county_fips':str})
    iss['county_fips'] = iss['county_fips'].astype(str).str.zfill(5).where(
        iss['county_fips'].notna() & (iss['county_fips']!='nan'), None)
    iss = iss[['ISSUER','STATECODE','county_fips','resolve_status']]
    RES = {'county_fips_direct','place_fips_via_crosswalk','cousub_fips_via_crosswalk','county_fips_override'}

    rows = []
    for ch in pd.read_sas(DEALS, encoding='latin-1', chunksize=200000):
        d = pd.to_datetime(ch['DELDATE'], errors='coerce')
        sub = ch[d.dt.year.between(2000,2025) & (ch['AMT']>=1) & (ch['CORPORATE_BACKED']=='No')
                 & ch['ISSTYPE_TRANS'].isin(TIER_A) & ch['ISSUER'].notna() & ch['STATECODE'].notna()
                ][['MASTER_DEAL_NO','DELDATE','ISSUER','STATECODE','AMT']].copy()
        sub['year']      = d[sub.index].dt.year.astype('Int64')
        sub['ISSUER']    = sub['ISSUER'].str.strip()
        sub['STATECODE'] = sub['STATECODE'].str.strip()
        rows.append(sub)
    deals = pd.concat(rows, ignore_index=True).merge(deal, on='MASTER_DEAL_NO', how='left').merge(iss, on=['ISSUER','STATECODE'], how='left')
    res = deals[deals['resolve_status'].isin(RES) & deals['county_fips'].notna()].copy()
    res['county_fips'] = res['county_fips'].astype(str).str.zfill(5)
    print(f'   resolved deals: {len(res):,}')

    # County-year par-weighted (par from deals_data AMT)
    def pwa(g, col):
        m = g[col].notna()
        if not m.any(): return np.nan
        w = g.loc[m,'AMT']
        return (g.loc[m,col] * w).sum() / w.sum()

    cy = res.groupby(['county_fips','year']).apply(lambda g: pd.Series({
        'cy_share_rated':       pwa(g, 'share_rated'),
        'cy_rated_avg_rating':  pwa(g, 'rated_avg_rating'),
        'cy_share_aaa':         pwa(g, 'share_aaa'),
        'cy_share_ig':          pwa(g, 'share_ig'),
        'cy_moody_avg':         pwa(g, 'moody_avg'),
        'cy_sp_avg':            pwa(g, 'sp_avg'),
    })).reset_index()
    cy['year'] = cy['year'].astype(int)

    pnl = pd.read_csv(PNL, dtype={'county_fips':str,'state_fips':str})
    pnl['county_fips'] = pnl['county_fips'].str.zfill(5)
    pnl = pnl.merge(cy, on=['county_fips','year'], how='left')

    tax = pd.read_csv(TAX_SHARE, dtype={'county_fips':str})
    tax['county_fips'] = tax['county_fips'].str.zfill(5)
    treat_fips = set(tax[tax['dc_share_mid']>=THRESHOLD]['county_fips'])
    never_host = set(pnl.groupby('county_fips')['n_dc_cumulative'].max().pipe(lambda s: s[s==0]).index)
    sample = pnl[pnl['county_fips'].isin(treat_fips | never_host)].copy()
    sample = sample[(sample['year']>=2010)&(sample['year']<=2025)]
    sample['cohort'] = sample['first_dc_year'].where(sample['county_fips'].isin(treat_fips), other=np.nan)
    sample = sample.set_index(['county_fips','year'])

    OUTCOMES = [
        ('cy_share_rated',      'Share of par rated (extensive margin)'),
        ('cy_rated_avg_rating', 'Avg rating | rated subsample (lower=better)'),
        ('cy_share_aaa',        'Share of par at AAA/Aaa'),
        ('cy_share_ig',         'Share of par investment-grade (≥ BBB-/Baa3)'),
        ('cy_moody_avg',        'Moody-only avg rating (lower=better)'),
        ('cy_sp_avg',           'S&P-only avg rating (lower=better)'),
    ]

    lines = []
    L = lambda s='': (print(s), lines.append(s))[1]
    L('# Rich rating outcomes — CS DiD on 1%-threshold sample\n')
    L(f'*Run {pd.Timestamp.now().date()}. Source: `scripts/python/21_rating_outcomes_rich.py`.*\n')
    L('Treatment: 125 counties with DC tax share ≥ 1%. Control: 2,776 never-DC-host counties. Panel 2010–2025.\n')
    L('Six rating-related outcomes split the question into extensive (do they get rated?), quality (how high?), and within-rated subsample (avg rating among rated).\n')

    L('## Coverage (county-year cells with non-null value)\n')
    L('| Outcome | N cells | Median |')
    L('|---|---:|---:|')
    for y, ylab in OUTCOMES:
        n = pnl[y].notna().sum()
        med = pnl[y].median()
        L(f'| {ylab} | {n:,} | {med:.3f} |')

    L('\n## CS-ATT results\n')
    L('| Outcome | ATT | SE | t | 95% CI | N (obs) |')
    L('|---|---:|---:|---:|---|---:|')
    ev_all = {}
    for y, ylab in OUTCOMES:
        r = cs_run(sample, y)
        if r is None:
            L(f'| **{ylab}** | — | — | — | insufficient | — |')
            continue
        att, se, n, ev = r
        t = att/se if se>0 else 0
        sig = '***' if abs(t)>2.58 else '**' if abs(t)>1.96 else '*' if abs(t)>1.645 else ''
        ci_lo = att-1.96*se; ci_hi = att+1.96*se
        L(f'| **{ylab}** | {att:+.4f}{sig} | {se:.4f} | {t:+.2f} | [{ci_lo:+.4f}, {ci_hi:+.4f}] | {n:,} |')
        ev_all[ylab] = (att, se, ev)
    L('\n*Stars: \\*\\*\\* p<0.01, \\*\\* p<0.05, \\* p<0.10.*\n')

    # Event-study buckets
    L('## Event-study buckets\n')
    L('| Outcome | t=−5..−2 | t=0 | t=+1..+3 | t=+4..+7 | t≥+8 |')
    L('|---|---:|---:|---:|---:|---:|')
    for ylab, (att, se, ev) in ev_all.items():
        tcol = ev.columns[0]; ac = ev.columns[1]
        bins = []
        for lo, hi in [(-5,-2),(0,0),(1,3),(4,7),(8,99)]:
            sel = ev[(ev[tcol]>=lo) & (ev[tcol]<=hi)]
            bins.append(sel[ac].mean() if len(sel) else float('nan'))
        L(f'| **{ylab}** | {bins[0]:+.4f} | {bins[1]:+.4f} | {bins[2]:+.4f} | {bins[3]:+.4f} | {bins[4]:+.4f} |')

    # Plot the key rating outcomes
    plot_outcomes = [
        ('cy_share_rated', 'Share rated (extensive)'),
        ('cy_rated_avg_rating', 'Avg rating | rated'),
        ('cy_share_aaa', 'Share AAA'),
        ('cy_share_ig', 'Share investment-grade'),
    ]
    valid_plots = [(y, l) for y, l in plot_outcomes if l in [ev_all_l for ev_all_l in [k for k in ev_all.keys()]] or
                   any(ylab.startswith(l[:20]) for ylab in ev_all)]
    # Simpler — just take the first 4 that have results
    keys_avail = [k for k in ev_all.keys()][:4]
    if keys_avail:
        fig, axes = plt.subplots(2, 2, figsize=(13,10))
        for ax, ylab in zip(axes.flat, keys_avail):
            att, se, ev = ev_all[ylab]
            tcol = ev.columns[0]; ac = ev.columns[1]; sc = ev.columns[2]
            sub = ev[(ev[tcol]>=-7) & (ev[tcol]<=10)]
            ax.errorbar(sub[tcol], sub[ac], yerr=1.96*sub[sc], marker='o', capsize=4, color='steelblue', lw=1.5)
            ax.axhline(0, color='black', lw=0.5)
            ax.axvline(-0.5, color='darkred', linestyle='--', lw=1, alpha=0.5)
            ax.set_xlabel('Years since first DC')
            ax.set_ylabel(ylab)
            ax.set_title(f'{ylab}\nATT = {att:+.3f} (SE {se:.3f})')
            ax.grid(alpha=0.3)
        fig.suptitle('Rich rating outcomes — CS DiD event study', y=1.00)
        fig.tight_layout()
        fig.savefig(OUT_FIG/'fig_rating_outcomes.png', dpi=140, bbox_inches='tight')
        plt.close()
        L(f'\n![Rich rating outcomes](figures/fig_rating_outcomes.png)\n')

    # Interpretation
    L('## Interpretation\n')
    for ylab, (att, se, ev) in ev_all.items():
        t = att/se if se>0 else 0
        sig = abs(t) > 1.96
        L(f'- **{ylab}**: {att:+.4f} (SE {se:.4f}, t={t:+.1f}). ' +
          ('**Significant.**' if sig else ('Marginal.' if abs(t)>1.645 else 'Null.')))

    L('\n### Honest reading\n')
    L('If **share_rated** moves up, it would mean DC counties seek public ratings more often after DC arrival (extensive margin — relevant for small rural counties that may not have been rated before).\n')
    L('If **rated_avg_rating** moves down (toward 1=AAA), it would mean DC counties already getting rated see their rating quality IMPROVE post-DC (intensive margin — fiscal capacity → better credit).\n')
    L('If **share_aaa** moves up and **share_ig** moves up, that\'s a distributional shift toward better credit quality, consistent with the fiscal-capacity story.\n')
    L('The per-agency splits tell us whether the rating change is driven by one specific agency (e.g., S&P\'s methodology weights different muni factors than Moody\'s).\n')

    OUT_MD.write_text('\n'.join(lines))
    print(f'\nWrote {OUT_MD}')

if __name__ == '__main__':
    main()
