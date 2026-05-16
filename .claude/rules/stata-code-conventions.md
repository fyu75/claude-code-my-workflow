---
paths:
  - "**/*.do"
  - "**/*.ado"
  - "scripts/stata/**"
---

# Stata Code Standards

**Standard:** Senior Principal Data Engineer + PhD researcher quality. Mirror of `r-code-conventions.md` for the Stata side of the pipeline.

This file is path-scoped — it loads only when Claude works on a `.do` / `.ado` file or anything under `scripts/stata/`.

---

## 1. Binary and version

- **Use only StataSE 19.0** at `/Applications/Stata/StataSE.app/Contents/MacOS/StataSE`. The user's license is for SE 19.
- **`stata-mp` on PATH is unlicensed** — do not invoke. Headless invocations must use the SE binary explicitly.
- **`version 19`** at the top of `_config.do` (every other script inherits).

## 2. Reproducibility

- `set seed $PROJECT_SEED` and `set sortseed $PROJECT_SEED` once in `_config.do` (mirrors INV-3 for R).
- All paths derive from `$root` (set in `00_run_all.do` from `c(pwd)`); no absolute paths anywhere (mirrors INV-2).
- `clear all`, `set more off`, `cap log close _all` at the top of `_config.do`.
- Every regression must `estimates save` to `$tab/est_<name>.ster` (mirrors INV-8 — RDS pattern in R).

## 3. Headless invocation

From the repo root:

| Mode | Command | Log behavior |
|---|---|---|
| Standard | `/Applications/Stata/StataSE.app/Contents/MacOS/StataSE -e do scripts/stata/00_run_all.do` | Respects the in-script `log using` path |
| Auto-log | `... -b do scripts/stata/00_run_all.do` | Drops the log next to the .do file; ignores `log using` |

`-e` is the default for this project because `00_run_all.do` writes its own log to `scripts/stata/00_run_all.log`.

## 4. Naming

- `snake_case` for variables, locals, globals, programs, .do filenames.
- Verb-noun pattern for programs (`build_panel`, `clean_owners`).
- Numbered prefixes for pipeline scripts (`01_import.do`, `02_clean.do`, …).

## 5. Discipline

- **Sort before merge / reshape.** Stata's `merge` is sort-stable, but explicit `sort` makes intent clear.
- **`isid <vars>`** to assert uniqueness on the join key before merging.
- **`compress`** before `save` to shrink intermediate `.dta`.
- **`label variable` and `label define`** before `save` so downstream readers don't see raw variable codes.
- **Explicit `replace` on `save`** is fine — overwriting intermediate files is the pipeline's job. But never overwrite `data/raw/`.

## 6. Outputs

- Tables: `esttab` (from `ssc install estout`) → `$tab/<name>.tex`. AEA-style: SE in parentheses, no significance stars.
- Figures: `graph export "$fig/<name>.pdf", replace` with explicit `width()` for consistent sizing.
- Estimates: `estimates save "$tab/est_<name>.ster", replace` for every regression.

## 7. Numerical discipline

- No `==` on floats — use `float()` cast or `inrange()`.
- Cluster-robust SEs at the appropriate level (county / state / issuer); document the choice in a comment next to each regression (INV-7).
- `xtset <panel> <time>` BEFORE any panel command (`xtreg`, `xtabond`, etc.).
- For staggered-DiD designs use `csdid` (Callaway--Sant'Anna) or `did_imputation` (Borusyak et al.) — not naive two-way FE.
- For deterministic bootstraps, set `set sortseed` in addition to `set seed`. Stata's `bsample` is sort-order-dependent.

## 8. Common pitfalls

| Pitfall | Impact | Prevention |
|---|---|---|
| `xtreg, fe` vs `areg` SE differences | Different cluster-robust df adjustments | Pick one, document; prefer `reghdfe` for high-dim FEs |
| Hardcoded absolute path | Breaks on co-author's machine | Always `$root/...`; never `/Users/...` |
| Missing `set sortseed` | Non-deterministic bootstraps | Set both `set seed` and `set sortseed` |
| `merge 1:1` vs `1:m` confusion | Silent duplication / drop | Always run `isid` on the master key first |
| Encoding strings before clean | Permanent data loss | `encode` only after standardizing case / trim |

## 9. Stata to LaTeX paper handoff

- Tables: `\input{../output/tables/reg_main.tex}` from `paper/main.tex`. Never hand-edit a `.tex` table — change the upstream `esttab`.
- Figures: `\includegraphics[width=\textwidth]{fig_main.pdf}` (graphicspath in `main.tex` resolves to `../output/figures/`).
- Numbers in body text: `\input{../output/tables/inline_<stat>.tex}` for one-line scalars (e.g., the headline ATT) — never type a number into the .tex by hand. (`/audit-reproducibility` enforces this at submission time.)

## 10. Code Quality Checklist

```
[ ] _config.do sourced or $root non-empty (so _config.do auto-sources)
[ ] version 19 in _config.do
[ ] set seed $PROJECT_SEED in _config.do
[ ] All paths via $raw / $int / $der / $tab / $fig globals
[ ] No absolute paths anywhere
[ ] sort + isid before every merge
[ ] compress + label before save
[ ] estimates save for every regression
[ ] Cluster-robust SE level documented in a comment
[ ] No == on floats
[ ] Comments explain WHY not WHAT
```
