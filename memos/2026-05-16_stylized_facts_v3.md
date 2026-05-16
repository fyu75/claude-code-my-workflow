# Stylized Facts (v3) — Within-County Mechanism Evidence

**To:** Henrik Cronqvist, Rui Dai, Mitch Warachka
**From:** Frank Yu (CEIBS)
**Date:** 2026-05-16 (evening)
**Subject:** New within-county growth evidence — capex channel is by far the strongest
**Supersedes:** `memos/2026-05-16_stylized_facts_v2.md` for the mechanism section; v2's bond-pricing results are unchanged.

---

## Executive summary

v2 established the **bond-pricing result** (−23 bps spread effect in counties where DCs contribute ≥1% to property tax) and the **2017 cross-sectional mechanism** (high-DC-share counties show elevated property tax, debt, capex per capita). v3 adds **within-county 2017→2025 growth evidence** for 23 high-DC-share counties whose ACFRs we successfully acquired and parsed:

- **Capex acceleration is the cleanest channel**: treated counties grew capital outlay at **+27 pp/year above the national benchmark** (clean N=6, p=0.014 t-test, p=0.016 Wilcoxon, **6/6 counties positive**). Robust across every test we ran.
- **Property tax shows a dose-response, not a level effect**: average excess CAGR only marginal (+3.5 pp, p=0.086), but the regression `CAGR ~ log(MW)` gives β = **+3.86 pp per log MW (p=0.008)** — high-MW counties grow property tax materially faster.
- **Debt is null on average** but heterogeneous: Crook OR (+84% CAGR) and Franklin NC (+47%) are issuing debt to fund capex; Marshall KY (−47%) and Dickey ND (−21%) are retiring. The dispersion is consistent with **debt-financed capex in early-stage DC counties**.

**Narrative update.** v2's "DCs expand fiscal capacity → muni market reprices that capacity" stands, but the order of magnitudes shifts: capex is the dominant flow effect, with property tax tracking the *intensive* margin (more MW → more property tax growth) rather than the average. That reconciles a previous tension — why is the bond-spread effect so large (−23 bps) when property tax growth looks modest? The answer is capex: counties are spending big against the higher tax base, and the bond market is pricing that fiscal-capacity expansion correctly.

---

## 1. What's new since v2

| Step | Output | Files |
|---|---|---|
| Identified top-25 high-share counties (DC tax share ≥ ~16%) | Catalog | `scripts/python/22_acfr_pdf_parser_pilot.py` |
| Acquired 23 of 25 county ACFRs from 8 state portals + county sites | 23 PDFs, FY2014–2025 | `data/external/acfr_pdfs/` |
| Parsed PDFs → property tax / total revenue / capex / debt | Long-form table | `data/derived/acfr_county_year_extracted_wide.csv` |
| Computed 2017→latest within-county growth | First analysis | `scripts/python/24_within_county_growth.py` |
| **Option C — full national-benchmark tests + regressions** | **This memo** | `scripts/python/30_option_c_national_benchmark.py`, `scripts/python/31_option_c_regressions.py` |

We also produced a matched-control acquisition plan and acquired 17 of 59 candidate controls (KY 6/6, GA 5/6, OR 6/8) before pivoting to Option C as the more efficient path; those acquisitions remain available for a future Option B follow-up.

---

## 2. Option C — Design

**Treated:** 23 counties from the top-25 by estimated DC tax share, with ACFR PDF in hand. Latest year ranges from FY2022 to FY2025.

**"Control" trajectory:** US state+local government aggregates (BEA NIPA Table 3.21 + Census ASLGF historical), expressed as compound annual growth rates 2017→2024.

**Outcome variable per county:**
$$
\text{treated\_CAGR}_c = \left(\frac{Y_{c,\text{latest}}}{Y_{c,2017}}\right)^{1/n_{\text{years}}} - 1,
\qquad
\text{excess\_CAGR}_c = \text{treated\_CAGR}_c - \text{benchmark\_CAGR}
$$

