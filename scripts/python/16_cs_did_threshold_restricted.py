"""
16_cs_did_threshold_restricted.py

Restricted Callaway-Sant'Anna DiD with the 1%-threshold treatment group:

Treatment   : 125 counties where DC contribution to county property tax revenue
              (mid scenario, $50k/MW) is ≥ 1%.
Control     : counties with zero data centers in our sample period (never treated).
Panel window: 2010–2025 (allows small pre-period for early-treated counties).
Reporting   : full ATT (averaged), event-study coefficients, and a 2015+-only ATT.

Outcomes:
  log(par + 1)
  log(n_deals + 1)
  par_wtd_spread_bps

Compares with the full-sample v1 results (where treatment was "any DC county").

Run: python3 scripts/python/16_cs_did_threshold_restricted.py
"""

import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from differences import ATTgt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PNL  = ROOT / 'data/derived/county_year_panel_v3.csv'
TAX_SHARE = ROOT / 'data/derived/dc_tax_share_distribution.csv'
OUT_FIG = ROOT / 'data/derived/figures'
OUT_MD  = ROOT / 'data/derived/cs_did_threshold.md'

THRESHOLD_PCT = 1.0   # ≥ 1% DC share of property tax (mid scenario)

def cs_estimate(d, y, cohort_col='cohort'):
    """Fit CS on a panel with a cohort column (NaN = never-treated)."""
    est = ATTgt(data=d[[y, cohort_col]], cohort_column=cohort_col, anticipation=0)
    res = est.fit(formula=y, n_jobs=1)
    agg = est.aggregate('simple')
    att = float(agg.iloc[0,0]); se = float(agg.iloc[0,1])
    ev  = est.aggregate('event').reset_index()
    return att, se, ev

