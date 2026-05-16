// =============================================================================
// 06_figures.do — Publication-ready figures for paper/main.tex.
//
// Outputs: output/figures/fig_*.pdf
//
// Use `graph export` with .pdf; explicit `width()`; consistent style across
// all figures (set theme in a helper if needed).
// =============================================================================

if "$root" == "" {
    global root "`c(pwd)'"
    do "$root/scripts/stata/_config.do"
}

di as text "06_figures.do — placeholder; populated alongside descriptive + analyze"