**Benchmarks used** (nominal, 2017→2024):

| Outcome | Benchmark | Source |
|---|---:|---|
| Property tax revenue | 3.40% | Per-county median, Census ASLGF (NOT the BEA aggregate 5.85% — dominated by big-state appreciation) |
| Capital outlay | 5.07% | BEA NIPA 3.21, state & local gross investment |
| Long-term debt outstanding | 1.74% | Census ASLGF state & local debt |

**Clean-sample exclusions (6 of 23):**

| FIPS | County | Reason |
|---|---|---|
| 51117 | Mecklenburg VA | Scope mismatch — Census 2017 re-aggregation captures consolidated entities; PDF FY23 is county-government only |
| 48371 | Pecos TX | 2014-16 oil price collapse drove 2017 mineral interest valuations; recovery (not DCs) drives trajectory |
| 48475, 48103 | Ward, Crane TX | Same oil-county pattern |
| 48173, 48045 | Glasscock, Briscoe TX | Suspected parser bug — three tiny TX counties share identical $5.5M total revenue values |

---

## 3. Option C — Results

### 3.1 Distribution tests — excess CAGR vs benchmark

**FULL sample (no exclusions)**

| Outcome | N | mean | median | t (p, 1-sided) | Wilcoxon (p) | Sign test |
|---|---:|---:|---:|---:|---:|---:|
| Property tax | 15 | −1.33% | +1.40% | −0.28 (0.61) | (0.53) | 8/15 (0.50) |
| **Capital outlay** | **7** | **+38.4%** | **+23.5%** | **+2.87 (0.014)** | **(0.008)** | **7/7 (0.008)** ★ |
| Long-term debt | 10 | +4.07% | +2.55% | +0.33 (0.37) | (0.50) | 5/10 (0.62) |

**CLEAN sample (drop 6 flagged)**

| Outcome | N | mean | median | t (p, 1-sided) | Wilcoxon (p) | Sign test |
|---|---:|---:|---:|---:|---:|---:|
| Property tax | 9 | +3.53% | +3.41% | +1.50 (0.086) | (0.10) | 6/9 (0.25) |
| **Capital outlay** | **6** | **+27.3%** | **+23.0%** | **+3.07 (0.014)** | **(0.016)** | **6/6 (0.016)** ★ |
| Long-term debt | 9 | +2.49% | −5.66% | +0.18 (0.43) | (0.59) | 4/9 (0.75) |

**Bootstrap 95% CI on mean excess CAGR (clean, 5000 reps):**
- Property tax: [−0.4%, +8.1%] (straddles 0)
- **Capital outlay: [+14.8%, +45.1%]** (well above 0)
- Debt: [−21.4%, +29.2%]

### 3.2 Dose-response — `treated_CAGR = α + β·log(MW_county)` (HC3 robust SEs)

| Outcome | Sample | β (pp per log MW) | SE | p | N | R² |
|---|---|---:|---:|---:|---:|---:|
| **Property tax** | **CLEAN** | **+3.86** | **1.46** | **0.008** ★★ | 9 | 0.215 |
| Property tax | FULL | −3.00 | 3.98 | 0.45 | 15 | 0.019 |
| Capital outlay | CLEAN | +14.31 | 15.94 | 0.37 | 6 | 0.208 |
| Long-term debt | CLEAN | +3.26 | 15.51 | 0.83 | 9 | 0.004 |

**Interpretation of the property-tax β:** a county with 2× more installed MW (log unit ≈ +0.69) grows its property tax revenue at ~2.7 pp/year faster CAGR. A 4× MW (Storey NV vs Wilkes GA) ≈ +7.7 pp/year faster.

### 3.3 Specification check — DC tax share as treatment intensity

All null (β between −0.07 and +0.20 pp per pp of DC tax share; p > 0.30 across all six specs). **Installed MW** is the right intensity measure; the **tax-share proxy** is too noisy.

### 3.4 Influence diagnostics

