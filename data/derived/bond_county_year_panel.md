# Bond County-Year Panel — County + Year FE (staggered TWFE)

**Date:** 2026-06-10. `scripts/python/63`. Within-county change in bond features when a DC arrives. treated_post = DC host AND year≥first_op_year; county FE + year FE; SEs clustered on county. Window 2008-2025; controls = never-DC-host.

Counties: treated 119, control 2,390.

| Outcome | Cut | β treated_post | SE | p | N |
|---|---|---:|---:|---:|---:|
| Spread (bps, −=cheaper) | ALL | **-4.967** | 6.638 | 0.454 | 19,293 |
| Spread (bps, −=cheaper) | clean_dc | **-19.369**** | 9.352 | 0.038 | 18,696 |
| Spread (bps, −=cheaper) | crypto | **+14.987** | 10.541 | 0.155 | 18,473 |
| log(1+par $M) issuance | ALL | **+0.000** | 0.000 | 0.230 | 45,162 |
| log(1+par $M) issuance | clean_dc | **+0.000** | 0.000 | 0.464 | 43,902 |
| log(1+par $M) issuance | crypto | **+0.000** | 0.000 | 0.675 | 43,920 |
| n deals | ALL | **-0.315**** | 0.155 | 0.041 | 45,162 |
| n deals | clean_dc | **-0.681**** | 0.291 | 0.019 | 43,902 |
| n deals | crypto | **+0.055** | 0.173 | 0.752 | 43,920 |
| P(issue this year) | ALL | **+0.016** | 0.028 | 0.567 | 45,162 |
| P(issue this year) | clean_dc | **+0.018** | 0.059 | 0.760 | 43,902 |
| P(issue this year) | crypto | **+0.022** | 0.037 | 0.557 | 43,920 |
| Any-rated par share | ALL | **-0.046**** | 0.022 | 0.033 | 21,530 |
| Any-rated par share | clean_dc | **-0.060*** | 0.035 | 0.092 | 20,896 |
| Any-rated par share | crypto | **-0.046** | 0.036 | 0.191 | 20,666 |
| Avg rating|rated (−=better) | ALL | **-0.187**** | 0.082 | 0.023 | 5,519 |
| Avg rating|rated (−=better) | clean_dc | **-0.265***** | 0.095 | 0.006 | 5,361 |
| Avg rating|rated (−=better) | crypto | **-0.033** | 0.162 | 0.838 | 5,261 |

## Event study — ALL treated (binned, ref −1; pre = parallel-trends test)
- **Spread (bps)**: -5:-18.30  -4:-2.32  -3:-14.85  -2:-5.07  +0:-8.11  +1:-17.45  +2:-13.31  +3:-29.13*  +4:-18.23  +5:-23.79*  (ref −1=0)
- **log(1+par)**: -5:+0.00  -4:+0.00  -3:+0.00*  -2:-0.00  +0:-0.00  +1:+0.00  +2:+0.00*  +3:-0.00  +4:+0.00*  +5:+0.00*  (ref −1=0)

## Reading
- County FE => identification is each county's bonds AFTER its DC vs BEFORE (and vs never-DC in same years).
- Spread − = cheaper borrowing; issuance/n_deals/P(issue) + = more borrowing; rating extensive + = more rated.
- Event-study pre-period (−5..−2) ≈ 0 => parallel trends; lags = dynamics. Staggered TWFE caveat -> Sun-Abraham/CS is the robustness.
