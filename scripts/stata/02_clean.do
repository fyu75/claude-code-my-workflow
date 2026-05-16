// =============================================================================
// 02_clean.do — Type coercion, joins, US filter, derived variables.
//
// Inputs:  data/intermediate/dc_*.dta
// Outputs: data/derived/<topic>.dta
//
// INV-4 reminder: US-firm filter is applied HERE, not silently in analysis.
// =============================================================================

if "$root" == "" {
    global root "`c(pwd)'"
    do "$root/scripts/stata/_config.do"
}

di as text "02_clean.do — placeholder; populated in next plan"
