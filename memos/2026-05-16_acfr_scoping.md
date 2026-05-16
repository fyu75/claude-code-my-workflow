# ACFR Ingestion Scoping Plan

**Date:** 2026-05-16
**Author:** Frank Yu (CEIBS), with Claude
**Status:** Scoping only — execution deferred until team approval

ACFR (Annual Comprehensive Financial Report) data is the county-level fiscal data we need to test whether the DC effect runs through tax revenue, capital expenditure, and debt — i.e., the mechanism panel in the project memo's §4.

This memo scopes the work; it does not execute it. The full ingestion is roughly a 3–5 day focused project, not a one-shot script.

---

## 1. Source landscape

**The canonical source: Census Bureau "Annual Survey of State and Local Government Finances" (ASLGF)**, also branded as the "Census of Governments — Finance" file in years ending in 2 and 7. Free, public, raw text files (not API).

URL hub: https://www.census.gov/programs-surveys/gov-finances.html

| Source | Coverage | County-level? | Format | Latest year |
|---|---|---|---|---|
| **Census ASLGF Individual Unit Files** | All US local governments incl. ~3,100 counties | ✅ Yes | Fixed-width or pipe-delimited per year | **2022** (FY2022 released Oct 2024) |
| **Census Govts Finance Tables** | Aggregated published tables | Partial | XLSX/PDF | 2022 |
| **Lincoln Institute Municipal Fiscal Database** | Big cities only | Mostly city not county | Cleaned panel | ~2021 |
| **Pierson Hand & Thompson (2015) State & Local Finance Initiative** | Academic-curated state-local panel | Yes | Replication archive | ~2017 |
| **GFOA / MuniNet practitioner archives** | Selected ACFRs as PDFs | One-at-a-time | PDF | rolling |
| **ACFR PDF scraping (the actual financial statements)** | Universe of counties | Yes, but unstructured | PDF | rolling |

**For our project the right pick is Census ASLGF Individual Unit Files.** It covers all ~3,100 US counties with consistent variable definitions back to 1967, with an FY-2022 endpoint that aligns reasonably with our 2000–2025 panel.

