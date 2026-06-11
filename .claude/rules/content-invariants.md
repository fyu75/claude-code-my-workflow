# Content Invariants (INV-1 through INV-9)

Numbered non-negotiable rules for content produced in this repository. Critic agents, reviewers, and audit agents should cite invariants by number (e.g., "violates INV-3") when flagging issues. Adapted from clo-author's enforcement pattern; rewritten 2026-05-10 for the **dc-muni** empirical-paper context (slide-specific INV-1 through INV-8 from the template were dropped).

## Pipeline invariants

- **INV-1: Authoritative source.** Stata `.do` files in `scripts/stata/` are authoritative for analysis. Tables (`\input{}`) and figures (`\includegraphics{}`) in `paper/main.tex` are derived artifacts. Never hand-edit a `.tex` table or paste a number into the paper that doesn't trace to `output/`. See `authoritative-source.md`.
- **INV-2: Relative paths only.** No absolute paths anywhere (`/Users/…`, `C:\…`, `~`). R uses `here::here(…)`; Stata uses `$root/…` derived from `_config.do`. Catches every co-author's machine.
- **INV-3: Reproducibility seed.** `set.seed(20260510)` (R) or `set seed $PROJECT_SEED` (Stata, with `$PROJECT_SEED 20260510` in `_config.do`) is set ONCE at the top of `00_run_all.{do,R}`. Never inside loops or functions. `set sortseed` matches `set seed` in Stata.
- **INV-4: US-firm filter at the cleaning stage.** The "filter to US firms" step happens in `02_clean.do`, never silently in analysis scripts. Sample restriction must be visible in the data lineage.
- **INV-5: Single bibliography.** `paper/refs.bib` is the authoritative bib file. No per-section `.bib` files. All `\cite{}` keys resolve against this one file.
- **INV-6: Stata version locked.** `version 19` at the top of `_config.do`. Every other Stata script inherits.

## Estimation invariants

- **INV-7: Cluster level documented.** Every regression specifies the SE-cluster level (county, state, or issuer) in a comment next to the command. The choice is defended in the methods section of the paper.
- **INV-8: Estimates persisted.** Every regression `estimates save`s to `output/tables/est_*.ster` (Stata) or `saveRDS` to `scripts/R/_outputs/` (R). `/audit-reproducibility` reads these to verify the paper's numeric claims.
- **INV-9: No silent sample changes.** When the analysis sample changes from one specification to the next (added control, dropped non-overlapping units, balanced panel), the change is logged in the regression comment and an N row in the table makes it visible.

---

## What this rule does NOT cover

- Notation conventions for the paper (yields vs spreads, unit definitions) — see `knowledge-base-template.md`.
- Quality scoring rubrics — see `quality-gates.md`.
- Replication tolerance thresholds — see `replication-protocol.md`.
- Cross-artifact review (paper ↔ code) — see `cross-artifact-review.md`.
