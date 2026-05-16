# Corporate Investment and Municipality Finances: Evidence from Data Centers

**Authors:** Henrik Cronqvist, Rui Dai, Mitch Warachka, Frank Yu (CEIBS)
**Status:** In progress (initialized 2026-05-10)

> **Working hypothesis.** Data centers represent the largest corporate-investment shock in modern U.S. public finance — projected to reach roughly one-fifth of U.S. capex in 2026 — yet the channel runs almost entirely through property and personal-property taxes rather than wage income, because data centers employ very few workers. This project estimates the elasticity of municipal tax collection to data-center investment and traces the response across muni capex, debt, ratings, and bond yields. Identification follows the winner-vs-loser county design of Greenstone, Hornbeck, and Moretti (2010, JPE).

## Repository layout

```
datacenter2/
├── CLAUDE.md                    # workflow conventions, commands, project state
├── MEMORY.md                    # accumulated [LEARN] entries across sessions
├── data/                        # raw symlink + intermediate + derived + external
├── scripts/
│   ├── stata/                   # primary analysis (numbered .do files)
│   └── R/                       # supplementary analysis
├── paper/                       # main.tex + sections/ + refs.bib
├── output/                      # tables/ and figures/ (consumed by paper/main.tex)
├── master_supporting_docs/      # related papers, case studies, industry reports
├── notes/                       # team notes from Henrik & Mitch
├── explorations/                # research sandbox
├── quality_reports/             # plans, session logs, merge reports
└── .claude/                     # rules, skills, agents, hooks
```

## Quick setup

```bash
# 1. Clone and validate
git clone <repo-url> datacenter2
cd datacenter2
./scripts/validate-setup.sh

# 2. Create the data symlink (per-machine; gitignored)
ln -sfn /path/to/your/datacenter/raw data/raw

# 3. Run the Stata pipeline (placeholder; populated by Plan 2)
/Applications/Stata/StataSE.app/Contents/MacOS/StataSE -e do scripts/stata/00_run_all.do

# 4. Compile the paper skeleton
cd paper && \
  xelatex -interaction=nonstopmode main.tex && \
  bibtex main && \
  xelatex -interaction=nonstopmode main.tex && \
  xelatex -interaction=nonstopmode main.tex
```

## Data

| Source | Status | Use |
|---|---|---|
| S&P 451 Research Data Center Database | ✅ Have (23 SAS7BDAT files) | DC properties, ownership, providers, clients, MW capacity, geography |
| County ACFRs | ☐ TODO | Muni revenue / expenditure / debt by year |
| TRACE / MSRB EMMA | ☐ TODO | Muni bond trade-level data |
| NCSL state DC tax incentives | ☐ TODO | Treatment-intensity variation |
| Moody's 2026 DC credit-risk hub | ☐ TODO | Institutional ratings perspective |
| S&P Global Ratings 2026 DC piece | ☐ TODO | Institutional ratings perspective |

## Tools

- **Stata SE 19.0** — primary analysis (binary at `/Applications/Stata/StataSE.app/Contents/MacOS/StataSE`)
- **R 4.x** — supplementary analysis (robustness, additional figures, simulations)
- **XeLaTeX** — paper compile (`paper/main.tex`)
- **MS Word (via pandoc)** — only when needed for non-technical co-authors

## Workflow

This repo uses an adapted version of the [pedrohcgs/claude-code-my-workflow](https://github.com/pedrohcgs/claude-code-my-workflow) academic Claude Code template. The original template README is preserved at [`README_TEMPLATE.md`](README_TEMPLATE.md) for reference.

Workflow conventions live in [`CLAUDE.md`](CLAUDE.md) (top-level), [`.claude/rules/`](.claude/rules/) (path-scoped), and [`.claude/WORKFLOW_QUICK_REF.md`](.claude/WORKFLOW_QUICK_REF.md) (one-page cheat sheet).

## License

Code: MIT (per the upstream template). Data and manuscript drafts are not for redistribution outside the author team.
