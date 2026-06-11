# Deal-Level Rating DiD (robust spec)

**Date:** 2026-06-10. Bond RATING as outcome on the script-50 spec (county FE + state×year FE, cluster county) — the design that survived for spread. `scripts/python/51`.

**Sign:** rating level lower = better (Aaa=1); NEGATIVE coef on a rating-level outcome = credit IMPROVES. POSITIVE coef on any_rated_share / share_ig / share_aaa = more/better-rated.

## Sample
- Deals: **98,650** | post (treated×after-DC) 4,988; of those rated 967
- Treated (≥1% DC) 119, never-host 2498
- Overall any-rated par share (mean): 0.263

## Results — coefficient on treated_post

| Outcome (spec: county + state×year FE) | β | SE | p | N |
|---|---:|---:|---:|---:|
| Extensive: any-rated par share (all deals) | **-0.0717***** | 0.0171 | 0.0000 | 98,428 |
|   + log(amount) control | **-0.0739***** | 0.0172 | 0.0000 | 98,428 |
| Intensive: avg rating | rated (lower=better) | **-0.0028** | 0.0585 | 0.9616 | 25,680 |
| Share investment-grade (≥BBB-) | **-0.0717***** | 0.0171 | 0.0000 | 98,428 |
| Share AAA/Aaa | **-0.0397***** | 0.0113 | 0.0005 | 98,428 |
| Intensive rating, 2015+ issues | **-0.0778** | 0.0955 | 0.4156 | 6,016 |

*Stars: \*\*\* p<0.01, \*\* p<0.05, \* p<0.10.*

## Reading guide
- Compare to county-year CS (script 21): there, avg-rating ATT was +0.065 (ratings WORSEN, ns) on the same fragile design that gave the −23bps spread. This deal-level spec is the robust check.
- Extensive margin uses ALL deals (well-powered); intensive uses only rated deals (~20%, selected toward larger issues — interpret with care).
- A credit-quality story needs rating to IMPROVE (negative level coef) and/or the extensive / IG / AAA shares to RISE. A null here is consistent with the spread null: no pricing-relevant credit improvement detectable.
- Same TWFE staggered-timing caveat as script 50.
