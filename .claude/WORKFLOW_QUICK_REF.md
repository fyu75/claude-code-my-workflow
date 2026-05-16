# Workflow Quick Reference — dc-muni

**Project:** Corporate Investment and Municipality Finances: Evidence from Data Centers
**Model:** Contractor (you direct, Claude orchestrates)

---

## The Loop

```
Your instruction
    ↓
[PLAN] (if multi-file or unclear) → Show plan → Your approval
    ↓
[EXECUTE] Implement, verify, done
    ↓
[REPORT] Summary + what's ready
    ↓
Repeat
```

---

## I Ask You When

- **Design forks:** "Option A (fast) vs. Option B (robust). Which?"
- **Scope question:** "Frame this around bond yields only, or across all five outcomes?"
- **Specification ambiguity:** "Cluster at county or state? Document choice."
- **Replication tolerance edge case:** "Just missed 0.01 — investigate or accept?"
- **External data uncertain:** "ACFR coverage incomplete for county X — drop or impute?"

---

## I Just Execute When

- Code fix is obvious (bug, pattern application)
- Verification (compile, render, tolerance checks)
- Documentation (logs, MEMORY [LEARN] entries)
- Plotting / tabulation per established standards
- Following the SSOT chain (Stata → output → paper)

---

## Quality Gates (advisory; enforced by /commit)

| Score | Action |
|-------|--------|
| ≥ 80 | Ready to commit |
| ≥ 90 | Ready to share with co-authors |
| < 80 | Fix blocking issues |

---

## Non-Negotiables (project-specific)

- **Path conventions:** Stata uses `$root/$raw/$int/$der/$tab/$fig`; R uses `here::here(...)`. No absolute paths anywhere (INV-2).
- **Seed:** `set seed $PROJECT_SEED` (Stata) and `set.seed(20260510)` (R). Set ONCE in `_config.do` / `00_run_all.R` (INV-3).
- **Stata version:** `version 19` in `_config.do`. SE binary only — never `stata-mp` (INV-6).
- **Tables:** `\input{../output/tables/<name>.tex}` from `paper/main.tex`. Never hand-edit. AEA-style: SE in parentheses, no significance stars (INV-1).
- **Figures:** `\includegraphics{<name>.pdf}` from `output/figures/`. Never reproduce manually (INV-1).
- **Numbers in body text:** never typed by hand. Use `\input{../output/tables/inline_<stat>.tex}` for one-line scalars.
- **US-firm filter:** applied in `02_clean.do`, not silently in analysis (INV-4).
- **Bibliography:** `paper/refs.bib` only. No per-section .bib files (INV-5).
- **Cluster level:** documented in regression comment; defended in methods section (INV-7).
- **Estimates persistence:** `estimates save` (Stata) / `saveRDS` (R) every regression for `/audit-reproducibility` (INV-8).
- **Tolerance thresholds:** point estimates < 0.01, SE < 0.05, integers exact (see `replication-protocol.md`).

---

## Project Frame (don't drift)

- **Outcome breadth:** muni tax-collection elasticity, muni capex, debt paydown, public services, ratings, AND bond yields/spreads. Do not narrow to bonds-only.
- **Where the action is:** rural / poor counties. Loudoun County, VA is the wealthy outlier — don't treat as representative.
- **Identification:** Greenstone–Hornbeck–Moretti winners-vs-losers template; Chava–Malakar–Singh subsidies (15.2 bps) is closest precedent.
- **Speed:** Giroud, Rauh, Chava, Gao all increasingly active in muni space. Move fast on identification + descriptive stylized facts.

---

## Preferences

**Visual:** Publication-ready finance figures — single-column, 6.5×4.0 in, white bg, `theme_dcmuni`. Tables AEA-style: SE in parens, no significance stars.
**Reporting:** Concise; surface key findings up front, details on request.
**Session logs:** Always (post-plan, incremental, end-of-session).
**Replication:** Strict — flag near-misses; do not silently round.

---

## Exploration Mode

For experimental work, use the **Fast-Track** workflow:
- Work in `explorations/` folder
- 60/100 quality threshold (vs. 80/100 for production)
- No plan needed — just a research value check (2 min)
- See `.claude/rules/exploration-fast-track.md`

---

## Cross-references

- `CLAUDE.md` — top-level project info, folder layout, commands
- `MEMORY.md` — accumulated [LEARN] entries
- `.claude/rules/single-source-of-truth.md` — paper SSOT chain
- `.claude/rules/content-invariants.md` — INV-1 through INV-9
- `.claude/rules/quality-gates.md` — scoring rubric
- `.claude/rules/r-code-conventions.md` — R standards
- `.claude/rules/stata-code-conventions.md` — Stata standards
- `.claude/rules/knowledge-base-template.md` — notation, mechanism, identification, S&P 451 vars

---

## Next Step

You provide task → I plan (if needed) → Your approval → Execute → Done.
