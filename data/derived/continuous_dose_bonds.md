# Continuous-Dose Bond Panel (DC fiscal-share ratio as treatment magnitude)

**Date:** 2026-06-10. `scripts/python/65`. dose = dc_share_mid (DC tax / county property tax, %) × buildout-fraction; outcome ~ dose | county + year FE, cluster county. β = effect per +1 percentage-point of DC fiscal share. Tests dose-response (does the effect scale with DC fiscal size?).

| Outcome | Cut | β per pp-share | SE | p | N |
|---|---|---:|---:|---:|---:|
| Spread (bps/pp-share) | ALL | **+0.2638** | 0.2072 | 0.203 | 19,293 |
| Spread (bps/pp-share) | clean_dc | **+0.6509** | 0.5166 | 0.208 | 18,696 |
| Spread (bps/pp-share) | crypto | **+0.1524** | 0.2012 | 0.449 | 18,473 |
| log(1+par) | ALL | **+0.0000** | 0.0000 | 0.661 | 45,162 |
| log(1+par) | clean_dc | **+0.0000** | 0.0000 | 0.117 | 43,902 |
| log(1+par) | crypto | **-0.0000** | 0.0000 | 0.694 | 43,920 |
| n deals | ALL | **+0.0028***** | 0.0010 | 0.007 | 45,162 |
| n deals | clean_dc | **+0.0009** | 0.0044 | 0.844 | 43,902 |
| n deals | crypto | **+0.0029***** | 0.0008 | 0.000 | 43,920 |
| any-rated share | ALL | **-0.0004** | 0.0004 | 0.397 | 21,530 |
| any-rated share | clean_dc | **-0.0009** | 0.0017 | 0.580 | 20,896 |
| any-rated share | crypto | **-0.0003** | 0.0004 | 0.491 | 20,666 |
| avg rating|rated | ALL | **-0.0054** | 0.0061 | 0.373 | 5,519 |
| avg rating|rated | clean_dc | **+0.0015** | 0.0108 | 0.893 | 5,361 |
| avg rating|rated | crypto | **-0.0119***** | 0.0017 | 0.000 | 5,261 |

## Reading
- dose-response: a significant β means bond features scale with the DC's fiscal share — stronger mechanism evidence than a 0/1 dummy, and harder to explain as a spurious trend.
- Spread β<0 = bigger DC share -> tighter spreads. Rating-avg β<0 = better quality.
- CAVEAT: continuous-treatment DiD (de Chaisemartin–D'Haultfœuille) subtleties; dose timing still anchored to OPERATIONAL year (anticipation not yet captured — needs announcement dates).
