# Power-Share vs Fiscal-Share Treatment Definition

**Date:** 2026-06-10. `scripts/python/52`. DC electricity / county electricity (physical intensity) vs the current DC-tax / county-property-tax >=1% cut (fiscal intensity).

**Numerator assumption:** DC MWh = MW x 8760 x 0.7 (load) x 1.5 (PUE) = 9,198 MWh/MW-yr. Sensitivity band: low (0.55x1.35) - high (0.85x1.60).

**Denominator:** NREL/OpenEI 2016 county total electricity (res+com+ind).

## Coverage
- DC counties with MW>0: **437**; matched to NREL electricity: **432** (5 unmatched FIPS)
- Fiscal-treated (dc_share_mid>=1%): **125**

## How physical and fiscal intensity relate
- Spearman rank corr( fiscal dc_share_mid , power_share ) = **0.973**
- Spearman rank corr( MW , power_share ) = 0.913  (power share is NOT just MW — county size matters)

## Do the two cuts select the same counties?
- Power cut set to match fiscal treated-set size (N=125) -> threshold **power_share >= 21.54%**
- **In BOTH: 114** | fiscal-only: 11 | power-only: 11 | Jaccard overlap **0.84**

## Top 20 counties by power share

| FIPS | County | ST | MW | power % (low–high) | fiscal % | pop |
|---|---|---|---:|---:|---:|---:|
| 48125 | Dickens County | TX | 180 | 4969.6 (3514.2–6436.8) | 181 | 2,237 |
| 41049 | Morrow County | OR | 1004 | 4557.0 (3222.4–5902.4) | 186 | 11,207 |
| 32029 | Storey County | NV | 603 | 4501.4 (3183.2–5830.4) | 176 | 3,941 |
| 38021 | Dickey County | ND | 440 | 3745.5 (2648.6–4851.3) | 145 | 5,160 |
| 48331 | Milam County | TX | 1192 | 3620.3 (2560.1–4689.1) | 157 | 24,372 |
| 48173 | Glasscock County | TX | 200 | 3399.8 (2404.2–4403.6) | 38 | 1,253 |
| 48275 | Knox County | TX | 166 | 3275.6 (2316.3–4242.6) | 115 | 3,807 |
| 48103 | Crane County | TX | 280 | 3125.4 (2210.1–4048.2) | 74 | 4,823 |
| 48109 | Culberson County | TX | 63 | 2489.0 (1760.0–3223.8) | 17 | 2,259 |
| 48371 | Pecos County | TX | 497 | 2067.3 (1461.9–2677.6) | 47 | 15,826 |
| 41013 | Crook County | OR | 404 | 1557.8 (1101.6–2017.7) | 81 | 21,334 |
| 48045 | Briscoe County | TX | 50 | 1431.7 (1012.4–1854.4) | 37 | 1,672 |
| 13075 | Cook County | GA | 270 | 1382.0 (977.3–1790.0) | 122 | 17,103 |
| 48475 | Ward County | TX | 423 | 1061.8 (750.9–1375.3) | 51 | 11,396 |
| 21127 | Lawrence County | KY | 250 | 1049.6 (742.2–1359.5) | 191 | 15,870 |
| 41059 | Umatilla County | OR | 795 | 1008.2 (712.9–1305.8) | 45 | 76,582 |
| 51107 | Loudoun County | VA | 4741 | 874.2 (618.2–1132.3) | 21 | 362,435 |
| 46119 | Sully County | SD | 30 | 866.0 (612.4–1121.7) | 21 | 1,456 |
| 41065 | Wasco County | OR | 170 | 790.2 (558.8–1023.6) | 23 | 25,657 |
| 35061 | Valencia County | NM | 414 | 666.0 (471.0–862.6) | 49 | 75,993 |

## Reading guide
- High rank corr + high Jaccard => the physical and fiscal cuts agree; power share buys OBJECTIVITY (no assessment/abatement assumptions) essentially for free, and gives a bounded continuous dose for intensity event-studies.
- Divergent counties are themselves informative: fiscal-only = DC is a big share of a small tax base but not of county load (or vice-versa); inspect for abatement vs industrial-county cases.
- Caveat: NREL county electricity is MODELED (2016 base year); DC MWh is derived from nameplate MW via load+PUE, not metered. Ranking is multiplier-invariant; the threshold is not.
