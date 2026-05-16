"""
11_callaway_santanna.py

Callaway-Sant'Anna staggered DiD on the county-year panel.

Why this matters: TWFE with staggered treatment (different counties get first DC
in different years) is biased — early-treated units serve as controls for
later-treated units, contaminating the estimate (Goodman-Bacon decomposition).

The differences package's ATTgt estimator gives clean ATT(g,t) by treatment cohort
and event time, aggregated to a single ATT and event-study coefficients.

Outcomes:
  log_par, log_deals, par_wtd_spread_bps

Outputs:
  data/derived/cs_did_results.md
  data/derived/figures/fig07_cs_event_study.png

Run: python3 scripts/python/11_callaway_santanna.py
"""

import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from differences import ATTgt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PNL  = ROOT / 'data/derived/county_year_panel_v3.csv'
OUT_FIG = ROOT / 'data/derived/figures'
OUT_MD  = ROOT / 'data/derived/cs_did_results.md'

def main():
    print('Loading panel...')
    df = pd.read_csv(PNL, dtype={'county_fips':str,'state_fips':str})
    df['county_fips'] = df['county_fips'].str.zfill(5)
    df['state_fips']  = df['state_fips'].str.zfill(2)
    df['log_par']     = np.log1p(df['par_total_M'])
    df['log_deals']   = np.log1p(df['n_deals'])

    # CS DiD requires: treatment cohort variable (year of first treatment, 0 for never-treated)
    df['cohort'] = df['first_dc_year']  # NaN for never-treated (required by ATTgt)
    df['t'] = df['year'].astype(int)
    # Make panel multiindex (entity, time)
    df = df.sort_values(['county_fips','t']).set_index(['county_fips','t'])

    lines = []
    def L(s=''): print(s); lines.append(s)
    L('# Callaway-Sant\'Anna staggered DiD')
    L(f'\n*Run {pd.Timestamp.now().date()}. Source: `scripts/python/11_callaway_santanna.py`.*\n')
    L('Estimator: Callaway & Sant\'Anna (2021), `differences` Python package, ATTgt.')
    L('Control group: **never-treated** counties (counties with no DC opening 2000-2025).')
    L('Standard errors: bootstrap, clustered at county_fips.')
    L('')

    OUTCOMES = [
        ('log_par',            'log(par + 1)'),
        ('log_deals',          'log(n_deals + 1)'),
        ('par_wtd_spread_bps', 'par-weighted spread (bps)'),
    ]

    # Track results across outcomes for event-study plot
    es_results = {}

    L('## Single-coefficient ATT (averaged across cohorts and event times)\n')
    L('| Outcome | ATT | SE | 95% CI | N |')
    L('|---|---:|---:|---|---:|')

    for y, ylab in OUTCOMES:
        d = df[[y,'cohort']].copy().rename(columns={'cohort':'cohort_t','year':'__dummy__'} if 'cohort' not in df.columns else {})
        d = d.dropna(subset=[y])
        # ATTgt expects: a single DataFrame with (entity, time) index, an outcome,
        # and a cohort column. Pass cohort_name=...
        try:
            est = ATTgt(data=d.assign(cohort=df.loc[d.index,'cohort']),
                        cohort_column='cohort',
                        anticipation=0)
            res = est.fit(formula=y, n_jobs=1)   # no covariates
            agg = est.aggregate('simple')
            att = float(agg.iloc[0, 0])         # ('SimpleAggregation','','ATT')
            se  = float(agg.iloc[0, 1])         # ('SimpleAggregation','analytic','std_error')
            ci_lo = att - 1.96*se; ci_hi = att + 1.96*se
            n = len(d)
            L(f'| **{ylab}** | {att:.4f} | {se:.4f} | [{ci_lo:.4f}, {ci_hi:.4f}] | {n:,} |')

            # Aggregation by event time for plot
            ev = est.aggregate('event')
            es_results[ylab] = ev
        except Exception as e:
            L(f'| **{ylab}** | — | — | — | failed: {e} |')
            print(f'  CS for {y} failed: {e}')

    # Event-study plot
    L('\n## Event-study aggregation (event-time ATT, with 95% CI)')
    if es_results:
        n_plots = len(es_results)
        fig, axes = plt.subplots(1, n_plots, figsize=(5.5*n_plots, 5), squeeze=False)
        for i, (ylab, ev) in enumerate(es_results.items()):
            ax = axes[0][i]
            # ev has MultiIndex columns; relative_period in index
            ev = ev.reset_index()
            # Flatten: ATT and std_error are first two value-columns
            tcol = 'relative_period'
            att_col, se_col = ev.columns[1], ev.columns[2]
            # Trim to ±10 for readability
            ev = ev[(ev[tcol] >= -10) & (ev[tcol] <= 10)]
            ax.errorbar(ev[tcol], ev[att_col], yerr=1.96*ev[se_col],
                        marker='o', capsize=4, color='steelblue')
            ax.axhline(0, color='black', lw=0.5)
            ax.axvline(-0.5, color='darkred', linestyle='--', lw=1)
            ax.set_xlabel('Event time (years from first DC)'); ax.set_ylabel(ylab)
            ax.set_title(f'CS event-study — {ylab}')
            ax.grid(alpha=0.3)
        fig.suptitle('Callaway-Sant\'Anna event-study (95% CI)', y=1.02)
        fig.tight_layout()
        fig.savefig(OUT_FIG/'fig07_cs_event_study.png', dpi=140, bbox_inches='tight')
        plt.close()
        L(f'\nSaved: `data/derived/figures/fig07_cs_event_study.png`')

    OUT_MD.write_text('\n'.join(lines))
    print(f'\nWrote {OUT_MD}')

if __name__ == '__main__':
    main()
