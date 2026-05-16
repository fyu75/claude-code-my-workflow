// =============================================================================
// _config.do — Project-wide Stata configuration. Sourced by every numbered .do.
//
// Reproducibility contract (enforced by review-r / audit-reproducibility):
//   - version locked
//   - PROJECT_SEED set once (centralized below)
//   - Project root resolved via $root (set by 00_run_all.do BEFORE sourcing this)
//   - All paths derived from $root — no absolute paths
// =============================================================================

version 19

set more off
cap log close _all
cap set niceness 0, perm

// ---- Path globals ---------------------------------------------------------
// 00_run_all.do sets $root = c(pwd) before sourcing this file. Every other
// path derives from $root, so the pipeline is fully relocatable.

global raw      "$root/data/raw"           // S&P 451 Research SAS files (symlinked)
global external "$root/data/external"      // ACFR / TRACE / MSRB / NCSL etc.
global int      "$root/data/intermediate"  // .dta after import + light cleaning
global der      "$root/data/derived"       // analysis-ready .dta
global out      "$root/output"
global tab      "$out/tables"
global fig      "$out/figures"
global code     "$root/scripts/stata"

cap mkdir "$int"
cap mkdir "$der"
cap mkdir "$out"
cap mkdir "$tab"
cap mkdir "$fig"

// ---- Reproducibility seed -------------------------------------------------
// Change ONLY with a recorded reason in the session log; load-bearing for
// identical numerical outputs.
global PROJECT_SEED 20260510
set seed $PROJECT_SEED
set sortseed $PROJECT_SEED
