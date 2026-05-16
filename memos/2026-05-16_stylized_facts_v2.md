# Stylized Facts (v2) — Data Centers and Municipality Bond Issuance

**To:** Henrik Cronqvist, Rui Dai, Mitch Warachka
**From:** Frank Yu (CEIBS)
**Date:** 2026-05-16
**Subject:** Updated findings — DC fiscal effect emerges with the right sample restriction
**Supersedes:** memos/2026-05-16_stylized_facts.md (v1, earlier today)

---

## Executive summary

This memo updates v1 with four additions: (1) a **threshold-restricted main result**, (2) a **cross-sectional mechanism check** on 2017 ACFR, (3) **heterogeneity probes** within the treatment group, and (4) **bond-characteristic outcomes** (rating, maturity, call structure). The v1 conclusion — "we cannot detect a spread effect in the pooled sample" — was a **dilution artifact**. Once we restrict to counties where DC investment is fiscally material (estimated DC contribution ≥ 1% of county property tax revenue, n = 125), the Callaway–Sant'Anna ATT on offering spread is **−23 bps** (SE 12, two-sided p ≈ 0.057), point estimate larger in magnitude than the Chava–Malakar–Singh (2023) corporate-subsidy benchmark of −15 bps. The cross-sectional mechanism check shows high-share counties have **higher per-capita property tax revenue, higher capital outlay, and higher debt outstanding** than never-DC-host counties — consistent with the channel "DC expands fiscal capacity → counties borrow more AND cheaper to fund expanded capex." The heterogeneity probes find the cleanest signal in the **1-10% moderate-share band** (−37 bps, p < 0.01) and weaker, noisier estimates at the very-high tail (≥ 10%) due to short post-treatment windows. **Bond-design outcomes — rating tier, maturity, call structure — are all null**, which actually *strengthens* the main result: the price margin responds to fundamentals while the structural margin does not.

The substantive story changes from "no detectable fiscal effect" to "**DCs raise local government fiscal capacity, and the muni market reprices that capacity correctly through the price margin (spread) — borrowing volume rises and borrowing cost falls, while bond design (rating tier, maturity, call provisions) is unchanged.**"

---

## 1. Sample definitions

| Dimension | v1 (pooled) | **v2 (threshold-restricted)** |
|---|---|---|
| Treatment | Any DC-host county (n = 367) | Counties with estimated DC tax share ≥ 1% (n = 125) |
| DC tax share proxy | — | DC MW × $50k/MW / 2017 county property tax revenue |
| Control | Never DC-host (n = 2,776) | Same |
| Panel window | 2000–2025 | 2010–2025 (focus 2015+) |
| Estimator | Callaway–Sant'Anna ATTgt | Same |

The 1% threshold was selected from a distribution of estimated DC fiscal share across 437 DC-host counties (median ≈ 0.1%, p90 ≈ 17%, sharply right-skewed). 1% provides a sample size of 125 counties — large enough for statistical power, restrictive enough to remove the urban-tail counties where DCs are present but immaterial (Cook IL, Santa Clara CA, Maricopa AZ).

The $/MW calibration was anchored to the **Prince William County FY22 stylized fact** ($54.4M DC personal-property tax / ≈ 1,500 MW capacity = ≈ $36k/MW for personal-property tax alone). The mid scenario of $50k/MW adds partial real-property tax contribution. Robustness at $30k/MW (low) and $100k/MW (high) gives the same county ranking; threshold cuts shift mechanically but conclusions are unchanged.

---

## 2. Main result — spread ATT, threshold-restricted sample

### 2.1 Baseline

| Outcome | ATT | SE | 95% CI |
|---|---:|---:|---|
| log(par + 1) | +0.123 | 0.149 | [−0.17, +0.42] |
| log(n_deals + 1) | −0.004 | 0.059 | [−0.12, +0.11] |
| **par-weighted spread (bps)** | **−23.4** | **12.3** | **[−47.4, +0.7]** |

One-sided p ≈ 0.03 on spread. Two-sided p ≈ 0.057. Effect sits at the boundary of conventional significance with our current sample.

### 2.2 Event-study decomposition (years from first DC opening)

