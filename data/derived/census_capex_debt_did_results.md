# Census 2022 Capex & Debt DiD (full-universe matched, channel rescue)

**Date:** 2026-06-10. `scripts/python/57`. Reuses the script-56 validated matched pairs (vetted treated × full clean Census controls); swaps outcome to capex / debt. Mirrors the script-56 matched-pair estimator. **Negative debt effect = DC counties deleverage MORE; positive capex = invest MORE.**

| Outcome (matched-pair, treated − controls) | Mean effect | Median | t / Wilcoxon p | Boot 95% CI | sign |
|---|---:|---:|---:|---:|---:|
| Capex — % growth (winsorized) | **+335.27pp** | -37.66 | t=0.579 / W=0.320 | [-750.42,+1593.40] | 31/74 pos |
| Capex — $M level change | **+2.60$M** | +0.12 | t=0.336 / W=0.476 | [-2.42,+8.02] | 51/97 pos |
| Capex/PT intensity — change (pp of PT) | **+0.03pp** | -0.01 | t=0.622 / W=0.645 | [-0.09,+0.17] | 48/97 pos |
| Debt o/s — % growth (winsorized) | **+104.07pp** | +1.41 | t=0.148 / W=0.588 | [-20.41,+254.37] | 43/85 pos |
| Debt o/s — $M level change | **-2.93$M** | -0.28 | t=0.869 / W=0.855 | [-43.34,+25.11] | 47/97 pos |
| Debt/PT intensity — change (pp of PT) | **-0.03pp** | -0.08 | t=0.848 / W=0.454 | [-0.35,+0.28] | 44/97 pos |

## Reading guide
- Coverage: 93 treated have both-year Census capex, 97 have debt o/s (vs MuniSpot capex N=41).
- Compare to MuniSpot (scripts 47/48): capex 'no usable signal' (N=41); debt-service-burden clean NULL. Census adds a debt STOCK test MuniSpot couldn't do.
- Property-tax-scaled intensity uses the one clean total we have; a full capex/totexp ratio needs total-expenditure parsing (enhancement).
- Winsorized at p1/p99 (capex % growth is lumpy); median + sign test are the robust reads.
