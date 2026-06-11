# Deal-Level Hedonic Bond-Spread DiD

**Date:** 2026-06-10. Referee-grade pricing test; resolves the county-year sign-flip (script 16 CS −23bps vs script 49 matched +21bps). `scripts/python/50`.

Unit = muni deal; outcome = spread over matched Treasury (bps). **Negative = tighten = cheaper borrowing.** treated_post = county is ≥1% DC and year ≥ its first-DC year. Hedonic ctrls = log(maturity), log(amount); rating/coupon excluded (bad control / collinear). County FE + state×year FE; SEs clustered on county.

## Sample
- Deals: **71,489** | treated-county deals 7,808, control-county deals 63,681
- Counties: 118 treated (≥1% DC), 2449 never-DC-host controls
- Post (treated × after DC year) deals: 4,072
- Years: 2000–2025

## Results — coefficient on treated_post (bps)

| Spec | β (spread, bps) | SE | p | N deals |
|---|---:|---:|---:|---:|
| A. county + year FE | **+5.86** | 5.67 | 0.3016 | 71,276 |
| B. county + state×year FE | **+6.10**** | 3.05 | 0.0455 | 71,237 |
| C. + hedonic ctrls (PREFERRED) | **+4.92** | 3.14 | 0.1181 | 71,237 |
| D. spec C, 2015+ issues | **-5.73** | 5.05 | 0.2564 | 27,981 |

*Stars: \*\*\* p<0.01, \*\* p<0.05, \* p<0.10.*

## Reading guide
- Compare to: CS-vs-never-treated county-year (script 16) **−23.4 bps** (p<0.10); matched county-year (script 49) **+21 bps mean / ≈0 median** (no clear effect).
- Spec C is preferred: bond composition controlled, rate cycle absorbed by state×year FE, county is its own pre/post control (no dependence on a chosen control group).
- If C is negative & significant → the credit-quality repricing survives and the pricing channel is real. If C is ≈0 / wrong-signed → the −23bps was a composition/control-group artifact and the pricing channel is not established.
- Caveat: TWFE generalized DiD; staggered timing + heterogeneity → a Sun-Abraham/CS deal-level version is the next robustness step.
