# Colo-dose confirmation in the secondary market — the apples-to-apples test

**Date:** 2026-06-11. `scripts/python/78`. Dependent variable: par-weighted yield-to-worst of OUTSTANDING bonds (%, bond x year; MSRB customer-sale trades, 2008-2025). Joint category doses (log1p cum >=50MW MW / 2017 PT $M), bond + year FE, cluster county. Coefficients x100 = bps per log-point of dose. Primary-market reference (script 71 §3, new-issue spreads): colo -46.5 (p=0.024) on the operational clock.

| Clock | colo-dose | hyperscale-dose | crypto-dose |
|---|---|---|---|
| op | -1.3 (4.8) p=0.787 | -0.7 (2.0) p=0.722 | +0.9 (1.2) p=0.460 |
| ann | +3.7 (7.0) p=0.593 | -2.6* (1.5) p=0.089 | +1.5 (1.3) p=0.242 |

Bonds in colo-dose>0 counties: 5,436; full panel 1,148,715 bond-years, 283,587 bonds, 2,294 counties.

## Conclusion
- If colo-dose here is null or positive: the §11 primary-market colo estimate is settled as NOT confirmed (footnote). If negative and significant: the multi-tenant-diversification pricing story survives the selection-free test and re-enters the paper.
