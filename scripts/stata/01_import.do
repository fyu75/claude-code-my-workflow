// =============================================================================
// 01_import.do — Read S&P 451 Research SAS7BDAT files into Stata .dta.
//
// Inputs:  data/raw/*.sas7bdat   (symlinked from /Users/fangyu/claude/datacenter/raw/)
// Outputs: data/intermediate/dc_*.dta
//
// Boring and idempotent. No transformations beyond `import sas`. Cleaning
// happens in 02_clean.do; descriptive work in 03_descriptive.do.
// =============================================================================

// _config.do has already been sourced by 00_run_all.do, so $raw / $int /
// $PROJECT_SEED are available. Re-sourcing here makes this file runnable
// stand-alone for debugging:
if "$root" == "" {
    global root "`c(pwd)'"
    do "$root/scripts/stata/_config.do"
}

// ---- TODO: populate per the next plan -------------------------------------
// The first analysis task (separate plan) will fill this with `import sas`
// commands for the relevant files (dcownership, dcprovider, dcclient,
// dcproperties, dcmarket, ciqcompany, providertype, dctenancytype, ...) and
// `save "$int/dc_<name>.dta", replace`.
//
// Skeleton example (commented out — DO NOT activate yet):
//
// import sas using "$raw/dcproperties_latest.sas7bdat", clear
// compress
// save "$int/dc_properties.dta", replace
// di as text "  imported dc_properties: `c(N)' obs"

di as text "01_import.do — placeholder; populated in next plan"
