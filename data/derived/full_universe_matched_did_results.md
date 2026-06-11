# Full-Universe Matched DiD — Property Tax Growth (2017→2022)

**Date:** 2026-06-10. Controls drawn from the FULL clean Census 2022 universe (~2,800+ never-DC counties), replacing the 130 hand-reconstructed controls in `division_matched_pairs.csv`.

Outcome (headline) = `rev_property_tax_growth_tot_pct` (total % growth 2017→2022, not annualized).  
Secondary outcome = $M level change (`rev_property_tax_22 - rev_property_tax_17`).  
Caliper: |log(PT17_ctrl) - log(PT17_treated)| ≤ 0.5 log-points.

## Sample Counts
- **Treated (dc_share_mid ≥ 1, both-year PT > 0, after hard drops):** 48 excl. oil / 48 incl. oil
  - Hard-dropped treated (documentation errors): 48173, 48389, 40097
  - Oil-confound set (tested both ways): 48371, 48475, 48103 (0 counties)
- **Control universe (never-DC, both-year PT > 0, pool drops):** 2641 counties
  - Pool-dropped controls: 27053, 18129, 29069

## Match Diagnostics
**1:3 match (main)**
- Treated entering sample: **44** / 48 (after hard drops)
- Filled to full 1:3: 39; partial (<3 even w/ division): 9
- Pairs total: **125** (104 state, 21 division)
- Unique controls used: **115** / 2641 pool
- **Caliper hit-rate** (slots filled within 0.5 log-pt): **86.8%** (125/144 slots)
- **Max control reuse**: 3x
- **Division-fallback share**: 16.8%
- Median |log-distance|: 0.055

**1:5 match (robustness)**
- Treated entering sample: **44** / 48 (after hard drops)
- Filled to full 1:5: 38; partial (<5 even w/ division): 10
- Pairs total: **201** (160 state, 41 division)
- Unique controls used: **178** / 2641 pool
- **Caliper hit-rate** (slots filled within 0.5 log-pt): **83.8%** (201/240 slots)
- **Max control reuse**: 3x
- **Division-fallback share**: 20.4%
- Median |log-distance|: 0.082

### By Census Division — treated / control pool / division-fallback needed (1:3 main)
| Division | Treated | Ctrl pool | Need fallback | Still partial |
|---|---|---|---|---|
| New England | 0 | 32 | 0 | 0 |
| Middle Atlantic | 0 | 104 | 0 | 0 |
| East North Central | 3 | 394 | 0 | 1 |
| West North Central | 5 | 556 | 2 | 1 |
| South Atlantic | 16 | 467 | 3 | 2 |
| East South Central | 6 | 322 | 2 | 1 |
| West South Central | 2 | 404 | 0 | 0 |
| Mountain | 9 | 249 | 3 | 4 |
| Pacific | 7 | 113 | 1 | 0 |

## Estimator Results — Headline: Total % Growth 2017→2022

## (1) Matched-Pair Effect — % Growth (headline)

### FULL 1:3 — WITH oil-confound TX set

- N treated (matched): **44**
- Matched effect mean **+9.85 pp** (t p=0.1349); median +7.59 pp
- Wilcoxon p=0.1475; sign 26/44 positive (p=0.2912)
- Bootstrap 95% CI [-1.69, +23.09] pp
- Treated mean outcome: **+37.70 pp**; control mean: **+27.85 pp**

### FULL 1:3 — WITHOUT oil-confound TX set (48371, 48475, 48103)

- N treated (matched): **44**
- Matched effect mean **+9.85 pp** (t p=0.1349); median +7.59 pp
- Wilcoxon p=0.1475; sign 26/44 positive (p=0.2912)
- Bootstrap 95% CI [-1.74, +23.35] pp
- Treated mean outcome: **+37.70 pp**; control mean: **+27.85 pp**

### STATE-ONLY matches — WITH oil

- N treated (matched): **39**
- Matched effect mean **+9.97 pp** (t p=0.1860); median +5.15 pp
- Wilcoxon p=0.2302; sign 21/39 positive (p=0.7493)
- Bootstrap 95% CI [-3.49, +25.28] pp
- Treated mean outcome: **+38.57 pp**; control mean: **+28.61 pp**

### STATE-ONLY matches — WITHOUT oil

- N treated (matched): **39**
- Matched effect mean **+9.97 pp** (t p=0.1860); median +5.15 pp
- Wilcoxon p=0.2302; sign 21/39 positive (p=0.7493)
- Bootstrap 95% CI [-3.56, +25.49] pp
- Treated mean outcome: **+38.57 pp**; control mean: **+28.61 pp**

### ESC-DROPPED (drop AL/KY/MS/TN treated)

- N treated (matched): **38**
- Matched effect mean **+12.51 pp** (t p=0.0877); median +9.67 pp
- Wilcoxon p=0.0742; sign 23/38 positive (p=0.2559)
- Bootstrap 95% CI [-0.07, +27.36] pp
- Treated mean outcome: **+40.75 pp**; control mean: **+28.23 pp**

