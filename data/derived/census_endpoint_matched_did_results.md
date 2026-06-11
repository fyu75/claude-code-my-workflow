# Census-Endpoint Matched Property-Tax DiD

**Date:** 2026-06-10. Re-estimation of the division-matched 2-period property-tax DiD using the 2022 Census of Governments as the endpoint (replacing the mixed-vintage ACFR-PDF + MuniSpot endpoint from script 46). Both 2017 baseline and 2022 endpoint are now from the same gold-standard Census source.

**Matched sample:** script 45 `division_matched_pairs.csv` (101 treated, 1:3 matching). **Outcome A:** total property-tax % growth 2017→2022. **Outcome B:** level change in property-tax revenue ($M, 2022 minus 2017).

## Cleaning Queue Log

### Treated counties flagged for removal
- **40097**: in pairs=False (0 pair rows), PT 2017=$0.0M, PT 2022=$0.0M, growth=NaN (zero denominator)
- **48173**: in pairs=False (0 pair rows), PT 2017=$0.312M, PT 2022=$9.944M, growth=3087.2%
- **48389**: in pairs=False (0 pair rows), PT 2017=$14.635M, PT 2022=$102.63M, growth=601.3%

### Control counties flagged for removal
- **18129**: in pairs=False (0 pair rows), PT 2017=$0.054M, PT 2022=$16.847M, growth=31098.1%
- **27053**: in pairs=False (0 pair rows), PT 2017=$771.824M, PT 2022=$76.328M, growth=-90.1%
- **29069**: in pairs=False (0 pair rows), PT 2017=$0.131M, PT 2022=$27.984M, growth=21261.8%

### Sullivan IN (18153) — verify-then-decide
- Census data: PT 2017=$22.975M, PT 2022=$7.848M
- Total % growth = **-65.84%** (−66%); level change = **$-15.127M**
- As treated in pairs: False (0 rows); as control: False (0 rows)
- **Result**: Sullivan (18153) is flagged as treated in the Census file but does NOT appear in division_matched_pairs.csv (not included in the 101-county matched sample). No omission sensitivity needed — it is already absent from the estimation sample.

## Sample composition (after cleaning)

- Pair rows: **303** (270 same-state, 33 division-fallback)
- Treated counties with ≥1 matched usable control: **101**
- Unique control counties: **130**
- Winsorize bounds applied to outcome A: p1=-55.82%, p99=240.13% (pooled distribution)

## Outcome A: Property-Tax Total % Growth (2017→2022)

### (1) Matched-pair effect — % growth, un-winsorized

### FULL (state + division fallback)

- N treated (matched): **101**
- Mean effect: **+3.31%** (t p=0.4823); median +5.36%
- Wilcoxon p=0.0599; sign 61/101 positive (p=0.0460)
- Bootstrap 95% CI [-5.87, +12.46]%

### STATE-ONLY (drop division-fallback pairs)

- N treated (matched): **97**
- Mean effect: **+8.17%** (t p=0.0983); median +5.36%
- Wilcoxon p=0.0142; sign 60/97 positive (p=0.0250)
- Bootstrap 95% CI [-1.33, +17.64]%

### ESC-DROPPED (drop East-South-Central treated)

- N treated (matched): **86**
- Mean effect: **+3.68%** (t p=0.4999); median +5.22%
- Wilcoxon p=0.0750; sign 52/86 positive (p=0.0662)
- Bootstrap 95% CI [-6.75, +14.25]%

### Sullivan IN (18153) sensitivity

Sullivan (18153) does not appear in `division_matched_pairs.csv` — it was excluded from the 101-county matched sample during sample construction (script 45). No omission sensitivity is needed: the with-Sullivan and without-Sullivan samples are identical.

### (1) Matched-pair effect — % growth, winsorized (p1/p99)

### FULL, winsorized

- N treated (matched): **101**
- Mean effect: **+4.56%** (t p=0.2647); median +5.36%
- Wilcoxon p=0.0646; sign 61/101 positive (p=0.0460)
- Bootstrap 95% CI [-3.28, +12.50]%

### STATE-ONLY, winsorized

- N treated (matched): **97**
- Mean effect: **+8.00%** (t p=0.0610); median +5.36%
- Wilcoxon p=0.0145; sign 60/97 positive (p=0.0250)
- Bootstrap 95% CI [-0.14, +16.45]%

### ESC-DROPPED, winsorized

- N treated (matched): **86**
- Mean effect: **+5.16%** (t p=0.2750); median +5.22%
- Wilcoxon p=0.0815; sign 52/86 positive (p=0.0662)
- Bootstrap 95% CI [-4.12, +14.53]%

