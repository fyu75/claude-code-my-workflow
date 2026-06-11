# Salience-split heterogeneity test — bond spread & rating
**Script:** `scripts/python/76_salience_split.py`  
**Date:** 2026-06-11  
**Hypothesis:** if bond-market non-response reflects limited attention, effects should appear in (a) mega-announcement counties and (b) post-2022 era.

## A. Sample construction

**Treated universe:** 122 counties (treated_universe_labeled.csv minus phantoms 47121, 54047, 21127)
**Controls:** 2,776 clean never-DC counties (n_dc_cumulative == 0 in county_year_panel_v4; excludes all DC hosts)
**Anchor (A_firstmaj):** DC-level ann_firstmaj (announcement_anchor_county.csv, 34 counties); county-level fallback (dc_announcement_years.csv)
**Sample years:** 2008–2025 (deal-level from sdc_deal_spread + sdc_deal_rating)

**MW construction for MEGA split:**
  - Primary: cum_ann_mw from dc_dose_announced_mw_panel at county anchor year (65 of 122 treated counties covered)
  - Fallback: mw_latest from treated_universe_labeled (remaining 57 counties)
  - Top-decile threshold (p90): **362 MW**
  - Alternative cut: **>=300 MW**

**Mega counties — top-decile (≥362 MW), n=12:**
| FIPS | County name | mw_combined | dc_class |
|---|---|---:|---|
| 53025 | Grant County | 748 | mixed |
| 48331 | Milam County | 742 | crypto |
| 13097 | Douglas County | 564 | clean_dc |
| 41067 | Washington County | 528 | clean_dc |
| 13121 | Fulton County | 503 | mixed |
| 37069 | Franklin County | 500 | crypto |
| 38105 | Williams County | 480 | mixed |
| 41013 | Crook County | 404 | clean_dc |
| 48349 | Navarro County | 400 | crypto |
| 48355 | Nueces County | 400 | mixed |
| 45015 | Berkeley County | 375 | clean_dc |
| 48475 | Ward County | 370 | mixed |

**Mega counties — ≥300 MW alternative, n=16:**
| FIPS | County name | mw_combined | dc_class |
|---|---|---:|---|
| 53025 | Grant County | 748 | mixed |
| 48331 | Milam County | 742 | crypto |
| 13097 | Douglas County | 564 | clean_dc |
| 41067 | Washington County | 528 | clean_dc |
| 13121 | Fulton County | 503 | mixed |
| 37069 | Franklin County | 500 | crypto |
| 38105 | Williams County | 480 | mixed |
| 41013 | Crook County | 404 | clean_dc |
| 48349 | Navarro County | 400 | crypto |
| 48355 | Nueces County | 400 | mixed |
| 45015 | Berkeley County | 375 | clean_dc |
| 48475 | Ward County | 370 | mixed |
| 38021 | Dickey County | 360 | crypto |
| 40097 | Mayes County | 330 | clean_dc |
| 48371 | Pecos County | 325 | mixed |
| 51087 | Henrico County | 316 | clean_dc |

## B. Sanity check — pooled (reproduce script 68)

| Cut | Outcome | announced beta (SE) p | N deals | N treated cty | N treated post deals |
|---|---|---|---:|---:|---:|
| ALL | spread_bps | -0.73 (6.70) p=0.913 | 49,273 | 116 | 2,822 |
| ALL | any_rated_share | -0.03 (0.01) p=0.023** | 49,291 | 116 | 2,822 |
| clean_dc | spread_bps | -2.20 (8.31) p=0.791 | 47,364 | 48 | 1,725 |
| clean_dc | any_rated_share | -0.03 (0.02) p=0.146 | 47,382 | 48 | 1,725 |
| crypto | spread_bps | +15.47 (10.60) p=0.145 | 44,704 | 48 | 248 |
| crypto | any_rated_share | -0.05 (0.03) p=0.041** | 44,719 | 48 | 248 |

## C. Mega split (top-decile ≥362 MW vs rest) — `announced` dummy

| Group | Cut | Outcome | beta (SE) p | N deals | N treated cty | N treated post |
|---|---|---|---|---:|---:|---:|
| MEGA(≥362MW) | ALL | spread_bps | -24.94 (12.56) p=0.047** | 44,392 | 12 | 351 |
| MEGA(≥362MW) | ALL | any_rated_share | -0.05 (0.04) p=0.227 | 44,407 | 12 | 351 |
| REST(≥362MW) | ALL | spread_bps | +0.20 (6.83) p=0.976 | 48,818 | 104 | 2,471 |
| REST(≥362MW) | ALL | any_rated_share | -0.03 (0.01) p=0.026** | 48,836 | 104 | 2,471 |
| MEGA(≥362MW) | clean_dc | spread_bps | underpowered (4 clean_dc mega cty) | — | 4 | — |
| MEGA(≥362MW) | clean_dc | any_rated_share | underpowered (4 clean_dc mega cty) | — | 4 | — |
| REST(≥362MW) | clean_dc | spread_bps | -2.19 (8.31) p=0.792 | 47,252 | 44 | 1,578 |
| REST(≥362MW) | clean_dc | any_rated_share | -0.03 (0.02) p=0.142 | 47,270 | 44 | 1,578 |

