# Salience-result verification (script 76's mega/era cells)

**Date:** 2026-06-11. `scripts/python/77`. Primary-market spec = script 68; secondary = script 73.

## 1. Primary market — oil-drop + leave-one-out
| Variant | beta (bps) | p |
|---|---:|---:|
| mega 12 (script 76 cell) | -25.20 | 0.047 |
| drop 2 oil counties (n=10) | -32.45 | 0.000 |
| LOO drop Douglas County | -32.47 | 0.000 |
| LOO drop Fulton County | -32.51 | 0.000 |
| LOO drop Franklin County | -38.78 | 0.000 |
| LOO drop Crook County | -32.45 | 0.000 |
| LOO drop Washington County | -32.48 | 0.000 |
| LOO drop Berkeley County | -32.44 | 0.000 |
| LOO drop Milam County | -32.03 | 0.000 |
| LOO drop Navarro County | -30.22 | 0.002 |
| LOO drop Nueces County | -19.71 | 0.405 |
| LOO drop Grant County | -32.50 | 0.000 |
| mega-ex-oil x post-2023 | -30.63 | 0.000 |

## 2. Secondary market (MSRB, bond + year FE) — confirmation test
| Variant | beta (bps) | p | mega bonds |
|---|---:|---:|---:|
| mega-ex-oil, announced | +0.7 | 0.746 | 5,331 |
| mega-ex-oil x post-2023 | -0.8 | 0.624 | 5,331 |
| drop Nueces, announced | +10.9 | 0.049 | 3,704 |
| drop Nueces, x post-2023 | -0.8 | 0.699 | 3,704 |

## Conclusion
- Primary market: point estimate stable across oil-drop and LOO (-20 to -39 bps) but significance depends on Nueces TX (drop it: p=0.405) -> inference rests on one county.
- Secondary market: NO effect in the same cells (announced +0.7 p=0.75; x post-2023 -0.8 p=0.62; 5,331 outstanding bonds, well-powered). The same bonds do not reprice.
- CONCLUSION: the script-76 salience cells are NOT confirmed — primary-market-only, single-county-dependent inference, threshold-sensitive (>=300MW cut p=0.149). Same failure pattern as the colo -46.5. Record as: no confirmed effect for mega-announcement counties or the post-2022 era.
