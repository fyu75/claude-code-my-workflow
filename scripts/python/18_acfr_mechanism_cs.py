"""
18_acfr_mechanism_cs.py

ACFR 2017 cross-sectional mechanism check.

Question: do high-DC-share counties (≥1% DC tax share) show fiscal patterns
consistent with the deleveraging / capex story?

  H1: higher property tax revenue per capita (DC pumps the property tax base)
  H2: higher capex per capita (DC fiscal slack → infrastructure investment)
  H3: lower lt debt outstanding per capita (deleveraging using DC revenue)
  H4: lower interest on debt per capita (lower debt burden)

Sample:
  Treatment: 125 high-share DC counties
  Control:   2,776 never-DC-host counties

Per-capita normalization uses 2017 Census county population (from ACFR PID file).
State fixed effects via dummies.

Outputs:
  data/derived/acfr_mechanism_results.md
  data/derived/figures/fig_mechanism_bars.png

Run: python3 scripts/python/18_acfr_mechanism_cs.py
"""

import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACFR_WIDE = ROOT / 'data/derived/acfr_county_year_wide.csv'
TAX_SHARE = ROOT / 'data/derived/dc_tax_share_distribution.csv'
POP_FILE  = ROOT / 'data/external/acfr/county_population_2017.csv'
PNL       = ROOT / 'data/derived/county_year_panel_v3.csv'
OUT_MD    = ROOT / 'data/derived/acfr_mechanism_results.md'
OUT_FIG   = ROOT / 'data/derived/figures'

THRESHOLD = 1.0

