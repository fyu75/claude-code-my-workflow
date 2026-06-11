# Test 3 refinements — clock (announcement vs operational) and type-split dose

**Date:** 2026-06-10. `scripts/python/71`. dose = cum >=50MW MW / 2017 PT ($M); log(1+dose) primary; county+year FE; cluster county; clean never pool; phantoms excluded. Per-DC crypto flag from S&P PROVIDERTYPE.

## 1. Clock comparison — log(1+dose), single dose term
| Outcome | Cut | ANNOUNCEMENT clock | OPERATIONAL clock |
|---|---|---|---|
| Spread (bps, deal hedonic) | ALL | +0.597 (3.671) p=0.871 | +0.521 (3.968) p=0.895 |
| Spread (bps, deal hedonic) | clean_dc | -1.953 (4.143) p=0.637 | -3.205 (3.660) p=0.381 |
| Spread (bps, deal hedonic) | crypto | +4.857 (7.244) p=0.503 | +9.957 (8.117) p=0.220 |
| Rating ext (any-rated, deal) | ALL | -0.015* (0.009) p=0.091 | -0.017 (0.011) p=0.103 |
| Rating ext (any-rated, deal) | clean_dc | -0.008 (0.014) p=0.542 | -0.007 (0.014) p=0.602 |
| Rating ext (any-rated, deal) | crypto | -0.027* (0.015) p=0.071 | -0.037* (0.020) p=0.066 |
| Spread par-wtd (cy) | ALL | +7.523** (3.601) p=0.037 | +9.404** (3.980) p=0.018 |
| Spread par-wtd (cy) | clean_dc | +11.574** (4.945) p=0.019 | +10.498 (6.603) p=0.112 |
| Spread par-wtd (cy) | crypto | +3.562 (5.568) p=0.522 | +9.957 (6.396) p=0.120 |

## 2. Type-split dose — crypto-MW and hyperscale-MW jointly, ALL counties
| Outcome | Clock | beta crypto-dose | beta hyperscale-dose |
|---|---|---|---|
| Spread (bps, deal hedonic) | ann | +2.957 (5.369) p=0.582 | -2.166 (4.040) p=0.592 |
| Spread (bps, deal hedonic) | op | +4.664 (6.028) p=0.439 | -4.431 (3.475) p=0.202 |
| Rating ext (any-rated, deal) | ann | -0.023** (0.011) p=0.033 | -0.007 (0.014) p=0.616 |
| Rating ext (any-rated, deal) | op | -0.029** (0.014) p=0.034 | -0.004 (0.014) p=0.797 |
| Spread par-wtd (cy) | ann | +4.588 (4.644) p=0.323 | +13.233*** (4.605) p=0.004 |
| Spread par-wtd (cy) | op | +8.326* (5.007) p=0.096 | +11.668* (6.062) p=0.054 |

## 3. Three-way category split — hyperscale / colocation / crypto doses jointly, ALL counties
93 hyperscale / 48 crypto / 27 colo / 3 other big DCs (MW share 37/50/11.5/1.6%). Colo sits in only 8 counties -> noisy. 'other' included as an unreported control term.
| Outcome | Clock | hyperscale-dose | colo-dose | crypto-dose |
|---|---|---|---|---|
| Spread (bps, deal hedonic) | ann | -1.148 (4.365) p=0.793 | -30.126 (31.005) p=0.331 | +2.904 (5.371) p=0.589 |
| Spread (bps, deal hedonic) | op | -3.214 (3.722) p=0.388 | -46.518** (20.597) p=0.024 | +4.605 (6.032) p=0.445 |
| Rating ext (any-rated, deal) | ann | -0.002 (0.013) p=0.850 | -0.114 (0.097) p=0.239 | -0.023** (0.011) p=0.032 |
| Rating ext (any-rated, deal) | op | -0.002 (0.014) p=0.910 | -0.031 (0.108) p=0.777 | -0.029** (0.014) p=0.034 |
| Spread par-wtd (cy) | ann | +14.840*** (4.812) p=0.002 | -29.055* (16.706) p=0.082 | +4.556 (4.644) p=0.327 |
| Spread par-wtd (cy) | op | +13.011** (6.348) p=0.041 | -20.951* (12.019) p=0.081 | +8.298* (5.007) p=0.098 |

### Colo-dose spread: leave-one-out (op clock, deal hedonic)
- full: colo -46.5 (p=0.024)
- drop Loudoun 51107: colo -37.3 (p=0.048)
- drop Loudoun+PWC: colo -38.0 (p=0.054)
-> survives LOO but rests on ~6-8 clusters, op clock only (ann clock ns): SUGGESTIVE, not a headline.

## Reading
- Clock: announce->operational lead is short (median 1yr) so large differences are not expected; if the operational clock shows pricing the announcement clock missed, the market reacts to CASH FLOWS not news (and vice versa).
- Type-split: identifies WHICH capacity type drives any response within one regression (mixed counties contribute to both terms). Prediction from the dummy results: crypto-dose carries any spread widening / rated-share retreat; hyperscale-dose flat.
- cy spread cells inherit the aggregation-weighting caveat from script 70's appendix; deal-level hedonic is preferred.
