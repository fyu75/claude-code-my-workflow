# Property-Tax Timing Event Study — does the tax base rise BEFORE operational?

**Date:** 2026-06-10. `scripts/python/64`. log(county property tax), v2 annual, county+year FE, event time vs first_op_year, ref −1. Tests construction-in-progress assessment (Frank's hypothesis).

**If coefficients at −2/−3 are POSITIVE & rising, the tax base responds DURING construction → operational date is too late.**

### ALL treated  (N treated cohorts: 15)
| event time | coef (log pt) | SE | p | |
|---|---:|---:|---:|---|
| -3 | +0.097 | 0.147 | 0.509 | **pre-operational** (construction test) |
| -2 | +0.030 | 0.040 | 0.455 | **pre-operational** (construction test) |
| +0 | -0.027 | 0.021 | 0.192 | **operational** |
| +1 | -0.024 | 0.022 | 0.277 | post |
| +2 | +0.037 | 0.095 | 0.696 | post |
| +3 | +0.249 | 0.154 | 0.108 | post |
| −1 | 0 (ref) | — | — | reference |

### Clean hyperscale/colo only  (N treated cohorts: 4)
| event time | coef (log pt) | SE | p | |
|---|---:|---:|---:|---|
| -3 | -0.086*** | 0.024 | 0.000 | **pre-operational** (construction test) |
| -2 | -0.006 | 0.008 | 0.466 | **pre-operational** (construction test) |
| +0 | -0.003 | 0.011 | 0.742 | **operational** |
| +1 | +0.040 | 0.027 | 0.140 | post |
| +2 | +0.315* | 0.182 | 0.083 | post |
| +3 | +0.255** | 0.124 | 0.040 | post |
| −1 | 0 (ref) | — | — | reference |

## Reading
- Positive pre-operational (−2,−3) => construction/assessment channel (tax up before 'operational').
- Flat pre + positive post => effect lags operational (assessment cycle AFTER completion).
- v2 thin (~16-31 treated) -> directional; the announcement-dated re-timing (agent-feasible, ~75% hit) is the proper fix.
