# Expanded Matched DiD — county property-tax growth (2017 -> latest)

**Date:** 2026-06-07  | All-funds county-government scope.  Matched 1:3 (script 42).
Effect = treated county-government property-tax CAGR − mean of its matched-control CAGRs.

## Coverage
- CLEAN (ACFR all-funds, hand-verified) usable treated: **33**
- WIDE (incl. MuniSpot v2 all-funds) usable treated: **33**
- ⚠ V2 level data has unreliable units (value_multiplier misfires ±1000×) → used ONLY for outlier-robust stats, never the mean.

## PRIMARY — clean ACFR all-funds matched effect
- N treated: **33**
- Median effect: **+1.60%/yr**
- Wilcoxon signed-rank: p=0.1045
- Sign test: 22/33 positive, p=0.0801
- Mean effect: **+2.00%/yr** (t-test p=0.0623)
- Bootstrap 95% CI: [+0.10%, +4.06%]/yr

## PRIMARY — clean treated CAGR vs benchmark (3.40%/yr)
- Mean treated CAGR: **+6.34%/yr** (median +5.25%)
- Mean excess over benchmark: **+2.94%/yr** (t-test p=0.0023)

## PRIMARY — pooled OLS (clean ACFR only): CAGR ~ treated + state FE
- Treated coef: **+1.75%/yr** (SE +1.04%, p=0.0926), N=101

## ROBUSTNESS — wide coverage (incl. V2), outlier-robust only
- N treated: **33**
- Median effect: **+1.60%/yr**
- Wilcoxon signed-rank: p=0.1045
- Sign test: 22/33 positive, p=0.0801
- (mean/CI omitted — V2 level units unreliable; robust stats only)

## Caveats
- V2 all-funds level units are unreliable (PWC post showed $818B; many controls off 1000×) — clean ACFR is the trustworthy source.
- 51 of 369 matched pairs are FALLBACK (control outside 0.5–2× PT band).
- True expansion to the full 125 needs the control-ACFR scraping wave (clean post-period data).
- Post source mix among CLEAN treated: {'acfr_allfunds': np.int64(23), 'verified': np.int64(10)}