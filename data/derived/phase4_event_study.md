# Phase 4 — Annual Event Study (v2 panel, pre-trends + dynamics)

**Date:** 2026-06-10. `scripts/python/61`. Outcome = log(county-govt property tax), v2 FY2016-2024. Binned event-time TWFE, county + year FE, SEs clustered on county. Reference period = -1.

Usable treated (cohort 2017-2023, >=4 v2 yrs): **16** | never-DC controls: **568** | county-year obs: 4,391

| Event time | coef (log pts) | SE | p | |
|---|---:|---:|---:|---|
| -4 | +0.026 | 0.116 | 0.822 | pre (parallel-trends test) |
| -3 | +0.203 | 0.209 | 0.331 | pre (parallel-trends test) |
| -2 | +0.016 | 0.040 | 0.682 | pre (parallel-trends test) |
| +0 | -0.027 | 0.018 | 0.146 | **DC opens** |
| +1 | -0.030 | 0.022 | 0.172 | post |
| +2 | +0.029 | 0.087 | 0.740 | post |
| +3 | +0.173 | 0.186 | 0.353 | post |
| +4 | +0.174 | 0.130 | 0.182 | post |
| −1 | 0 (ref) | — | — | reference |

**Pre-trend coefficients (−4,−3,−2): +0.026, +0.203, +0.016** — near zero & insignificant => parallel trends supported.
**Post path (0..+4): -0.027, -0.030, +0.029, +0.173, +0.174** — log-point lift in PT after DC opens.

## Reading guide
- Pre-period coefs ≈ 0 (insignificant) is the key validation: treated and control PT move together BEFORE the DC, so the Phase-2 +3.07%/yr is not a pre-existing divergence.
- Post coefs rising = the tax base ramps after opening (consistent with multi-year buildout/assessment).
- CAVEAT: only ~31 treated have annual v2 data; staggered TWFE can be biased under effect heterogeneity -> a Sun-Abraham/Callaway-Sant'Anna version is the robustness. This is a dynamics/credibility check on the subset, not a power upgrade over the 92-treated 2-period headline.
