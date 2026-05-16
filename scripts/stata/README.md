# `scripts/stata/` — Reproducibility-first Stata pipeline

Primary analysis pipeline for the **dc-muni** project. Mirrors the conventions of `scripts/R/` but targets Stata SE 19.0 as the primary tool.

## Conventions

- **Run everything from `00_run_all.do`** — never `do` mid-pipeline scripts directly except for debugging. They auto-source `_config.do` if `$root` is empty so they're still runnable stand-alone.
- **Stata binary:** `/Applications/Stata/StataSE.app/Contents/MacOS/StataSE`. The `stata-mp` on PATH is unlicensed — never use it.
- **Headless invocation** (from repo root):
  ```bash
  /Applications/Stata/StataSE.app/Contents/MacOS/StataSE -e do scripts/stata/00_run_all.do
  ```
  `-e` respects the in-script `log using` path. `-b` drops the log next to the .do file (ignores in-script log paths).
- **Paths:** never absolute; always `$root/...`. The `$root` global is set in `00_run_all.do` from `c(pwd)`, then `_config.do` derives every other path globally.
- **Seed:** `$PROJECT_SEED 20260510` — set in `_config.do`. Change only with a recorded reason in the session log.
- **Outputs:** tables to `$tab` (= `output/tables/*.tex`), figures to `$fig` (= `output/figures/*.pdf`), estimates to `$tab/est_*.ster`, intermediate `.dta` to `$int`, analysis-ready `.dta` to `$der`.

## Files

| Script | Responsibility |
| --- | --- |
| `_config.do` | Globals, paths, seed, version. Sourced by every other script. |
| `00_run_all.do` | Orchestrator. Sets `$root`, sources `_config.do`, runs 01–06. |
| `01_import.do` | Read S&P 451 Research SAS7BDAT files → `$int/dc_*.dta`. |
| `02_clean.do` | Type coercion, joins, US-firm filter, derived variables → `$der/`. |
| `03_descriptive.do` | Tabulation, summary stats → `$tab/desc_*.tex`, `$fig/desc_*.pdf`. |
| `04_analyze.do` | Regressions and tests → `$tab/est_*.ster`. |
| `05_tables.do` | Pretty regression tables via `esttab` → `$tab/reg_*.tex`. |
| `06_figures.do` | Publication-ready figures → `$fig/fig_*.pdf`. |

## First-time setup

Required Stata packages:

```stata
ssc install estout       // esttab for regression tables
ssc install reghdfe      // high-dim fixed effects
ssc install ftools       // dependency for reghdfe
ssc install ivreghdfe    // IV with high-dim FEs
```

Then from the repo root:

```bash
/Applications/Stata/StataSE.app/Contents/MacOS/StataSE -e do scripts/stata/00_run_all.do
```

Expected log: `scripts/stata/00_run_all.log`. Expected outputs (once the body of 01–06 is filled in by the next plan):

| File | Source |
| --- | --- |
| `data/intermediate/dc_*.dta` | 01_import |
| `data/derived/<topic>.dta` | 02_clean |
| `output/tables/desc_*.tex` | 03_descriptive |
| `output/tables/est_*.ster` | 04_analyze |
| `output/tables/reg_*.tex` | 05_tables |
| `output/figures/*.pdf` | 03/06 |

## Reviewing

A future `/review-stata` skill (or extend `/review-r`) will run a Stata-version of the code review protocol. Until then, use the discipline checklist in `.claude/rules/stata-code-conventions.md`.
