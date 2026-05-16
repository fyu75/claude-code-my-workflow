# Stylized Facts — Data Centers and Municipal Bond Issuance

**To:** Henrik Cronqvist, Rui Dai, Mitch Warachka
**From:** Frank Yu (CEIBS)
**Date:** 2026-05-16
**Subject:** First-look findings, project "Corporate Investment and Municipality Finances: Evidence from Data Centers"

---

## Executive summary

Over the past two weeks, I have built a county-year panel that joins the S&P 451 data center database to SDC Public Finance muni-bond issuance, 2000–2025. The data work is in good shape: 100% of US data centers are mapped to county FIPS, 83% of Tier-A muni deals (~$5T par) are mapped. **First-cut regression findings, however, are sobering. The simplest two-way fixed effects spec produces statistically-significant coefficients that switch sign or vanish under proper staggered-DiD treatment. There is no detectable effect of DC entry on offering spreads at conventional levels of significance. There is, however, a robust ~12% reduction in number of deals issued per county-year post-DC, which is consistent with the "deleveraging" channel but cannot be distinguished from confounding without the fiscal data (ACFR).**

The data infrastructure makes the rest of the project tractable. The empirical findings, as they stand, suggest we need ACFR before the paper has a clean story.

---

## 1. Data infrastructure status

### What is built

| Component | Status | Coverage |
|---|---|---|
| S&P 451 properties → county FIPS | ✓ done | 4,507/4,507 US DCs with coords = 100% |
| SDC issuer → county FIPS | ✓ done | 33,165 unique issuers, 83% of $1M+ Tier-A deals resolved |
| Tranche-level coupon (from `maturity.sas7bdat`) | ✓ done | 68% of resolved deals have par-weighted coupon |
| Treasury benchmark (FRED DGS5/10/20) | ✓ done | 2000–2025 yearly |
| Deal-level spread (coupon − maturity-matched Treasury) | ✓ done | 156,933 deals with valid spread |
| County-year panel (balanced) | ✓ done | 81,718 cells (3,143 counties × 26 years) |
| ACFR (county fiscal data) | not started | needs ~3–5 day ingestion |
| MSRB secondary trades | not started | filter pass deferred until panel is firm |
| EMMA scrape (special-district residuals) | not started | unblocks last ~16% of par |

### Data-cleaning decisions worth flagging

1. **Sample restriction**: AMT ≥ $1M (literature standard); 2000–2025; `CORPORATE_BACKED = 'No'` (drops 10% conduit/private-activity bonds); ISSTYPE_TRANS in {District, City/Town/Vlg, Local Authority, County/Parish} — i.e., Tier A. State-level issuers, multi-county authorities, and conduits are classified out of the main sample.

2. **NYC dropped from main sample** (`metro_excluded` tag, 4 issuers). NYC's $90B+ budget operates as a single fiscal unit across 5 counties; cannot be cleanly assigned. Empirically 63 of 4,507 US DCs sit in NYC boroughs (mostly small Manhattan carrier hotels) — losing them is a 1.4% cost. The actual NY-metro DC cluster is in NJ.

3. **Multi-county authorities flagged, not assigned** (`multi_county_authority` tag, 34 issuers including BART, MARTA, SoCal Metro Water, etc.): par is $182B in this bucket. These get a separate identification design or are dropped in robustness.

4. **120-entry hand override** of the largest residual issuers. The Census Place+cousub crosswalks resolve 70% of issuers via regex; the override fills ~$77B of additional par for issuers whose names don't reveal a county (LADWP, NYC Housing, JEA, etc.).

Full documentation in `memos/2026-05-16_data_inventory.md`.

---

## 2. The county-year panel

| Dimension | Value |
|---|---:|
| County-years | 81,718 |
| US counties (50 states + DC) | 3,143 |
| Years | 2000–2025 |
| **DC-host counties** (≥1 DC opened by 2025) | **367** |
| Counties with any SDC issuance | 2,858 (91%) |
| DC-host counties with SDC issuance | **360 / 367 (98%)** |
| Treated cells (post-first-DC) | 4,621 (5.7%) |
| Pre-treatment cells in DC-host counties | 4,921 |
| Total Tier-A deals (resolved to FIPS) | 188,307 |

### DC-host treatment timing

| First-DC year | # counties first treated | Cumulative |
|---:|---:|---:|
| 2000 | 30 | 30 |
| 2005 | 4 | 87 |
| **2013** (Big Data inflection) | **55** | **190** |
| 2020 | 4 | 263 |
| 2025 | 16 | 367 |