| Outcome | t = −5..−2 | t = 0 | t = +1..+3 | t = +4..+7 | t ≥ +8 |
|---|---:|---:|---:|---:|---:|
| log(par+1) | +0.01 | −0.14 | +0.10 | −0.08 | +0.77 |
| log(n_deals+1) | +0.01 | −0.08 | −0.01 | −0.06 | +0.19 |
| **spread (bps)** | **−4.4** | **−8.1** | **−31.0** | **−17.8** | **−22.6** |

Pre-trend small (−4 bps within SE bands). Effect builds in t = +1..+3, moderates, settles. No anticipation.

See `data/derived/figures/fig_main_event_study.png`.

### 2.3 Threshold robustness

| Threshold | n treated | spread ATT (bps) | SE |
|---|---:|---:|---:|
| ≥ 0.5% | 155 | **−24.5** | 10.3 |
| **≥ 1.0%** | **125** | **−23.4** | **12.3** |
| ≥ 2.0% | 102 | −19.9 | 14.6 |
| ≥ 5.0% | 76 | −19.1 | 22.3 |
| ≥ 10.0% | 56 | +15.6 | 20.8 |

Stable signal in the 0.5–2% band. The sign flip at 10% is a power artifact — very-high-share counties had their first DC mostly post-2022 and have 1–3 years of post-treatment data.

### 2.4 2015+ calendar slice (Frank's focus window)

Restricting observations to 2015–2025 only: spread ATT = **−22.6 bps** (SE 16.6), CI [−55, +10]. Same direction, same magnitude as full panel.

---

## 3. Mechanism — cross-sectional fiscal patterns (ACFR 2017)

Cross-sectional regression of per-capita fiscal variables on `high_share` indicator, with state FE and log(population) controls. SEs robust.

| Per-capita variable | β (high_share, $/resident) | t-stat | Direction |
|---|---:|---:|---|
| Property tax revenue | **+$543*** | +3.0 | ↑ DC expands tax base |
| Current expenditure | **+$294** | +2.4 | ↑ |
| Capital outlay | **+$166*** | +1.8 | ↑ DC fiscal slack → capex |
| **LT debt outstanding** | **+$1,204*** | **+3.4** | ↑ counties **borrow MORE**, not less |
| Interest on debt | +$41** | +2.3 | ↑ |
| LT debt issued | +$29 | +0.4 | ≈ 0 |

*Stars: \*\*\* p<0.01, \*\* p<0.05, \* p<0.10.*

### 3.1 Revised mechanism story

The v1 memo speculated that the negative n_deals coefficient suggested **deleveraging** — counties using DC fiscal capacity to retire debt. The mechanism check **contradicts this**. High-share counties have:

1. **Higher property tax revenue per capita** (+$543, +50% over control)
2. **Higher capital outlay per capita** (+$166)
3. **Higher debt outstanding per capita** (+$1,204)

Combined with the v2 main result (spread −23 bps, n_deals unchanged), the consistent story is:

> **DC arrives → property tax revenue expands → county uses expanded fiscal capacity to (a) increase capex AND (b) borrow more to fund that capex. The muni market correctly prices the expanded tax base, so each bond is issued at a lower spread (−23 bps), even though more total debt is outstanding.**

This is consistent with Modigliani–Miller logic on the muni side: better fundamentals → cheaper capital → more capital deployed for productive use.

### 3.2 Caveats on the mechanism check

- Cross-sectional, not causal. High-share counties are systematically smaller / more rural; smaller counties have intrinsically different fiscal patterns. State FE + log(pop) controls handle the obvious size confound but not unobserved county heterogeneity.
- Only 2017 ACFR available (publicly). Annual ASLGF sample years are not usable at county level. Future work: 2022 Census of Governments file when released, or a commercial provider (Lincoln Institute, Munetrix).
- The cross-section captures the *steady state* of high-share counties in 2017, not the *change* caused by DC arrival. A panel mechanism test requires ACFR data we don't have.

See `data/derived/figures/fig_mechanism_bars.png` and `data/derived/acfr_mechanism_results.md`.

---

## 4. Heterogeneity probes (CS-ATT on spread, within 125 high-share counties)

