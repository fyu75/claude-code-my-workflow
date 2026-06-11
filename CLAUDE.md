# CLAUDE.md — Data Centers and Municipality Finances

**Project (working title):** Corporate Investment and Municipality Finances: Evidence from Data Centers
**Authors:** Henrik Cronqvist, Rui Dai, Mitch Warachka, Frank Yu (CEIBS)
**Branch:** main
**Initialized:** 2026-05-10

---

## Core Principles

- **Plan first** — enter plan mode before non-trivial tasks; save plans to `quality_reports/plans/`
- **Verify after** — run `Stata` / `R` / `xelatex` and confirm output at the end of every task
- **Authoritative scripts** — `scripts/python/NN_*.py` are authoritative; tables / figures / numeric claims in memos and the paper are derived from `data/derived/` outputs (never hand-edited). See `.claude/rules/authoritative-source.md`.
- **Quality gates** — nothing ships below 80/100 (advisory; enforced by `/commit`)
- **Frame is broader than yields** — multiple downstream outcomes (tax revenue, capex, debt, ratings, AND yields). Don't narrow to bonds-only without team approval.
- **[LEARN] tags** — when corrected, save `[LEARN:category] wrong → right` to [MEMORY.md](MEMORY.md)

Cross-session context lives in [MEMORY.md](MEMORY.md); past plans, specs, and session logs are in [quality_reports/](quality_reports/).

---

## Folder Structure

```
datacenter2/
├── CLAUDE.md                    # This file
├── MEMORY.md                    # [LEARN] entries
├── .claude/                     # Rules, skills, agents, hooks
├── data/
│   ├── raw -> /Users/fangyu/claude/datacenter/raw   # symlink (gitignored) — S&P 451 Research
│   ├── external/                # ACFR, TRACE/MSRB, NCSL, ratings reports (gitignored)
│   ├── intermediate/            # .dta after import (gitignored)
│   └── derived/                 # analysis-ready
├── scripts/
│   ├── python/                  # PRIMARY — numbered 01–31, end-to-end pipeline
│   ├── stata/                   # legacy skeleton, retained but inactive
│   └── R/                       # legacy skeleton, retained but inactive
├── memos/                       # team-facing memos (dated YYYY-MM-DD_topic.md)
├── paper/
│   ├── main.tex                 # LaTeX-first authoritative paper
│   ├── refs.bib                 # Bibliography (paper/refs.bib only — INV-5)
│   ├── sections/                # intro / data / empirical / results / conclusion
│   └── figures/                 # hand-drawn / non-code-generated figures
├── output/
│   ├── tables/                  # .tex tables → \input{} into paper
│   └── figures/                 # .pdf figures → \includegraphics{} into paper
├── master_supporting_docs/
│   ├── related_papers/          # cited literature PDFs
│   ├── case_studies/            # PWC VA fiscal report, Loudoun, etc.
│   ├── industry_reports/        # Moody's, S&P Ratings, NCSL, Nuveen
│   └── data_documentation/      # S&P 451 codebook, ACFR guide, MSRB docs
├── notes/                       # team notes (Henrik, Mitch input)
├── explorations/                # research sandbox
├── quality_reports/             # plans, session logs, merge reports
└── templates/                   # session log, quality report, requirements spec, etc.
```

---

## Commands

```bash
# Python pipeline (primary) — run individual scripts in numeric order
python3 scripts/python/01_*.py    # data ingest
# … through …
python3 scripts/python/71_dose_clock_and_type_split.py    # current latest

# Compile paper (when manuscript is ready; main.tex is currently skeleton)
cd paper && xelatex main.tex && bibtex main && xelatex main.tex && xelatex main.tex

# Validate setup
./scripts/validate-setup.sh
```

---

## Quality Thresholds (advisory; enforced by `/commit`)

| Score | Checkpoint | Meaning |
|-------|------|---------|
| 80 | Commit | Good enough to save |
| 90 | PR / share with co-authors | Ready for collaborator review |
| 95 | Submission-ready | Aspirational |

Direct `git commit` bypasses the gate. See `.claude/rules/quality-gates.md`.

---

## Skills Quick Reference

