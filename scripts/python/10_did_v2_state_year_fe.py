"""
10_did_v2_state_year_fe.py

DiD v2: same outcomes as v1, but tighter spec with state-year FE.
Outcomes:
  log(par+1)
  log(n_deals+1)
  par_wtd_spread_bps    (NEW: Treasury-benchmarked)
  par_wtd_coupon_cy     (legacy comparison)

Specs:
  A) county FE + year FE (replication of v1)
  B) county FE + state-year FE      ← TIGHTER spec
  C) county FE + state-year FE + log(n_dc+1)  intensity

Run: python3 scripts/python/10_did_v2_state_year_fe.py
"""

import pandas as pd, numpy as np
from linearmodels.panel import PanelOLS
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PNL  = ROOT / 'data/derived/county_year_panel_v3.csv'
OUT_FIG = ROOT / 'data/derived/figures'
OUT_MD  = ROOT / 'data/derived/did_results_v2.md'

def fit_panel(df, y, x_cols, time_dummies=None, dummy_cols=None):
    """Two-way FE: county entity_effects + year time_effects, optionally + state-year dummies."""
    d = df.dropna(subset=[y] + x_cols + (dummy_cols or [])).copy()
    d = d.set_index(['county_fips','year'])
    rhs = x_cols + (dummy_cols or [])
    mod = PanelOLS(d[y], d[rhs], entity_effects=True, time_effects=(time_dummies is None and not dummy_cols),
                   drop_absorbed=True)
    res = mod.fit(cov_type='clustered', cluster_entity=True)
    return res