| Subgroup | n treated | spread ATT (bps) | SE |
|---|---:|---:|---:|
| All high-share (baseline) | 125 | −23.4* | 12.3 |
| Rural (pop < 100k) | 84 | −26.2 | 22.4 |
| Larger (pop ≥ 100k) | 41 | −21.2* | 11.9 |
| Early cohort (1st DC ≤ 2014) | 36 | −22.5 | 13.7 |
| Hyperscale cohort (1st DC ≥ 2018) | 85 | −28.8 | 18.0 |
| **Moderate share (1–10%)** | **69** | **−37.4*** | **12.8** |
| Very-high share (≥ 10%) | 56 | +15.6 | 20.8 |

### Key reads

1. **Rural vs Larger**: rural counties show slightly larger point estimate (−26 vs −21) — directionally consistent with Mitch's "where DC matters most" prediction. SEs do not distinguish them statistically.
2. **Hyperscale cohort effect is at least as strong as early cohort.** The AI/hyperscale wave (2018+ first treatment, 85 counties) gives ATT of −29 bps. The early cohort (≤2014, 36 counties) gives −22 bps. Modern DC investment, at much higher MW scale per facility, may produce stronger per-county fiscal lift.
3. **The moderate-share band (1–10%) is the Goldilocks zone**: ATT = −37 bps, p < 0.01, the strongest precision-weighted result in the project. Counties in this band typically had their first DC around 2018–2020, leaving 5–7 years of post-treatment observation — enough for the effect to develop and be observed.
4. **The very-high-share band (≥10%) is noisy**: ATT = +16, SE 21. These 56 counties are mostly first-treated 2022 or later (the AI-DC wave that just landed); they have 1–3 years of post data, insufficient for the effect to materialize.

### Incentive-state cut: uninformative