This is staggered treatment with cohort sizes 1–55 per year. Proper estimators (Callaway-Sant'Anna or de Chaisemartin-D'Haultfœuille) are required.

### Top DC-host counties — descriptive snapshot

| County | DCs | First DC | # bond deals | Total par | Mean YTM |
|---|---:|---:|---:|---:|---:|
| Loudoun, VA | 206 | 2000 | 99 | $6.8B | (low N, large dispersion) |
| Maricopa, AZ | 83 | 2001 | 1,130 | $61.3B | |
| Santa Clara, CA | 74 | 2000 | 798 | $40.0B | |
| Prince William, VA | 72 | 2003 | 41 | $1.4B | |
| Dallas, TX | 65 | 2000 | 1,109 | $49.5B | |
| Cook, IL | 57 | 2000 | 2,668 | $99.6B | |
| Polk, IA | 30 | 2013 | 686 | $8.6B | (post-2013 cohort) |

This shows the heterogeneity in the sample: rural-poor DC-host counties (e.g., Polk IA, Morrow OR, Grant WA) versus mature urban ones (Cook, Dallas, Maricopa). The DC-fiscal-mechanism should be strongest in the rural-poor tail.

---

## 3. First-cut empirical findings

### Specification

Three estimators applied to three outcomes:

- **TWFE-A**: outcome ~ post_dc | county_fe + year_fe
- **TWFE-B**: outcome ~ post_dc | county_fe + **state-year_fe** (tighter)
- **CS**: Callaway-Sant'Anna (2021) ATTgt, never-treated control, simple aggregation across (cohort, event time)

Outcomes: log(par+1), log(n_deals+1), par-weighted offering spread (bps).

### Side-by-side coefficient table

| Outcome | TWFE-A | TWFE-B (state×year FE) | **Callaway-Sant'Anna** | CS 95% CI |
|---|---:|---:|---:|---|
| log(par+1) | −0.052 (0.043) | −0.038 (0.037) | **−0.078 (0.065)** | [−0.21, +0.05] |
| log(n_deals+1) | −0.120*** (0.020) | −0.100*** (0.017) | **−0.123*** (0.028)** | [−0.18, −0.07] |
| **spread (bps)** | **+4.98** (2.27) | +2.85 (1.97) | **−3.17 (3.72)** | [−10.5, +4.1] |

*\*\*\* p<0.01, \*\* p<0.05, \* p<0.10. SEs in parens, county-clustered.*

### Reference point from prior literature

- **Chava–Malakar–Singh (2023) corporate subsidies → muni spread**: estimated **−15.2 bps** (significant). Our point estimate of −3.17 bps with [−10.5, +4.1] CI does *not* include the C-M-S point — and the difference is statistically distinguishable. Either DC-as-shock is qualitatively different from explicit-corporate-subsidy, or our power is insufficient to detect the magnitudes seen in that literature.
- **Goldsmith-Pinkham–Gustafson–Lewis–Schwert (2022) SLR exposure → muni yields**: their effect sizes range 5–20 bps depending on horizon. Our CI on spread is wide enough that we cannot rule out a 5–10 bps effect; we also cannot rule out zero.

### What the sign-flips tell us

The most striking pattern: **the spread coefficient flips sign** from TWFE-A (+5 bps, p<0.05) to CS (−3 bps, n.s.). This is exactly the Goodman-Bacon (2021) prediction for staggered treatment with heterogeneous effects: early-treated counties (year 2000 cohort) serve as controls for later-treated counties (year 2013 cohort) in TWFE, generating a "negative weight" that distorts the estimate. **TWFE here is the wrong estimator. CS is the right one and gives null on spread.**

