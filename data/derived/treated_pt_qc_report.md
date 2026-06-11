# Phase 1 — Treated PT Triangulation (on-disk sources, no agents)

**Date:** 2026-06-10. `scripts/python/59`. Census primary; 95-county hand-verified spine as QC + gap-fill; ACFR-PDF fallback. Validation = Census 2017 ($M) vs verified baseline (FY2017 all-funds).

## Coverage
- Treated universe: **125**; PT both years final: **124** (gaps filled: 1 remaining).
## Census ↔ verified-spine validation (the free QC)
- Overlap with gold hand-checks: **40** treated; **29 agree within ±10% (72%)**.
- **11 disagree >10%** — review candidates (Census may carry a residual scope/collector error):

| County | ST | Census 2017 ($M) | Verified 2017 ($M) | % diff | note |
|---|---|---:|---:|---:|---|
| Laramie County | WY | 27.3 | 13.3 | 106% | Cheyenne/Microsoft. COUNTY-ONLY govwide PT (Census $27.28M = ALL overl |
| Loudon County | TN | 27.8 | 15.4 | 81% | TN Schedule J-5/K-6 Current Property Tax, all gov funds, COUNTY-ONLY ( |
| Franklin County | NC | 16.7 | 46.8 | 64% | NC LGC/Treasurer 10yr table + FY23 ACFR Total Gov Funds (ad valorem).  |
| Polk County | IA | 209.8 | 149.2 | 41% | CONFLICT resolved: v2 ($149.2M) RIGHT, Census $209.8M OVER by 41% (IA  |
| Nueces County | TX | 108.9 | 80.2 | 36% | CONFLICT resolved: v2 ($80.2M) RIGHT, Census $108.9M OVER by 36% (Nuec |
| Scott County | TN | 5.0 | 3.9 | 28% | TN Exhibit J-5/J-6 Current Property Tax, COUNTY-ONLY (excl school $1.6 |
| Dallas County | IA | 26.5 | 22.3 | 19% | CONFLICT resolved: v2 ($22.3M) RIGHT, Census $26.5M OVER (+19%; IA cou |
| Jackson County | GA | 27.6 | 23.3 | 18% | GA govwide (Jefferson, I-85 DC corridor). Census $27.62M was +18% HIGH |
| Morrow County | OR | 7.6 | 8.7 | 13% | OR no sales tax; Note-14 cash basis Total Gov Funds. AWS/Boardman DCs  |
| McDowell County | WV | 4.4 | 4.0 | 11% | WV SAO Chief Inspector. Coal county; PT 100% in GF. DECLINE -4.6% over |
| Wilkes County | GA | 4.4 | 5.0 | 10% | GA govwide Statement of Activities. FLAT/slight decline despite dc_sha |

## Reading guide
- 'validated_ok' counties: Census 2017 confirmed by an independent hand-check -> locked.
- 'FLAG_disagree': decide case-by-case; per 'Census unless proven wrong', keep Census unless the verified note proves a scope error (e.g., GA govwide, collector-state, TN school-levy).
- Gaps (Silver Bow MT, Mayes OK) filled from verified/PDF — see src_*_final.
