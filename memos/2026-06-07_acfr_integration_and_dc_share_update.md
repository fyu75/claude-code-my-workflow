# ACFR Integration + DC Share Formula Update
**Date:** 2026-06-07  
**Session:** A→B→D→E plan  
**Status:** All four steps complete; key analytic finding requires team discussion before DiD re-run

---

## What Was Done (A → B → D → E)

### A — Integrate Tier 3-5 ACFR Sprint Results

**Script:** `scripts/python/extract_acfr_agent_outputs.py` + `scripts/python/37_integrate_acfr_sprint_results.py`

Parsed 138 JSONL task-output files from the prior ACFR scraping campaign (Tier 1-5). Each file contains structured `COUNTY: / GF_PROPERTY_TAX: / ALLFUNDS_PROPERTY_TAX: / ...` blocks from agent completions.

**Key bugs fixed in the extractor:**
1. Was including USER messages that had `<int>` template placeholders → all values parsed as null. Fix: `msg.get('role') == 'assistant'` only.
2. Empty string `''` in `NULL_STRINGS` made `'$3.7M'.lower().startswith('')` always `True` → every number discarded. Fix: use `NULL_PREFIXES` tuple (no empty string), separate check for blank/dash strings.
3. FY regex didn't handle `FY: FY2022` (prefix before digit). Fix: `r'^FY:\s*(?:FY)?(\d{4})'`.

**Suspicious values corrected manually after integration:**
- Newton County GA (13217): GF PT = $39.50 (a rate, not dollars) → nulled
- Cass County MI (26027): all values < $100 → all nulled  
- Franklin County OH (39049): GF values nulled (subtable fragment; allfunds retained)
- Jackson County GA (13157): allfunds PT = $39.6M < GF PT = $76.6M (impossible) → allfunds nulled

**Result:** Wide CSV expanded from 47 → 79 rows, 28 → 60 counties.

---

### B — Add Matched Control Counties from MuniSpot v2

**Script:** `scripts/python/38_add_controls_from_munispot.py`

Controls don't have FILOT/IDA-leasehold distortions, so MuniSpot v2 GF data is reliable for them. Used `tier_with_pilot` (widest PT coverage). Matched against `data/derived/matched_controls_named.csv` (59 control counties total).

**Technical notes:**
- Must use `python3.12` (pyenv), not system Python 3.14 (Homebrew) — system Python lacks pyarrow
- Correct MuniSpot v2 column names: `municipality_name` and `state` (NOT `entity_name` / `state_abbr`)
- Rows tagged `state_pt_structure = 'munispot_v2_gf'` to identify data source

**Result:** 79 → 110 rows, 60 → 91 counties. 85 counties with any PT data; 34 with dual-scope (GF + allfunds).

**28 control counties still missing** (no MuniSpot v2 match, no extraction done):

| State | Counties |
|---|---|
| GA | Early (13099), Peach (13225), Union (13291), Wilkinson (13319) |
| KY | Fleming (21069), Greenup (21089), Harrison (21097), Hopkins (21107), Lincoln (21137) |
| NV | Eureka (32011), Humboldt (32013) |
| ND | Bottineau (38009), Mountrail (38061), Pembina (38067) |
| OR | Josephine (41033) |
| TX | Armstrong (48011), Bowie (48037), Jack (48237), Kenedy (48261), Kimble (48267), McMullen (48311), Stonewall (48433), Sutton (48435) |
| WA | Asotin (53003), Cowlitz (53015), Lewis (53041), Lincoln (53043), Skamania (53059) |

Options: (a) run another PDF extraction wave, (b) use Census 2017 ACFR as pre-period only for these 28, (c) drop from DiD.

---

### D — Add `pt_structure_state` to DC Share Distribution

**Script:** `scripts/python/39_add_pt_structure_state.py`

Added `pt_structure_state` column to `data/derived/dc_tax_share_distribution.csv` (437 counties). State-level assignment (last-match-wins, county overrides trump state):

| Category | Logic |
|---|---|
| `SC-FILOT` | All SC counties |
| `GA-IDA-leasehold` | All GA counties |
| `OH-categorical-no-TPP` | All OH counties |
| `TX-Chapter-312-abatement` | All TX counties |
| `KY-consolidated-with-PILOT` | All KY counties |
| `VA-consolidated` | All VA counties |
| `AL-abatement-heavy` | 01089 Madison AL, 01071 Jackson AL (ACFR-confirmed) |
| `NV-Switch-deals` | 32029 Storey NV, 32003 Clark NV |
| `standard` | All others |

**Distribution in the naive treated set (dc_share_mid ≥ 1%, n=348):**

```
standard                      232
TX-Chapter-312-abatement       43
VA-consolidated                18
GA-IDA-leasehold               17
OH-categorical-no-TPP          17
KY-consolidated-with-PILOT      9
SC-FILOT                        8
NV-Switch-deals                 2
AL-abatement-heavy              2
```

---

### E — Adjusted DC Share Formula (computed, needs team review)

**Same script as D.** Added `dc_tax_M_{low,mid,high}_adjusted` and `dc_share_{low,mid,high}_adjusted` columns.

