# Option C — Full statistical tests

Treated counties extracted: 23; clean sample (drop 6 flagged): 17

## 1. Distribution tests on excess CAGR

### FULL sample

| Outcome | N | mean | median | SD | t (p₁) | Wilcoxon (p₁) | Sign test (p) | 95% CI mean |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Property tax | 15 | -1.33% | 1.40% | 18.28 | -0.28 (p=0.6086) | 59.0 (p=0.5330) | 8/15 (p=0.5000) | [-10.43%, 7.80%] |
| Capital outlay | 7 | 38.37% | 23.51% | 35.39 | 2.87 (p=0.0142) | 28.0 (p=0.0078) | 7/7 (p=0.0078) | [17.33%, 64.98%] |
| Long-term debt | 10 | 4.07% | 2.55% | 38.95 | 0.33 (p=0.3742) | 28.0 (p=0.5000) | 5/10 (p=0.6230) | [-17.54%, 27.87%] |

### CLEAN sample

| Outcome | N | mean | median | SD | t (p₁) | Wilcoxon (p₁) | Sign test (p) | 95% CI mean |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Property tax | 9 | 3.53% | 3.41% | 7.05 | 1.50 (p=0.0859) | 34.0 (p=0.1016) | 6/9 (p=0.2539) | [-0.39%, 8.11%] |
| Capital outlay | 6 | 27.31% | 23.05% | 21.79 | 3.07 (p=0.0139) | 21.0 (p=0.0156) | 6/6 (p=0.0156) | [14.80%, 45.11%] |
| Long-term debt | 9 | 2.49% | -5.66% | 40.96 | 0.18 (p=0.4301) | 21.0 (p=0.5898) | 4/9 (p=0.7461) | [-21.37%, 29.17%] |

## 2. Continuous-treatment regressions

Specification: `outcome_CAGR_c = α + β · log(MW_c) + γ · state_FE + ε_c`
Standard errors: HC3 robust.

### FULL sample

| Outcome | Spec | β (log MW) | SE | t | p | N | R² |
|---|---|---:|---:|---:|---:|---:|---:|
| Property tax | log MW only | -3.00pp | 3.98 | -0.75 | 0.4513 | 15 | 0.019 |
| Property tax | log MW + state FE | -11.46pp | inf | -0.00 | 1.0000 | 15 | 0.324 |
| Capital outlay | log MW only | 7.33pp | 26.69 | 0.27 | 0.7836 | 7 | 0.018 |
| Long-term debt | log MW only | 2.68pp | 13.84 | 0.19 | 0.8463 | 10 | 0.003 |

### CLEAN sample

| Outcome | Spec | β (log MW) | SE | t | p | N | R² |
|---|---|---:|---:|---:|---:|---:|---:|
| Property tax | log MW only | 3.86pp | 1.46 | 2.64 | 0.0083 | 9 | 0.215 |
| Capital outlay | log MW only | 14.31pp | 15.94 | 0.90 | 0.3692 | 6 | 0.208 |
| Long-term debt | log MW only | 3.26pp | 15.51 | 0.21 | 0.8334 | 9 | 0.004 |

## 3. Continuous-treatment regressions — DC tax share

Specification: `outcome_CAGR_c = α + β · dc_share_mid_c + ε_c`  (no state FE)

### FULL sample

| Outcome | β (per 1pp DC share) | SE | t | p | N | R² |
|---|---:|---:|---:|---:|---:|---:|
| Property tax | 0.047pp | 0.071 | 0.66 | 0.5071 | 15 | 0.023 |
| Capital outlay | -0.072pp | 0.381 | -0.19 | 0.8493 | 7 | 0.015 |
| Long-term debt | -0.050pp | 0.183 | -0.28 | 0.7831 | 10 | 0.007 |

### CLEAN sample

| Outcome | β (per 1pp DC share) | SE | t | p | N | R² |
|---|---:|---:|---:|---:|---:|---:|
| Property tax | 0.015pp | 0.030 | 0.50 | 0.6142 | 9 | 0.019 |
| Capital outlay | 0.204pp | 0.209 | 0.98 | 0.3292 | 6 | 0.287 |
| Long-term debt | -0.028pp | 0.219 | -0.13 | 0.8997 | 9 | 0.002 |

## 4. Influence diagnostics — property_tax_cagr ~ log_mw (CLEAN)

| FIPS | County | State | log_mw | CAGR | leverage | studentized | Cook's D |
|---|---|---|---:|---:|---:|---:|---:|
| 37069 | Franklin County | 37 | 6.21 | 21.96% | 0.132 | 3.68 | 0.369 |
| 38021 | Dickey County | 38 | 6.09 | -1.70% | 0.120 | -1.71 | 0.156 |
| 48125 | Dickens County | 48 | 5.19 | 0.34% | 0.190 | -0.64 | 0.052 |
| 41059 | Umatilla County | 41 | 6.68 | 6.81% | 0.226 | -0.52 | 0.045 |
| 37039 | Cherokee County | 37 | 4.90 | 4.80% | 0.274 | 0.26 | 0.015 |
| 41049 | Morrow County | 41 | 6.91 | 9.52% | 0.301 | -0.24 | 0.014 |
| 32029 | Storey County | 32 | 6.40 | 10.64% | 0.161 | 0.25 | 0.007 |
| 13317 | Wilkes County | 13 | 4.41 | 1.75% | 0.481 | 0.09 | 0.004 |
| 41013 | Crook County | 41 | 6.00 | 8.22% | 0.114 | 0.11 | 0.001 |