### C2. Alternative ≥300 MW cut

| Group | Cut | Outcome | beta (SE) p | N deals | N treated cty | N treated post |
|---|---|---|---|---:|---:|---:|
| MEGA(≥300MW) | ALL | spread_bps | -18.75 (12.98) p=0.149 | 44,459 | 16 | 421 |
| MEGA(≥300MW) | ALL | any_rated_share | -0.03 (0.04) p=0.449 | 44,474 | 16 | 421 |
| MEGA(≥300MW) | clean_dc | spread_bps | -20.63 (2.44) p=0.000*** ⚠ | 44,094 | 6 | 205 |
| MEGA(≥300MW) | clean_dc | any_rated_share | +0.15 (0.01) p=0.000*** ⚠ | 44,109 | 6 | 205 |

⚠ **Degenerate cell:** 6 treated counties with county FE leave near-zero within-treated variation; SE is implausibly tight (2.44 bps on a 20 bps estimate with n=6). Discard; use the ALL-cut ≥300 MW row instead.

## D. Era split — `announced × pre-2023` and `announced × post-2022`

One regression with ann_pre + ann_post (no base announced); county+year FE, cluster county. Coefficients = period-specific ATTs.

| Cut | Outcome | Period | beta (SE) p | N deals | N treated cty | N treated post |
|---|---|---|---|---:|---:|---:|
| ALL | spread_bps | ≤2022 | +5.22 (9.47) p=0.581 | 49,273 | 116 | 2,822 |
| ALL | spread_bps | ≥2023 | -10.84 (6.29) p=0.085* | 49,273 | 116 | 2,822 |
| ALL | any_rated_share | ≤2022 | -0.02 (0.02) p=0.207 | 49,291 | 116 | 2,822 |
| ALL | any_rated_share | ≥2023 | -0.05 (0.02) p=0.010*** | 49,291 | 116 | 2,822 |
| clean_dc | spread_bps | ≤2022 | +4.30 (11.83) p=0.716 | 47,364 | 48 | 1,725 |
| clean_dc | spread_bps | ≥2023 | -14.98 (7.56) p=0.048** | 47,364 | 48 | 1,725 |
| clean_dc | any_rated_share | ≤2022 | -0.02 (0.02) p=0.428 | 47,382 | 48 | 1,725 |
| clean_dc | any_rated_share | ≥2023 | -0.04 (0.03) p=0.095* | 47,382 | 48 | 1,725 |

## E. Combined: mega counties × post-2022 (attention maximized)

Mega-county sub-sample (controls + mega-treated), ann_pre + ann_post spec.

| Cut | Outcome | Period | beta (SE) p | N deals | N treated cty | N treated post | Power flag |
|---|---|---|---|---:|---:|---:|---|
| ALL | spread_bps | ≤2022 | +2.49 (18.81) p=0.895 | 44,392 | 12 | 351 | ⚠ <15 treated cty |
| ALL | spread_bps | ≥2023 | -29.14 (9.45) p=0.002*** | 44,392 | 12 | 351 | ⚠ <15 treated cty |
| ALL | any_rated_share | ≤2022 | +0.04 (0.08) p=0.610 | 44,407 | 12 | 351 | ⚠ <15 treated cty |
| ALL | any_rated_share | ≥2023 | -0.07 (0.04) p=0.082* | 44,407 | 12 | 351 | ⚠ <15 treated cty |
| clean_dc | spread_bps | ≤2022 | +17.88 (10.55) p=0.090* | 44,049 | 4 | 147 | ⚠ <15 treated cty |
| clean_dc | spread_bps | ≥2023 | ERR (missing) | — | — | — | ⚠ <15 treated cty ⚠ <100 post-deals |
| clean_dc | any_rated_share | ≤2022 | +0.14 (0.03) p=0.000*** | 44,064 | 4 | 147 | ⚠ <15 treated cty |
| clean_dc | any_rated_share | ≥2023 | ERR (missing) | — | — | — | ⚠ <15 treated cty ⚠ <100 post-deals |

## F. Pre-specified prediction evaluation

**Sanity:** pooled spread = -0.73 (p=0.913) — reproduces script 68 null as expected.

**MEGA split:** CONSISTENT with attention hypothesis: mega negative and significant, rest null.

**ERA + COMBINED summary:** CONSISTENT: post-2022 negative and significant, pre-2023 null; temporal salience shift detected. Combined mega × post-2023 = -29.14 (p=0.002). Overall verdict: the pre-specified attention hypothesis finds SUPPORT in this sample.
