"""
08_first_did.py

First-cut DiD regressions on the county-year panel.

Specifications (each with county FE + state-year FE, county-clustered SEs):
  Outcome 1: log(par_total_M + 1)         — issuance volume
  Outcome 2: log(n_deals + 1)              — issuance count
  Outcome 3: par_wtd_coupon_cy             — par-weighted coupon (yield proxy)

Treatment variable: treated_t (1 if county has had at least one DC operational by year)

Caveats noted in output:
  * DiD here is descriptive, NOT identified — DC siting is endogenous.
  * Coupon outcome is a noisy yield proxy; absence of Treasury benchmark.
  * NYC excluded from SDC issuers but counties still in skeleton (no SDC data).

Outputs:
  data/derived/figures/fig05_event_study_coupon.png
  data/derived/figures/fig06_event_study_par.png
  data/derived/did_results.md

Run: python3 scripts/python/08_first_did.py
"""

import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from linearmodels.panel import PanelOLS
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PNL  = ROOT / 'data/derived/county_year_panel_v2.csv'
OUT_FIG = ROOT / 'data/derived/figures'
OUT_FIG.mkdir(parents=True, exist_ok=True)
OUT_MD = ROOT / 'data/derived/did_results.md'

def fit(df, y, x_cols, cluster):
    """Two-way FE PanelOLS: county FE (entity_effects) + year FE absorbed via entity_effects + time_effects.
    state-year FE done by dropping state-year means via residualization here just uses entity + time effects.
    cluster: pass entity (county) for clustering.
    """
    d = df.dropna(subset=[y] + x_cols).copy()
    d = d.set_index(['county_fips','year'])
    mod = PanelOLS(d[y], d[x_cols], entity_effects=True, time_effects=True, drop_absorbed=True)
    res = mod.fit(cov_type='clustered', cluster_entity=True)
    return res