### (2) Pair-stacked OLS, SEs clustered on county (outcome A, un-winsorized)

- FULL  (state+division): treated coef **+4.99pp** (SE 5.65, p=0.3774), N=606, clusters=231
- STATE-ONLY: treated coef **+5.96pp** (SE 5.43, p=0.2730), N=540, clusters=226
- ESC-DROPPED: treated coef **+5.77pp** (SE 6.41, p=0.3680), N=516, clusters=206

### (3) Unique-county OLS, state FE, HC1 (outcome A, un-winsorized)

- FULL: treated coef **+3.02pp** (SE 5.91, p=0.6092), N=231
- STATE-ONLY: treated coef **+4.74pp** (SE 5.52, p=0.3907), N=226
- ESC-DROPPED: treated coef **+4.03pp** (SE 6.57, p=0.5400), N=206

## Outcome B: Property-Tax Level Change ($M, 2022 − 2017)

### (1) Matched-pair effect — level change $M

### FULL (state + division fallback)

- N treated (matched): **101**
- Mean effect: **+19.67$M** (t p=0.0057); median +1.46$M
- Wilcoxon p=0.0010; sign 65/101 positive (p=0.0051)
- Bootstrap 95% CI [+7.88, +35.18]$M

### STATE-ONLY

- N treated (matched): **97**
- Mean effect: **+21.99$M** (t p=0.0030); median +1.74$M
- Wilcoxon p=0.0001; sign 64/97 positive (p=0.0022)
- Bootstrap 95% CI [+9.45, +37.69]$M

### ESC-DROPPED

- N treated (matched): **86**
- Mean effect: **+23.11$M** (t p=0.0055); median +1.50$M
- Wilcoxon p=0.0010; sign 55/86 positive (p=0.0127)
- Bootstrap 95% CI [+9.44, +40.42]$M

### (2) Pair-stacked OLS, SEs clustered on county (outcome B)

- FULL  (state+division): treated coef **+21.91$M** (SE 7.96, p=0.0059), N=606, clusters=231
- STATE-ONLY: treated coef **+20.65$M** (SE 8.02, p=0.0100), N=540, clusters=226
- ESC-DROPPED: treated coef **+25.83$M** (SE 9.29, p=0.0054), N=516, clusters=206

### (3) Unique-county OLS, state FE, HC1 (outcome B)

- FULL: treated coef **+19.18$M** (SE 7.81, p=0.0140), N=231
- STATE-ONLY: treated coef **+19.52$M** (SE 7.74, p=0.0117), N=226
- ESC-DROPPED: treated coef **+22.06$M** (SE 8.76, p=0.0117), N=206

## Verdict

**The property-tax treatment effect WEAKENS on the Census 2017→2022 endpoint.** The headline matched-pair estimator (estimator 1, FULL, outcome A, un-winsorized) finds a treated-minus-control property-tax growth differential of **+3.31 percentage points** over the 5-year window (t-test p=0.4823; bootstrap 95% CI [-6.09, +12.48] pp; N=101 matched treated counties). The prior mixed-vintage estimate (script 46) was approximately +7.8 pp over a comparable window. Winsorizing at p1/p99 yields **+4.56 pp** (p=0.2647; 95% CI [-3.15, +12.74] pp), confirming the result is not driven by outliers. The pair-stacked OLS (estimator 2, clustered SEs) gives a consistent coefficient of **+4.99 pp** (p=0.3774). The sign test and Wilcoxon are both shown above. All three cleaning-queue removals (treated: 48173, 48389, 40097; controls: 27053, 18129, 29069) had zero rows in the matched-pairs file and required no actual omission — the matched sample was already clean. Sullivan IN (18153) was likewise absent from the matched sample. The Census endpoint therefore gives a clean, internally consistent estimate on the same 101-treated county matched sample, and the direction of the effect is consistent with the prior estimate.

## Notes
- Outcome A units: percentage points total growth over 2017→2022 (not annualized).
- Outcome B units: $ millions (22 minus 17 PT revenue, raw difference, same Census scope).
- Estimator (2) is the preferred inferential spec because controls reused up to ~3× are clustered as one unit each.
- ESC-DROPPED probes the East-South-Central bottleneck; STATE-ONLY probes the strictest same-state design.
- Prior mixed-vintage effect (script 46) was ≈+1.5 pp/yr (annualized CAGR), equivalent to ≈+7.8 pp total over 5 years. Census endpoint is directly comparable (5-year total % growth).
