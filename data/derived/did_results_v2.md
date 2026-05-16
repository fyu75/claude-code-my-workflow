# DiD v2 — Tighter spec with state-year FE + spread outcome

*Run 2026-05-16. Source: `scripts/python/10b_did_v2_pyfixest.py`.*

All regressions: balanced county-year panel 2000-2025, SEs clustered at county_fips.

| Spec | Fixed effects |
|---|---|
| A | county + year (two-way) |
| B | county + state×year (tighter — absorbs state-level boom dynamics) |
| C | county + state×year + log(n_dc+1) intensity |

## Coefficient table

| Outcome | A: cty+yr FE | B: cty+state-yr FE | C: B + log_n_dc | N (B) |
|---|---|---|---|---:|
| **log(par + 1)** | -0.0521 (0.0418) | -0.0379 (0.0372) | post_dc: -0.0950* (0.0544); log_n_dc: 0.0572 (0.0415) | 81,692 |
| **log(n_deals + 1)** | -0.1203*** (0.0195) | -0.1005*** (0.0165) | post_dc: -0.0320 (0.0245); log_n_dc: -0.0687*** (0.0198) | 81,692 |
| **par-weighted spread (bps)** | 4.9821** (2.2738) | 2.8452 (1.9741) | post_dc: 2.6407 (2.8759); log_n_dc: 0.2070 (2.0353) | 33,465 |
| **par-weighted coupon (%)** | 0.0377* (0.0224) | 0.0182 (0.0199) | post_dc: 0.0363 (0.0285); log_n_dc: -0.0183 (0.0208) | 33,477 |

*Stars: \*\*\* p<0.01, \*\* p<0.05, \* p<0.10. SEs in parens, clustered by county.*

## Event study (county + state-year FE)

Saved event-study plot: `data/derived/figures/fig06_event_study_v2.png`