| Command | What It Does |
|---------|-------------|
| `/compile-latex [file]` | 3-pass XeLaTeX + bibtex on `paper/main.tex` |
| `/proofread [file]` | Grammar / typo / consistency review |
| `/review-r [file]` | R code quality review |
| `/validate-bib` | Cross-reference citations vs `paper/refs.bib` |
| `/commit [msg]` | Stage, commit, PR, merge (halts if score < 80) |
| `/lit-review [topic]` | Literature search + synthesis |
| `/research-ideation [topic]` | Research questions + strategies |
| `/interview-me [topic]` | Interactive research interview |
| `/review-paper [file]` | Manuscript review (single-pass / `--adversarial` / `--peer <journal>`) |
| `/respond-to-referees [report] [manuscript]` | R&R cross-reference + response draft |
| `/data-analysis [dataset]` | End-to-end R analysis |
| `/audit-reproducibility [paper]` | Enforce tolerance thresholds on paper ↔ code |
| `/seven-pass-review` | Seven-pass adversarial manuscript review |
| `/verify-claims [file]` | CoVe fact-check (forked verifier, fresh context) |
| `/checkpoint [topic]` | Save state snapshot before stop / handoff |
| `/preregister [--style ...]` | Draft a preregistration document |
| `/learn [skill-name]` | Extract discovery into persistent skill |
| `/context-status` | Show context usage and session health |
| `/deep-audit` | Repository-wide consistency audit |
| `/permission-check` | Diagnose permission layers |

---

## Python Conventions (active pipeline)

| Convention | Value |
|---|---|
| Python binary | `python3` (system; project uses pandas, numpy, statsmodels, scipy, pyfixest, differences) |
| Script numbering | `scripts/python/NN_short_name.py`, NN increments sequentially; each script self-contained |
| Project root | `pathlib.Path(__file__).resolve().parents[2]` in each script |
| Seed | `np.random.default_rng(20260516)` for bootstraps (project seed locked in earlier scripts) |
| Outputs | `data/derived/*.csv` for analysis-ready data; `data/derived/*.md` for tables-as-markdown |
| Memos | `memos/YYYY-MM-DD_topic.md`; numbers in memos must trace to a `data/derived/` file |

---

## Current Project State

| Component | Status |
|---|---|
| Workflow scaffolding | ✅ Adapted from `pedrohcgs/claude-code-my-workflow` 2026-05-10 |
| Pipeline language | 🔵 Pivoted Stata → Python (numbered `scripts/python/01–31`); R/Stata skeletons retained but unused |
| S&P 451 Research DC database | ✅ 4,507 US DCs spatial-joined to county FIPS (100% coverage) |
| SDC Public Finance muni bonds | ✅ Tier-A filtered (~177k deals 2005+), 83% deal-weighted county-FIPS resolved |
| Census ASLGF / ACFR 2017 | ✅ Re-aggregated to county-govt only (type=1); 3,020 counties |
| Acquired ACFR PDFs (high-DC-share) | ✅ 23 of 25 top-25 counties; 17 of 59 candidate controls |
| MSRB historical trades | ✅ Converted to `data/msrb/msrb.parquet` (4.1 GB zstd, 215.8M trades, script 33); secondary-market analysis not yet run |
| Empirical results | ✅ PT matched DiD +3.39%/yr (clean +2.59**); bond pricing channel NULL (dummy/dose/placebo/announcement — the old −23bps was a control-group artifact, do NOT cite); crypto: spreads widen, less rated debt. See memos/dc_mechanism_evidence_running_notes.md §6–11 |
| Team-facing memo | ✅ `memos/2026-05-16_stylized_facts_combined.md` (supersedes v1/v2/v3) |

## Key Derived Files (saves grep-archaeology)

