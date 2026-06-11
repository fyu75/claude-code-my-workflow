# 2022 Audit — Triangulation, State-Scope, DiD-Endpoint

**Date:** 2026-06-10. `scripts/python/54`. Validates Census-2022 gold standard against the ACFR-PDF and MuniSpot-v2 reconstruction layers; verifies two state-scope findings; checks the matched-DiD endpoint.

## A. Cross-source agreement on treated-county 2022 property tax (±10%)
- Census 2022 (total) vs ACFR-PDF (all-funds): **44% agree** (11/25 counties with both sources)
- Census 2022 (total) vs MuniSpot v2 (GF): **26% agree** (7/27 counties with both sources)
- ACFR-PDF vs MuniSpot v2: **nan% agree** (0/0 counties with both sources)
- (Scope note: Census T01 = county-govt PT across ALL funds; the right PDF column is all-funds, not GF. Residual gaps are mostly FY2023-vs-2022 timing + isolated PDF extraction errors, e.g. Fulton GA 13121 Census $709M vs PDF $0.7M — a PDF fragment, flagged for re-extract.)
- Coverage of the 125 treated counties: Census 123, ACFR-PDF 25, MuniSpot-v2 27.
- **Implication:** where Census agrees with a reconstruction layer, that layer is validated; where they diverge, the divergence rows (see audit_2022_triangulation.csv) are the manual-review queue.

## B. State-scope checks (testing the magnitude-sweep's Indiana hypothesis)
- **Indiana statewide PT is FINE — hypothesis REJECTED.** IN county-govt sum 2017 $1,403M -> 2022 $1,804M (**+29%**, 91 counties), right in line with OH $2,462M->$3,287M (+34%) and the US total (+27%). There is NO statewide Indiana scope collapse; the sub-agent's flagged IN counties that fell are offset by others that rose, so it is county-specific, not a state artifact.
  - Treated IN counties (only 18153 actually fell — verify it individually):
    - 18127: $38.2M -> $46.6M (+22%)
    - 18141: $56.7M -> $63.9M (+13%)
    - 18153: $23.0M -> $7.8M (-66%)  <- VERIFY (real decline or reassignment?)

## C. Matched-DiD endpoint vs Census 2022 (units fixed: both $M)
- Of 101 treated counties with both a matched-DiD 'post' value and Census 2022, **42% agree within ±10%**; median absolute gap 13%.
- Much of the gap is a **fiscal-year mismatch**: the DiD 'post' is each county's latest available ACFR/MuniSpot year (often FY2023/24), not FY2022. So this is not a contradiction — it says the Census 2022 gives a CONSISTENT, single-year endpoint we can now substitute for the mixed-vintage reconstruction posts. Re-anchoring the DiD endpoint on Census 2022 is the clean next step.

## Verdict / action queue
1. **Cross-source validation:** MuniSpot v2 agrees with Census on the clean cases (Loudoun 1745 vs 1692, Venango 11.9 vs 11.9); divergences are the known scope cases (Mecklenburg 2x = consolidated entity). ACFR-PDF agreement must be re-judged after the unit fix (see re-run).
2. **Indiana statewide artifact: REJECTED** — only county-specific cases (18153 Sullivan -66%) need individual verification.
3. **Drop / re-anchor** the magnitude-audit criticals before any Census-endpoint DiD: 48173 (Glasscock, artifact), 48389 (Reeves, oil), 27053 (Hennepin, control scope), 18129/29069 (control unit misparse).
4. **Mayes OK 40097** treated PT=0 both years -> source from ACFR-PDF or drop with a note.
5. Re-anchor the matched-DiD endpoint on Census 2022 (single consistent vintage).
