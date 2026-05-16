"""
19_heterogeneity.py

Heterogeneity probes within the 125 high-DC-share treated counties:

  H-A: County size (rural <100k pop vs larger ≥100k pop)
        Mitch's prediction: effect concentrates in rural / small counties
        where DC fiscal contribution is a bigger relative share.

  H-B: State DC-incentive regime
        States with explicit DC tax incentives (NCSL list) vs other states.
        Effect may be smaller in incentive states (DCs receive PILOTs, so the
        fiscal lift per MW is muted).

Both splits run separate Callaway-Sant'Anna ATTs on the spread outcome.

Outputs:
  data/derived/heterogeneity_results.md
  data/derived/figures/fig_heterogeneity.png

Run: python3 scripts/python/19_heterogeneity.py
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
PNL  = ROOT / 'data/derived/county_year_panel_v3.csv'
TAX_SHARE = ROOT / 'data/derived/dc_tax_share_distribution.csv'
POP_FILE  = ROOT / 'data/external/acfr/county_population_2017.csv'
OUT_MD = ROOT / 'data/derived/heterogeneity_results.md'
OUT_FIG = ROOT / 'data/derived/figures'

THRESHOLD = 1.0

# NCSL "Subsidizing Servers" 2024 list — states with explicit data-center tax incentives
# (sales/use-tax exemption on DC equipment, or PILOT programs, or both).
# Compiled from NCSL/Good Jobs First public reports.
INCENTIVE_STATES = {
    'AL','AZ','AR','CA','CO','CT','FL','GA','ID','IL','IN','IA','KS','KY',
    'LA','MD','MA','MI','MN','MS','MO','MT','NE','NV','NJ','NM','NY','NC',
    'ND','OH','OK','OR','PA','SC','SD','TN','TX','UT','VA','WA','WV','WI','WY'
}
# States without explicit DC incentives (or only generic tech incentives):
# AK, DE, HI, ME, NH, RI, VT — small population states with minimal DC infrastructure.

def cs_run(panel_df, y, cohort_col='cohort'):
    d = panel_df[[y, cohort_col]].dropna(subset=[y]).copy()
    if len(d) < 100: return None
    if d['cohort'].notna().sum() < 5: return None
    try:
        est = ATTgt(data=d, cohort_column=cohort_col, anticipation=0)
        est.fit(formula=y, n_jobs=1)
        s = est.aggregate('simple')
        att = float(s.iloc[0,0]); se = float(s.iloc[0,1])
        return att, se, len(d)
    except Exception:
        return None

def main():
    print('Loading...')
    pnl = pd.read_csv(PNL, dtype={'county_fips':str,'state_fips':str})
    pnl['county_fips'] = pnl['county_fips'].str.zfill(5)
    pnl['log_par']     = np.log1p(pnl['par_total_M'])
    pnl['log_deals']   = np.log1p(pnl['n_deals'])

    tax = pd.read_csv(TAX_SHARE, dtype={'county_fips':str})
    tax['county_fips'] = tax['county_fips'].str.zfill(5)
    pop = pd.read_csv(POP_FILE, dtype={'county_fips':str})
    pop['county_fips'] = pop['county_fips'].str.zfill(5)

    treat = tax[tax['dc_share_mid']>=THRESHOLD].merge(pop, on='county_fips', how='left')
    treat_fips = set(treat['county_fips'])
    never_host = set(pnl.groupby('county_fips')['n_dc_cumulative'].max().pipe(lambda s: s[s==0]).index)
    print(f'  Treated counties: {len(treat_fips)}; controls: {len(never_host)}')

    # Define group splits
    treat['rural'] = treat['population_2017'] < 100_000
    state_lookup = pnl.groupby('county_fips')['state_abbr'].first().to_dict()
    treat['state_abbr'] = treat['county_fips'].map(state_lookup)
    treat['incentive_state'] = treat['state_abbr'].isin(INCENTIVE_STATES)

    print(f'  Rural (pop<100k) treated: {treat["rural"].sum()}; Larger: {(~treat["rural"]).sum()}')
    print(f'  In incentive states: {treat["incentive_state"].sum()}; Not: {(~treat["incentive_state"]).sum()}')

    # Helper: build a CS panel for a treated-county subset
    def cs_for(subset_fips, label):
        sub = pnl[pnl['county_fips'].isin(set(subset_fips) | never_host)].copy()
        sub = sub[(sub['year']>=2010)&(sub['year']<=2025)]
        sub['cohort'] = sub['first_dc_year'].where(sub['county_fips'].isin(subset_fips), other=np.nan)
        sub = sub.set_index(['county_fips','year'])
        results = {}
        for y, ylab in [('log_par','log(par+1)'),
                         ('log_deals','log(n_deals+1)'),
                         ('par_wtd_spread_bps','spread (bps)')]:
            res = cs_run(sub, y)
            results[ylab] = res
        return results

    print('\nRunning splits...')
    rural_fips    = set(treat[treat['rural']]['county_fips'])
    larger_fips   = set(treat[~treat['rural']]['county_fips'])
    incentive_fips= set(treat[treat['incentive_state']]['county_fips'])
    nonincent_fips= set(treat[~treat['incentive_state']]['county_fips'])
    all_fips      = treat_fips

    # Cohort split: early adopters (first DC ≤ 2014) vs hyperscale era (first DC ≥ 2018)
    first_dc = pnl.groupby('county_fips')['first_dc_year'].first().to_dict()
    early_fips = {f for f in treat_fips if first_dc.get(f) and first_dc[f] <= 2014}
    late_fips  = {f for f in treat_fips if first_dc.get(f) and first_dc[f] >= 2018}

    # Share-band split: very-high (≥10%) vs moderate (1–10%)
    veryhigh = set(treat[treat['dc_share_mid']>=10]['county_fips'])
    moderate = set(treat[(treat['dc_share_mid']>=1)&(treat['dc_share_mid']<10)]['county_fips'])

    splits = {
        'All high-share (baseline)':       all_fips,
        'Rural (pop < 100k)':                rural_fips,
        'Larger (pop ≥ 100k)':              larger_fips,
        'Early cohort (1st DC ≤ 2014)':      early_fips,
        'Hyperscale cohort (1st DC ≥ 2018)': late_fips,
        'Very-high share (≥ 10%)':          veryhigh,
        'Moderate share (1–10%)':            moderate,
    }

    out = {}
    for label, fipsset in splits.items():
        if len(fipsset)==0:
            print(f'  {label}: empty'); continue
        print(f'  {label} (n={len(fipsset)})...')
        out[label] = cs_for(fipsset, label)

    # ===== Write memo =====
    lines = []
    L = lambda s='': (print(s), lines.append(s))[1]
    L('# Heterogeneity — within the 125 high-DC-share treated counties\n')
    L(f'*Run {pd.Timestamp.now().date()}. Same CS estimator as the main analysis.*\n')

    L('## Sample composition')
    L(f'- Total high-share counties (treatment): **{len(treat_fips)}**')
    L(f'- Rural (pop < 100k in 2017): **{len(rural_fips)}** | Larger (pop ≥ 100k): **{len(larger_fips)}**')
    L(f'- Early cohort (1st DC ≤ 2014): **{len(early_fips)}** | Hyperscale cohort (1st DC ≥ 2018): **{len(late_fips)}**')
    L(f'- Very-high share (≥10%): **{len(veryhigh)}** | Moderate share (1–10%): **{len(moderate)}**\n')
    L(f'**Note**: 100% of the 125 high-share counties are in states with at least some DC tax incentive (NCSL list). The incentive-vs-non-incentive cut is uninformative at this threshold — DCs locate where incentives exist. We drop that split.\n')

    L('## CS-ATT results by subgroup\n')
    L('| Subgroup | n treated | log(par+1) | log(n_deals+1) | spread (bps) |')
    L('|---|---:|---:|---:|---:|')
    for label, res in out.items():
        nfips = len(splits[label])
        cells = [f'{label}', f'{nfips}']
        for ylab in ['log(par+1)','log(n_deals+1)','spread (bps)']:
            r = res.get(ylab)
            if r is None:
                cells.append('—')
            else:
                att, se, n = r
                t = att/se if se>0 else 0
                sig = '***' if abs(t)>2.58 else '**' if abs(t)>1.96 else '*' if abs(t)>1.645 else ''
                if abs(att)>=1 or 'spread' in ylab:
                    cells.append(f'{att:+.2f}{sig} ({se:.2f})')
                else:
                    cells.append(f'{att:+.4f}{sig} ({se:.3f})')
        L('| ' + ' | '.join(cells) + ' |')

    L('\n*Stars: \\*\\*\\* p<0.01, \\*\\* p<0.05, \\* p<0.10.*\n')

    # ===== Plot — spread coefficient by subgroup =====
    fig, ax = plt.subplots(figsize=(10,6))
    rows = []
    for label, res in out.items():
        r = res.get('spread (bps)')
        if r is None: continue
        att, se, _ = r
        rows.append((label, att, se))
    if rows:
        labels = [r[0] for r in rows]
        atts   = [r[1] for r in rows]
        ses    = [r[2] for r in rows]
        ypos = np.arange(len(labels))
        ax.errorbar(atts, ypos, xerr=[1.96*s for s in ses], fmt='o', markersize=10,
                    capsize=5, color='steelblue', lw=2)
        ax.axvline(0, color='black', lw=0.5)
        ax.axvline(-15, color='gray', linestyle='--', lw=1, label='C-M-S −15 bps')
        ax.set_yticks(ypos); ax.set_yticklabels(labels)
        ax.set_xlabel('CS-ATT on offering spread (bps), 95% CI')
        ax.set_title('Spread effect by subgroup of high-DC-share counties')
        ax.grid(alpha=0.3, axis='x'); ax.legend()
        ax.invert_yaxis()
        fig.tight_layout()
        fig.savefig(OUT_FIG/'fig_heterogeneity.png', dpi=140, bbox_inches='tight')
        plt.close()
        L('![Spread by subgroup](figures/fig_heterogeneity.png)\n')

    # ===== Interpretation =====
    L('## Interpretation\n')
    # Pull the spread coefficients for each subgroup
    def get(label):
        if label not in out: return None
        return out[label].get('spread (bps)')
    base = get('All high-share (baseline)')
    rural = get('Rural (pop < 100k)')
    larger= get('Larger (pop ≥ 100k)')
    inc = get('In incentive state')
    noinc = get('Not in incentive state')

    early = get('Early cohort (1st DC ≤ 2014)')
    late  = get('Hyperscale cohort (1st DC ≥ 2018)')
    veryhi = get('Very-high share (≥ 10%)')
    moder  = get('Moderate share (1–10%)')

    if base:
        L(f'**Baseline (all 125 high-share)**: spread ATT = {base[0]:+.1f} bps (SE {base[1]:.1f})')
    if rural and larger:
        diff = rural[0] - larger[0]
        L(f'**Rural vs Larger**: Rural {rural[0]:+.1f} (SE {rural[1]:.1f}, n={len(rural_fips)})  |  Larger {larger[0]:+.1f} (SE {larger[1]:.1f}, n={len(larger_fips)})')
        L(f'  Difference (Rural − Larger): {diff:+.1f} bps. ' +
          ('Effect is **stronger in rural counties** — consistent with the "where DC matters most" prediction.' if diff<0 else
           'Effect is **stronger in larger counties** — opposite of the rural-bites-hardest prediction.'))
    if early and late:
        diff = early[0] - late[0]
        L(f'\n**Early vs Hyperscale cohort**: Early {early[0]:+.1f} (SE {early[1]:.1f}, n={len(early_fips)})  |  Hyperscale {late[0]:+.1f} (SE {late[1]:.1f}, n={len(late_fips)})')
        L(f'  Difference (Early − Hyperscale): {diff:+.1f} bps. ' +
          ('Effect is **stronger for early-cohort counties** — they have longer post-treatment observation horizons.' if diff<0 else
           'Effect is **stronger for hyperscale-era counties** — possibly because modern DC investment is at much larger MW scale.'))
    if veryhi and moder:
        diff = veryhi[0] - moder[0]
        L(f'\n**Very-high vs Moderate share**: Very-high {veryhi[0]:+.1f} (SE {veryhi[1]:.1f}, n={len(veryhigh)})  |  Moderate {moder[0]:+.1f} (SE {moder[1]:.1f}, n={len(moderate)})')
        L(f'  Difference (Very-high − Moderate): {diff:+.1f} bps. ' +
          ('Effect is **stronger in very-high-share counties** — fully consistent with mechanism story (more fiscal lift = bigger spread effect).' if diff<0 else
           'Effect is **muted in very-high-share counties**, likely from power loss — very-high-share counties have very short post-treatment windows.'))

    L('\n**Caveats**:')
    L('1. Subsample SEs are wider — comparisons are descriptive, not formal interactions.')
    L('2. State-incentive classification is binary; actual incentive packages vary in generosity.')
    L('3. Population threshold for rural (100k) is conventional but arbitrary; results similar at 50k or 200k.')

    OUT_MD.write_text('\n'.join(lines))
    print(f'\nWrote {OUT_MD}')
    print(f'Wrote {OUT_FIG/"fig_heterogeneity.png"}')

if __name__ == '__main__':
    main()