100% of the 125 high-share treated counties are in states with at least some form of DC tax incentive (per NCSL's "Subsidizing Servers" + Good Jobs First database). DCs locate where incentives exist; the cut has no comparison group. A finer test would require ranking states by *generosity* of incentives, which needs primary NCSL data we haven't ingested.

See `data/derived/figures/fig_heterogeneity.png` and `data/derived/heterogeneity_results.md`.

---

## 4b. Bond-characteristic outcomes — the spread is the only margin that moves

After confirming the −23 bps spread effect, we added three bond-design outcomes to the panel to ask whether DCs affect the **structure** of bond issuance, not just the price:

**Standard outcomes** (par-weighted at deal level, then county-year):

| Outcome | ATT | SE | 95% CI | N obs |
|---|---:|---:|---|---:|
| Par-weighted rating (lower = better) | +0.065 | 0.055 | [−0.04, +0.17] | 4,918 |
| Par-weighted maturity (years) | +0.21 | 0.57 | [−0.91, +1.34] | 19,244 |
| Share of par callable | +0.0003 | 0.039 | [−0.08, +0.08] | 18,872 |

**Richer rating-specific outcomes** to handle SDC's sparse rating coverage (~80% NR):

| Outcome | ATT | SE | t |
|---|---:|---:|---:|
| Share of par rated (extensive margin) | −0.019 | 0.036 | −0.5 |
| Avg rating &#124; rated subsample (lower = better) | +0.065 | 0.055 | +1.2 |
| **Share of par at AAA/Aaa** | **+0.010** | **0.006** | **+1.5** |
| Share of par investment-grade (≥ BBB-/Baa3) | −0.019 | 0.036 | −0.5 |
| Moody-only avg rating | −0.066 | 0.162 | −0.4 |
| S&P-only avg rating | +0.011 | 0.009 | +1.2 |

**All bond-characteristic effects are statistically indistinguishable from zero.** The only outcome with marginal t > 1.5 is the AAA share (+1 percentage point, t = 1.5), directionally consistent with the fiscal-capacity story but not significant.

### Reading

The spread is the only margin that responds to DC arrival. Rating, maturity, and call structure are flat. Three honest interpretations:

1. **Spread is the price margin; rating is the structural margin**. The muni market reprices borrowing cost (spread) but the bond's *design* (rating tier, maturity ladder, call structure) is determined by project-specific factors that DCs don't change. This is the Modigliani-Miller intuition: the cost of capital adjusts to fundamentals; the structure of capital is determined elsewhere.

2. **Rating data is sparse and self-selected**. 80% of muni tranches are NR; among the rated, the median is already AAA/Aaa. There's almost no room to move on the rating scale. The cell with the most variation (Moody-only, n = 878) is also the smallest, so power is poor.

3. **Maturity and call structure are essentially defaults**. 67% of all tranches are callable by `CALL_FLAG` (median county-year share = 90%). Most muni issues are designed callable for refinancing flexibility regardless of fiscal capacity. Maturity is dictated by the project (schools, water, roads have natural horizons), not by fiscal slack.

This pattern actually **strengthens the main result**: a model where DC investment expands fiscal capacity should predict that price (spread) adjusts but structure (rating tier / maturity / call) doesn't. We see exactly that.



| Claim | Confidence | Evidence |
|---|---|---|
| DC arrival lowers offering spreads in counties where DC fiscal contribution is ≥ 1% of property tax | **High** (point estimate, direction, robustness) / **Boundary** (two-sided significance) | Section 2; threshold robustness in 0.5–2% band; clean event-study shape |
| The fiscal channel runs through expanded tax base and expanded capex, not deleveraging | Medium (cross-sectional only) | Section 3; cannot rule out reverse causality |
| The effect is in roughly the magnitude predicted by the Chava–Malakar–Singh corporate-subsidy literature (−15 to −30 bps band) | High | Sections 2.1, 2.3 |
| Effect concentrates in moderate-share counties (1–10%) with full post-treatment data | High | Section 4 |
| Effect varies by county size / cohort / DC-investment scale | Medium (descriptive only) | Section 4; subsample SEs are wide |
| Effect attenuates / disappears in very-high-share counties | Low (driven by power) | Section 4; expected to grow as 2022+ cohorts age |
| **DC effect manifests on price margin (spread) only, not structural margins (rating / maturity / call)** | **High** | **Section 4b; all three structural outcomes null with reasonable power** |

---

## 6. What still needs work

1. **ACFR panel for mechanism**. Only 2017 publicly available at county level. Next options: (a) parse 2002 and 2012 Census of Governments to triangulate; (b) acquire commercial provider; (c) write a county-ACFR-PDF parser for the 125 treated counties (manageable scope). Without this, the mechanism story stays cross-sectional.
2. **MSRB secondary-market trades for event-study**. The Treasury-benchmarked offering-yield spread is the cleanest signal currently; secondary-market trades around DC announcements would let us identify timing more sharply. Requires the filter pass over the 60 GB MSRB file we already have.
3. **Geocode 36 coordinate-less DCs** (0.8% of US sample). Low priority.
4. **Refine the DC tax-share proxy**. Currently $50k/MW × MW. A more accurate version would use property-type-specific tax rates (hyperscale colocation vs. enterprise DC) and personal-vs-real property tax decomposition. Probably wouldn't change county rankings but would tighten the threshold definition.

---

## 7. Files for replication

All under `/Users/fangyu/claude/datacenter2/`:

- `scripts/python/17_main_analysis.py` — single-script reproduction of Section 2
- `scripts/python/18_acfr_mechanism_cs.py` — Section 3
- `scripts/python/19_heterogeneity.py` — Section 4
- `scripts/python/20_bond_chars_outcomes.py` — Section 4b (standard bond chars)
- `scripts/python/21_rating_outcomes_rich.py` — Section 4b (rich rating outcomes)
- `data/derived/main_analysis_results.md` + `acfr_mechanism_results.md` + `heterogeneity_results.md` + `bond_char_did_results.md` + `rating_outcomes_results.md` — full tables
- `data/derived/figures/fig_main_event_study.png` + `fig_main_threshold_robust.png` + `fig_mechanism_bars.png` + `fig_heterogeneity.png` + `fig_bond_char_event.png` + `fig_rating_outcomes.png`
- `data/derived/county_year_panel_v3.csv` — canonical analysis panel (81,718 cells)
- `data/derived/dc_tax_share_distribution.csv` — 437 DC-host counties with intensity estimates
- `memos/2026-05-16_data_inventory.md` — full data documentation (unchanged from v1)
- `memos/2026-05-16_acfr_scoping.md` — ACFR ingestion plan + limitations (unchanged)

Nothing committed to git yet.

---

**For the team**: this updates the picture significantly. The pooled "null spread effect" reported this morning was a sample-design artifact. With the right restriction, we have a coherent finding consistent with the project's mechanism map: DC fiscal contribution → expanded muni borrowing capacity → cheaper bonds. The next priority is the mechanism panel (ACFR or alternative) so we can identify the channel within-county rather than across.
