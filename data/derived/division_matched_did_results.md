# Division-Matched 2-Period Property-Tax Growth DiD

**Date:** 2026-06-10. First DiD on the 101-treated / 1:3 division-matched sample (script 45 `division_matched_pairs.csv`), run after Frank's sign-off on sample construction.

Outcome = within-county annualized property-tax CAGR (FY2017 -> post) from the triangulated verified spine. Benchmark = national county-govt PT CAGR +3.40%/yr.

## Sample composition
- Pairs: **303** (270 same-state, 33 division-fallback)
- Treated with >=1 matched usable control: **101**
- Unique controls used: **130**
- Treated by tier: {'PRIMARY': np.int64(49), 'CENSUS_TRUST': np.int64(32), 'EXPANDED': np.int64(20)}

## (1) Matched-pair effect (headline + robustness)

### FULL (state + division fallback)

- N treated (matched): **101**
- Matched effect mean **+1.62%/yr** (t p=0.0001); median +0.92%
- Wilcoxon p=0.0002; sign 68/101 positive (p=0.0006)
- Bootstrap 95% CI [+0.82, +2.41]%/yr
- Treated CAGR mean **+5.76%/yr** vs 3.40% benchmark -> excess **+2.36%/yr** (p=0.0000)

### STATE-ONLY (drop division-fallback pairs)

- N treated (matched): **97**
- Matched effect mean **+1.42%/yr** (t p=0.0013); median +0.72%
- Wilcoxon p=0.0017; sign 63/97 positive (p=0.0042)
- Bootstrap 95% CI [+0.61, +2.27]%/yr
- Treated CAGR mean **+5.76%/yr** vs 3.40% benchmark -> excess **+2.36%/yr** (p=0.0000)

### ESC-DROPPED (drop East-South-Central treated)

- N treated (matched): **86**
- Matched effect mean **+1.91%/yr** (t p=0.0001); median +1.57%
- Wilcoxon p=0.0001; sign 61/86 positive (p=0.0001)
- Bootstrap 95% CI [+1.02, +2.84]%/yr
- Treated CAGR mean **+5.81%/yr** vs 3.40% benchmark -> excess **+2.41%/yr** (p=0.0000)

## (2) Pair-stacked OLS, SEs clustered on county (reused control = one cluster)

- FULL  (state+division): treated coef **+1.54%/yr** (SE 0.52, p=0.0034), N=606, clusters=231
- STATE-ONLY: treated coef **+1.38%/yr** (SE 0.51, p=0.0069), N=540, clusters=226
- ESC-DROPPED: treated coef **+1.83%/yr** (SE 0.58, p=0.0017), N=516, clusters=206

## (3) Unique-county pooled OLS, state FE, HC1 (comparable to script 44)

- FULL: treated coef **+1.27%/yr** (SE 0.52, p=0.0152), N=231
- STATE-ONLY: treated coef **+1.28%/yr** (SE 0.52, p=0.0148), N=226
- ESC-DROPPED: treated coef **+1.48%/yr** (SE 0.57, p=0.0099), N=206

## Notes
- Headline = estimator (1) FULL. Estimators (2)/(3) are regression analogues; (2) is the preferred inferential spec because it clusters on county (controls are reused up to ~8x).
- match_tier robustness isolates the strict same-state design; ESC-dropped probes the control-reuse bottleneck flagged in sample construction.
- CAGRs and tiers inherited from script 44; DROP set and high-risk gating already applied there.