The n_deals coefficient is robustly negative across all three estimators: **counties post-DC issue ~12% fewer bond deals per year**. This is consistent with the *deleveraging* interpretation (DC arrives → property tax revenue grows → county doesn't need to borrow as much). But it could also reflect compositional shifts or other confounders. Without ACFR fiscal data, we cannot distinguish.

---

## 4. Honest assessment

### What the data shows

1. **Strong descriptive pattern**: par/deals roughly **double** in DC-host counties post-first-DC. But almost all of this is **absorbed by year FE alone** — i.e., it reflects secular muni growth in tech corridors, not a DC-specific shock.

2. **Within-county within-state-year identification**: par is flat, deals are down ~12%, spread is statistically indistinguishable from zero.

3. **Power for spread is limited**: 33k cells with spread data, wide CI. We can rule out the +15 bps tail but not −10 bps.

### What the data does not yet test

The motivating mechanism — **DC investment → property tax base ↑ → muni capex / debt → eventually yields** — is partially observable in our data. We see "bond market response" but not the upstream channels:

- Property tax revenue per county-year: **ACFR data, not yet ingested**
- County capital outlay: **ACFR, not yet ingested**
- Long-term debt outstanding: **ACFR, not yet ingested**
- Ratings transitions: **separate ratings dataset, not yet ingested**

Without these, we have a "reduced-form" on the wrong endpoint. The story we can currently tell is "DC entry → fewer bond deals", which is *consistent with* but does not *establish* the deleveraging mechanism.

### What could change the picture

If ACFR shows property tax revenue rising in DC-host counties (relative to controls), and capital outlay also rising, and debt outstanding falling — then the deal-count finding becomes coherent: DC counties have more fiscal slack and don't need to borrow as aggressively. The spread null becomes interpretable: marginal issuance happens but with the same risk-return profile.

If ACFR shows property tax revenue *not* moving in DC-host counties — the DC tax-base story is wrong in its premise, and the paper needs a different framing (e.g., shift to land use, environmental, ratings-only, or comparative across states with different tax regimes).

---

## 5. Three open questions for the team

1. **How much of the paper hinges on offering-spread effects?** If the spread null holds with ACFR, do we still have a paper? My read: yes, if mechanism (tax revenue → capex → deleveraging) is clean. The paper becomes "DC fiscal effects don't show up in spreads because counties don't need to borrow more — they deleverage." This is a coherent contribution different from C-M-S.

2. **Heterogeneity**. The 367 DC-host counties span Loudoun (mature DC hub) to Polk IA (recent rural). The "where the shock bites hardest" hypothesis (per Mitch) is **untestable without subsamples**. Cohort-specific or county-quartile-specific estimates require more sample design.

3. **Multi-county authorities and conduit-bond exclusions**. Currently 18 multi-county and 12 state-conduit issuers are out of the main sample. These cover $300B+ par. A robustness check that includes them with imperfect attribution might be informative.

---

## 6. Recommended next steps

### Primary track — ACFR ingestion (~1 week)

Census ASLGF Individual Unit Files, 2000–2022. The dependent variables we need are:
- Total general revenue, total property tax revenue
- Total capital outlay (by function: education, highway, general)
- Long-term debt outstanding, debt issued, debt service interest

Plan in `memos/2026-05-16_acfr_scoping.md`. Estimate 3–5 focused days. Without this, the mechanism story cannot be tested.

### Parallel track A — Heterogeneity probe (1 day)

Re-run CS estimator with cohort-by-cohort breakdown:
- 2000–2005 cohorts (mature DCs, suburban/urban)
- 2006–2012 cohorts (Big Data era)
- 2013+ cohorts (hyperscale/rural)

If effects differ across cohorts, the project memo's "where the shock bites hardest" hypothesis gains empirical traction.

### Parallel track B — MSRB extract for top-30 DC counties (~2 days)

Build a CUSIP universe for the top-30 DC-host counties from the v3 panel, then do a single filter pass over the 57 GB MSRB file. This unlocks **secondary-market yields** for an event-study around DC announcements — a much cleaner outcome than offering yields. If the event-study shows a clean −X bps reaction, that's a much stronger paper.

### Deferred until decision

- EMMA scrape (recover last 16% of par)
- Geocode 36 coord-less DCs
- State conduit / multi-county imputation rules

---

## 7. Files for replication

All under `/Users/fangyu/claude/datacenter2/`:

- `data/derived/county_year_panel_v3.csv` — canonical analysis panel (21 cols)
- `data/derived/dc_property_county_fips.csv` — every DC mapped to county
- `data/derived/sdc_issuer_county_full_v3.csv` — every SDC issuer mapped or annotated
- `data/derived/sdc_deal_spread.csv` — deal-level spread
- `data/derived/cs_did_results.md` — Callaway-Sant'Anna table
- `data/derived/did_results_v2.md` — TWFE table
- `scripts/python/05_build_county_year_panel.py` — panel construction
- `scripts/python/11_callaway_santanna.py` — CS DiD
- `memos/2026-05-16_data_inventory.md` — full data documentation

Nothing is committed to git yet. Happy to walk anyone through the pipeline.

---

**Bottom line for team:** the data infrastructure is solid; the first regression results suggest we cannot tell the offering-spread story without ACFR-based mechanism evidence. I'd like to go ahead and ingest ACFR next week, while running the heterogeneity probe in parallel. Holler if you'd rather pivot the framing first.
