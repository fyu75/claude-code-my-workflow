// =============================================================================
// 05_tables.do — Publication-ready regression tables for paper/main.tex.
//
// Inputs:  output/tables/est_*.ster   (from 04_analyze.do)
// Outputs: output/tables/reg_*.tex    (input via \input{} into paper)
//
// AEA-style: SE in parentheses, no significance stars (let editor decide).
// Use `esttab` from estout package.
// =============================================================================

if "$root" == "" {
    global root "`c(pwd)'"
    do "$root/scripts/stata/_config.do"
}

di as text "05_tables.do — placeholder; populated alongside 04_analyze.do"
