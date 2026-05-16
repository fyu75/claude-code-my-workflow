"""
20_bond_chars_outcomes.py

Add three new outcome variables to the county-year panel and run CS DiD on the
1%-threshold high-share sample:

  Outcome 1 — par-weighted rating (numeric scale, LOWER = BETTER)
  Outcome 2 — par-weighted years-to-maturity (longer = more confidence?)
  Outcome 3 — share of par with callable structure

Methodology:
  - Tranche → deal: par-weighted average across tranches in each MASTER_DEAL_NO
  - Deal → county-year: par-weighted average across deals in the (county, year) cell
  - Counties without resolved FIPS or out of Tier A are excluded (same filters as
    main analysis)

Outputs:
  data/derived/county_year_panel_v4.csv          (v3 + 3 new outcomes)
  data/derived/bond_char_did_results.md          (CS DiD on the 3 outcomes)
  data/derived/figures/fig_bond_char_event.png   (event study)

Run: python3 scripts/python/20_bond_chars_outcomes.py
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
MATURITY = ROOT / 'data/sdc_muni/sdc_municipals/maturity.sas7bdat'
RATINGS  = ROOT / 'data/sdc_muni/sdc_municipals/ratings.sas7bdat'
CALL     = ROOT / 'data/sdc_muni/sdc_municipals/calldata.sas7bdat'
DEALS    = ROOT / 'data/sdc_muni/sdc_municipals/deals_data.sas7bdat'
ISS_MAP  = ROOT / 'data/derived/sdc_issuer_county_full_v3.csv'
PNL_V3   = ROOT / 'data/derived/county_year_panel_v3.csv'
TAX_SHARE= ROOT / 'data/derived/dc_tax_share_distribution.csv'

OUT_PNL  = ROOT / 'data/derived/county_year_panel_v4.csv'
OUT_MD   = ROOT / 'data/derived/bond_char_did_results.md'
OUT_FIG  = ROOT / 'data/derived/figures'

TIER_A = {'District','City, Town Vlg','Local Authority','County/Parish'}
THRESHOLD = 1.0   # ≥1% DC share

# Standardized numeric rating scale (lower = better)
# Top: Aaa/AAA = 1; D = 22; NR / unknown → NaN
RATING_MAP = {
    # Moody's
    'Aaa':1,'Aa1':2,'Aa2':3,'Aa3':4,'A1':5,'A2':6,'A3':7,
    'Baa1':8,'Baa2':9,'Baa3':10,'Ba1':11,'Ba2':12,'Ba3':13,
    'B1':14,'B2':15,'B3':16,'Caa1':17,'Caa2':18,'Caa3':19,
    'Ca':20,'C':21,
    # S&P and Fitch (same scale, different lettering)
    'AAA':1,'AA+':2,'AA':3,'AA-':4,'A+':5,'A':6,'A-':7,
    'BBB+':8,'BBB':9,'BBB-':10,'BB+':11,'BB':12,'BB-':13,
    'B+':14,'B':15,'B-':16,'CCC+':17,'CCC':18,'CCC-':19,
    'CC':20,'D':22,
    # Short forms / Moody-style aggregates (best effort)
    'Aa':3,'Ba':12,'Baa':9,
}

def map_rating(x):
    if pd.isna(x): return np.nan
    s = str(x).strip()
    if s in ('NR','WR','',' '): return np.nan
    return RATING_MAP.get(s, np.nan)

def main():
    # =================================================================
    # 1. Tranche-level → deal-level
    # =================================================================
    print('1. Tranche-level files → deal-level aggregates...')

    # === Ratings ===
    print('   ratings...')
    r = pd.read_sas(RATINGS, encoding='latin-1')
    # Convert each agency to numeric, then average across agencies
    r['m_num'] = r['MOODY_RATING'].map(map_rating)
    r['s_num'] = r['SP_RATING'].map(map_rating)
    r['f_num'] = r['FITCHRATING1'].map(map_rating)
    r['avg_rating'] = r[['m_num','s_num','f_num']].mean(axis=1)
    # Tranche-level rating
    tr_rating = r[['MASTER_DEAL_NO','MUNITRANCHE','avg_rating']]
    print(f'     tranches with rating: {tr_rating["avg_rating"].notna().sum():,} / {len(tr_rating):,}')

    # === Maturity (already have years to maturity from script 09) ===
    print('   maturity (tranche)...')
    t = pd.read_sas(MATURITY, encoding='latin-1')[['MASTER_DEAL_NO','MUNITRANCHE','AMTMATY','MATURITY']]
    t['MATURITY'] = pd.to_datetime(t['MATURITY'], errors='coerce')
    t['amt'] = pd.to_numeric(t['AMTMATY'], errors='coerce')

    # === Call data ===
    print('   calldata...')
    c = pd.read_sas(CALL, encoding='latin-1')[['MASTER_DEAL_NO','MUNITRANCHE','CALL_FLAG']]
    c['callable'] = (c['CALL_FLAG']=='Y').astype(float)
    c.loc[c['CALL_FLAG'].isna(), 'callable'] = np.nan

    # Merge on (MASTER_DEAL_NO, MUNITRANCHE)
    tr = t.merge(tr_rating, on=['MASTER_DEAL_NO','MUNITRANCHE'], how='left') \
          .merge(c[['MASTER_DEAL_NO','MUNITRANCHE','callable']], on=['MASTER_DEAL_NO','MUNITRANCHE'], how='left')
    print(f'   merged tranches: {len(tr):,}')

    # =================================================================
    # 2. Need DELDATE per deal for yrs-to-maturity calc
    # =================================================================
    print('2. Joining DELDATE for yrs-to-maturity...')
    deldates = []
    for ch in pd.read_sas(DEALS, encoding='latin-1', chunksize=200000):
        d = pd.to_datetime(ch['DELDATE'], errors='coerce')
        deldates.append(pd.DataFrame({'MASTER_DEAL_NO': ch['MASTER_DEAL_NO'], 'DELDATE': d}))
    dd = pd.concat(deldates, ignore_index=True).drop_duplicates('MASTER_DEAL_NO')
    tr = tr.merge(dd, on='MASTER_DEAL_NO', how='left')
    tr['yrs2mat'] = (tr['MATURITY'] - tr['DELDATE']).dt.days / 365.25
    tr = tr[(tr['amt']>0) & (tr['yrs2mat']>0) & (tr['yrs2mat']<=50)].copy()
    print(f'   usable tranches: {len(tr):,}')

    # =================================================================
    # 3. Deal-level par-weighted aggregates
    # =================================================================
    print('3. Aggregating to deal level...')
    tr['rxa'] = tr['avg_rating'] * tr['amt']
    tr['mxa'] = tr['yrs2mat']    * tr['amt']
    tr['cxa'] = tr['callable']   * tr['amt']

    deal = tr.groupby('MASTER_DEAL_NO').agg(
        par_M_w   = ('amt','sum'),
        par_rated = ('avg_rating', lambda s: tr.loc[s.index,'amt'][s.notna()].sum()),
        rxa_sum   = ('rxa','sum'),
        mxa_sum   = ('mxa','sum'),
        par_call  = ('callable', lambda s: tr.loc[s.index,'amt'][s.notna()].sum()),
        cxa_sum   = ('cxa','sum'),
    ).reset_index()
    deal['par_wtd_rating']  = deal['rxa_sum'] / deal['par_rated'].replace(0,np.nan)
    deal['par_wtd_yrs2mat'] = deal['mxa_sum'] / deal['par_M_w'].replace(0,np.nan)
    deal['share_callable']  = deal['cxa_sum'] / deal['par_call'].replace(0,np.nan)
    deal = deal[['MASTER_DEAL_NO','par_wtd_rating','par_wtd_yrs2mat','share_callable']]
    print(f'   deals with chars: {len(deal):,}')
    print(f'   rating coverage: {deal["par_wtd_rating"].notna().sum():,}')
    print(f'   maturity coverage: {deal["par_wtd_yrs2mat"].notna().sum():,}')
    print(f'   callable coverage: {deal["share_callable"].notna().sum():,}')

    # =================================================================
    # 4. Apply issuer mapping → aggregate to county-year
    # =================================================================
    print('4. Joining to deals + issuer FIPS, aggregating to county-year...')
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
    deals = pd.concat(rows, ignore_index=True)
    deals = deals.merge(deal, on='MASTER_DEAL_NO', how='left')
    deals = deals.merge(iss, on=['ISSUER','STATECODE'], how='left')
    res = deals[deals['resolve_status'].isin(RES) & deals['county_fips'].notna()].copy()
    res['county_fips'] = res['county_fips'].astype(str).str.zfill(5)
    print(f'   resolved deals: {len(res):,}')

    # Par-weighted county-year aggregates
    res['rxa_d']  = res['par_wtd_rating']  * res['AMT']
    res['mxa_d']  = res['par_wtd_yrs2mat'] * res['AMT']
    res['cxa_d']  = res['share_callable']  * res['AMT']
    cy = res.groupby(['county_fips','year']).agg(
        par_total=('AMT','sum'),
        par_rated_total=('rxa_d', lambda s: res.loc[s.index,'AMT'][res.loc[s.index,'par_wtd_rating'].notna()].sum()),
        rxa=('rxa_d','sum'),
        par_mat_total=('mxa_d', lambda s: res.loc[s.index,'AMT'][res.loc[s.index,'par_wtd_yrs2mat'].notna()].sum()),
        mxa=('mxa_d','sum'),
        par_call_total=('cxa_d', lambda s: res.loc[s.index,'AMT'][res.loc[s.index,'share_callable'].notna()].sum()),
        cxa=('cxa_d','sum'),
    ).reset_index()
    cy['cy_par_wtd_rating']  = cy['rxa'] / cy['par_rated_total'].replace(0,np.nan)
    cy['cy_par_wtd_mat_yrs'] = cy['mxa'] / cy['par_mat_total'].replace(0,np.nan)
    cy['cy_share_callable']  = cy['cxa'] / cy['par_call_total'].replace(0,np.nan)
    cy['year'] = cy['year'].astype(int)
    cy = cy[['county_fips','year','cy_par_wtd_rating','cy_par_wtd_mat_yrs','cy_share_callable']]

    # Merge into panel v3 → v4
    pnl = pd.read_csv(PNL_V3, dtype={'county_fips':str,'state_fips':str})
    pnl['county_fips'] = pnl['county_fips'].str.zfill(5)
    pnl = pnl.merge(cy, on=['county_fips','year'], how='left')
    pnl.to_csv(OUT_PNL, index=False)
    print(f'   wrote {OUT_PNL}  ({len(pnl):,} cells × {len(pnl.columns)} cols)')

    # Sanity
    print(f'\nSanity — county-year coverage:')
    for c in ['cy_par_wtd_rating','cy_par_wtd_mat_yrs','cy_share_callable']:
        n = pnl[c].notna().sum()
        med = pnl[c].median()
        print(f'   {c}: {n:,} cells (median = {med:.3f})')

    # =================================================================
    # 5. CS DiD on the high-share treatment group
    # =================================================================
    print('\n5. Running CS DiD on bond-char outcomes...')
    tax = pd.read_csv(TAX_SHARE, dtype={'county_fips':str})
    tax['county_fips'] = tax['county_fips'].str.zfill(5)
    treat_fips = set(tax[tax['dc_share_mid']>=THRESHOLD]['county_fips'])
    never_host = set(pnl.groupby('county_fips')['n_dc_cumulative'].max().pipe(lambda s: s[s==0]).index)

    sample = pnl[pnl['county_fips'].isin(treat_fips | never_host)].copy()
    sample = sample[(sample['year']>=2010)&(sample['year']<=2025)]
    sample['cohort'] = sample['first_dc_year'].where(sample['county_fips'].isin(treat_fips), other=np.nan)
    sample = sample.set_index(['county_fips','year'])

    OUTCOMES = [
        ('cy_par_wtd_rating',  'Par-weighted rating (lower = better)'),
        ('cy_par_wtd_mat_yrs', 'Par-weighted maturity (years)'),
        ('cy_share_callable',  'Share of par with callable structure'),
    ]

    lines = []
    L = lambda s='': (print(s), lines.append(s))[1]
    L('# Bond-characteristic outcomes — CS DiD on 1%-threshold sample\n')
    L(f'*Run {pd.Timestamp.now().date()}. Source: `scripts/python/20_bond_chars_outcomes.py`.*\n')
    L('Treatment: 125 counties with DC tax share ≥ 1%. Control: 2,776 never-DC-host counties. Panel 2010–2025.')
    L('Outcomes are county-year par-weighted aggregates of deal-level par-weighted tranche aggregates.\n')

    L('## Coverage of bond-characteristic outcomes\n')
    L('| Outcome | # county-year cells | Median |')
    L('|---|---:|---:|')
    for y, ylab in OUTCOMES:
        n = pnl[y].notna().sum(); med = pnl[y].median()
        L(f'| **{ylab}** | {n:,} | {med:.3f} |')

    L('\n## ATT results (Callaway–Sant\'Anna)\n')
    L('| Outcome | ATT | SE | 95% CI | N (obs) |')
    L('|---|---:|---:|---|---:|')

    ev_results = {}
    for y, ylab in OUTCOMES:
        d = sample[[y,'cohort']].dropna(subset=[y])
        if len(d) < 100 or d['cohort'].notna().sum() < 5:
            L(f'| **{ylab}** | — | — | insufficient data | {len(d):,} |')
            continue
        try:
            est = ATTgt(data=d, cohort_column='cohort', anticipation=0)
            est.fit(formula=y, n_jobs=1)
            s = est.aggregate('simple')
            att = float(s.iloc[0,0]); se = float(s.iloc[0,1])
            t = att/se if se>0 else 0
            sig = '***' if abs(t)>2.58 else '**' if abs(t)>1.96 else '*' if abs(t)>1.645 else ''
            ci_lo = att - 1.96*se; ci_hi = att + 1.96*se
            L(f'| **{ylab}** | {att:+.4f}{sig} ({se:.4f}) | {se:.4f} | [{ci_lo:+.4f}, {ci_hi:+.4f}] | {len(d):,} |')
            ev = est.aggregate('event').reset_index()
            ev_results[ylab] = (att, se, ev)
        except Exception as e:
            L(f'| **{ylab}** | failed: {str(e)[:50]} | — | — | — |')

    L('\n*Stars: \\*\\*\\* p<0.01, \\*\\* p<0.05, \\* p<0.10.*\n')

    # Event-study bucket table
    L('## Event-study buckets (CS event-time ATT averaged within windows)\n')
    L('| Outcome | t=−5..−2 | t=0 | t=+1..+3 | t=+4..+7 | t≥+8 |')
    L('|---|---:|---:|---:|---:|---:|')
    for ylab, (att, se, ev) in ev_results.items():
        tcol = ev.columns[0]; ac = ev.columns[1]
        bins = []
        for lo, hi in [(-5,-2),(0,0),(1,3),(4,7),(8,99)]:
            sel = ev[(ev[tcol]>=lo) & (ev[tcol]<=hi)]
            bins.append(sel[ac].mean() if len(sel) else float('nan'))
        L(f'| **{ylab}** | {bins[0]:+.3f} | {bins[1]:+.3f} | {bins[2]:+.3f} | {bins[3]:+.3f} | {bins[4]:+.3f} |')

    # Event-study figure
    if ev_results:
        fig, axes = plt.subplots(1, len(ev_results), figsize=(6*len(ev_results), 5))
        if len(ev_results)==1: axes = [axes]
        for ax, (ylab, (att, se, ev)) in zip(axes, ev_results.items()):
            tcol = ev.columns[0]; ac = ev.columns[1]; sc = ev.columns[2]
            sub = ev[(ev[tcol]>=-7) & (ev[tcol]<=10)]
            ax.errorbar(sub[tcol], sub[ac], yerr=1.96*sub[sc], marker='o', capsize=4, color='steelblue', lw=1.5)
            ax.axhline(0, color='black', lw=0.5)
            ax.axvline(-0.5, color='darkred', linestyle='--', lw=1, alpha=0.5, label='first DC')
            ax.set_xlabel('Years since first DC')
            ax.set_ylabel(ylab)
            ax.set_title(f'{ylab}\nATT = {att:+.3f} (SE {se:.3f})')
            ax.grid(alpha=0.3); ax.legend(fontsize=9)
        fig.suptitle('Bond-characteristic outcomes — CS DiD, high-DC-share treatment vs never-host control', y=1.02)
        fig.tight_layout()
        fig.savefig(OUT_FIG/'fig_bond_char_event.png', dpi=140, bbox_inches='tight')
        plt.close()
        L(f'\n![Bond-char event-study](figures/fig_bond_char_event.png)\n')

    # Interpretation
    L('## Interpretation\n')
    if 'Par-weighted rating (lower = better)' in ev_results:
        att, se, _ = ev_results['Par-weighted rating (lower = better)']
        L(f'**Rating (numeric scale, lower = better)**: ATT = {att:+.3f} (SE {se:.3f}). ')
        if att < -0.05: L('  Negative coefficient = bond ratings IMPROVE post-DC. Consistent with the fiscal-capacity story: better tax base → better credit.\n')
        elif att > 0.05: L('  Positive coefficient = bond ratings WORSEN post-DC. Surprising.\n')
        else: L('  Coefficient ≈ 0 — no detectable rating change. Possibly because most muni bonds are NR or AAA-insured; the marginal rating doesn\'t move.\n')
    if 'Par-weighted maturity (years)' in ev_results:
        att, se, _ = ev_results['Par-weighted maturity (years)']
        L(f'**Maturity (years)**: ATT = {att:+.3f} (SE {se:.3f}). ')
        if att > 0.5: L('  Positive = longer maturities post-DC. Consistent with expanded confidence in long-term fiscal capacity.\n')
        elif att < -0.5: L('  Negative = shorter maturities post-DC. Possibly counties become more conservative.\n')
        else: L('  Roughly no change. Maturity choice may not be driven by fiscal-capacity dynamics.\n')
    if 'Share of par with callable structure' in ev_results:
        att, se, _ = ev_results['Share of par with callable structure']
        L(f'**Callable share**: ATT = {att:+.4f} (SE {se:.4f}). ')
        if att < -0.02: L('  Negative = LESS callable structure post-DC. Counties less likely to issue with call options (don\'t need future refinance flexibility).\n')
        elif att > 0.02: L('  Positive = MORE callable structure post-DC.\n')
        else: L('  ≈ 0 — call structure largely unchanged.\n')

    L('### Caveats')
    L('1. Rating data is **sparse**: ~17% of muni tranches carry an agency rating (the rest are NR or insured). Selection: rated bonds are typically larger / higher-quality issues, so the rating outcome is for a non-random subset.')
    L('2. Maturity is par-weighted across all tranches in a deal, including short serials. Long-end maturity may not move much.')
    L('3. Callable share is the share of par with explicit `CALL_FLAG=Y`; SDC field has ~99% coverage among tranches but the definition of "callable" varies (some call provisions are restrictive).')

    OUT_MD.write_text('\n'.join(lines))
    print(f'\nWrote {OUT_MD}')

if __name__ == '__main__':
    main()
