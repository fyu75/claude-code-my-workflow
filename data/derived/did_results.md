# First-Cut DiD Results — County-Year Panel

*Run 2026-05-16. Source: `scripts/python/08_first_did.py`.*

## Specifications

All regressions include **county fixed effects** (absorb time-invariant county heterogeneity)
and **year fixed effects** (absorb common macro shocks). Standard errors clustered at the county level.
Sample: 2000–2025, balanced county-year panel, 3,143 counties × 26 years.

**Caveats** (this is descriptive only — not causal identification):
- DC siting is endogenous (correlated with local economic conditions).
- No state×year FE in this first cut (degree-of-freedom heavy with 26 years × 51 states); add in v2.
- Coupon outcome lacks a Treasury benchmark — interpret only as a relative measure.
- The `post_dc` indicator is a binary "ever-treated × post" — does NOT distinguish DC count or MW intensity.

## Spec 1: Issuance volume, `log(par + 1) ~ post_dc`
```
                          PanelOLS Estimation Summary                           
================================================================================
Dep. Variable:                log_par   R-squared:                     5.238e-05
Estimator:                   PanelOLS   R-squared (Between):             -0.0059
No. Observations:               81718   R-squared (Within):            9.756e-05
Date:                Sat, May 16 2026   R-squared (Overall):             -0.0049
Time:                        13:56:55   Log-likelihood                 -1.12e+05
Cov. Estimator:             Clustered                                           
                                        F-statistic:                      4.1145
Entities:                        3143   P-value                           0.0425
Avg Obs:                       26.000   Distribution:                 F(1,78549)
Min Obs:                       26.000                                           
Max Obs:                       26.000   F-statistic (robust):             1.4905
                                        P-value                           0.2221
Time periods:                      26   Distribution:                 F(1,78549)
Avg Obs:                       3143.0                                           
Min Obs:                       3143.0                                           
Max Obs:                       3143.0                                           
                                                                                
                             Parameter Estimates                              
==============================================================================
            Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
------------------------------------------------------------------------------
post_dc       -0.0521     0.0426    -1.2209     0.2221     -0.1356      0.0315
==============================================================================

F-test for Poolability: 54.083
P-value: 0.0000
Distribution: F(3167,78549)

Included effects: Entity, Time
```
**Coef on post_dc: -0.0521  SE: 0.0426  t: -1.22  p: 0.2221**
Interpret: in counties that get a DC, log(par+1) changes by -0.052 on average post-DC.

## Spec 2: Issuance count, `log(n_deals + 1) ~ post_dc`
```
                          PanelOLS Estimation Summary                           
================================================================================
Dep. Variable:              log_deals   R-squared:                        0.0017
Estimator:                   PanelOLS   R-squared (Between):             -0.0289
No. Observations:               81718   R-squared (Within):               0.0037
Date:                Sat, May 16 2026   R-squared (Overall):             -0.0243
Time:                        13:56:55   Log-likelihood                 -3.82e+04
Cov. Estimator:             Clustered                                           
                                        F-statistic:                      133.57
Entities:                        3143   P-value                           0.0000
Avg Obs:                       26.000   Distribution:                 F(1,78549)
Min Obs:                       26.000                                           
Max Obs:                       26.000   F-statistic (robust):             36.462
                                        P-value                           0.0000
Time periods:                      26   Distribution:                 F(1,78549)
Avg Obs:                       3143.0                                           
Min Obs:                       3143.0                                           
Max Obs:                       3143.0                                           
                                                                                
                             Parameter Estimates                              
==============================================================================
            Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
------------------------------------------------------------------------------
post_dc       -0.1203     0.0199    -6.0384     0.0000     -0.1593     -0.0812
==============================================================================

F-test for Poolability: 79.575
P-value: 0.0000
Distribution: F(3167,78549)

Included effects: Entity, Time
```
**Coef on post_dc: -0.1203  SE: 0.0199  t: -6.04  p: 0.0000**

## Spec 3: Par-weighted coupon, `par_wtd_coupon_cy ~ post_dc`
(restricted to county-years with coupon data)