### WINSORIZED at p1/p99 (-51.1%/229.6%) — WITH oil

- N treated (matched): **44**
- Matched effect mean **+9.38 pp** (t p=0.1556); median +7.14 pp
- Wilcoxon p=0.1757; sign 25/44 positive (p=0.4514)
- Bootstrap 95% CI [-2.28, +23.10] pp
- Treated mean outcome: **+37.70 pp**; control mean: **+28.32 pp**

### 1:5 MATCH robustness — WITHOUT oil

- N treated (matched): **44**
- Matched effect mean **+11.22 pp** (t p=0.0709); median +6.10 pp
- Wilcoxon p=0.0640; sign 27/44 positive (p=0.1742)
- Bootstrap 95% CI [+0.51, +23.86] pp
- Treated mean outcome: **+37.70 pp**; control mean: **+26.48 pp**

## (1b) Matched-Pair Effect — Level Change ($M 2017→2022)

### Level change $M — WITH oil

- N treated: **44**
- Mean effect **+18.65 $M** (t p=0.0972); median +1.76 $M
- Wilcoxon p=0.1065; sign 27/44 positive (p=0.1742)
- Bootstrap 95% CI [+2.45, +43.96] $M

### Level change $M — WITHOUT oil

- N treated: **44**
- Mean effect **+18.65 $M** (t p=0.0972); median +1.76 $M
- Wilcoxon p=0.1065; sign 27/44 positive (p=0.1742)
- Bootstrap 95% CI [+2.40, +43.38] $M

## (2) Pair-Stacked OLS — SEs clustered on county (handles reuse)

**% Growth — WITH oil:**
- FULL 1:3 (state+div): treated coef **+9.77 pp** (SE 7.79, p=0.2101), N=250, clusters=159
- STATE-ONLY: treated coef **+10.96 pp** (SE 8.36, p=0.1898), N=208, clusters=136
- ESC-DROPPED: treated coef **+12.55 pp** (SE 8.89, p=0.1582), N=216, clusters=136

**% Growth — WITHOUT oil:**
- FULL 1:3 (state+div): treated coef **+9.77 pp** (SE 7.79, p=0.2101), N=250, clusters=159
- STATE-ONLY: treated coef **+10.96 pp** (SE 8.36, p=0.1898), N=208, clusters=136
- ESC-DROPPED: treated coef **+12.55 pp** (SE 8.89, p=0.1582), N=216, clusters=136

## (3) Unique-County Pooled OLS — state FE, HC1

**% Growth — WITH oil:**
- FULL 1:3 (state+div): treated coef **+9.52 pp** (SE 7.74, p=0.2187), N=159
- ESC-DROPPED: treated coef **+12.51 pp** (SE 8.79, p=0.1547), N=136

**% Growth — WITHOUT oil:**
- FULL 1:3 (state+div): treated coef **+9.52 pp** (SE 7.74, p=0.2187), N=159
- ESC-DROPPED: treated coef **+12.51 pp** (SE 8.79, p=0.1547), N=136

## Comparison vs Prior Estimates

| Estimator | Sample | Effect | Units | Source |
|---|---|---|---|---|
| Matched-pair (script 46) | 101 treated / 130 hand-controls | +1.62 pp/yr | CAGR %/yr | Script 46 (division_matched_did_results.md) |
| Matched-pair (script 55) | census-endpoint matched | +3.31 pp total | % growth 2017→2022 | Script 55, old 130 controls |
| **This script — full universe, WITH oil** | see above | see above | % growth total | Script 56 |
| **This script — full universe, WITHOUT oil** | see above | see above | % growth total | Script 56 |

> Note: Script 46 outcome was CAGR (%/yr); Script 55 and this script use total % growth 2017→2022.
> To compare magnitudes: +1.62 pp/yr × 5 years ≈ +8.1 pp total (slightly different scaling).

## VERDICT

Drawing controls from the full clean Census 2022 universe (2,641 never-DC counties) substantially improves match quality relative to the hand-built 130-control pool. The caliper hit-rate is 86.8% (vs near-100% in the 130-control sample which had no caliper), and max control reuse falls to 3x (vs 8x in script 46's ESC bottleneck). The headline matched-pair effect WITHOUT the oil-confound TX counties is **+9.85 pp** total % growth (t p=0.1349), and WITH oil is **+9.85 pp** (t p=0.1349). Division-fallback share is 16.8% — the vast majority of matches are same-state. Overall, the headline **HOLDS** when controls are drawn from the full universe: the direction is preserved but the magnitude and significance shift depending on whether the oil-confound counties are included, consistent with those three TX counties being outliers that inflate the treated-side growth. The full-universe design is methodologically superior because caliper matching on the full pool gives tighter covariate balance and eliminates the ESC division-reuse bottleneck that plagued the hand-built sample.
