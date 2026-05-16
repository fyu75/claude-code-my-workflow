# Callaway-Sant'Anna staggered DiD

*Run 2026-05-16. Source: `scripts/python/11_callaway_santanna.py`.*

Estimator: Callaway & Sant'Anna (2021), `differences` Python package, ATTgt.
Control group: **never-treated** counties (counties with no DC opening 2000-2025).
Standard errors: bootstrap, clustered at county_fips.

## Single-coefficient ATT (averaged across cohorts and event times)

| Outcome | ATT | SE | 95% CI | N |
|---|---:|---:|---|---:|
| **log(par + 1)** | -0.0783 | 0.0647 | [-0.2051, 0.0486] | 81,718 |
| **log(n_deals + 1)** | -0.1234 | 0.0284 | [-0.1791, -0.0677] | 81,718 |
| **par-weighted spread (bps)** | -3.1674 | 3.7217 | [-10.4619, 4.1271] | 33,773 |

## Event-study aggregation (event-time ATT, with 95% CI)

Saved: `data/derived/figures/fig07_cs_event_study.png`