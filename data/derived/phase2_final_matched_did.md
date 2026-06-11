# Phase 2 — Final Matched PT DiD (CAGR, finalized treated foundation)

**Date:** 2026-06-10. `scripts/python/60`. Outcome = annualized property-tax CAGR (%/yr). Treated = finalized scope-consistent PT (Phase 1, gold-verified where available); controls = full clean Census never-DC-host universe; 1:3 caliper match. Matched-pair effect vs matched controls.

Treated operating-by-2022 w/ final PT: **92** | control pool: **2,641** | pairs: 259

| Cut | Mean effect (%/yr) | Median | N treated | t / Wilcoxon p | Boot 95% CI |
|---|---:|---:|---:|---:|---:|
| ALL (operating by 2022) | **+3.07***** | +1.34 | 88 | t=0.007/W=0.001 | [+1.08,+5.37] |
| Clean hyperscale/colo | **+1.87*** | +2.13 | 35 | t=0.092/W=0.046 | [-0.18,+3.99] |
| Crypto-mining | **+4.31*** | +0.97 | 35 | t=0.093/W=0.062 | [-0.02,+9.55] |
| Mixed | **+3.00**** | +1.17 | 18 | t=0.039/W=0.024 | [+0.63,+5.65] |
| Clean + Mixed (non-pure-crypto) | **+2.25***** | +1.52 | 53 | t=0.010/W=0.004 | [+0.67,+3.93] |
| ALL, oil-confound dropped | **+1.72**** | +1.16 | 83 | t=0.020/W=0.003 | [+0.31,+3.12] |
| Clean, oil-confound dropped | **+1.87*** | +2.13 | 35 | t=0.092/W=0.046 | [-0.21,+4.04] |

*Stars: \*\*\* p<.01, \*\* p<.05, \* p<.10. Effect = treated CAGR − mean matched-control CAGR.*

## Reading guide
- Hypothesis (memo §6): clean hyperscale/colo DCs raise PT growth; crypto miners barely beat benchmark.
- vs raw medians (clean +5.6 / crypto +3.8 / control bench ~3.4 %/yr): the matched effect nets out region/size.
- N is small per cut (clean ~39, crypto ~35) -> the 2-period design is power-limited; the event-study (Phase 4) is the power fix. Report point estimates + CIs, not just stars.
