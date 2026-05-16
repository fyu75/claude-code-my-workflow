// =============================================================================
// 03_descriptive.do — Tabulation and summary statistics.
//
// Inputs:  data/derived/*.dta
// Outputs: output/tables/desc_*.tex (via esttab)
//          output/figures/desc_*.pdf (via graph export)
//
// First analysis task lives here: tabulate major US DC owners / providers /
// clients + county-level geographic distribution (rural vs urban; per-state).
// =============================================================================

if "$root" == "" {
    global root "`c(pwd)'"
    do "$root/scripts/stata/_config.do"
}

di as text "03_descriptive.do — placeholder; populated in next plan (tabulate owners/providers/clients + geo)"