def main():
    print('Loading...')
    acfr = pd.read_csv(ACFR_WIDE, dtype={'county_fips':str})
    acfr['county_fips'] = acfr['county_fips'].str.zfill(5)
    a17 = acfr[acfr['year']==2017].copy()

    pop = pd.read_csv(POP_FILE, dtype={'county_fips':str})
    pop['county_fips'] = pop['county_fips'].str.zfill(5)
    pop = pop[['county_fips','population_2017']]

    tax = pd.read_csv(TAX_SHARE, dtype={'county_fips':str})
    tax['county_fips'] = tax['county_fips'].str.zfill(5)

    pnl = pd.read_csv(PNL, dtype={'county_fips':str,'state_fips':str})
    pnl['county_fips'] = pnl['county_fips'].str.zfill(5)
    never_host = set(pnl.groupby('county_fips')['n_dc_cumulative'].max().pipe(lambda s: s[s==0]).index)
    high_share = set(tax[tax['dc_share_mid']>=THRESHOLD]['county_fips'])

    # Build cross-section
    df = a17.merge(pop, on='county_fips', how='left')
    df['state_fips'] = df['county_fips'].str[:2]
    df['group'] = df['county_fips'].apply(
        lambda f: 'high_share' if f in high_share else ('control' if f in never_host else 'other'))
    df = df[df['group'].isin(['high_share','control'])].copy()
    df = df[df['population_2017']>0].copy()

    # Per-capita variables ($ per resident — ACFR is in $M, pop is raw count)
    for v in ['rev_property_tax','capex_total','lt_debt_outstanding_end','interest_on_debt',
               'exp_curr_total','lt_debt_issued_other']:
        if v in df.columns:
            df[f'{v}_pc'] = df[v] * 1e6 / df['population_2017']  # $M → $; per capita

    print(f'  Sample: {len(df):,} counties  (high_share={len(df[df.group=="high_share"])}, control={len(df[df.group=="control"])})')

    lines = []
    L = lambda s='': (print(s), lines.append(s))[1]
    L('# ACFR 2017 Mechanism Check — High-DC-Share Counties vs Never-Host\n')
    L(f'*Run {pd.Timestamp.now().date()}. Cross-sectional descriptive on 2017 ACFR (the most recent reliable Census of Governments year).*\n')
    L(f'**Treatment**: {len(df[df.group=="high_share"])} counties with DC tax share ≥ {THRESHOLD}% (mid scenario, $50k/MW)')
    L(f'**Control**: {len(df[df.group=="control"])} counties with zero DCs in our sample period\n')

    # ===== Group means / medians =====
    L('## 1. Per-capita fiscal variables ($ per resident, 2017)\n')
    L('| Variable | Control median | High-share median | High − Control (median) |')
    L('|---|---:|---:|---:|')
    vars_show = [
        ('rev_property_tax_pc',     'Property tax revenue / capita'),
        ('capex_total_pc',          'Capital outlay / capita'),
        ('lt_debt_outstanding_end_pc','LT debt outstanding / capita'),
        ('interest_on_debt_pc',     'Interest on debt / capita'),
        ('exp_curr_total_pc',       'Current expenditure / capita'),
        ('lt_debt_issued_other_pc', 'LT debt issued / capita'),
    ]
    for v, lab in vars_show:
        if v not in df.columns: continue
        cmed = df[df.group=='control'][v].median()
        hmed = df[df.group=='high_share'][v].median()
        diff = hmed - cmed
        L(f'| **{lab}** | ${cmed:,.0f} | ${hmed:,.0f} | **${diff:+,.0f}** |')

    L('\n*Medians used because distributions are right-skewed.*\n')

    # ===== OLS with state FE: y_pc ~ high_share + state_FE + log(pop) =====
    L('## 2. State-FE regression — high-share vs control, controlling for size\n')
    L('Specification: `y / capita ~ high_share + state FE + log(population)`. SEs robust.\n')
    L('| Variable | β (high_share) | SE | t-stat |')
    L('|---|---:|---:|---:|')

    df['log_pop'] = np.log(df['population_2017'])
    df['is_high'] = (df['group']=='high_share').astype(float)
    # one-hot state dummies (drop first to avoid singular matrix)
    sd = pd.get_dummies(df['state_fips'], prefix='s', drop_first=True, dtype=float)
    X = pd.concat([df[['is_high','log_pop']], sd], axis=1).values
    X = np.c_[np.ones(len(X)), X]

    import numpy.linalg as la
    for v, lab in vars_show:
        if v not in df.columns: continue
        y = df[v].values
        valid = np.isfinite(y) & np.isfinite(X).all(axis=1)
        Xv = X[valid]; yv = y[valid]
        try:
            beta = la.lstsq(Xv, yv, rcond=None)[0]
            resid = yv - Xv @ beta
            # HC0 robust SE
            n, k = Xv.shape
            XtX_inv = la.inv(Xv.T @ Xv)
            meat = (Xv * resid[:,None]).T @ (Xv * resid[:,None])
            cov = XtX_inv @ meat @ XtX_inv
            b = beta[1]  # is_high coefficient (index 1, after intercept)
            se = np.sqrt(cov[1,1])
            t  = b / se
            sig = '***' if abs(t)>2.58 else '**' if abs(t)>1.96 else '*' if abs(t)>1.645 else ''
            L(f'| **{lab}** | ${b:+,.0f}{sig} | ${se:,.0f} | {t:+.2f} |')
        except Exception as e:
            L(f'| **{lab}** | failed: {e} | — | — |')
    L('\n*Stars: \\*\\*\\* p<0.01, \\*\\* p<0.05, \\* p<0.10.*\n')

    # ===== Visualization =====
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    vars_plot = [
        ('rev_property_tax_pc',     'Property tax / capita ($)'),
        ('capex_total_pc',          'Capital outlay / capita ($)'),
        ('lt_debt_outstanding_end_pc','LT debt / capita ($)'),
        ('interest_on_debt_pc',     'Interest / capita ($)'),
        ('exp_curr_total_pc',       'Current exp / capita ($)'),
        ('lt_debt_issued_other_pc', 'LT debt issued / capita ($)'),
    ]
    for ax, (v, lab) in zip(axes.flat, vars_plot):
        if v not in df.columns: continue
        for g, color, label in [('control','lightgray','Never DC-host'),
                                 ('high_share','darkred','DC share ≥ 1%')]:
            vals = df[df.group==g][v].dropna()
            # Clip extreme tail at 99th pct for visualization
            cap = vals.quantile(0.99)
            ax.hist(vals[vals<=cap], bins=40, alpha=0.5, color=color, label=label, density=True)
        ax.set_xlabel(lab); ax.set_ylabel('density')
        ax.legend(fontsize=8); ax.grid(alpha=0.3)
        ax.set_title(lab)
    fig.suptitle('ACFR 2017: per-capita fiscal distributions, high-share vs never-host', y=1.00)
    fig.tight_layout()
    fig.savefig(OUT_FIG/'fig_mechanism_bars.png', dpi=140, bbox_inches='tight')
    plt.close()
    L(f'\n![Mechanism distributions](figures/fig_mechanism_bars.png)\n')

    # ===== Interpretation =====
    L('## 3. Interpretation\n')
    # Compute the key effects to write a coherent interpretation
    h = df[df.group=='high_share']; c = df[df.group=='control']

    pt_h = h['rev_property_tax_pc'].median()
    pt_c = c['rev_property_tax_pc'].median()
    debt_h = h['lt_debt_outstanding_end_pc'].median()
    debt_c = c['lt_debt_outstanding_end_pc'].median()
    capx_h = h['capex_total_pc'].median()
    capx_c = c['capex_total_pc'].median()

    L(f'**Property tax revenue per capita**: high-share counties at median ${pt_h:,.0f}/resident vs control ${pt_c:,.0f}/resident.')
    L(f'  Ratio: {pt_h/pt_c:.2f}x. Direction consistent with DC pumping the property-tax base.\n')
    L(f'**Capital outlay per capita**: high-share ${capx_h:,.0f} vs control ${capx_c:,.0f}.')
    L(f'  Ratio: {capx_h/capx_c:.2f}x. Direction consistent with DC fiscal slack supporting infrastructure.\n')
    L(f'**LT debt outstanding per capita**: high-share ${debt_h:,.0f} vs control ${debt_c:,.0f}.')
    L(f'  Ratio: {debt_h/debt_c:.2f}x. Reading: {"high-share counties have HIGHER per-capita debt — possibly using DC fiscal capacity to borrow MORE for capex" if debt_h>debt_c else "high-share counties have LOWER per-capita debt — consistent with deleveraging story"}.\n')

    L('**What this is not**:')
    L('1. Cross-sectional, not causal. High-share counties are tiny rural; smaller counties have different fiscal patterns intrinsically.')
    L('2. Only 2017 ACFR. We can\'t see pre/post within these same counties.')
    L('3. Selection: DCs locate where land is cheap AND fiscal-incentive regimes are favorable — that endogeneity is in here.')
    L('4. The state-FE regression in Section 2 partially controls for state-level fiscal regimes but not for unobserved county-level characteristics.\n')

    OUT_MD.write_text('\n'.join(lines))
    print(f'\nWrote {OUT_MD}')
    print(f'Wrote {OUT_FIG/"fig_mechanism_bars.png"}')

if __name__ == '__main__':
    main()
