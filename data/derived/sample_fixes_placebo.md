# Sample fixes + metro placebo (referee-proofing)

**Date:** 2026-06-10. `scripts/python/69`. (A) control-pool purge of 137 tiny-DC hosts + phantom/cancelled treated drop (47121, 54047, 21127); headline robustness under BASELINE / PURGED / PURGED+PHANTOM. (B) placebo: 11 big-DC metro counties (fiscal share <1%) — fiscal mechanism off, predicted null.

- raw never pool 2,776 -> clean (no S&P DC of any size) **2,639**
- placebo metros: Los Angeles County CA, Santa Clara County CA, Cook County IL, Erie County NY, Summit County OH, Philadelphia County PA, Knox County TN, Bexar County TX, Dallas County TX, Denton County TX, Galveston County TX

## A1. Phase-2 PT headline (matched CAGR %/yr) under the fixes
| Variant | Cut | Mean | Median | N | t-p | Boot 95% CI |
|---|---|---:|---:|---:|---:|---:|
| BASELINE (script 60) | ALL | **+3.07***** | +1.34 | 88 | 0.007 | [+1.08,+5.37] |
| BASELINE (script 60) | clean_dc | **+1.87*** | +2.13 | 35 | 0.092 | [-0.18,+3.99] |
| BASELINE (script 60) | crypto | **+4.31*** | +0.97 | 35 | 0.093 | [-0.02,+9.55] |
| PURGED controls | ALL | **+3.30***** | +1.16 | 87 | 0.004 | [+1.32,+5.68] |
| PURGED controls | clean_dc | **+2.59**** | +2.11 | 34 | 0.032 | [+0.39,+4.86] |
| PURGED controls | crypto | **+4.26*** | +0.95 | 35 | 0.097 | [-0.01,+9.52] |
| PURGED + phantom drop | ALL | **+3.39***** | +1.16 | 85 | 0.004 | [+1.34,+5.84] |
| PURGED + phantom drop | clean_dc | **+2.59**** | +2.11 | 34 | 0.032 | [+0.38,+4.90] |
| PURGED + phantom drop | crypto | **+4.53*** | +0.95 | 33 | 0.096 | [-0.10,+10.20] |

## A2. Announcement bond DiD (clean_dc cut) — BASELINE vs PURGED+PHANTOM
| Outcome | BASELINE (raw never) | PURGED + phantom drop |
|---|---|---|
| Spread (bps, deal hedonic) | -2.20 (8.31) p=0.791 N=47,364 | -1.17 (8.50) p=0.890 N=41,409 |
| Rating ext (any-rated, deal) | -0.01 (0.02) p=0.375 N=64,845 | -0.02 (0.02) p=0.349 N=57,154 |
| Issuance P(any deal) (cy) | +0.03 (0.03) p=0.274 N=73,450 | +0.03 (0.03) p=0.277 N=69,888 |
| Issuance log(1+par) (cy) | +0.10 (0.11) p=0.353 N=73,450 | +0.10 (0.11) p=0.366 N=69,888 |
| Spread par-wtd (cy) | -5.49 (6.94) p=0.429 N=27,242 | -5.47 (6.96) p=0.432 N=24,963 |
| Maturity par-wtd yrs (cy) | -0.31** (0.15) p=0.042 N=30,442 | -0.31** (0.15) p=0.045 N=27,991 |

## B. Metro placebo — big DC, negligible fiscal share (predicted NULL)
Anchor for BOTH groups = first >=50MW DC operational year (metros have no announcement dates; symmetric by construction). Controls = clean never pool. Caveat: 11 placebo clusters.
| Outcome | Treated big-DC counties (n=72) | Placebo metros (n=11) |
|---|---|---|
| Spread (bps, deal hedonic) | -1.14 (8.87) p=0.898 N=42,193 | -3.42 (5.56) p=0.539 N=41,442 |
| Rating ext (any-rated, deal) | -0.03* (0.02) p=0.079 N=58,345 | -0.01 (0.03) p=0.633 N=57,865 |
| Issuance P(any deal) (cy) | -0.03 (0.03) p=0.353 N=70,486 | +0.03 (0.03) p=0.234 N=68,822 |
| Issuance log(1+par) (cy) | -0.07 (0.09) p=0.447 N=70,486 | +0.13 (0.20) p=0.517 N=68,822 |
| Spread par-wtd (cy) | +9.01 (7.82) p=0.249 N=25,204 | -10.70 (9.02) p=0.236 N=24,310 |
| Maturity par-wtd yrs (cy) | -0.36*** (0.12) p=0.003 N=28,240 | -1.00*** (0.12) p=0.000 N=27,292 |

## Reading
- **A1:** the +3.07%/yr PT headline and clean/crypto cuts should move only trivially under the purge (contaminated controls were all <50MW, <0.3% fiscal share) and strengthen slightly with phantoms out.
- **A2:** bond results stable under both fixes -> contamination was not driving any null or any crypto effect.
- **B:** if metros show no spread/issuance/rating response while treated big-DC counties show the same (null clean / crypto-widening) pattern, the bond findings are tied to the FISCAL channel, not generic 'tech investment arrived'. Metro nulls + strong PT first stage = the mechanism story.
