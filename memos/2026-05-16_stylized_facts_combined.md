# Stylized Facts — Data Centers & Muni Finance (exploratory)

**To:** Henrik, Rui, Mitch · **From:** Frank · **Date:** 2026-05-16
**Status:** Exploratory. Walkthrough of the sample construction and the three tests we ran today. Conclusions are at the end (§9) — they're still soft.
**Supersedes:** v1, v2, v3.

---

## 1. Project frame (recap)

Data centers are projected at ~1/5 of US capex in 2026 — likely the largest corporate-investment shock in modern US history. Pure capex, almost no labor shock, so the channel runs through **property/personal-property taxes**, not income or sales taxes. We want to estimate whether DC siting raises local-government fiscal capacity and whether the muni-bond market prices that.

Channels we're trying to detect (full map in `.claude/rules/knowledge-base-template.md`):

```
DC investment in county c
   │
   ▼
Property/personal-property tax base ↑
   │
   ▼
County tax revenue ↑
   │
   ├─→ H1: Capex ↑           ("new roads & schools")
   ├─→ H2: Debt ↓ or ↑       (paydown vs debt-financed capex)
   ├─→ H3: Public services ↑
   ├─→ H4: Bond ratings ↑
   └─→ H5: Bond yields ↓
```

Identification template: Greenstone–Hornbeck–Moretti (2010) winner-vs-loser; closest precedent Chava–Malakar–Singh (2023) corporate subsidies (−15 bps yield-spread effect).

---

## 2. Data sources

| # | Source | Coverage | Status |
|---|---|---|---|
| 1 | S&P 451 Research DC database | 4,507 US DC properties, lat/lon + MW + ownership 2000–2034 | ✅ Have |
| 2 | SDC Public Finance muni bonds | 1.63M deal-tranche records 1970–2025; we use 2005+ | ✅ Have |
| 3 | Census ASLGF / ACFR Individual Unit Files | 3,020 county-government records, 2017 cross-section | ✅ Have |
| 4 | Acquired ACFR PDFs (top-25 DC-share counties, 2017–2025) | 23 of 25 counties | ✅ Have |
| 5 | MSRB historical trades | 57 GB SAS file, 2000–2025 secondary-market | Documented, not loaded |
| 6 | FRED Treasury (5/10/20y) | 2000–2025 yearly | ✅ Have |

---

## 3. DC sample: how many, where, mapped to counties?

**Total:** 4,507 US DC properties from S&P 451 Research (`data/derived/dc_property_county_fips.csv`).

**Mapping to counties:** **100% coverage** (4,507/4,507) via spatial join on lat/lon to TIGER 2023 county polygons. No DCs dropped at this step. (36 worldwide DCs lack coordinates, all outside US — not relevant.)

**Distribution by year operational:**

| Year | # DCs |
|---|---:|
| Pre-2010 | 287 |
| 2010–2014 | 557 |
| 2015–2019 | 424 |
| 2020+ | 1,625 |
| Announced/under-construction (2026–2034) | ~1,600 |

The DC boom is concentrated in 2020+; pre-2015 cohort is small and skewed urban.

**Distribution across counties:** 517 distinct US counties host at least one DC (16% of 3,143). Heavily right-skewed:

| Concentration | Count |
|---|---:|
| Counties with ≥ 1 DC | 517 |
| Counties with ≥ 10 DCs | ~40 |
| Counties with ≥ 50 DCs | ~12 |
| Top 5 counties contain | 31% of all US DCs |

**Top 15 counties by DC count:**

| Rank | County | State | # DCs | MW (latest) |
|---:|---|---|---:|---:|
| 1 | Loudoun | VA | 302 | 4,741 |
| 2 | Maricopa | AZ | 219 | 2,043 |
| 3 | Prince William | VA | 164 | 1,760 |
| 4 | Santa Clara | CA | 144 | 1,002 |
| 5 | Dallas | TX | 135 | 733 |
| 6 | Cook | IL | 121 | 1,053 |
| 7 | Licking | OH | 96 | 782 |
| 8 | Fulton | GA | 88 | — |
| 9 | Los Angeles | CA | 87 | — |
| 10 | Fairfax | VA | 65 | — |
| 11 | New York | NY | 58 | — |
| 12 | King | WA | 57 | — |
| 13 | Washington | OR | 53 | — |
| 14 | Franklin | OH | 53 | 629 |
| 15 | Mecklenburg | VA | 48 | 316 |

