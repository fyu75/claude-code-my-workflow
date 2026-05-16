// =============================================================================
// 04_analyze.do — Main regressions and tests. `estimates save` everything.
//
// Inputs:  data/derived/*.dta
// Outputs: output/tables/est_*.ster (Stata estimates)
//
// INV-7: cluster-robust SEs at the appropriate level — county or state or
// issuer; document choice in a comment next to each regression.
// INV-8: every regression must `estimates save` for /audit-reproducibility.
// =============================================================================

if "$root" == "" {
    global root "`c(pwd)'"
    do "$root/scripts/stata/_config.do"
}

di as text "04_analyze.do — placeholder; populated when muni bond data arrives"
