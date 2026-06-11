# Triangulated Matched DiD v2 (Census x v2, + CENSUS_TRUST tier)

**Date:** 2026-06-08.

## Sample build
**Treated** (n=123): USABLE=101, SINGLE_census_hirisk_nopost=10, DROP=6, SINGLE_census_nopost=5, SINGLE_census_HIRISK=1

**Controls** (n=304): USABLE=137, SINGLE_census_nopost=83, SINGLE_census_hirisk_nopost=60, CONFLICT=19, DROP=2, SINGLE_census_HIRISK=2, CAGR_OUT=1

- Usable treated by tier: {'PRIMARY': 49, 'EXPANDED': 20, 'CENSUS_TRUST': 32}  (total 101)
- Usable controls by tier: {'PRIMARY': 22, 'EXPANDED': 50, 'CENSUS_TRUST': 65}  (total 137)

## PRIMARY
- N treated (matched): **5**
- Matched effect mean **+1.53%/yr** (t p=0.1405); median +1.79%
- Wilcoxon p=0.1875; sign 4/5 (p=0.3750); bootstrap CI [-0.10,+2.75]%
- Treated CAGR mean **+5.72%/yr** vs 3.40% bench -> excess **+2.32%/yr** (p=0.0557)

## EXPANDED
- N treated (matched): **39**
- Matched effect mean **+0.41%/yr** (t p=0.4479); median +0.41%
- Wilcoxon p=0.3647; sign 23/39 (p=0.3368); bootstrap CI [-0.63,+1.42]%
- Treated CAGR mean **+5.44%/yr** vs 3.40% bench -> excess **+2.04%/yr** (p=0.0002)

## FULL
- N treated (matched): **85**
- Matched effect mean **+1.15%/yr** (t p=0.0198); median +1.04%
- Wilcoxon p=0.0174; sign 54/85 (p=0.0165); bootstrap CI [+0.22,+2.09]%
- Treated CAGR mean **+5.61%/yr** vs 3.40% bench -> excess **+2.21%/yr** (p=0.0000)

## FULL pooled OLS: CAGR ~ treated + state FE
- Treated coef **+1.25%/yr** (SE 0.52, p=0.0154), N=238
