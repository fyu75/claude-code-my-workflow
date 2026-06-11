# 2017 -> 2022 Census of Governments Growth (county-government scope)

**Date:** 2026-06-10. `scripts/python/53`. Full-universe Census 2022 (released Oct 2024) vs Census 2017, type=1 county-government scope — brackets the DC boom on Census-grade data.

**Parser validation vs trusted 2017 file:** property tax 100.0% / debt 100.0% within $10k -> **GATE PASS**.

## Coverage
- Counties in 2017: 3,025; in 2022: 3,020; in both: 3,014
- Treated (>=1% DC) with both-year property tax: 123 of 125

## Median 2017->2022 total growth (%), treated vs control

| Outcome | Treated median | Control median | Treated−Control |
|---|---:|---:|---:|
| Property tax | +23.4% | +20.1% | +3.3pp |
| Capital outlay | +90.3% | +53.0% | +37.4pp |
| LT debt o/s | -10.6% | -14.6% | +4.0pp |

*Median total growth over the 5-year window; CAGR columns also in the CSV.*

## Caveats
- County-government (type=1) scope only — consolidated city-counties (Denver, Honolulu) and independent cities are scoped per Census convention; cross-check separately.
- This is the GOLD-STANDARD endpoint to validate the ACFR-PDF and MuniSpot v2 2022 extractions against (next: triangulation audit).
