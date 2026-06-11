# Matched Bond-Spread DiD (same sample as the property-tax DiD)

**Date:** 2026-06-10. Bond-spread outcome re-estimated on the 101-treated / 1:3 division-matched sample (script 45), event-aligned to each treated county's first-DC year, so pricing and property tax share ONE identification strategy. `scripts/python/49`.

Outcome = within-county change in par-weighted spread (post-DC mean − pre-DC mean), bps. **NEGATIVE = spread tightened = cheaper borrowing.** Each matched control is split at its matched treated's DC year.

## Sample composition
- Pairs with treated DC-year: 303 (270 state, 33 division)
- Treated usable (pre & post spread): **69**
- Unique controls contributing a change: 99

## (1) Matched-pair effect (headline + robustness)

### FULL (state + division)

- N treated (matched): **69**
- Matched effect mean **+20.98 bps** (t p=0.0168); median +8.74 bps
- Wilcoxon p=0.0383; **29/69 tightened (negative)** (p=0.2284)
- Bootstrap 95% CI [+4.82, +37.70] bps

### STATE-ONLY (drop division-fallback pairs)

- N treated (matched): **68**
- Matched effect mean **+21.25 bps** (t p=0.0159); median +6.91 bps
- Wilcoxon p=0.0395; **29/68 tightened (negative)** (p=0.2750)
- Bootstrap 95% CI [+5.10, +38.38] bps

### ESC-DROPPED (drop East-South-Central treated)

- N treated (matched): **62**
- Matched effect mean **+23.90 bps** (t p=0.0120); median +7.36 bps
- Wilcoxon p=0.0351; **27/62 tightened (negative)** (p=0.3742)
- Bootstrap 95% CI [+6.45, +42.10] bps

## (2) Pair-stacked OLS, SEs clustered on county

- FULL: treated coef **+28.38 bps** (SE 13.26, p=0.0323), N=416, clusters=171
- STATE-ONLY: treated coef **+28.87 bps** (SE 13.73, p=0.0356), N=382, clusters=164
- ESC-DROPPED: treated coef **+35.52 bps** (SE 14.73, p=0.0159), N=369, clusters=156

## (3) Unique-county OLS, state FE, HC1

- FULL: treated coef **+18.55 bps** (SE 13.94, p=0.1833), N=171

## Notes
- Sign: negative = spreads fell after DC arrival relative to matched controls.
- Directly comparable to script 46 (property tax, +1.5pp/yr) and script 48 (capex/debt): same matched pairs, same three estimators, same two robustness columns.
- Compare to the CS-vs-never-treated spec (script 16): ATT −23.4 bps (SE 12.3, p<0.10). This matched version swaps the control group from all never-DC-host counties to the size-and-region-matched controls.
- Caveat: spread observed only in county-years with a Treasury-benchmarked issue; pre/post means rest on whatever years each county came to market.