def main():
    print('Loading panel...')
    df = pd.read_csv(PNL, dtype={'county_fips':str,'state_fips':str})
    df['county_fips'] = df['county_fips'].str.zfill(5)
    df['state_fips']  = df['state_fips'].str.zfill(2)
    df['state_year']  = df['state_fips'] + '_' + df['year'].astype(str)
    df['log_par']     = np.log1p(df['par_total_M'])
    df['log_deals']   = np.log1p(df['n_deals'])
    df['log_n_dc']    = np.log1p(df['n_dc_cumulative'])
    df['post_dc']     = df['treated_t'].astype(int)

    # Diagnostics
    print(f'  rows: {len(df):,}')
    print(f'  counties: {df.county_fips.nunique():,}')
    print(f'  DC-host counties: {df["is_dc_host"].astype(bool).groupby(df["county_fips"]).any().sum():,}')

    lines = []
    def L(s=''): print(s); lines.append(s)

    L('# First-Cut DiD Results — County-Year Panel')
    L(f'\n*Run {pd.Timestamp.now().date()}. Source: `scripts/python/08_first_did.py`.*')
    L('\n## Specifications\n')
    L('All regressions include **county fixed effects** (absorb time-invariant county heterogeneity)')
    L('and **year fixed effects** (absorb common macro shocks). Standard errors clustered at the county level.')
    L('Sample: 2000–2025, balanced county-year panel, 3,143 counties × 26 years.\n')
    L('**Caveats** (this is descriptive only — not causal identification):')
    L('- DC siting is endogenous (correlated with local economic conditions).')
    L('- No state×year FE in this first cut (degree-of-freedom heavy with 26 years × 51 states); add in v2.')
    L('- Coupon outcome lacks a Treasury benchmark — interpret only as a relative measure.')
    L('- The `post_dc` indicator is a binary "ever-treated × post" — does NOT distinguish DC count or MW intensity.')

    L('\n## Spec 1: Issuance volume, `log(par + 1) ~ post_dc`')
    res = fit(df, 'log_par', ['post_dc'], cluster='county_fips')
    L(f'```\n{res}\n```')
    L(f'**Coef on post_dc: {res.params["post_dc"]:.4f}  SE: {res.std_errors["post_dc"]:.4f}  t: {res.tstats["post_dc"]:.2f}  p: {res.pvalues["post_dc"]:.4f}**')
    L(f'Interpret: in counties that get a DC, log(par+1) changes by {res.params["post_dc"]:.3f} on average post-DC.')

    L('\n## Spec 2: Issuance count, `log(n_deals + 1) ~ post_dc`')
    res = fit(df, 'log_deals', ['post_dc'], cluster='county_fips')
    L(f'```\n{res}\n```')
    L(f'**Coef on post_dc: {res.params["post_dc"]:.4f}  SE: {res.std_errors["post_dc"]:.4f}  t: {res.tstats["post_dc"]:.2f}  p: {res.pvalues["post_dc"]:.4f}**')

    L('\n## Spec 3: Par-weighted coupon, `par_wtd_coupon_cy ~ post_dc`')
    L('(restricted to county-years with coupon data)\n')
    res = fit(df, 'par_wtd_coupon_cy', ['post_dc'], cluster='county_fips')
    L(f'```\n{res}\n```')
    L(f'**Coef on post_dc: {res.params["post_dc"]:.4f}  SE: {res.std_errors["post_dc"]:.4f}  t: {res.tstats["post_dc"]:.2f}  p: {res.pvalues["post_dc"]:.4f}**')
    L(f'Interpret: in counties that get a DC, par-weighted coupon changes by {res.params["post_dc"]*100:.1f} bps on average post-DC.')

    L('\n## Spec 4: Intensity — log(par+1) ~ log(n_dc+1)')
    res = fit(df, 'log_par', ['log_n_dc'], cluster='county_fips')
    L(f'```\n{res}\n```')
    L(f'**Coef on log_n_dc: {res.params["log_n_dc"]:.4f}  SE: {res.std_errors["log_n_dc"]:.4f}**')
    L(f'Elasticity interpretation: a 10% increase in DC count → {res.params["log_n_dc"]*0.1:.4f} log change in par issuance.')

    L('\n## Spec 5: Intensity on coupon — coupon ~ log(n_dc+1)')
    res = fit(df, 'par_wtd_coupon_cy', ['log_n_dc'], cluster='county_fips')
    L(f'```\n{res}\n```')
    L(f'**Coef: {res.params["log_n_dc"]:.4f}**, *p={res.pvalues["log_n_dc"]:.3f}*')

    # === Event study ===
    L('\n## Event study: coupon and par by years-since-first-DC')
    L('(DC-host counties only; t=0 is first-DC year; reference period t=-1)\n')
    es = df[df['is_dc_host']==1].copy()
    es['t'] = es['years_since_first_dc']
    es = es[es['t'].between(-7, 10)].copy()
    # Drop t = -1 as reference; binary indicators for each
    for t in range(-7, 11):
        if t == -1: continue
        es[f't_{t}'] = (es['t']==t).astype(int)

    # Run two outcomes
    fig, axes = plt.subplots(1, 2, figsize=(14,5))
    for ax, y, ylab in [(axes[0],'par_wtd_coupon_cy','Par-weighted coupon (%)'),
                         (axes[1],'log_par','log(par + 1)')]:
        x_cols = [f't_{t}' for t in range(-7,11) if t!=-1]
        try:
            r = fit(es, y, x_cols, cluster='county_fips')
            est = r.params.to_dict()
            se  = r.std_errors.to_dict()
            coefs = []
            for t in range(-7, 11):
                if t==-1:
                    coefs.append((t, 0.0, 0.0))
                else:
                    k = f't_{t}'
                    coefs.append((t, est.get(k, np.nan), se.get(k, np.nan)))
            coefs = pd.DataFrame(coefs, columns=['t','b','se'])
            ax.errorbar(coefs['t'], coefs['b'], yerr=1.96*coefs['se'],
                        marker='o', capsize=4, color='steelblue')
            ax.axhline(0, color='black', lw=0.5)
            ax.axvline(-0.5, color='darkred', lw=1, linestyle='--', alpha=0.5, label='first DC opening')
            ax.set_xlabel('Years since first DC opening'); ax.set_ylabel(ylab)
            ax.set_title(f'Event study — {ylab}')
            ax.legend(); ax.grid(alpha=0.3)
        except Exception as e:
            ax.text(0.5,0.5,f'Failed: {e}',ha='center'); print(f'  {y}: {e}')

    fig.suptitle('Event-study coefficients (95% CI), DC-host counties only', y=1.02)
    fig.tight_layout()
    fig.savefig(OUT_FIG/'fig05_event_study.png', dpi=140, bbox_inches='tight')
    plt.close()
    L(f'Saved event-study plot: `data/derived/figures/fig05_event_study.png`')

    OUT_MD.write_text('\n'.join(lines))
    print(f'\nWrote {OUT_MD}')

if __name__ == '__main__':
    main()
