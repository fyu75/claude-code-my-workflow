# CLAUDE.md — Data Centers and Municipality Finances

**Project (working title):** Corporate Investment and Municipality Finances: Evidence from Data Centers
**Authors:** Henrik Cronqvist, Rui Dai, Mitch Warachka, Frank Yu (CEIBS)
**Branch:** main
**Initialized:** 2026-05-10

---

## Core Principles

- **Plan first** — enter plan mode before non-trivial tasks; save plans to `quality_reports/plans/`
- **Verify after** — run `Stata` / `R` / `xelatex` and confirm output at the end of every task
- **Single source of truth** — Stata `.do` files are authoritative; tables / figures / numeric claims in the paper are derived (never hand-edited). See `.claude/rules/single-source-of-truth.md`.
- **Quality gates** — nothing ships below 80/100 (advisory; enforced by `/commit`)
- **Frame is broader than yields** — multiple downstream outcomes (tax revenue, capex, debt, ratings, AND yields). Don't narrow to bonds-only without team approval.
- **[LEARN] tags** — when corrected, save `[LEARN:category] wrong → right` to [MEMORY.md](MEMORY.md)

Cross-session context lives in [MEMORY.md](MEMORY.md); past plans, specs, and session logs are in [quality_reports/](quality_reports/).

---

## Folder Structure

```
datacenter2/
├── CLAUDE.md                    # This file
├── MEMORY.md                    # [LEARN] entries
├── .claude/                     # Rules, skills, agents, hooks
├── data/
│   ├── raw -> /Users/fangyu/claude/datacenter/raw   # symlink (gitignored) — S&P 451 Research
│   ├── external/                # ACFR, TRACE/MSRB, NCSL, ratings reports (gitignored)
│   ├── intermediate/            # .dta after import (gitignored)
│   └── derived/                 # analysis-ready
├── scripts/
│   ├── stata/                   # PRIMARY — _config.do, 00_run_all.do, 01–06
│   └── R/                       # SUPPLEMENTARY — 00_run_all.R, 01–05
├── paper/
│   ├── main.tex                 # LaTeX-first authoritative paper
│   ├── refs.bib                 # Bibliography (paper/refs.bib only — INV-5)
│   ├── sections/                # intro / data / empirical / results / conclusion
│   └── figures/                 # hand-drawn / non-code-generated figures
├── output/
│   ├── tables/                  # .tex tables → \input{} into paper
│   └── figures/                 # .pdf figures → \includegraphics{} into paper
├── master_supporting_docs/
│   ├── related_papers/          # cited literature PDFs
│   ├── case_studies/            # PWC VA fiscal report, Loudoun, etc.
│   ├── industry_reports/        # Moody's, S&P Ratings, NCSL, Nuveen
│   └── data_documentation/      # S&P 451 codebook, ACFR guide, MSRB docs
├── notes/                       # team notes (Henrik, Mitch input)
├── explorations/                # research sandbox
├── quality_reports/             # plans, session logs, merge reports
└── templates/                   # session log, quality report, requirements spec, etc.
```

---

## Commands

```bash
# Stata (primary). NEVER use `stata-mp` — unlicensed.
/Applications/Stata/StataSE.app/Contents/MacOS/StataSE -e do scripts/stata/00_run_all.do

# R supplementary
Rscript scripts/R/00_run_all.R

# LaTeX paper (3-pass + bibtex; from repo root)
cd paper && \
  xelatex -interaction=nonstopmode main.tex && \
  bibtex main && \
  xelatex -interaction=nonstopmode main.tex && \
  xelatex -interaction=nonstopmode main.tex

# Quality score
python scripts/quality_score.py paper/main.tex
python scripts/quality_score.py scripts/stata/04_analyze.do

# Validate setup
./scripts/validate-setup.sh
```

---

## Quality Thresholds (advisory; enforced by `/commit`)

| Score | Checkpoint | Meaning |
|-------|------|---------|
| 80 | Commit | Good enough to save |
| 90 | PR / share with co-authors | Ready for collaborator review |
| 95 | Submission-ready | Aspirational |

Direct `git commit` bypasses the gate. See `.claude/rules/quality-gates.md`.

---

## Skills Quick Reference

| Command | What It Does |
|---------|-------------|
| `/compile-latex [file]` | 3-pass XeLaTeX + bibtex on `paper/main.tex` |
| `/proofread [file]` | Grammar / typo / consistency review |
| `/review-r [file]` | R code quality review |
| `/validate-bib` | Cross-reference citations vs `paper/refs.bib` |
| `/commit [msg]` | Stage, commit, PR, merge (halts if score < 80) |
| `/lit-review [topic]` | Literature search + synthesis |
| `/research-ideation [topic]` | Research questions + strategies |
| `/interview-me [topic]` | Interactive research interview |
| `/review-paper [file]` | Manuscript review (single-pass / `--adversarial` / `--peer <journal>`) |
| `/respond-to-referees [report] [manuscript]` | R&R cross-reference + response draft |
| `/data-analysis [dataset]` | End-to-end R analysis |
| `/audit-reproducibility [paper]` | Enforce tolerance thresholds on paper ↔ code |
| `/seven-pass-review` | Seven-pass adversarial manuscript review |
| `/verify-claims [file]` | CoVe fact-check (forked verifier, fresh context) |
| `/checkpoint [topic]` | Save state snapshot before stop / handoff |
| `/preregister [--style ...]` | Draft a preregistration document |
| `/learn [skill-name]` | Extract discovery into persistent skill |
| `/context-status` | Show context usage and session health |
| `/deep-audit` | Repository-wide consistency audit |
| `/permission-check` | Diagnose permission layers |

---

## Stata Conventions (snapshot — full rule in `.claude/rules/stata-code-conventions.md`)

| Convention | Value |
|---|---|
| Binary | `/Applications/Stata/StataSE.app/Contents/MacOS/StataSE` |
| Version directive | `version 19` (in `_config.do`) |
| Project root | `$root = c(pwd)` (set in `00_run_all.do`); all paths derive from `$root` |
| Seed | `set seed $PROJECT_SEED` with `$PROJECT_SEED 20260510` (set once in `_config.do`) |
| Headless | `-e` (respects in-script log path) |
| Estimates | `estimates save "$tab/est_<name>.ster", replace` for every regression |
| Tables | `esttab` → `output/tables/<name>.tex`; AEA-style (no significance stars) |
| Figures | `graph export "$fig/<name>.pdf", replace` with explicit `width()` |

---

## Current Project State

| Component | Status |
|---|---|
| Workflow scaffolding | ✅ Adapted from `pedrohcgs/claude-code-my-workflow` 2026-05-10 |
| Stata pipeline skeleton | ✅ `scripts/stata/_config.do` + `00–06.do` placeholders |
| R pipeline (template, supplementary) | ✅ `scripts/R/00_run_all.R` + `01–05.R` placeholders |
| Paper LaTeX skeleton | ✅ `paper/main.tex` + 5 sections + `refs.bib` (16 pre-vetted refs) |
| Bibliography | 🔵 Seeded by Henrik (2026-04-30); needs DOI / page verification |
| Data: S&P 451 Research DC database | ✅ 23 SAS files at `data/raw` (symlink) |
| Data: ACFR (county financials) | ☐ TODO |
| Data: TRACE / MSRB EMMA muni bonds | ☐ TODO (later) |
| Data: NCSL state DC incentives | ☐ TODO |
| Data: Moody's / S&P 2026 ratings reports | ☐ TODO |
| First analysis: tabulate US owners/providers/clients + geography | ☐ Plan 2 (next) |
