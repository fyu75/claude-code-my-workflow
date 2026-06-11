# Announcement-Timed Event Study (anticipation test)

**Date:** 2026-06-10. `scripts/python/66`. DC announcement years (6-agent wave) -> announcement→operational lead, and bond-spread event study RE-TIMED to announcement.

## Coverage: 119 counties | confidence H=74 M=32 L=13
## Announcement → Operational LEAD (the anticipation window)
- Mean lead **0.3 yrs**, median **1 yrs** (H+M, n=106)
- lead distribution: -1y:15, 0y:24, 1y:38, 2y:15, 3y:7, 4y:5, 5y:1, 7y:1
- clean_dc mean lead -0.2y vs crypto 0.8y (hyperscale plans further ahead than crypto)

## Spread event study RE-TIMED to ANNOUNCEMENT (county+year FE, bps; ref −1)
| event time vs ANNOUNCE | coef (bps) | p | |
|---|---:|---:|---|
| -4 | -11.01 | 0.295 | pre-announcement (placebo) |
| -3 | -7.45 | 0.559 | pre-announcement (placebo) |
| -2 | -10.28 | 0.388 | pre-announcement (placebo) |
| +0 | +8.66 | 0.451 | **announced** |
| +1 | -13.07 | 0.348 | post-announcement |
| +2 | -5.15 | 0.710 | post-announcement |
| +3 | -19.41 | 0.145 | post-announcement |
| +4 | -21.29** | 0.048 | post-announcement |
| −1 | 0 (ref) | — | reference |

## Reading
- If spreads are FLAT pre-announcement and FALL after announcement (0,+1,+2 negative) -> ANTICIPATION confirmed: the market reprices at announcement, which the operational-dated specs mistimed as a 'pre-trend'.
- If pre-announcement is also negative/noisy -> still a level/selection difference, not anticipation.
- Mean lead 1yrs means the operational-dated event study's 'year −1' ≈ this study's 'year 0' (announcement).
- LOW-confidence counties dropped; small crypto miners w/o press releases have unreliable announce timing.
