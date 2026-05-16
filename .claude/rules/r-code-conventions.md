---
paths:
  - "**/*.R"
  - "scripts/**/*.R"
---

# R Code Standards

**Standard:** Senior Principal Data Engineer + PhD researcher quality.

R is **supplementary** in this project (Stata is primary; see `.claude/rules/stata-code-conventions.md`). R scripts handle robustness checks, additional figures, simulations, and any analysis that doesn't fit cleanly in Stata. They MUST read from `data/derived/<topic>.dta` (Stata's clean output) — never redefine cleaning logic independently.

---

## 1. Reproducibility

- `set.seed(20260510)` called ONCE at the top of `00_run_all.R` (matches `$PROJECT_SEED` in Stata's `_config.do`; INV-3)
- All packages loaded at top via `library()` (not `require()`)
- All paths via `here::here(...)` — no absolute paths, no `setwd()` (INV-2)
- `dir.create(..., recursive = TRUE)` for output directories

## 2. Function Design

- `snake_case` naming, verb-noun pattern
- Roxygen-style documentation
- Default parameters, no magic numbers
- Named return values (lists or tibbles)

## 3. Domain Correctness

For dc-muni specifically — see `.claude/rules/knowledge-base-template.md` for the mechanism map and notation registry. Headline pitfalls:

- **Read from `data/derived/`, not `data/raw/`.** R must not re-do cleaning that Stata already did.
- **Match Stata's cluster level.** If `04_analyze.do` clusters at county, the R robustness must too.
- **Check estimator parity.** `feols(y ~ x | id, cluster = ~id)` and `xtreg, fe vce(cluster id)` may differ in df adjustment — document if you see a difference.
- **Sample size match.** `nrow(df)` in R must equal the N in Stata's regression for the same specification, before you trust the coefficient comparison.

## 4. Visual Identity

```r
# --- Project palette (neutral / publication-ready) ---
primary_navy   <- "#1f3a5f"   # main color for treated / focal lines
accent_coral   <- "#c8553d"   # contrast / control / "bad" outcomes
neutral_gray   <- "#525252"
positive_green <- "#15803d"
negative_red   <- "#b91c1c"
```

### Custom Theme

```r
theme_dcmuni <- function(base_size = 11) {
  theme_minimal(base_size = base_size) +
    theme(
      plot.title    = element_text(face = "bold", color = primary_navy),
      legend.position = "bottom",
      panel.grid.minor = element_blank()
    )
}
```

### Figure Dimensions for the Paper

```r
ggsave(filepath, width = 6.5, height = 4.0, units = "in")
```

(Standard single-column finance-paper figure. Use `bg = "white"` since the paper uses a white background — no transparent-bg requirement now that we're not on slides.)

## 5. RDS Data Pattern

Heavy computations saved as RDS so subsequent scripts (and `/audit-reproducibility`) can pick them up without rerunning.

```r
saveRDS(result, here::here("scripts", "R", "_outputs", "descriptive_name.rds"))
```

## 6. Common Pitfalls (project-specific)

| Pitfall | Impact | Prevention |
|---------|--------|------------|
| Hardcoded path | Breaks on co-author's machine | Always `here::here()` |
| Re-cleaning data inside R | Drift from Stata's `data/derived/` | Read from `data/derived/` only; if extension needed, write to `data/derived/_R_aux/` |
| `feols` vs `xtreg` SE mismatch | Different cluster df | Document the difference; pick one consistently |
| `tidyverse::filter` on factor | Silent NA when factor level is unused | Use `droplevels()` after subsetting |
| `na.rm = TRUE` default | Hides missingness in summary stats | Always specify explicitly |

## 7. Line Length & Mathematical Exceptions

Standard: keep lines ≤ 100 characters.

Exception: mathematical formulas may exceed 100 chars when (a) breaking would harm readability of an influence function / matrix op / formula matching a paper equation, AND (b) an inline comment explains the operation, AND (c) the line lives in a numerically intensive section (simulation loops, estimation routines).

## 8. Numerical Discipline

See [`r-reviewer.md`](../agents/r-reviewer.md) Category 11 for the full checklist. Headline rules:

- **No float equality.** Never use `==` on doubles. Use `all.equal()` or `abs(a - b) < tol`.
- **CDF clamping** to an OPEN interval. Exact 0 or 1 passed to `qnorm()` produces `±Inf`. Project epsilon: `eps <- 1e-12; p <- pmin(1 - eps, pmax(eps, p))`.
- **Integer literals for counts.** `nrow <- 1000L` (not `1000`).
- **Pre-allocate vectors** before loops (`numeric(n)`, `vector("list", n)`).
- **Deterministic bootstrap seeding.** Set seed before the bootstrap; per-replicate seeds as `seed_base + b`.
- **Explicit `na.rm = TRUE/FALSE`.** Never rely on defaults.
- **No `T` / `F`.** They're variables, not constants — write `TRUE` / `FALSE`.

## 9. Code Quality Checklist

```
[ ] Packages at top via library()
[ ] set.seed(20260510) once at top of 00_run_all.R (INV-3)
[ ] All paths via here::here() (INV-2)
[ ] Reads from data/derived/ — does NOT re-clean from data/raw/
[ ] Functions documented (Roxygen)
[ ] Figures: explicit dimensions; theme_dcmuni applied
[ ] saveRDS for every persistent computed object (INV-8)
[ ] Cluster level matches Stata's (INV-7) — documented in comment
[ ] Comments explain WHY not WHAT
[ ] Numerical discipline: no float ==, CDF clamping with eps, pre-allocated vectors
```
