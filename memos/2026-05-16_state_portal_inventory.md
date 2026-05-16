# State Portal Inventory — ACFR Bulk Access for High-DC-Share Counties

**Date:** 2026-05-16
**Status:** Working draft — inventory of state-level financial-report portals discovered while building the 2025 ACFR collection pipeline.

The 125 high-DC-share counties span ~20 states. Per-county website scraping is feasible but tedious. State portals are the bulk shortcut where they exist.

## Confirmed working

### Oklahoma — `sai.ok.gov` and `digitalprairie.ok.gov`
- **Oklahoma State Auditor & Inspector** has searchable PDFs at https://www.sai.ok.gov/Search%20Reports/database/
- **Digital Prairie** has audit archives at https://digitalprairie.ok.gov/digital/collection/audits/
- **Tested**: Mayes County FY2024 ACFR via `digitalprairie.ok.gov/digital/api/collection/audits/id/15962/download` — works, 1 MB born-digital PDF.
- **URL pattern**: each audit has an `id/{N}/download` endpoint; N appears sequential and findable via the collection search page.

### Virginia — `apa.virginia.gov` (Azure blob backend)
- **Virginia Auditor of Public Accounts** has all county financial reports at `apa.virginia.gov/local-government/reports/`
- Each report has a numeric ID; the actual PDF lives at `https://dlasprodpublic.blob.core.windows.net/apa/{GUID}.pdf`
- **Tested**: Mecklenburg County FY2023 via direct Azure blob URL — works, 2.2 MB.
- **Caveat**: the search page itself is JS-driven; need to capture the GUID per report. The portal's search UI returns the GUID after Apply.
- **All VA counties × 2017-2024 likely accessible** once the GUID-extraction pattern is figured out (XHR endpoint or Selenium).

### Kentucky — `auditor.ky.gov`
- Local-government audits index at https://www.auditor.ky.gov/Auditreports/Pages/LocalGovernmentAuditsReleased.aspx
- PDFs at predictable paths like `auditor.ky.gov/Auditreports/{County}/2024{County}FC-audit.pdf`
- **Covers**: Lawrence County (FIPS 21127) and Marshall County (FIPS 21157) — both in our top-25.

### Oregon — `secure.sos.state.or.us/muni/public.do`
- Oregon SOS Municipal Audit Search Database — covers all OR counties
- Form-based POST search; need to capture the query parameters
- **Covers**: Crook, Morrow, Umatilla (our top-3 in OR)

### Washington — `sao.wa.gov`
- WA State Auditor's office — covers all WA counties
- **Covers**: Grant County (top-25), Pend Oreille (top-25)
- Search interface at https://www.sao.wa.gov/reports-data/audit-reports/

## Documented but not yet validated

### North Carolina — `nctreasurer.gov` AFIR
- Annual Financial Information Report (AFIR) program — all NC counties file standardized financial summaries with the NC Treasurer
- **Likely covers**: Franklin County (37069), Cherokee County (37039)
- Worth investigating if AFIR provides line-item data sufficient for our needs (may be standardized in a way that doesn't require PDF parsing).

### Texas — `comptroller.texas.gov/transparency/local/`
- Texas Comptroller's local government transparency portal
- **Bulk source** for: Dickens, Milam, Knox, Crane, Ward, Pecos, Glasscock, Briscoe (8 of our top-25)
- May offer machine-readable line-item data instead of PDFs.

### Georgia — `audits.ga.gov` (Department of Audits)
- Standardized county audit filings
- **Covers**: Cook (13075), Washington (13303), Wilkes (13317)

### Other states with bulk portals
- Nevada: Storey County has own page at storeycounty.org
- North Dakota: ND State Auditor for Dickey
- New Mexico: NM State Auditor for Valencia

## Per-state bulk acquisition feasibility (top-25 counties)

| State | # of top-25 counties | Bulk portal? | Path forward |
|---|---:|---|---|
| Texas | 8 | Texas Comptroller | Validate API/scraping for Comptroller's local transparency portal |
| Oregon | 3 | OR SOS Muni Audit | Capture POST parameters or scrape SOS search results |
| Georgia | 3 | GA Dept of Audits | Probe audits.ga.gov |
| North Carolina | 2 | NC Treasurer AFIR | Look at AFIR machine-readable feeds (likely XML/JSON) |
| Kentucky | 2 | KY Auditor | URL pattern looks predictable |
| Washington | 2 | WA SAO | Search portal; may need form data capture |
| Virginia | 1 | VA APA (Azure blob) | One-off Azure GUID lookups |
| Oklahoma | 1 | OK SAI / Digital Prairie | Confirmed working |
| Nevada | 1 | Storey directly | Single county; visit page |
| North Dakota | 1 | ND State Auditor | Single county; investigate |
| New Mexico | 1 | NM State Auditor | Single county; investigate |
| **Total** | **25** | | |

## Pragmatic next-session plan

1. **Highest-ROI moves first** — TX Comptroller (8 counties), NC AFIR (2 counties standardized).
2. **Pattern probes** — for KY (predictable URLs) and OK (already-confirmed bulk DB), bulk-download in scripted loops.
3. **One-off downloads** for NV, NM, ND (single-county states).
4. **VA APA + WA SAO + OR SOS** — these need form-data capture; use browser DevTools to identify XHR endpoints, then replay in curl.
5. **Build the 2-period DiD panel** once 50% of top-25 are downloaded — even partial coverage is enough to validate the approach.

## Where we are right now

| State | Status |
|---|---|
| Oklahoma (Mayes) | ✅ 2024 downloaded, validated |
| Virginia (Mecklenburg) | ✅ 2023 downloaded |
| Washington (Grant) | ✅ 2023 downloaded |
| Oregon (Crook, Morrow, Umatilla) | ✅ Various years downloaded |
| **All others (Lawrence KY, Storey NV, Milam TX, Dickens TX, Franklin NC, Cook GA, etc.)** | ⚪ Source identified but not yet acquired |

**Pilot county count (with at least 1 PDF)**: 6 of 25 high-share counties.

## OCR fallback (deferred)

A meaningful fraction of older ACFRs (FY ≤ 2020) are scanned images. Tesseract install was deferred this session (required Homebrew prompt). Documented for next session:

```bash
brew install tesseract poppler
python3 -m pip install pytesseract pdf2image
```

For the 2017→2025 two-period DiD, OCR is **not** required — 2017 comes from Census ACFR (text-extractable already), and 2025 ACFRs are uniformly born-digital. OCR only matters if we want to fill in 2018-2023 trajectory years.
