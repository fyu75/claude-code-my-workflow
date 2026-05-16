---
paths:
  - "scripts/**/*.R"
  - "scripts/**/*.do"
  - "paper/**/*.tex"
---

# Quality Review & Scoring Rubrics

> **Framing:** Thresholds are **advisory at the harness level**. The `/commit` skill runs `quality_score.py` and halts on failure until the user fixes or explicitly overrides. There is no git pre-commit hook that blocks a direct `git commit` — if you bypass the skill, you bypass the review. "Gate" in this file means "checkpoint enforced by a specific skill," not "repo-wide block."

## Thresholds

- **80/100 = Commit** — good enough to save
- **90/100 = PR** — ready for deployment / sharing with co-authors
- **95/100 = Excellence** — submission-ready

---

## R Scripts (`.R`)

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | Syntax errors / script fails to source | -100 |
| Critical | Domain-specific bugs (wrong estimator, wrong sample filter) | -30 |
| Critical | Hardcoded absolute paths (INV-2 violation) | -20 |
| Major | Missing `set.seed()` (INV-3) | -10 |
| Major | Missing figure / table generation declared in script header | -5 |
| Major | No `saveRDS` for downstream regression objects (INV-8) | -5 |
| Minor | Long lines (>100 chars) outside documented math sections | -1 per line |
| Minor | Mixed `T`/`F` instead of `TRUE`/`FALSE` | -1 |

## Stata Scripts (`.do`)

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | Syntax errors / script fails to do | -100 |
| Critical | Domain-specific bugs (wrong estimator, wrong sample filter) | -30 |
| Critical | Hardcoded absolute paths (INV-2 violation) | -20 |
| Major | Missing `version` directive (INV-6) | -5 |
| Major | Missing `set seed` / `set sortseed` (INV-3) | -10 |
| Major | Missing `estimates save` for a regression (INV-8) | -5 |
| Major | `merge` without prior `isid` on the master key | -5 |
| Major | Cluster-SE level undocumented in regression comment (INV-7) | -3 |
| Minor | Hardcoded numeric thresholds in script body (use a global) | -1 |

## LaTeX Paper (`paper/main.tex`, `paper/sections/*.tex`)

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | XeLaTeX compilation failure | -100 |
| Critical | Hand-edited number in body text that doesn't trace to `output/` (INV-1 + audit-reproducibility) | -25 |
| Critical | Hand-edited table / figure body (INV-1) | -20 |
| Critical | Undefined `\cite{}` key | -15 |
| Major | Overfull hbox > 10pt | -5 |
| Major | Missing `\input{}` for a referenced table (file exists in output/ but paper duplicates it inline) | -10 |
| Minor | Inconsistent natbib style (`\citet` vs `\citep` mixing) | -1 per file |

---

## Enforcement (by the `/commit` skill only)

- **Score < 80:** Halt within `/commit`. List blocking issues. User may override with an explicit natural-language signal ("commit anyway" / "skip quality gate") and a reason — the override is logged in the commit body.
- **Score < 90:** Allow commit within `/commit`, warn. List recommendations.
- **Direct `git commit`** (bypassing the skill): no enforcement. For hard enforcement, install a git pre-commit hook that wraps `quality_score.py`.

## Quality Reports

Generated **only at merge time**. Use `templates/quality-report.md` for format. Save to `quality_reports/merges/YYYY-MM-DD_[branch-name].md`.

---

## Tolerance Thresholds (Research)

For `/audit-reproducibility`. Mirrors `replication-protocol.md`.

| Quantity | Tolerance | Rationale |
|----------|-----------|-----------|
| Integers (N, counts) | Exact match | No reason for any difference |
| Point estimates (β, ATT) | < 0.01 | Display rounding in the paper |
| Standard errors | < 0.05 | Bootstrap / cluster-robust variation |
| t-stats / z-stats | < 0.05 | Display rounding |
| P-values | Same significance threshold (5% / 1% boundary unchanged) | Exact p may differ slightly |
| R² / pseudo-R² | < 0.001 | Display rounding |
| Percentages | < 0.1pp | Display rounding |
