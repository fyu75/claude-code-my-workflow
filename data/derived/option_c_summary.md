# Option C: National-benchmark within-county growth

Treated counties extracted: 23; clean sample: 17 (dropped 6: Mecklenburg VA, Pecos/Ward/Crane TX oil counties, Glasscock/Briscoe TX parser-suspected)
Benchmarks: property tax 3.4% (per-county median); capex 5.07% (BEA aggregate); debt 1.74% (Census ASLGF)

## Excess CAGR — FULL SAMPLE

| Outcome | N | Mean excess | t-stat | p (1-sided) | Benchmark |
|---|---:|---:|---:|---:|---:|
| Property tax revenue | 15 | -1.33% | -0.28 | 0.6086 | 3.40% |
| Capital outlay (capex) | 7 | 38.37% | 2.87 | 0.0142 | 5.07% |
| Long-term debt outstanding | 10 | 4.07% | 0.33 | 0.3742 | 1.74% |

## Excess CAGR — CLEAN SAMPLE

| Outcome | N | Mean excess | t-stat | p (1-sided) | Benchmark |
|---|---:|---:|---:|---:|---:|
| Property tax revenue | 9 | 3.53% | 1.50 | 0.0859 | 3.40% |
| Capital outlay (capex) | 6 | 27.31% | 3.07 | 0.0139 | 5.07% |
| Long-term debt outstanding | 9 | 2.49% | 0.18 | 0.4301 | 1.74% |

## Per-county detail

|   county_fips | county_name         | state   |   property_tax_excess |   capital_outlay_cagr |   capital_outlay_excess |   lt_debt_outstanding_excess |   property_tax_cagr |   lt_debt_outstanding_cagr |
|--------------:|:--------------------|:--------|----------------------:|----------------------:|------------------------:|-----------------------------:|--------------------:|---------------------------:|
|         13075 | Cook County         | GA      |           nan         |              0.138513 |               0.0878131 |                  nan         |        nan          |                nan         |
|         13303 | Washington County   | GA      |           nan         |            nan        |             nan         |                  nan         |        nan          |                nan         |
|         13317 | Wilkes County       | GA      |            -0.0165346 |            nan        |             nan         |                    0.1076    |          0.0174654  |                  0.125     |
|         21127 | Lawrence County     | KY      |           nan         |            nan        |             nan         |                   -0.0565565 |        nan          |                 -0.0391565 |
|         21157 | Marshall County     | KY      |           nan         |            nan        |             nan         |                   -0.482675  |        nan          |                 -0.465275  |
|         32029 | Storey County       | NV      |             0.0724125 |              0.750755 |               0.700055  |                   -0.363743  |          0.106413   |                 -0.346343  |
|         35061 | Valencia County     | NM      |           nan         |            nan        |             nan         |                  nan         |        nan          |                nan         |
|         37039 | Cherokee County     | NC      |             0.013991  |              0.196075 |               0.145375  |                  nan         |          0.047991   |                nan         |
|         37069 | Franklin County     | NC      |             0.185635  |              0.295023 |               0.244323  |                    0.452805  |          0.219635   |                  0.470205  |
|         38021 | Dickey County       | ND      |            -0.0510028 |            nan        |             nan         |                   -0.223555  |         -0.0170028  |                 -0.206155  |
|         40097 | Mayes County        | OK      |           nan         |            nan        |             nan         |                  nan         |        nan          |                nan         |
|         41013 | Crook County        | OR      |             0.0481517 |              0.276707 |               0.226007  |                    0.823459  |          0.0821517  |                  0.840859  |
|         41049 | Morrow County       | OR      |             0.061245  |              0.285772 |               0.235072  |                    0.114099  |          0.095245   |                  0.131499  |
|         41059 | Umatilla County     | OR      |             0.0340713 |            nan        |             nan         |                   -0.147773  |          0.0680713  |                 -0.130373  |
|         48045 | Briscoe County      | TX      |             0.0835306 |            nan        |             nan         |                  nan         |          0.117531   |                nan         |
|         48103 | Crane County        | TX      |            -0.199051  |            nan        |             nan         |                  nan         |         -0.165051   |                nan         |
|         48125 | Dickens County      | TX      |            -0.0306141 |            nan        |             nan         |                  nan         |          0.00338588 |                nan         |
|         48173 | Glasscock County    | TX      |             0.387621  |            nan        |             nan         |                  nan         |          0.421621   |                nan         |
|         48371 | Pecos County        | TX      |            -0.360076  |            nan        |             nan         |                  nan         |         -0.326076   |                nan         |
|         48475 | Ward County         | TX      |            -0.237923  |            nan        |             nan         |                  nan         |         -0.203923   |                nan         |
|         51117 | Mecklenburg County  | VA      |            -0.190478  |              1.09829  |               1.04759   |                    0.183664  |         -0.156478   |                  0.201064  |
|         53025 | Grant County        | WA      |           nan         |            nan        |             nan         |                  nan         |        nan          |                nan         |
|         53051 | Pend Oreille County | WA      |           nan         |            nan        |             nan         |                  nan         |        nan          |                nan         |