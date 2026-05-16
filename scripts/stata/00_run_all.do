// =============================================================================
// 00_run_all.do — Orchestrator. Run this, not the individual scripts.
//
// Usage (from repo root):
//   /Applications/Stata/StataSE.app/Contents/MacOS/StataSE -e do scripts/stata/00_run_all.do
//
// The -e flag respects the in-script log path. -b would drop the log next
// to this file instead.
// =============================================================================

clear all

// $root must be set BEFORE sourcing _config.do. We set it from c(pwd) under
// the contract that this file is invoked from the repo root.
global root "`c(pwd)'"

do "$root/scripts/stata/_config.do"

// ---- Pipeline log ---------------------------------------------------------
log using "$root/scripts/stata/00_run_all.log", replace text

di as text "Running dc-muni Stata pipeline with seed $PROJECT_SEED at `c(current_date)' `c(current_time)'"
di as text "  root      = $root"
di as text "  raw       = $raw"
di as text "  derived   = $der"
di as text "  output    = $out"

// ---- Pipeline -------------------------------------------------------------
// Each script consumes the previous stage's outputs and writes its own.
// Adding a stage: add it here, write the .do, follow naming convention.

local pipeline 01_import 02_clean 03_descriptive 04_analyze 05_tables 06_figures

foreach script of local pipeline {
    di as text _newline "==> running `script'.do"
    do "$root/scripts/stata/`script'.do"
}

// ---- Session capture ------------------------------------------------------
// Mirror of R's sessionInfo() — the version + creturn(macro) state so any
// reviewer can verify the environment.
di as text _newline "==> environment capture"
creturn list

di as text _newline "Pipeline complete."

log close