The ACFR PDF route (parsing each county's annual financial statement as a PDF) is the highest-fidelity source but is enormous engineering — *not feasible without a budget for paid services like Munetrix or by writing a dedicated parser*. For a baseline pass, the Census aggregates suffice.

---

## 2. What variables we need

From the project memo §1 mechanism map: property tax revenue ↑ → muni revenue ↑ → muni capex ↑ / muni debt ↓ / public services ↑.

Mapping the mechanism to Census ASLGF fields:

| Mechanism node | Census ASLGF variable code | Field name (approx.) |
|---|---|---|
| Property tax revenue | `T01` | Property Tax Revenue |
| General sales tax | `T09` | General Sales Tax |
| Personal property tax (DC equipment) | embedded in `T01` | Mostly not separated; ACFR detail varies by state |
| Total general revenue | `R01–R99` series | Total General Revenue |
| Federal IGA | `R36` | Federal Intergovernmental Revenue |
| State IGA | `R20–R32` | State Intergov't Revenue |
| Capital outlay total | `F12` series | Capital Outlay (by function) |
| Education capital outlay | `F12–E12` | Capital outlay for education |
| Highways capital outlay | `F44–E44` | Highways |
| General government capital | `F89–E89` | General govt capital |
| Total current expenditure | `E01–E99` | Current operations |
| Long-term debt outstanding | `M89` | Long-term debt outstanding (end of FY) |
| Long-term debt issued (year) | `M84` | Long-term debt issued |
| Long-term debt retired (year) | `M85` | Long-term debt retired |
| Debt service (interest) | `I89` | Interest on general debt |

The actual variable code list is in the Census **GovFin Methodology** document, ~80 pages, updated annually. Pre-2010 vs post-2010 the codes are mostly stable but a few items rename.

---

## 3. Data acquisition steps

### Phase A — Acquisition (≈ 1 day)

1. **Download the 22 county-level files** (FY2000 through FY2022 ASLGF Individual Unit Files), one per year. Each is roughly 5–20 MB compressed.
2. **Download the codebook** for each year (or use a single consolidated one if structure is stable).
3. Verify file integrity (row counts vs published totals).

The download URLs follow the pattern `https://www2.census.gov/programs-surveys/gov-finances/datasets/YYYY/individual-unit-file/...`. The exact path varies year-to-year; some years are zip, some are tar, some are fixed-width text. A small wrapper script handles all 22.

### Phase B — Parsing and normalization (≈ 2 days)

The Individual Unit File is fixed-width text with one record per local-government unit. Per-county records appear as multiple rows: one record per fiscal-year-end roll-up plus per-program-area sub-records. Joining requires:

1. Identifying the county records (record type `1` = county; `2` = sub-county; `3` = school; `5` = special district).
2. Building a `county_fips` key (the file uses Census `IDCODE` not FIPS — a crosswalk is shipped with the codebook).
3. Pivoting from long-format records to a wide variable set for the 12 key items.
4. Aggregating sub-county records where appropriate (the DC fiscal effect operates partly at county and partly at school-district / special-district level — keep both).

### Phase C — Validation and integration (≈ 1 day)

1. Compare top-line revenue and debt aggregates to published Census tables (sanity check).
2. Spot-check against ACFR PDFs for 5 well-known DC counties (Loudoun, Prince William, Maricopa, Santa Clara, Cook) — confirm ASLGF numbers match the published ACFR within tolerance.
3. Merge into the existing county-year panel.

---

## 4. Known issues to flag upfront

- **Fiscal year mismatch.** Census uses each unit's fiscal year (varies; most counties are July-June). The match to a calendar-year SDC issuance can be off by 6 months for any given county. The Census `FY_ENDING` field handles this — we collapse to the calendar year by some rule (use FY ending in calendar year `t`).
- **Personal property tax is not always broken out.** Some states report it as a separate item; others fold it into the general property tax line. The Virginia DC counties report personal property tax separately, which is good — but state-by-state heterogeneity matters for the Prince William stylized fact.
- **Sample drift.** Pre-2010 Individual Unit Files have ~38,000 local-government units; post-2010 have ~39,000. Some counties merge / dissolve school districts mid-panel. Handle with a balanced or unbalanced-with-FE specification.
- **Lag between ACFR release and Census ASLGF release.** The Census FY-2022 file was released in Oct 2024 — about 2 years post-FY. So even with full ingestion we'd have 2000-2022 fiscal data, lagging our 2000-2025 SDC issuance by 3 years.

---

## 5. What this enables

Once integrated, the county-year panel grows from ~17 columns to ~30, with the addition of:

- `property_tax_rev_M` (annual property tax revenue, $M nominal)
- `total_general_rev_M`
- `capital_outlay_M` (total, plus by function: education / highways / general)
- `lt_debt_outstanding_M`
- `lt_debt_issued_M`
- `interest_on_debt_M`

The mechanism regressions then become first-class:

```
property_tax_revenue   ~ DC_indicator    [DC → property tax base]
capital_outlay         ~ property_tax     [tax revenue → capex]
lt_debt_outstanding    ~ DC_indicator    [DC → deleveraging]
par_issued (SDC)       ~ property_tax     [revenue → issuance]
```

Each can be run with county and state-year FE. Together they trace the full mechanism map.

---

## 6. Recommendation

**Approve the work and schedule for the next focused session (1 week of available days).** ACFR is on the critical path for the mechanism story — without it we can document descriptive issuance patterns but cannot test the property-tax → capex → debt channel that motivates the paper.

**Defer if-and-only-if** the team decides the first results paper focuses on issuance-only (no fiscal channels) — in which case ACFR can wait until after baseline results.

**Alternative**: pay for a commercial provider like Munetrix or Lincoln Institute panel. ~$5-10k per year. Trades engineering time for budget. Probably not justified for one paper but worth considering if the team plans multiple papers using county fiscal data.