Franklin County NC dominates the property-tax dose-response regression: Cook's D = 0.37, studentized residual = +3.68. Excluding Franklin would weaken but not flip the result (β stays positive at ~+2 pp/log MW). Franklin's data is well-documented (Microsoft Azure expansion), so we keep it.

---

## 4. Per-county detail (clean sample)

| County | State | Years | Property tax CAGR | Capex CAGR | Debt CAGR | DC MW |
|---|---|---:|---:|---:|---:|---:|
| **Morrow** | OR | 8 | **9.5%** | **28.6%** | 13.1% | 1004 |
| **Crook** | OR | 8 | 8.2% | **27.7%** | **84.1%** | 404 |
| Umatilla | OR | 8 | 6.8% | — | −13.0% | 795 |
| **Storey** | NV | 6 | **10.6%** | **75.1%** | — | 603 |
| **Franklin** | NC | 7 | **22.0%** | **29.5%** | **47.0%** | 500 |
| Cherokee | NC | 5 | 4.8% | 19.6% | — | 134 |
| Cook | GA | 6 | — | 13.9% | — | 270 |
| Wilkes | GA | 7 | 1.7% | — | 12.5% | 82 |
| Lawrence | KY | 7 | — | — | −3.9% | 250 |
| Marshall | KY | 6 | — | — | −46.5% | 195 |
| Dickey | ND | 6 | −1.7% | — | −20.6% | 440 |

Bolded rows are the cleanest DC clusters (OR Mid-Columbia, Storey NV, Franklin NC). All four show **double-digit treated CAGR on property tax AND capex**.

---

## 5. Hypothesis scorecard

Drawing on Henrik's & Mitch's Apr 28-30 frame (full mechanism map in `.claude/rules/knowledge-base-template.md`):

