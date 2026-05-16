"""
10b_did_v2_pyfixest.py

Re-run DiD v2 using pyfixest (much cleaner for multi-way FE):
  Spec A: y ~ post_dc | county + year                            (replication of v1)
  Spec B: y ~ post_dc | county + state^year                      (TIGHTER: state-year FE)
  Spec C: y ~ post_dc + log_n_dc | county + state^year           (intensity)

Outcomes:
  log(par+1), log(n_deals+1), par_wtd_spread_bps, par_wtd_coupon_cy

Run: python3 scripts/python/10b_did_v2_pyfixest.py
"""

import pandas as pd, numpy as np
import pyfixest as pf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PNL  = ROOT / 'data/derived/county_year_panel_v3.csv'
OUT_FIG = ROOT / 'data/derived/figures'
OUT_MD  = ROOT / 'data/derived/did_results_v2.md'

def fmt(b, s, p):
    stars = '***' if p<0.01 else '**' if p<0.05 else '*' if p<0.10 else ''
    return f'{b:.4f}{stars} ({s:.4f})'

def main():
    print('Loading panel v3...')
    df = pd.read_csv(PNL, dtype={'county_fips':str,'state_fips':str})
    df['county_fips'] = df['county_fips'].str.zfill(5)
    df['state_fips']  = df['state_fips'].str.zfill(2)
    df['state_year']  = df['state_fips'] + '_' + df['year'].astype(str)
    df['log_par']     = np.log1p(df['par_total_M'])
    df['log_deals']   = np.log1p(df['n_deals'])
    df['log_n_dc']    = np.log1p(df['n_dc_cumulative'])
    df['post_dc']     = df['treated_t'].astype(int)
    print(f'  rows: {len(df):,}    counties: {df.county_fips.nunique():,}')

    lines = []
    def L(s=''): print(s); lines.append(s)

    L('# DiD v2 — Tighter spec with state-year FE + spread outcome')
    L(f'\n*Run {pd.Timestamp.now().date()}. Source: `scripts/python/10b_did_v2_pyfixest.py`.*\n')
    L('All regressions: balanced county-year panel 2000-2025, SEs clustered at county_fips.')
    L('')
    L('| Spec | Fixed effects |')
    L('|---|---|')
    L('| A | county + year (two-way) |')
    L('| B | county + state×year (tighter — absorbs state-level boom dynamics) |')
    L('| C | county + state×year + log(n_dc+1) intensity |')

    OUTCOMES = [
        ('log_par',            'log(par + 1)'),
        ('log_deals',          'log(n_deals + 1)'),
        ('par_wtd_spread_bps', 'par-weighted spread (bps)'),
        ('par_wtd_coupon_cy',  'par-weighted coupon (%)'),
    ]

    rows = []
    for y, ylab in OUTCOMES:
        # Drop rows missing y
        d = df.dropna(subset=[y,'post_dc','log_n_dc'])
        # Spec A: county FE + year FE
        fA = pf.feols(f'{y} ~ post_dc | county_fips + year', data=d, vcov={'CRV1':'county_fips'})
        # Spec B: county FE + state-year FE
        fB = pf.feols(f'{y} ~ post_dc | county_fips + state_year', data=d, vcov={'CRV1':'county_fips'})
        # Spec C: + intensity
        fC = pf.feols(f'{y} ~ post_dc + log_n_dc | county_fips + state_year', data=d, vcov={'CRV1':'county_fips'})

        def get(r, key):
            try:
                tab = r.tidy()
                row = tab.loc[key] if key in tab.index else tab[tab.index.str.contains(key, regex=False)].iloc[0]
                return float(row['Estimate']), float(row['Std. Error']), float(row['Pr(>|t|)'])
            except Exception as e:
                return None, None, None

        bA, sA, pA = get(fA, 'post_dc')
        bB, sB, pB = get(fB, 'post_dc')
        bC, sC, pC = get(fC, 'post_dc')
        bDc, sDc, pDc = get(fC, 'log_n_dc')

        rows.append({
            'outcome': ylab,
            'A_post_dc': fmt(bA, sA, pA),
            'B_post_dc': fmt(bB, sB, pB),
            'C_post_dc': fmt(bC, sC, pC),
            'C_log_n_dc': fmt(bDc, sDc, pDc),
            'N_B': int(fB._N),
        })

    L('\n## Coefficient table')
    L('\n| Outcome | A: cty+yr FE | B: cty+state-yr FE | C: B + log_n_dc | N (B) |')
    L('|---|---|---|---|---:|')
    for r in rows:
        L(f'| **{r["outcome"]}** | {r["A_post_dc"]} | {r["B_post_dc"]} | post_dc: {r["C_post_dc"]}; log_n_dc: {r["C_log_n_dc"]} | {r["N_B"]:,} |')
    L('\n*Stars: \\*\\*\\* p<0.01, \\*\\* p<0.05, \\* p<0.10. SEs in parens, clustered by county.*')

    # === Event study with state-year FE ===
    L('\n## Event study (county + state-year FE)')
    es = df[df['is_dc_host']==1].copy()
    es['t'] = es['years_since_first_dc']
    es = es[es['t'].between(-7,10)].copy()
    es['t'] = es['t'].astype(int)
    # Use i() syntax: pyfixest supports i(t, ref=-1)
    fig, axes = plt.subplots(1, 2, figsize=(14,5))
    for ax, y, ylab in [(axes[0],'par_wtd_spread_bps','Spread (bps)'),
                         (axes[1],'log_par','log(par+1)')]:
        d = es.dropna(subset=[y])
        try:
            r = pf.feols(f'{y} ~ i(t, ref=-1) | county_fips + state_year', data=d,
                         vcov={'CRV1':'county_fips'})
            tab = r.tidy().reset_index().rename(columns={'index':'term'})
            tab['t_int'] = tab['term'].str.extract(r'C\(t\)\[T\.(-?\d+)\]').astype(float)
            tab = tab.dropna(subset=['t_int']).sort_values('t_int')
            # Add reference (t=-1, coef=0)
            ref = pd.DataFrame({'t_int':[-1],'Estimate':[0.0],'Std. Error':[0.0]})
            tab = pd.concat([tab[['t_int','Estimate','Std. Error']], ref], ignore_index=True).sort_values('t_int')
            ax.errorbar(tab['t_int'], tab['Estimate'], yerr=1.96*tab['Std. Error'],
                        marker='o', capsize=4, color='steelblue')
            ax.axhline(0, color='black', lw=0.5)
            ax.axvline(-0.5, color='darkred', lw=1, linestyle='--', alpha=0.5, label='first DC opening')
            ax.set_xlabel('Years since first DC opening'); ax.set_ylabel(ylab)
            ax.set_title(f'Event study — {ylab}')
            ax.legend(); ax.grid(alpha=0.3)
        except Exception as e:
            print(f'  ES {y} failed: {e}')
            ax.text(0.5,0.5,f'failed: {e}', ha='center', va='center')

    fig.suptitle('Event-study (county FE + state-year FE, 95% CI)', y=1.02)
    fig.tight_layout()
    fig.savefig(OUT_FIG/'fig06_event_study_v2.png', dpi=140, bbox_inches='tight')
    plt.close()
    L(f'\nSaved event-study plot: `data/derived/figures/fig06_event_study_v2.png`')

    OUT_MD.write_text('\n'.join(lines))
    print(f'\nWrote {OUT_MD}')

if __name__ == '__main__':
    main()
