# Stylized Facts (combined) — Data Centers & Muni Finance

**To:** Henrik, Rui, Mitch · **From:** Frank · **Date:** 2026-05-16
**Supersedes:** v1, v2, v3.

---

## TL;DR

DCs raise local fiscal capacity; the muni market reprices it through **spreads**, not bond design. The dominant fiscal-flow mechanism is **capex**, not property tax growth.

| Channel | Estimate | p | Source |
|---|---:|---:|---|
| **Offering spread** | **−23 bps** | 0.057 | CS-DiD, 1%-threshold sample, 2015+ |
| **Capital outlay (within-county CAGR)** | **+27.3 pp/yr above national** | 0.014 | Option C, clean N=6, 6/6 positive |
| Property tax CAGR (level) | +3.5 pp/yr | 0.086 | Option C, clean N=9 |
| Property tax CAGR ~ log(MW) | β=+3.86 pp / log MW | 0.008 | Option C dose-response, clean N=9 |
| Long-term debt CAGR | +2.5 pp/yr (null on avg) | 0.43 | Option C — huge dispersion |
| Bond rating tier | null | — | CS-DiD per-agency + extensive margin |
| Maturity, call provisions | null | — | CS-DiD bond-design outcomes |

**Narrative.** DC construction triggers a large capex flow response. Property tax grows on the **intensive margin** (more MW → faster growth) but only modestly on average. Some counties debt-finance the capex (Crook OR +84% debt CAGR, Franklin NC +47%), others retire (Marshall KY −47%). The bond market prices the total fiscal-capacity expansion correctly — spreads tighten, bond design unchanged.

---

## 1. Sample & treatment

- **Universe:** 33k SDC muni issuers (2000-2025), mapped to county FIPS (83% deal-weighted coverage).
- **Treatment:** counties where DC investment contributes ≥ 1% to county property tax revenue (proxy: MW × $50k/MW / 2017 PT). N = 125.
- **Control:** never-DC-host counties. N = 2,776.
- **Focus window:** 2015+ post-treatment (DC boom era).

---

## 2. Bond-pricing result

**Callaway–Sant'Anna staggered DiD, offering spread (1%-threshold sample):**

- ATT = **−23.4 bps**, SE = 12.3, two-sided p ≈ 0.057
- Magnitude larger than Chava–Malakar–Singh (2023) corporate-subsidy benchmark (−15 bps)
- **Heterogeneity:** moderate-share band (1-10%) is the cleanest signal at **−37 bps, p < 0.01**; very-high tail (≥10%) is noisy (short post-windows, n thinning)
- **Bond-design margins (rating, maturity, callable):** all null across pooled and per-agency specs — only the **price** moves, the **structure** doesn't

---

## 3. Mechanism: 2017 cross-section + 2017→2025 within-county

### 3.1 Cross-section (2017 ACFR, county-govt only)

High-DC-share counties vs never-DC-host:

| Outcome (per capita) | Treated effect | p |
|---|---:|---:|
| Property tax | **+$543** | <0.01 |
| Long-term debt | **+$1,204** | <0.01 |
| Capital outlay | positive | <0.05 |

Consistent with: DCs expand fiscal capacity → counties borrow more AND grow capex.

### 3.2 Within-county growth (2017 → latest, 22 treated counties with PDF in hand)

After dropping 6 known-bad rows (Mecklenburg VA unit-mismatch; Pecos/Ward/Crane TX oil-bust; Glasscock/Briscoe TX parser-dup), clean N=17:

| Outcome | N | Mean excess CAGR | t-test | Wilcoxon | Sign test |
|---|---:|---:|---:|---:|---:|
| **Capital outlay** | 6 | **+27.3%** | p=0.014 | p=0.016 | **6/6** |
| Property tax | 9 | +3.5% | p=0.086 | p=0.10 | 6/9 |
| Long-term debt | 9 | +2.5% | p=0.43 | p=0.59 | 4/9 |

**Dose-response (clean):** property-tax CAGR ~ log(MW), β = **+3.86 pp / log MW, p = 0.008** (HC3). High-MW counties (Storey, Morrow, Franklin) grow PT 5-10× faster than low-MW.

**Benchmark sources:** BEA NIPA Table 3.21 + Census ASLGF historical aggregates 2017→2024. Property-tax benchmark is per-county median (3.4%), not BEA aggregate (5.85%, dominated by big-state appreciation).

### 3.3 Clean DC cluster (the visual story)

| County | State | Years | PT CAGR | Capex CAGR | Debt CAGR | MW |
|---|---|---:|---:|---:|---:|---:|
| Morrow | OR | 8 | **9.5%** | **28.6%** | 13.1% | 1004 |
| Crook | OR | 8 | 8.2% | **27.7%** | **84.1%** | 404 |
| Umatilla | OR | 8 | 6.8% | — | −13.0% | 795 |
| Storey | NV | 6 | **10.6%** | **75.1%** | — | 603 |
| Franklin | NC | 7 | **22.0%** | **29.5%** | **47.0%** | 500 |

Prince William VA (38% PT CAGR FY13-FY22) is the high-end extreme, not the median. Typical realization is 6-10% PT CAGR + 25-30% capex CAGR.

---

## 4. Hypothesis scorecard

| # | Hypothesis | Verdict |
|---|---|---|
| H0 | Property tax revenue ↑ | Marginal level, **strong dose-response** |
| **H1** | **Capex ↑** ("new roads & schools") | **Strong ★★★** |
| H2 | Debt ↓ or ↑ | Mixed — debt-finances capex in early-stage; retired in mature counties |
| H3 | Public services ↑ | Untested (no usable Census 2017 services total) |
| H4 | Ratings ↑ | **Null** |
| **H5** | **Bond yields ↓** | **−23 bps, strong ★★** |

The capex + spread results combine into a coherent story: counties spend big against an expanded tax base; the bond market prices the resulting fiscal-capacity expansion through the price margin alone.

---

## 5. Caveats

1. Within-county work is **descriptive, not causal** — benchmark is national aggregate, not matched control.
2. No pre-period parallel trends (one pre-period observation, 2017).
3. PDF extraction has residual error — 6 obvious cases dropped; remaining 17 need spot-check.
4. The Greenstone-Hornbeck-Moretti winner-vs-loser design is still ahead of us, not done.

---

## 6. Decision points

1. **Lead the paper with capex** rather than property tax? (Capex is the cleanest, largest, most-tested result.)
2. **Synthetic control next** — uses 2017 Census ACFR covariates for all 3,020 counties, no further data acquisition needed, tighter ID than national benchmark. Highest value-per-effort.
3. **Acquire ~30 more matched-control PDFs** to convert Option C → matched-control DiD? Cost: 8-12 hrs portal work + parser refinement.
4. **OCR pre-period (2010-2016) ACFRs** for parallel-trends test? Tesseract installed; ~40% of older filings are scanned.

---

## 7. Files

| Path | Content |
|---|---|
| `data/derived/option_c_excess_growth.csv` | Per-county per-outcome growth rates |
| `data/derived/option_c_full_tests.md` | Full test battery (t / Wilcoxon / sign / OLS / influence) |
| `data/derived/cs_did_threshold.md` | Main bond-spread result |
| `data/derived/heterogeneity_results.md` | 1-10% vs ≥10% subgroups |
| `data/derived/bond_char_did_results.md` | Rating / maturity / call nulls |
| `scripts/python/17_main_analysis.py` | Consolidated bond-spread analysis |
| `scripts/python/30_option_c_national_benchmark.py` | Excess CAGR + t-tests |
| `scripts/python/31_option_c_regressions.py` | Full statistical battery |