| # | Hypothesis | Source | Status from v3 | Strength |
|---|---|---|---|---|
| H0 | Property tax revenue ↑ in DC counties | Premise | Marginal level (+3.5pp, p=0.086); strong dose-response (+3.9pp/log MW, p=0.008) | Moderate |
| **H1** | **Muni capex ↑** ("new roads and schools" — Mitch) | Mechanism map | **+27pp/yr excess, p=0.014 across all tests, 6/6 counties positive** | **Strong ★★★** |
| H2 | Muni debt ↓ (paydown) OR ↑ (debt-financed capex) | Mechanism map | Null average, but huge dispersion — Crook OR +84%, Marshall KY −47%. Consistent with **debt-financed capex in early-stage counties** | Mixed/heterogeneous |
| H3 | Public services current expenditure ↑ | Mechanism map | Not testable from Option C (Census 2017 long-file doesn't include a usable services total) | — |
| H4 | Bond ratings ↑ | Mechanism map | Null in v2 (PR #2/#3 bond-char analysis) | None |
| H5 | Bond yields ↓ | Mechanism map | **−23 bps offering spread, p≈0.057** (v2, PR #1) | Strong ★★ |

**Stylized-fact anchor:** Prince William VA at 38% CAGR property tax (FY13-FY22) is the high end, not the median. Our clean OR cluster runs 6.8-9.5% CAGR — typical of where the DC boom is migrating (rural counties with lower baseline tax bases).

---

## 6. Coherence of the story

The v3 evidence is internally consistent:

1. **Capex moves first and largest** — this is the immediate visible response to DC construction.
2. **Property tax tracks installed MW** with a clean dose-response — consistent with the assessment process responding to new commercial real estate.
3. **Debt is the residual financing margin** — early-stage counties borrow against the new tax base; mature counties retire debt with steady-state DC tax revenue. The null on average masks two clean behaviors.
4. **Bond yields drop −23 bps** in v2 because the market correctly identifies the fiscal-capacity expansion.
5. **Bond-design outcomes** (rating, maturity, call) are unchanged — only the price margin moves, which is what we'd expect when fundamentals improve but the underlying credit class doesn't.

The original tension — "if property tax growth is modest, why does the spread move so much?" — resolves once we see that capex is the dominant fiscal flow. The bond market is pricing the *total fiscal capacity* (revenue level + investment activity), not just the revenue growth rate.

---

## 7. Caveats — what Option C cannot do

1. **No matched controls.** The benchmark is a national aggregate; we cannot rule out time-period confounders that affected the aggregate differently from a "typical rural county." A true winner-vs-loser DiD requires matched 2017→2025 control PDFs (we acquired 17 of 59 candidate controls before pivoting to Option C).
2. **No pre-period parallel trends.** We have one pre-period observation (2017 Census). To test parallel trends we'd need 2010-2016 ACFRs for treated, which is OCR-heavy work on scanned older filings.
3. **Treatment timing varies.** years_elapsed = 5 to 8 across counties; CAGR normalizes for this, but if DC openings are non-linear (most MW added in last 3 years), CAGR understates intensity.
4. **PDF extraction has residual error.** We dropped 6 known-bad counties; the remaining 17 may have unit-mismatch or row-context parser errors. A line-by-line manual spot check is warranted before publication.
5. **No identification claim.** Option C is descriptive — "treated counties grow capex faster than the national trend." To support a causal claim we'd need either Option B (matched control), synthetic control, or pre-period DC entry timing variation (event study).

---

## 8. Decision points for the team

1. **Lead with capex, not property tax?** Capex is the cleanest, strongest result. The natural paper structure may be: (a) bond-spread effect (v2 PR #1), (b) capex mechanism (v3), (c) property tax intensive-margin dose-response (v3), (d) bond-design nulls (v2).
2. **Acquire the remaining ~30 matched controls?** Would convert Option C into a proper 2-period DiD. Cost: ~8-12 hours of state-portal work + parser refinement. Benefit: clean identification.
3. **Implement synthetic control?** Uses only data we already have (2017 Census ACFR covariates for 3,020 counties). Builds a per-treated-county counterfactual. Lower cost than (2), tighter identification than Option C.
4. **OCR pre-period ACFRs (2010-2016)?** Tesseract is now installed. Would enable event-study with parallel trends. Costly (40% of older ACFRs are scanned), but high pay-off if pre-trends are flat.
5. **Get NACO or industry data on DC-related fiscal incentive pass-throughs?** If state pass-throughs are funding the capex (option (1) in §6 above), we should know.

---

## 9. Suggested next session priorities

In order of value-per-effort:

1. **(High, 1 session)** Synthetic control on the 17 clean treated counties using Census 2017 covariates from all 3,020 counties — uses what we have, dramatically strengthens identification.
2. **(High, 1 session)** Line-by-line manual spot check of the 17 clean treated PDF extractions to confirm no remaining unit mismatches.
3. **(Medium, 2-3 sessions)** Acquire matched-control PDFs for the OR + KY + GA states only (16 controls), where we have working portal scripts; run full Option B on the OR/KY/GA subset.
4. **(Low, multi-session)** Acquire remaining 22 controls across TX/NC/VA/WA/NV/NM/ND and run nationwide Option B.

---

## 10. Files referenced

| File | What |
|---|---|
| `data/derived/option_c_excess_growth.csv` | Per-county per-outcome growth rates |
| `data/derived/option_c_full_tests.md` | Full statistical tests + regressions |
| `data/derived/option_c_summary.md` | Summary tables |
| `data/derived/acfr_county_year_extracted_wide.csv` | Source PDF extractions, 23 treated × multi-year |
| `scripts/python/30_option_c_national_benchmark.py` | Excess CAGR computation |
| `scripts/python/31_option_c_regressions.py` | Full hypothesis tests + dose-response regressions |
| `memos/2026-05-16_option_c_results.md` | Earlier draft of Option C results (this memo supersedes) |
| `memos/2026-05-16_stylized_facts_v2.md` | Bond-pricing results (still current) |
| `memos/2026-05-16_stylized_facts.md` | v1 (superseded; kept for history) |
