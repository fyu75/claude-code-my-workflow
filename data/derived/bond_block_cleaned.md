# Bond Block — CLEANED treatment (operating-by-2022, crypto labeled, op-year timing)

**Date:** 2026-06-10. `scripts/python/62`. Supersedes 16/49/50/51. treated_post = treated AND year≥first_op_year; cluster county. Controls = never-DC-host (2,498).


Treated issuing bonds: **119** (clean 49 / crypto 50 / mixed 20); controls 2,776. Timing = first_op_year (staggered, deals to 2025).

## A. Deal-level hedonic spread — β on treated_post (NEGATIVE = tighter/cheaper)

| Cut | β (bps) | SE | p | N |
|---|---:|---:|---:|---:|
| ALL | **+4.92** | 3.14 | 0.118 | 71,237 |
| clean_dc | **+1.31** | 4.23 | 0.757 | 68,468 |
| crypto | **+15.65*** | 9.02 | 0.083 | 64,533 |
| mixed | **+8.80**** | 4.16 | 0.034 | 65,086 |

## B. Issuance, county-year — β on treated_post (POSITIVE = issue more)

| Cut | log(1+par $M) | log(n deals) |
|---|---|---|
| ALL | **+0.000**** | 0.000 | 0.013 | 31,371 | **-0.050** | 0.043 | 0.242 | 31,371 |
| clean_dc | **+0.000**** | 0.000 | 0.025 | 30,448 | **-0.099** | 0.064 | 0.123 | 30,448 |
| crypto | **+0.000** | 0.000 | 0.447 | 30,107 | **+0.071** | 0.068 | 0.296 | 30,107 |
| mixed | **+0.000** | 0.000 | 0.320 | 29,888 | **-0.071** | 0.078 | 0.359 | 29,888 |

## C. Rating — β on treated_post (extensive +=more rated; intensive −=better quality)

| Cut | extensive (any-rated share) | intensive (avg rating\|rated) |
|---|---|---|
| ALL | **-0.074***** | 0.017 | 0.000 | 98,428 | **-0.003** | 0.059 | 0.954 | 25,680 |
| clean_dc | **-0.081***** | 0.029 | 0.005 | 94,730 | **+0.024** | 0.079 | 0.759 | 24,669 |
| crypto | **-0.054**** | 0.022 | 0.012 | 89,942 | **+0.059** | 0.096 | 0.540 | 23,547 |
| mixed | **-0.090***** | 0.033 | 0.007 | 90,646 | **-0.103** | 0.088 | 0.240 | 23,669 |

## vs OLD (contaminated) results
- OLD: spread −23bps (artifact→+4.9 ns); issuance NULL; rating intensive NULL, extensive −7pp.
- KEY: does clean_dc differ from crypto? Real infrastructure (clean) is where any pricing/issuance/credit effect should concentrate; crypto is transient/leased.