def main():
    print('Loading panel...')
    df = pd.read_csv(PNL, dtype={'county_fips':str,'state_fips':str})
    df['county_fips'] = df['county_fips'].str.zfill(5)
    df['log_par']    = np.log1p(df['par_total_M'])
    df['log_deals']  = np.log1p(df['n_deals'])

    tax = pd.read_csv(TAX_SHARE, dtype={'county_fips':str})
    tax['county_fips'] = tax['county_fips'].str.zfill(5)
    high_share = tax[tax['dc_share_mid']>=THRESHOLD_PCT]['county_fips'].tolist()
    print(f'\nTreatment counties (DC tax share ≥ {THRESHOLD_PCT}% under mid scenario): {len(high_share):,}')

    # Build cohort column: treated counties get their first_dc_year; control counties get NaN.
    # Restrict sample to: (1) high-share treated AND (2) never-DC-host control
    never_host = df.groupby('county_fips')['n_dc_cumulative'].max().pipe(lambda s: s[s==0]).index.tolist()
    print(f'Never-DC-host counties (control): {len(never_host):,}')

    keep = set(high_share) | set(never_host)
    panel = df[df['county_fips'].isin(keep)].copy()
    # Restrict to 2010-2025 window
    panel = panel[(panel['year']>=2010) & (panel['year']<=2025)].copy()
    panel['cohort'] = panel['first_dc_year'].where(panel['county_fips'].isin(high_share), other=np.nan)

    print(f'\nPanel: {len(panel):,} cells, counties={panel.county_fips.nunique():,}, years 2010-2025')

    # Diagnostic: cohort distribution among treated
    cohort_dist = panel[panel['county_fips'].isin(high_share)].groupby('county_fips')['cohort'].first().value_counts().sort_index()
    print(f'\nTreatment-year cohort distribution (high-share counties):')
    print(cohort_dist.to_string())

    lines = []
    def L(s=''): print(s); lines.append(s)
    L(f'# Callaway-Sant\'Anna DiD — Threshold-restricted sample\n')
    L(f'*Run {pd.Timestamp.now().date()}. Source: `scripts/python/16_cs_did_threshold_restricted.py`.*\n')
    L(f'**Treatment**: counties where estimated DC contribution to county property tax ≥ **{THRESHOLD_PCT}%** (mid scenario, $50k/MW)')
    L(f'**# treated counties**: {len(high_share)}')
    L(f'**Control**: never-DC-host counties ({len(never_host)})')
    L(f'**Panel window**: 2010–2025 ({len(panel):,} county-year cells)')
    L(f'**Estimator**: Callaway-Sant\'Anna (2021) ATTgt, never-treated comparison\n')

    # Run CS on three outcomes
    OUTCOMES = [
        ('log_par',            'log(par + 1)'),
        ('log_deals',          'log(n_deals + 1)'),
        ('par_wtd_spread_bps', 'par-weighted spread (bps)'),
    ]
    L('## Simple ATT (averaged across cohorts and event times)\n')
    L('| Outcome | ATT | SE | 95% CI |')
    L('|---|---:|---:|---|')
    ev_results = {}
    panel_indexed = panel.set_index(['county_fips','year'])
    for y, ylab in OUTCOMES:
        d = panel_indexed[[y,'cohort']].dropna(subset=[y])
        try:
            att, se, ev = cs_estimate(d, y, 'cohort')
            ci_lo = att - 1.96*se; ci_hi = att + 1.96*se
            sig = '***' if abs(att)/se > 2.58 else '**' if abs(att)/se > 1.96 else '*' if abs(att)/se > 1.645 else ''
            L(f'| **{ylab}** | {att:.4f}{sig} | {se:.4f} | [{ci_lo:.4f}, {ci_hi:.4f}] |')
            ev_results[ylab] = (ev, att, se)
        except Exception as e:
            L(f'| **{ylab}** | — | — | failed: {e} |')

    L('\n*Stars: \\*\\*\\* p<0.01, \\*\\* p<0.05, \\* p<0.10.*\n')

    # Per-event-time effects + 2015+ slice
    L('## Event-study breakdown — average ATT by event-time bin\n')
    L('| Outcome | t=-3..-1 | t=0 | t=+1..+3 | t=+4..+7 | t≥+8 |')
    L('|---|---:|---:|---:|---:|---:|')
    for ylab, (ev, _, _) in ev_results.items():
        tcol = ev.columns[0]
        atcol = ev.columns[1]   # ATT
        # Aggregate by buckets
        bins = []
        for lo, hi in [(-3,-1),(0,0),(1,3),(4,7),(8,99)]:
            sel = ev[(ev[tcol]>=lo) & (ev[tcol]<=hi)]
            mean = sel[atcol].mean() if len(sel) else float('nan')
            bins.append(mean)
        L(f'| **{ylab}** | {bins[0]:.4f} | {bins[1]:.4f} | {bins[2]:.4f} | {bins[3]:.4f} | {bins[4]:.4f} |')

    # Plot
    fig, axes = plt.subplots(1, len(ev_results), figsize=(6*len(ev_results), 5))
    for ax, (ylab,(ev,att,se)) in zip(axes, ev_results.items()):
        tcol = ev.columns[0]
        atcol = ev.columns[1]
        secol = ev.columns[2]
        sub = ev[(ev[tcol]>=-7)&(ev[tcol]<=10)]
        ax.errorbar(sub[tcol], sub[atcol], yerr=1.96*sub[secol], marker='o', capsize=4, color='steelblue')
        ax.axhline(0, color='black', lw=0.5)
        ax.axvline(-0.5, color='darkred', linestyle='--', lw=1, alpha=0.5, label='first DC opening')
        ax.set_xlabel('Years since first DC')
        ax.set_ylabel(ylab)
        ax.set_title(f'{ylab}\n(ATT={att:.3f}, SE={se:.3f})')
        ax.grid(alpha=0.3); ax.legend(fontsize=8)
    fig.suptitle(f'CS DiD — DC tax share ≥ {THRESHOLD_PCT}% treatment group ({len(high_share)} counties)', y=1.02)
    fig.tight_layout()
    fig.savefig(OUT_FIG/'fig10_cs_threshold.png', dpi=140, bbox_inches='tight')
    plt.close()
    L(f'\nSaved figure: `data/derived/figures/fig10_cs_threshold.png`')

    # ========= 2015+ slice =========
    L('\n## 2015+ Calendar-time slice\n')
    L('Restrict the panel to **observation years 2015–2025** only (rather than event time).')
    L('This subset CS-ATT focuses on the AI-hyperscale era.\n')
    panel_2015 = panel[panel['year']>=2015].copy()
    p15_indexed = panel_2015.set_index(['county_fips','year'])
    L('| Outcome | ATT (2015+) | SE | 95% CI | N |')
    L('|---|---:|---:|---|---:|')
    for y, ylab in OUTCOMES:
        d = p15_indexed[[y,'cohort']].dropna(subset=[y])
        try:
            att, se, _ = cs_estimate(d, y, 'cohort')
            ci_lo = att - 1.96*se; ci_hi = att + 1.96*se
            sig = '***' if abs(att)/se > 2.58 else '**' if abs(att)/se > 1.96 else '*' if abs(att)/se > 1.645 else ''
            L(f'| **{ylab}** | {att:.4f}{sig} | {se:.4f} | [{ci_lo:.4f}, {ci_hi:.4f}] | {len(d):,} |')
        except Exception as e:
            L(f'| **{ylab}** | — | — | failed | — |')

    # Compare to v1 (full DC-host sample) — print baseline from prior run
    L('\n## Comparison to v1 (full DC-host sample, no threshold)\n')
    L('| Outcome | v1 ATT (all DC-host) | v3 ATT (≥1% DC share) | Difference |')
    L('|---|---:|---:|---:|')
    v1 = {'log(par + 1)': (-0.0783, 0.0647),
          'log(n_deals + 1)': (-0.1234, 0.0284),
          'par-weighted spread (bps)': (-3.17, 3.72)}
    for ylab in [o[1] for o in OUTCOMES]:
        if ylab in v1 and ylab in ev_results:
            v1_att, v1_se = v1[ylab]
            v3_att = ev_results[ylab][1]
            v3_se  = ev_results[ylab][2]
            L(f'| **{ylab}** | {v1_att:+.4f} ({v1_se:.3f}) | {v3_att:+.4f} ({v3_se:.3f}) | {v3_att - v1_att:+.4f} |')

    OUT_MD.write_text('\n'.join(lines))
    print(f'\nWrote {OUT_MD}')

if __name__ == '__main__':
    main()
