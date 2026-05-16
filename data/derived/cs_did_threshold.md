# Callaway-Sant'Anna DiD — Threshold-restricted sample

*Run 2026-05-16. Source: `scripts/python/16_cs_did_threshold_restricted.py`.*

**Treatment**: counties where estimated DC contribution to county property tax ≥ **1.0%** (mid scenario, $50k/MW)
**# treated counties**: 125
**Control**: never-DC-host counties (2776)
**Panel window**: 2010–2025 (46,416 county-year cells)
**Estimator**: Callaway-Sant'Anna (2021) ATTgt, never-treated comparison

## Simple ATT (averaged across cohorts and event times)

| Outcome | ATT | SE | 95% CI |
|---|---:|---:|---|
| **log(par + 1)** | 0.1227 | 0.1490 | [-0.1693, 0.4147] |
| **log(n_deals + 1)** | -0.0037 | 0.0591 | [-0.1196, 0.1122] |
| **par-weighted spread (bps)** | -23.3542* | 12.2657 | [-47.3949, 0.6866] |

*Stars: \*\*\* p<0.01, \*\* p<0.05, \* p<0.10.*

## Event-study breakdown — average ATT by event-time bin

| Outcome | t=-3..-1 | t=0 | t=+1..+3 | t=+4..+7 | t≥+8 |
|---|---:|---:|---:|---:|---:|
| **log(par + 1)** | 0.0092 | -0.1347 | 0.0996 | -0.0845 | 0.7684 |
| **log(n_deals + 1)** | -0.0064 | -0.0812 | -0.0131 | -0.0556 | 0.1916 |
| **par-weighted spread (bps)** | 7.7565 | -8.0660 | -31.0008 | -17.7686 | -22.6219 |

Saved figure: `data/derived/figures/fig10_cs_threshold.png`

## 2015+ Calendar-time slice

Restrict the panel to **observation years 2015–2025** only (rather than event time).
This subset CS-ATT focuses on the AI-hyperscale era.

| Outcome | ATT (2015+) | SE | 95% CI | N |
|---|---:|---:|---|---:|
| **log(par + 1)** | -0.1552 | 0.1685 | [-0.4855, 0.1752] | 31,911 |
| **log(n_deals + 1)** | -0.0908 | 0.0576 | [-0.2038, 0.0221] | 31,911 |
| **par-weighted spread (bps)** | -22.6279 | 16.5905 | [-55.1453, 9.8896] | 11,290 |

## Comparison to v1 (full DC-host sample, no threshold)

| Outcome | v1 ATT (all DC-host) | v3 ATT (≥1% DC share) | Difference |
|---|---:|---:|---:|
| **log(par + 1)** | -0.0783 (0.065) | +0.1227 (0.149) | +0.2010 |
| **log(n_deals + 1)** | -0.1234 (0.028) | -0.0037 (0.059) | +0.1197 |
| **par-weighted spread (bps)** | -3.1700 (3.720) | -23.3542 (12.266) | -20.1842 |