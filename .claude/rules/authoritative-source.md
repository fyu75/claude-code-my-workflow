---
paths:
  - "paper/**"
  - "scripts/**/*.do"
  - "scripts/**/*.R"
  - "output/**"
---

# Authoritative Source: Paper Chain

**Stata `.do` files in `scripts/stata/` are the authoritative source for analysis. Tables and figures in the paper are derived artifacts — never hand-edited.**

## The Authoritative Chain

```
data/raw/ (S&P 451 Research SAS files)         data/external/ (ACFR, MSRB, NCSL, etc.)
     │                                                  │
     └─────────────────────┬────────────────────────────┘
                           ▼
              scripts/stata/01_import.do  →  data/intermediate/dc_*.dta
                           │
                           ▼
              scripts/stata/02_clean.do  →  data/derived/<topic>.dta   ◄── SOURCE OF TRUTH for cleaned variables
                           │
              ┌────────────┴───────────────────────────┐
              ▼                                        ▼
   scripts/stata/03..06.do        (R supplementary)  scripts/R/*.R   ─── may NOT redefine cleaned variables
              │                                        │
              ▼                                        ▼
       output/tables/*.tex                     output/tables/*.tex
       output/figures/*.pdf                    output/figures/*.pdf
              │                                        │
              └──────────────────┬─────────────────────┘
                                 ▼
                         paper/main.tex      (consumes via \input{} and \includegraphics{})
                                 │
                                 ▼
                          paper/main.pdf

NEVER edit tables, figures, or numeric claims in the paper directly.
ALWAYS propagate changes upstream: data → cleaning → analysis → output → paper.
```

---

## Tables

- **All regression tables enter the paper via `\input{../output/tables/<name>.tex}`.**
- Tables are produced by `esttab` (Stata) or `modelsummary` (R) — never typed into the paper by hand.
- AEA convention: SE in parentheses, no significance stars. The paper's `\bibliographystyle{aer}` matches.
- If a table needs a layout-specific tweak (column widths, multirow), do it in the .tex output written by `esttab` (via `prefoot()` / `posthead()`) — not by editing the file after the fact.

## Figures

- **All figures enter the paper via `\includegraphics{<name>.pdf}`** with `\graphicspath{{../output/figures/}{figures/}}` resolving the path.
- `output/figures/` is for code-generated figures (Stata `graph export`, R `ggsave`).
- `paper/figures/` is for hand-drawn or non-code-generated diagrams (e.g., conceptual diagrams created in TikZ or external tools). Use sparingly.
- Match the dimensions in `paper/main.tex` to the dimensions used in the upstream `graph export width(...)` / `ggsave(width=, height=)` call.

## Numbers in body text

- Inline numeric claims (the headline ATT, sample size, R²) should not be typed by hand.
- Use `\input{../output/tables/inline_<stat>.tex}` for one-line scalars produced by Stata `file write` or R `writeLines`.
- `/audit-reproducibility` will flag any inline number in the manuscript that doesn't match an upstream output file (within the tolerance defined in `replication-protocol.md`).

## R supplementary

- `scripts/R/` is supplementary analysis (robustness, additional figures, simulations).
- R scripts MUST read from `data/derived/<topic>.dta` (Stata's clean output) — never redefine cleaning logic independently.
- If R needs to re-clean for a specific extension, do it in a clearly-labelled `99_R_extension_<topic>.R` script that loads from `data/derived/` and writes to `data/derived/_R_aux/`. The `99_` prefix flags it as outside the main pipeline.

## Bibliography

- `paper/refs.bib` is authoritative. No per-section `.bib` files (INV-5).
- All `\cite{}` keys must resolve against `paper/refs.bib`.
- Verify with `/validate-bib` before submission.