```
                          PanelOLS Estimation Summary                           
================================================================================
Dep. Variable:      par_wtd_coupon_cy   R-squared:                        0.0001
Estimator:                   PanelOLS   R-squared (Between):              0.0013
No. Observations:               33785   R-squared (Within):              -0.0018
Date:                Sat, May 16 2026   R-squared (Overall):              0.0021
Time:                        13:56:55   Log-likelihood                -3.034e+04
Cov. Estimator:             Clustered                                           
                                        F-statistic:                      3.6233
Entities:                        2808   P-value                           0.0570
Avg Obs:                       12.032   Distribution:                 F(1,30951)
Min Obs:                       1.0000                                           
Max Obs:                       26.000   F-statistic (robust):             2.5959
                                        P-value                           0.1072
Time periods:                      26   Distribution:                 F(1,30951)
Avg Obs:                       1299.4                                           
Min Obs:                       913.00                                           
Max Obs:                       1535.0                                           
                                                                                
                             Parameter Estimates                              
==============================================================================
            Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
------------------------------------------------------------------------------
post_dc        0.0377     0.0234     1.6112     0.1072     -0.0082      0.0837
==============================================================================

F-test for Poolability: 18.488
P-value: 0.0000
Distribution: F(2832,30951)

Included effects: Entity, Time
```
**Coef on post_dc: 0.0377  SE: 0.0234  t: 1.61  p: 0.1072**
Interpret: in counties that get a DC, par-weighted coupon changes by 3.8 bps on average post-DC.

## Spec 4: Intensity — log(par+1) ~ log(n_dc+1)
```
                          PanelOLS Estimation Summary                           
================================================================================
Dep. Variable:                log_par   R-squared:                     5.236e-06
Estimator:                   PanelOLS   R-squared (Between):             -0.0019
No. Observations:               81718   R-squared (Within):             2.04e-05
Date:                Sat, May 16 2026   R-squared (Overall):             -0.0016
Time:                        13:56:56   Log-likelihood                 -1.12e+05
Cov. Estimator:             Clustered                                           
                                        F-statistic:                      0.4113
Entities:                        3143   P-value                           0.5213
Avg Obs:                       26.000   Distribution:                 F(1,78549)
Min Obs:                       26.000                                           
Max Obs:                       26.000   F-statistic (robust):             0.1491
                                        P-value                           0.6994
Time periods:                      26   Distribution:                 F(1,78549)
Avg Obs:                       3143.0                                           
Min Obs:                       3143.0                                           
Max Obs:                       3143.0                                           
                                                                                
                             Parameter Estimates                              
==============================================================================
            Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
------------------------------------------------------------------------------
log_n_dc      -0.0124     0.0322    -0.3861     0.6994     -0.0756      0.0507
==============================================================================

F-test for Poolability: 54.974
P-value: 0.0000
Distribution: F(3167,78549)

Included effects: Entity, Time
```
**Coef on log_n_dc: -0.0124  SE: 0.0322**
Elasticity interpretation: a 10% increase in DC count → -0.0012 log change in par issuance.

## Spec 5: Intensity on coupon — coupon ~ log(n_dc+1)
```
                          PanelOLS Estimation Summary                           
================================================================================
Dep. Variable:      par_wtd_coupon_cy   R-squared:                        0.0001
Estimator:                   PanelOLS   R-squared (Between):              0.0011
No. Observations:               33785   R-squared (Within):              -0.0019
Date:                Sat, May 16 2026   R-squared (Overall):              0.0020
Time:                        13:56:56   Log-likelihood                -3.034e+04
Cov. Estimator:             Clustered                                           
                                        F-statistic:                      3.4366
Entities:                        2808   P-value                           0.0638
Avg Obs:                       12.032   Distribution:                 F(1,30951)
Min Obs:                       1.0000                                           
Max Obs:                       26.000   F-statistic (robust):             2.6976
                                        P-value                           0.1005
Time periods:                      26   Distribution:                 F(1,30951)
Avg Obs:                       1299.4                                           
Min Obs:                       913.00                                           
Max Obs:                       1535.0                                           
                                                                                
                             Parameter Estimates                              
==============================================================================
            Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
------------------------------------------------------------------------------
log_n_dc       0.0268     0.0163     1.6424     0.1005     -0.0052      0.0588
==============================================================================

F-test for Poolability: 18.501
P-value: 0.0000
Distribution: F(2832,30951)

Included effects: Entity, Time
```
**Coef: 0.0268**, *p=0.101*

## Event study: coupon and par by years-since-first-DC
(DC-host counties only; t=0 is first-DC year; reference period t=-1)

Saved event-study plot: `data/derived/figures/fig05_event_study.png`