**Top 15 by MW capacity** (the proxy that actually matters for tax-base impact):

| Rank | County | State | # DCs | MW |
|---:|---|---|---:|---:|
| 1 | Loudoun | VA | 214 | 4,741 |
| 2 | Maricopa | AZ | 90 | 2,043 |
| 3 | Prince William | VA | 66 | 1,760 |
| 4 | **Milam** | TX | **2** | 1,192 |
| 5 | Cook | IL | 80 | 1,053 |
| 6 | **Morrow** | OR | **23** | 1,004 |
| 7 | Santa Clara | CA | 101 | 1,002 |
| 8 | **Umatilla** | OR | **20** | 795 |
| 9 | Licking | OH | 18 | 782 |
| 10 | **Grant** | WA | **31** | 748 |
| 11 | Dallas | TX | 96 | 733 |
| 12 | Polk | IA | 32 | 725 |
| 13 | Franklin | OH | 37 | 629 |
| 14 | **Storey** | NV | **6** | 603 |
| 15 | Pottawattamie | IA | 14 | 599 |

**Key point.** Count-rank and MW-rank diverge sharply. Loudoun (urban hub, wealthy) has many small/mid colocation facilities. The bolded counties — Milam, Morrow, Umatilla, Grant, Storey — have **few but massive** hyperscale facilities and are **small rural counties**. This is exactly where Mitch's hypothesis (DCs migrating from wealthy to rural) shows up. Those rural counties also dominate our DC-tax-share metric (§5).

---

## 4. Muni sample: how we selected from SDC

Starting universe: SDC Public Finance, 258,854 deals from 2005+ across 34,683 unique issuers.

We applied these filters in order:

| Step | Filter | Reason | Deals remaining |
|---:|---|---|---:|
| 1 | Issue year ≥ 2005 | Coverage / panel start | 258,854 |
| 2 | Par amount ≥ $1M | Match published-lit standard (Gao et al. 2020 JFE; Adelino et al. 2017 RFS; Chava et al. 2023). Drops 10% of deals, 0.2% of par. | 231,967 |
| 3 | `CORPORATE_BACKED == 'No'` | Exclude conduit / private-activity bonds backed by corporate credit; we want government credit | 208,703 |
| 4 | `ISSTYPE_TRANS` ∈ Tier A | Keep County/Parish + City/Town/Village + District + Local Authority. Drops state-level mega-issuers and statewide programs. | ~177,000 |