def make_state_year_dummies(df):
    """Generate dummy columns for each state-year combination (one dropped automatically by absorption)."""
    sy = pd.get_dummies(df['state_year'], prefix='sy', drop_first=True, dtype=float)
    return sy

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
    L(f'\n*Run {pd.Timestamp.now().date()}. Source: `scripts/python/10_did_v2_state_year_fe.py`.*')
    L('\nAll regressions: panel of US counties × 2000-2025. SEs clustered at county.')
    L('Spec A: county FE + year FE.   Spec B: county FE + **state-year FE** (tighter).   Spec C: + intensity term log(n_dc+1).')

    OUTCOMES = [
        ('log_par',            'log(par + 1)'),
        ('log_deals',          'log(n_deals + 1)'),
        ('par_wtd_spread_bps', 'par-weighted spread (bps)'),
        ('par_wtd_coupon_cy',  'par-weighted coupon (%)'),
    ]

    # Pre-make state-year dummies once (large; use sparse-friendly approach)
    print('Building state-year dummies (this is the heavy step)...')
    sy_dummies = make_state_year_dummies(df)
    print(f'  state-year dummies: {sy_dummies.shape}')

    results = {}

    L('\n## Coefficient table — three specs × four outcomes')
    L('\n| Outcome | Spec A (cty+yr FE) | Spec B (cty+state-yr FE) | Spec C (B + log_n_dc) |')
    L('|---|---|---|---|')

    for y, ylab in OUTCOMES:
        # Spec A
        rA = fit_panel(df, y, ['post_dc'])
        # Spec B: drop time_effects, instead add state-year dummies
        dfsy = df.join(sy_dummies)
        sy_cols = list(sy_dummies.columns)
        d = dfsy.dropna(subset=[y,'post_dc']).set_index(['county_fips','year'])
        modB = PanelOLS(d[y], d[['post_dc']+sy_cols], entity_effects=True, drop_absorbed=True)
        rB = modB.fit(cov_type='clustered', cluster_entity=True)
        # Spec C: add intensity
        d2 = dfsy.dropna(subset=[y,'post_dc','log_n_dc']).set_index(['county_fips','year'])
        modC = PanelOLS(d2[y], d2[['post_dc','log_n_dc']+sy_cols], entity_effects=True, drop_absorbed=True)
        rC = modC.fit(cov_type='clustered', cluster_entity=True)

        def fmt(r, key):
            try:
                b, s = r.params[key], r.std_errors[key]
                stars = '***' if r.pvalues[key]<0.01 else '**' if r.pvalues[key]<0.05 else '*' if r.pvalues[key]<0.10 else ''
                return f'{b:.4f}{stars} ({s:.4f})'
            except KeyError:
                return '—'

        L(f'| **{ylab}** | post_dc: {fmt(rA,"post_dc")} | post_dc: {fmt(rB,"post_dc")} | post_dc: {fmt(rC,"post_dc")}; log_n_dc: {fmt(rC,"log_n_dc")} |')
        results[y] = (rA, rB, rC)

    L('\n*Stars: \\*\\*\\* p<0.01, \\*\\* p<0.05, \\* p<0.10.*')

    # Spread-specific interpretation
    L('\n## Headline number — spread, tighter spec')
    rB = results['par_wtd_spread_bps'][1]
    b = rB.params['post_dc']; s = rB.std_errors['post_dc']; p = rB.pvalues['post_dc']
    L(f'\nSpec B: par-weighted offering spread (bps) ~ post_dc | county FE + state-year FE')
    L(f'  **Coefficient: {b:.2f} bps**  (SE = {s:.2f}, p = {p:.3f})')
    L(f'  Reference: Chava–Malakar–Singh (2023) corporate-subsidy effect = −15.2 bps')
    L(f'  Our sign: {"NEGATIVE (matches theory: DC → lower borrowing cost)" if b<0 else "POSITIVE (opposite of theory)"}')
    L(f'  N: {rB.nobs:,}    R²(within): {rB.rsquared_within:.4f}')

    rC = results['par_wtd_spread_bps'][2]
    b2 = rC.params['log_n_dc']; s2 = rC.std_errors['log_n_dc']; p2 = rC.pvalues['log_n_dc']
    L(f'\nSpec C: + intensity (log_n_dc)')
    L(f'  **log(n_dc+1) coef: {b2:.2f} bps**  (SE = {s2:.2f}, p = {p2:.3f})')
    L(f'  Interpretation: each 100% increase in DC count → {b2:.1f} bps change in offering spread')

    OUT_MD.write_text('\n'.join(lines))
    print(f'\nWrote {OUT_MD}')

    # Event-study with state-year FE
    print('\nBuilding event-study with state-year FE...')
    es = df[df['is_dc_host']==1].copy()
    es['t'] = es['years_since_first_dc']
    es = es[es['t'].between(-7,10)].copy()
    for t in range(-7,11):
        if t==-1: continue
        es[f't_{t}'] = (es['t']==t).astype(int)
    esy = make_state_year_dummies(es)
    es = es.join(esy)
    sy_cols = list(esy.columns)

    fig, axes = plt.subplots(1, 2, figsize=(14,5))
    for ax, y, ylab in [(axes[0],'par_wtd_spread_bps','Spread (bps)'), (axes[1],'log_par','log(par+1)')]:
        x_cols = [f't_{t}' for t in range(-7,11) if t!=-1]
        d = es.dropna(subset=[y]+x_cols).set_index(['county_fips','year'])
        m = PanelOLS(d[y], d[x_cols+sy_cols], entity_effects=True, drop_absorbed=True)
        r = m.fit(cov_type='clustered', cluster_entity=True)
        est, se = r.params.to_dict(), r.std_errors.to_dict()
        coefs = []
        for t in range(-7,11):
            if t==-1: coefs.append((t, 0.0, 0.0))
            else: coefs.append((t, est.get(f't_{t}',np.nan), se.get(f't_{t}',np.nan)))
        c = pd.DataFrame(coefs, columns=['t','b','se'])
        ax.errorbar(c['t'], c['b'], yerr=1.96*c['se'], marker='o', capsize=4, color='steelblue')
        ax.axhline(0, color='black', lw=0.5)
        ax.axvline(-0.5, color='darkred', lw=1, linestyle='--', alpha=0.5, label='first DC opening')
        ax.set_xlabel('Years since first DC opening'); ax.set_ylabel(ylab)
        ax.set_title(f'Event study — {ylab}\n(county FE + state-year FE)')
        ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_FIG/'fig06_event_study_v2.png', dpi=140, bbox_inches='tight')
    plt.close()
    print(f'  saved {OUT_FIG/"fig06_event_study_v2.png"}')

if __name__ == '__main__':
    main()