| Path | Content |
|---|---|
| `data/derived/county_year_panel_v4.csv` | Main analysis panel: county × year × DC presence × muni issuance × spreads |
| `data/derived/dc_property_county_fips.csv` | 4,507 US DCs mapped to county FIPS (100% coverage) |
| `data/derived/dc_tax_share_distribution.csv` | DC tax-share proxy per county (low/mid/high estimates) — defines the ≥ 1% treatment cut |
| `data/derived/acfr_2017_county_govt_only.csv` | Census 2017 ACFR re-aggregated to type=1 county-government scope only (3,020 counties) |
| `data/derived/acfr_county_year_extracted_wide.csv` | PDF-extracted multi-year fiscals for 23 high-DC-share treated counties |
| `data/derived/option_c_excess_growth.csv` | 2017→latest within-county CAGR for property tax / capex / debt |
| `data/derived/option_c_full_tests.md` | Full test battery (t / Wilcoxon / sign / OLS / influence) for Option C |
| `data/derived/cs_did_threshold.md` | Main bond-spread CS-DiD result (1% threshold sample) |
| `data/munispot/parquet_v2/statement_type=*/fiscal_year=*/part-*.parquet` | MuniSpot Academic License v2 (Raj's 2026-06 interim update): 4.04M rows of all-governmental-funds line items FY2016–FY2026, county-government entities only (`municipality_type=='County-General Purpose Government'`), partitioned by `(statement_type, fiscal_year)`. Predicate pushdown ready. **License-restricted; gitignored.** Use `column_index==1` to isolate General Fund (v1-comparable), `column_index==-1` for "Total Governmental Funds". |
| `data/munispot/parquet/` | MuniSpot v1 (Apr 2026 delivery, GF-only, FY16-24). **Superseded by v2** but kept on disk for v1↔v2 audit; v1 included school-district and city entities mixed with counties — never join v1 on `county_fips` without filtering `municipality_type=='County-General Purpose Government'`. |
| `data/derived/muni_property_tax_v2_classified_{gf_only,allfunds}_FY2016_2026.{csv,parquet}` | v2 PT classifier output. Three tier flags per row: `tier_strict` (Raj's `class_1=='PROPERTY TAX REVENUES'` minus negation rows), `tier_extended` (+ `ad valorem`/`real estate`/`real property` keywords in MISC/LOCAL REVENUE), `tier_with_pilot` (+ Payments In Lieu Of Taxes). Coverage: 1,092 counties at tier_with_pilot vs 927 at tier_strict (+18%). |
| `data/derived/muni_{property_tax,total_revenue,total_expenditures}_v2_{gf_only,allfunds}_FY2016_2026.{csv,parquet}` | v2 raw `class_1`-bucket subsets (no reported_stat classification). GF-only PT: 7,029 rows; all-funds PT: 6,547 rows. |
| `data/derived/dc_treated_coverage_v2_vs_acfr.csv` | One-row-per-treated-county matrix: v2 PT coverage flags × our ACFR PDF coverage flags. 54 of 125 treated counties (43%) have PT from at least one source. |
| `data/derived/dc_dc_level_announcements.csv` + `announcement_anchor_county.csv` + `treatment_anchors_compare.csv` | Per-DC announcement years (140 rows, 99% H/M; all 172 real ≥50MW treated DCs dated) + county anchors. Adopted event anchor = `cap50_oy` (capacity-midpoint, script 67) |
| `data/derived/dc_dose_announced_mw_panel.csv` | County×year continuous dose: cum announced ≥50MW MW / 2017 PT $M (assumption-free; scripts 70–71) |
| `data/derived/clean_never_dc_controls.csv`, `treated_exclusions_phantom.csv` | Verified DC-free control pool (2,639) and phantom/cancelled treated drop list — standard inputs for all bond tests (script 69) |
| `memos/2026-05-16_stylized_facts_combined.md` | Current authoritative team-facing memo (supersedes v1/v2/v3) |

---

## Data Gotchas (re-discovered the painful way)

- **Census ASLGF Annual ≠ Census of Govts.** Annual files (2003–2016 ex-Census years) are a SAMPLE survey with thin county coverage. Only 1992/1997/2002/2007/2012/2017 are full Census of Govts. Cook IL 2012 annual file shows $11.7M property tax vs $12.5B real. Use Census-of-Govts years only for cross-section work.
- **Pre-2017 ACFR state codes are Census alphabetical codes, NOT FIPS.** VA = 47 (not 51). Crosswalk in `scripts/python/13_acfr_parse_all_years.py`.
- **Pre-2014 ACFR row format has 7-char unit-ID, not 6.** Shifts item-code position from `[12:15]` to `[14:17]`. Detect by line length before parsing.
- **PDF extraction parser dup pattern.** Glasscock 48173, Briscoe 48045, Ward 48475 share identical $5.5M total revenue + $3.66M property tax — row-context confusion suspected. Treat as unreliable until manually verified.
- **Mecklenburg VA (51117) scope mismatch.** Census 2017 county aggregation captures consolidated entities; PDF FY23 is county-government only. Drop from within-county growth tests.
- **TX small oil counties (Pecos 48371, Ward 48475, Crane 48103)** — 2017→2024 trajectory dominated by 2014-16 oil price collapse, not DC investment. Drop from DC-mechanism samples.
- **OR SOS portal trips JS bot wall under `urllib`.** Shell out to `curl` subprocess. Pattern: POST `/muni/search.do` → parse `doc_rsn` → POST `/muni/report.do`. See `scripts/python/27_acquire_or_controls.py`.
- **FRED CSV endpoint flakes intermittently** (HTTP/2 INTERNAL_ERROR). Fallback: `urllib` with `Mozilla/5.0` UA, or use the JSON API (requires key).
- **Tesseract OCR installed** at `/opt/homebrew/bin/tesseract` 5.5.2. ~40% of older ACFRs are scanned and need OCR.
- **MuniSpot v1 mixed entity types.** v1's income statement had 57% school districts + 24% cities + 14% counties — all tagged with `county_fips`. Joining v1 on county_fips alone over-counts ~6×. v2 is restricted to County-General Purpose Government; safe to join on county_fips. **Always prefer v2 (`data/munispot/parquet_v2/`); v1 is retained only for audit comparison.**
- **MuniSpot v2 `class_1='PROPERTY TAX REVENUES'` is narrow.** Raj's normalized bucket captures only 927 of 2,055 counties. ~165 more counties (LA parishes' "Ad valorem", various states' "Real estate taxes") sit in the `MISCELLANEOUS` and `LOCAL REVENUE` buckets — recoverable via `reported_stat` patterns. Use `muni_property_tax_v2_classified_*` (output of `35_classify_munispot_property_tax.py`), not the raw bucket subset. ~960 counties report only an aggregate `"Taxes"` line (mostly TN) — not extractable from v2; needs source ACFR PDF.
- **MuniSpot v2 entity filter is inconsistent for consolidated city-counties.** Denver (08031) and Honolulu (15003) pass Raj's `municipality_type='County-GP'` filter, but Indianapolis-Marion (18097), Louisville-Jefferson (21111), Philadelphia (42101), DC (11001), Baltimore (24510), St. Louis (29510), Carson City (32510), and all 38 VA independent cities (51-510..51-840) get excluded because they're labeled Municipality-GP. Plan accordingly when building national panels.
- **S&P periodic rollups: group by `PROPERTYUNIQUEID`, never `DCPROPERTIESPERIODICID`** (per-row ID; wrong key silently gives 5% match). `TOTALITPOWER` is kW (/1000 for MW; 97% coverage); the static `dcproperties` power field is empty.
- **S&P 451 phantom/geocode errors**: McDowell WV 54047 "Panther" is really Carbon PA; Hood TX "McCamey" is really Granbury (McCamey = Upton 48461); duplicate Ellendale ND rows. Phantom/cancelled treated (Meigs TN, McDowell WV, Lawrence KY) in `data/derived/treated_exclusions_phantom.csv` — always exclude.
- **Bond-test control pool**: panel-v4 "never" (n_dc_cumulative==0) contains 137 tiny-DC S&P hosts. Use `data/derived/clean_never_dc_controls.csv` (2,639, verified DC-free).
- **Dose regressions**: winsorize linear dose at 50 MW/$M (Glasscock 48173 = 641 flips signs); prefer deal-level hedonic over county-year par-wtd spread (cy equal-weights tiny rare issuers — aggregation artifact, see script 70 appendix).
- **pyfixest 0.50.1 has no `sunab`**; `event_study(estimator='saturated')` is beta and crashes on sparse multi-cohort panels. `differences` (Callaway–Sant'Anna) is installed.
- **Amazon/Meta DCs are not press-announced per building** — date them via county/Port tax-abatement votes (Morrow CREZ waves, Hermiston LRZE). For agent search waves, seed queries with the operator name from `data/derived/dc_operator_seed.csv` (98% coverage), not S&P's opaque dcname codes.