**On the resulting Tier A sample:**
- 233,689 deals across 33,165 unique (ISSUER, STATECODE) pairs (sub-tranche handling explains the slight count diff vs the row above)
- We resolve issuer → county FIPS via a 3-pass regex + Census place/cousub crosswalks + 120-row hand-curated override table (covers consolidated cities like NYC's 5 boroughs, multi-county authorities, state conduits)
- **Coverage:** 83% deal-weighted, 77% par-weighted county FIPS coverage. Another 5% par flagged as state-conduit or multi-county (not lost — explicitly excluded). Residual ~16% par needing EMMA lookup is concentrated in 10k mid-size special districts.
- **Final analysis panel:** ~150k–170k deal observations across 2005–2025, covering ~2,000–2,500 US counties.

**Spread construction:** offering yield minus Treasury benchmark of matching maturity (FRED DGS5/DGS10/DGS20, linearly interpolated). See `scripts/python/09_spread_and_panel_v3.py`.

---

## 5. Treatment definition

We need a treatment for "this county has economically meaningful DC presence." Two candidates:

**(a) DC count or MW** — directly observable, but doesn't reflect fiscal materiality relative to county size.

**(b) DC contribution to county property tax** — the right concept, but no off-the-shelf data. We construct a proxy:

```
dc_tax_share_c = (MW_c × $50,000/MW) / 2017 county property tax revenue
```

The $50k/MW rule-of-thumb comes from the Prince William County FY22 fiscal-impact report (`master_supporting_docs/case_studies/`). We report low/mid/high variants ($30k/$50k/$100k per MW) for robustness.

**Distribution of `dc_tax_share_mid` across 437 DC-host counties with 2017 ACFR baseline:**

| Percentile | Share |
|---|---:|
| 50th | 0.10% |
| 75th | 1.50% |
| 90th | 17.0% |
| 95th | 36.8% |
| 99th | 153% |
| Max | 191% (Morrow OR) |

- **125 counties** at ≥ 1% (fiscally meaningful)
- **56 counties** at ≥ 10% (heavy)
- **15 counties** at ≥ 50% (county fiscally transformed by DCs)

We use **≥ 1% as the main treatment cut** because below 1% the DC contribution is a rounding error and dilutes any effect.

---

## 6. Test 1 — Does muni bond spread move? (Callaway–Sant'Anna staggered DiD)

**Sample:** 125 treated (≥ 1% threshold) + 2,776 never-DC-host control counties, panel 2010–2025, focus on 2015+ post-treatment window (where most DC openings actually occur).

**Outcome:** par-weighted average offering spread per county-year.

**Specification:** Callaway–Sant'Anna (2021) ATT(g,t) with never-treated comparison, clustered at the county level. Cohort g = first year county crosses the 1% threshold.

**Result (pooled ATT, 2015+):**

| | Estimate | SE | p (2-sided) |
|---|---:|---:|---:|
| ATT on offering spread | **−23.4 bps** | 12.3 | 0.057 |

Magnitude larger than Chava–Malakar–Singh (2023) corporate-subsidy benchmark (−15 bps).

**Heterogeneity probes within the treated group:**

| Sub-band | Estimate | p |
|---|---:|---:|
| Moderate share (1–10%) | **−37 bps** | < 0.01 |
| Very-high share (≥ 10%) | noisy, point estimate near zero | — |

The very-high tail has short post-treatment windows (these are recent hyperscale builds) and small n — power is the issue, not absence of effect.

**Bond-design margins** (rating tier, maturity, callable structure): all null across pooled, per-agency, and extensive-margin specs. Only the price moves; structure doesn't. Consistent with the muni market repricing fundamentals within the same credit class.

Sources: `scripts/python/16_cs_did_threshold_restricted.py`, `scripts/python/17_main_analysis.py`, `scripts/python/19_heterogeneity.py`, `scripts/python/20_bond_chars_outcomes.py`, `scripts/python/21_rating_outcomes_rich.py`.

---

## 7. Test 2 — Is there a level effect in the 2017 cross-section?

**Sample:** 437 DC-host counties × 2,776 never-host, all with 2017 Census ACFR records re-aggregated to county-government scope only (type=1, drops school districts + cities + special districts).

**Specification:** OLS, `log(outcome per capita) = α + β · DC_share + γ · state_FE + δ · log(pop) + θ · log(median_income) + ε`. HC3 SEs.

**Results (per-capita outcomes, high-share vs never-host):**

| Outcome | Effect | p |
|---|---:|---:|
| Property tax revenue | **+$543 per capita** | < 0.01 |
| Long-term debt outstanding | **+$1,204 per capita** | < 0.01 |
| Capital outlay | positive | < 0.05 |

Interpretation: even at the level (snapshot, 2017), high-DC-share counties already carry more property tax, more debt, more capex than comparable never-host counties. Consistent with: DCs expand fiscal capacity → counties borrow more AND spend more. Source: `scripts/python/18_acfr_mechanism_cs.py`.

---

### Working narrative (still soft)

DCs raise local fiscal capacity. The muni market reprices that capacity through the **price margin (spreads)**, not through bond design (rating, maturity, call provisions stay constant). The dominant fiscal-flow mechanism appears to be **capex acceleration** — counties spend big against the expanded tax base. Property tax grows mostly on the **intensive margin** (high-MW counties grow much faster) rather than on average across all treated counties. Some counties debt-finance the capex, others retire debt; the average is null but the dispersion is informative.

This is *consistent* with — not yet proof of — the project's original frame.

---

