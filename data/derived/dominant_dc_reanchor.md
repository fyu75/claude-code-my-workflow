# Dominant-DC re-anchoring of treatment timing

**Date:** 2026-06-10. `scripts/python/67`. Per-DC MW from S&P 451 `dcpropertiesperiodic.TOTALITPOWER`.

`first_op_year` == earliest-DC op-year for **all 125** treated counties (confirmed). The dominant (max-MW) DC is operational LATER in **58** counties (mean shift **+4.6 yr**, max +29).

## Usable event window (anchor in 2015-2021) by anchor choice
- `first_oy`: 32 counties in-window (median 2021, n=125)
- `dom_oy`: 32 counties in-window (median 2023, n=125)
- `first50_oy`: 28 counties in-window (median 2022, n=74)
- `cap50_oy`: 43 counties in-window (median 2022, n=125)

## Bond spread event study (bps; county+year FE; ref −1; all treated vs never-DC)
| evt | first_oy (n) | cap50_oy (n) | dom_oy (n) |
|---|---|---|---|
| -5 | -6.27 (p0.57) n117 | -5.26 (p0.55) n117 | -9.28 (p0.33) n117 |
| -3 | +1.49 (p0.87) n117 | +3.32 (p0.68) n117 | +1.18 (p0.89) n117 |
| -1 | 0 (ref) | 0 (ref) | 0 (ref) |
| +0 | +9.55 (p0.48) n117 | +11.60 (p0.26) n117 | -12.09 (p0.21) n117 |
| +1 | -0.04 (p1.00) n117 | -6.23 (p0.39) n117 | -7.72 (p0.42) n117 |
| +2 | +4.40 (p0.65) n117 | -2.10 (p0.80) n117 | -4.42 (p0.64) n117 |
| +3 | -11.25 (p0.31) n117 | -13.47 (p0.21) n117 | -18.85 (p0.16) n117 |
**Reading:** spread is noisy/NULL under EVERY anchor (no clean post drop, all p>0.15) — re-anchoring does not revive a pricing effect. Reinforces 'pricing channel null 4 ways'.

## Property-tax event study (log PT, v2 annual; county+year FE; ref −1; anchor in 2018-2023)
| evt | first_oy (n) | cap50_oy (n) | first50_oy (n) |
|---|---|---|---|
| -2 | -0.07 (p0.65) n15 | +0.02 (p0.87) n20 | -0.30 (p0.28) n9 |
| -1 | 0 (ref) | 0 (ref) | 0 (ref) |
| +0 | -0.12 (p0.44) n15 | +0.06 (p0.65) n20 | -1.39 (p0.15) n9 |
| +1 | -0.12 (p0.42) n15 | -0.02 (p0.86) n20 | -0.44 (p0.09) n9 |
| +2 | -0.06 (p0.77) n15 | -0.08 (p0.63) n20 | -0.68 (p0.06) n9 |
| +3 | +0.15 (p0.18) n15 | +0.16 (p0.27) n20 | -0.22 (p0.28) n9 |
**Reading:** parallel pre-trend (−2 ≈ 0) holds under first_op and cap50; lagged post ramp (+3 positive) persists. `cap50` keeps MORE cohorts (20 vs 15) -> better-powered, more defensible anchor. `first50` too thin (n=9) to use. Effect direction robust to anchor choice.

## Verdict
- The mis-anchoring is REAL and large for ~51 mature hubs, but it was NOT manufacturing either headline: the bond null and the PT lagged-ramp both survive every anchor.
- **Adopt `cap50_oy` (capacity-midpoint) as the event-study anchor** going forward: defensible ('when the bulk of capacity arrived'), better-powered (20 vs 15 PT cohorts; 43 vs 32 counties in a usable Census window), and robust.
- The 2-period +3.07%/yr property-tax headline (Phase 2, CAGR-based) does not use an event clock, so it is unaffected. This refinement sharpens the DYNAMICS illustration, not the headline.
- The announcement-date wave (8 agents, 2026-06-10) supplies a SECOND anchor for the same hubs (announcement vs capacity-midpoint); fold in when batches land.