**Mid-point multipliers used:**

| Category | Multiplier | Rationale |
|---|---|---|
| SC-FILOT | ×0.50 | FILOT reduces assessment from 10.5% to 4–6% |
| GA-IDA-leasehold | ×0.20 | IDA holds title; effective DC PT ~20% of formula |
| AL-abatement-heavy | ×0.15 | 90–100% abatement; net ~10–15% of gross |
| OH-categorical-no-TPP | ×0.20 | No personal property tax; only building shell |
| TX-Chapter-312-abatement | ×0.25 | 85% abatement on improvements + 100% personal prop |
| KY-consolidated-with-PILOT | ×0.90 | Mostly standard; PILOT adds ~5–10% |
| VA-consolidated | ×1.00 | No structural abatement |
| NV-Switch-deals | ×0.50 | Abatements typical but not universal |
| standard | ×1.00 | — |

**Key finding — treated set collapses under aggressive adjustment:**

| Threshold | Naive | Adjusted |
|---|---|---|
| dc_share_mid ≥ 1% | **348 counties** | **109 counties** |
| Drop-outs | — | 239 counties (69%) |

The biggest drops come from TX (43 counties × 0.25) and GA+OH (17 each × 0.20). 

**⚠ Important caveat:** The multipliers were calibrated from a few specific ACFR extractions (Berkeley SC FILOT, Newton GA IDA leasehold) and applied **uniformly to entire states**. But:
- TX §312 abatement requires individual company applications — not every TX DC county has granted blanket abatements
- GA IDA leasehold applies only where DCs are in IDA-financed buildings — not all GA DC counties
- OH lacks TPP on servers, but DCs still pay real property tax on the building shell

The `pt_structure_state` column is immediately usable for **heterogeneity analysis** regardless of whether we adopt the adjusted formula. The adjusted shares should be discussed with Henrik and Mitch before use in the DiD.

---

## Current State of Key Files

| File | Rows | Counties | Notes |
|---|---|---|---|
| `data/derived/acfr_county_year_extracted_wide.csv` | 110 | 91 | 85 with any PT; 34 dual-scope |
| `data/derived/dc_tax_share_distribution.csv` | 437 | — | Now has `pt_structure_state` + adjusted shares |
| `data/derived/acfr_agent_extracted_raw.csv` | 39 | — | Intermediate; 39 county-year records from 138 agent outputs |
| `data/derived/matched_controls_named.csv` | 59 rows | — | 31 controls now in wide CSV; 28 missing |

**Wide CSV schema:**
```
county_fips, county_name, state, fy,
property_tax_gf, total_revenue_gf, capital_outlay_gf,
lt_debt_outstanding, interest_expense,
property_tax_allfunds, total_revenue_allfunds, capital_outlay_allfunds,
state_pt_structure
```

---

## Scripts Created This Session

| Script | Purpose |
|---|---|
| `scripts/python/extract_acfr_agent_outputs.py` | Parse 138 JSONL task outputs → `acfr_agent_extracted_raw.csv` |
| `scripts/python/37_integrate_acfr_sprint_results.py` | Merge raw extract into master wide CSV |
| `scripts/python/38_add_controls_from_munispot.py` | Add control county PT from MuniSpot v2 parquet |
| `scripts/python/39_add_pt_structure_state.py` | Add `pt_structure_state` + adjusted DC share to distribution CSV |

---

## Pending Decisions / Next Steps

### Team discussion needed
1. **Multiplier calibration for adjusted DC share.** Three options:
   - (a) Apply blanket state multipliers as done (aggressive; 348 → 109 treated)
   - (b) Apply multipliers only to counties with ACFR-confirmed evidence (conservative)
   - (c) Keep naive as primary; use adjusted as robustness/heterogeneity check

2. **28 missing control counties.** Drop vs. extract vs. Census 2017 as pre-period only.

3. **KY retroactive correction.** KY ACFR "Taxes" line bundles ad valorem + occupational tax — prior KY entries in wide CSV should be flagged that `property_tax_gf` is actually combined taxes, not property-only.

### Analysis next steps (after team input)
- Re-run within-county growth tests with adjusted vs naive dc_share definitions
- Run DiD on both definitions and report as robustness table
- Backfill allfunds for counties with GF-only data where available

### KY-specific note
KY counties in the wide CSV currently have `property_tax_gf` populated, but for KY the "Taxes" line in ACFR GF statements bundles ad valorem (property) + occupational + other taxes. The number is not property-tax-only. Flag these rows as `state_pt_structure = 'KY-combined-taxes-not-separable'` if/when re-extracting.

---

## ACFR Jackson County AL Finding (paper-grade)

Jackson County AL (01071, flagged `AL-abatement-heavy`): **Note 12 of FY2022 ACFR** confirms 100% property tax abatements to two multinational DC companies totaling **$971,910 in FY2022**. This is direct ACFR-sourced mechanism evidence (abatements ≡ forgone tax revenue) — citable in the paper as a concrete example of the abatement mechanism.
