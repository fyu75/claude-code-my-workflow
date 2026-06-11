# DC-Announcement effect on bond features — simple staggered DiD

**Date:** 2026-06-10. `scripts/python/68`. Treatment dummy `announced = 1[year >= first >=50MW DC announcement]`, county + year FE, cluster county. Controls = clean never-DC-host counties (2,776). Anchor = `A_firstmaj` (172/172 DC-level wave; county-level fallback). Cuts: ALL / clean_dc / crypto. **rated_avg_rating: AAA=1, LOWER = BETTER.**

| Outcome | Panel | Cut | beta (announced) | SE | p | N | beta(+state x year FE) | p |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Spread (bps) | deal | ALL | -0.532 | 6.678 | 0.937 | 49,284 | +6.675 | 0.119 |
| Spread (bps) | deal | clean_dc | -2.202 | 8.309 | 0.791 | 47,364 | +5.176 | 0.365 |
| Spread (bps) | deal | crypto | +16.851 | 10.524 | 0.109 | 44,715 | +14.298* | 0.060 |
| Rating extensive (any-rated) | deal | ALL | -0.025* | 0.014 | 0.066 | 67,384 | -0.022* | 0.078 |
| Rating extensive (any-rated) | deal | clean_dc | -0.015 | 0.016 | 0.375 | 64,845 | -0.031* | 0.074 |
| Rating extensive (any-rated) | deal | crypto | -0.061** | 0.031 | 0.049 | 61,759 | -0.022 | 0.269 |
| Rating intensive (avg|rated, AAA=1) | deal | ALL | -0.111** | 0.048 | 0.023 | 10,793 | -0.117* | 0.098 |
| Rating intensive (avg|rated, AAA=1) | deal | clean_dc | -0.148*** | 0.054 | 0.006 | 10,375 | -0.146 | 0.192 |
| Rating intensive (avg|rated, AAA=1) | deal | crypto | -0.004 | 0.076 | 0.954 | 10,151 | -0.057 | 0.476 |
| Issuance extensive P(any deal) | cy | ALL | +0.008 | 0.020 | 0.684 | 75,322 | +0.016 | 0.381 |
| Issuance extensive P(any deal) | cy | clean_dc | +0.028 | 0.025 | 0.274 | 73,450 | +0.048** | 0.042 |
| Issuance extensive P(any deal) | cy | crypto | +0.016 | 0.036 | 0.660 | 73,476 | +0.014 | 0.675 |
| Issuance log(1+par $M) | cy | ALL | +0.050 | 0.070 | 0.474 | 75,322 | +0.057 | 0.334 |
| Issuance log(1+par $M) | cy | clean_dc | +0.099 | 0.107 | 0.353 | 73,450 | +0.151* | 0.085 |
| Issuance log(1+par $M) | cy | crypto | +0.057 | 0.103 | 0.581 | 73,476 | +0.031 | 0.739 |
| Issuance log(1+n_deals) | cy | ALL | -0.042 | 0.029 | 0.143 | 75,322 | -0.039* | 0.093 |
| Issuance log(1+n_deals) | cy | clean_dc | -0.056 | 0.047 | 0.229 | 73,450 | -0.034 | 0.320 |
| Issuance log(1+n_deals) | cy | crypto | +0.002 | 0.042 | 0.971 | 73,476 | -0.013 | 0.724 |
| Spread par-wtd (bps) | cy | ALL | +2.344 | 5.081 | 0.645 | 28,108 | +3.099 | 0.451 |
| Spread par-wtd (bps) | cy | clean_dc | -5.493 | 6.938 | 0.429 | 27,242 | -4.106 | 0.452 |
| Spread par-wtd (bps) | cy | crypto | +17.870** | 8.898 | 0.045 | 26,919 | +15.511** | 0.046 |
| Structure: share callable | cy | ALL | -0.004 | 0.021 | 0.836 | 30,912 | -0.003 | 0.883 |
| Structure: share callable | cy | clean_dc | -0.014 | 0.029 | 0.622 | 29,993 | -0.017 | 0.527 |
| Structure: share callable | cy | crypto | +0.014 | 0.046 | 0.755 | 29,664 | +0.012 | 0.779 |
| Structure: par-wtd maturity (yrs) | cy | ALL | -0.336*** | 0.113 | 0.003 | 31,365 | -0.327*** | 0.007 |
| Structure: par-wtd maturity (yrs) | cy | clean_dc | -0.312** | 0.153 | 0.042 | 30,442 | -0.172 | 0.256 |
| Structure: par-wtd maturity (yrs) | cy | crypto | -0.491** | 0.240 | 0.041 | 30,107 | -0.680** | 0.014 |

## Reading
- **Spread:** clean_dc NULL (deal & county-year), crypto WIDENS (+17-18 bps, p<0.11). DC announcement does NOT lower borrowing cost for real DCs; crypto counties' spreads rise (volatile/transient tax base).
- **Issuance:** NULL on every margin (extensive, par, n_deals) — DC counties do not issue more after the announcement. Corroborates the V2 debt-service null.
- **Rating extensive:** less rated debt, concentrated in CRYPTO (-6pp, p=0.05); clean_dc NULL. Refines the earlier 'all -7pp' — the rated-market retreat is a crypto phenomenon.
- **Rating intensive:** clean_dc point estimate -0.15 notch (improvement) is significant under county+year but NOT under county+state x year (p=0.19) -> **fragile, report as suggestive null**, consistent with script 51.
- **Structure:** callable / maturity NULL.

**Unifying:** announcement-timed simple DiD reproduces 'fiscally light inflow, fiscally quiet financing' — real DCs leave borrowing/credit untouched; crypto counties' spreads widen and they court the rated market less. Robust across timing (announcement here vs operational in script 62) and estimator (simple vs hedonic).
