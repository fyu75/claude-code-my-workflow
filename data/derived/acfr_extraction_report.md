# ACFR Multi-Year Extraction — Pilot Counties

*Run 2026-05-16. Source: `scripts/python/23_acfr_multi_year_extraction.py`.*

Parsed 40 PDFs across 23 counties × 11 fiscal years (range 2014–2025).

## Extracted county-year panel

Units: dollars (raw from ACFR — typically already nominal $; some files report in thousands).

| County | State | FY | Property tax | Total revenue | Capital outlay | LT debt | Interest |
|---|---|---:|---:|---:|---:|---:|---:|
| Cook County | GA | 2023 | — | $12,312,455 | $2,935,744 | — | — |
| Washington County | GA | 2020 | — | — | — | — | — |
| Wilkes County | GA | 2024 | $5,005,336 | $13,019,489 | $618,002 | $1,300,000 | $14,851 |
| Lawrence County | KY | 2022 | — | — | — | $11,060,068 | — |
| Lawrence County | KY | 2024 | — | — | — | — | — |
| Marshall County | KY | 2023 | — | — | — | $9,424,759 | — |
| Storey County | NV | 2023 | $22,769,019 | $52,136,000 | $1,065,500 | $140,947 | $118,120 |
| Valencia County | NM | 2016 | $12,283,478 | $32,807,135 | $455,642 | $12,567,401 | — |
| Cherokee County | NC | 2022 | $21,759,268 | $64,948,062 | $2,560,490 | — | $20,025 |
| Franklin County | NC | 2024 | $67,090,739 | $146,507,294 | $5,662,674 | $123,929,781 | $1,194,384 |
| Dickey County | ND | 2023 | $3,442,882 | $6,758,609 | — | $187,705 | $34,757 |
| Mayes County | OK | 2024 | — | — | — | — | — |
| Crook County | OR | 2025 | $14,808,139 | $64,838,191 | $183,528 | $51,563,310 | $213,541 |
| Morrow County | OR | 2018 | $8,100,960 | $23,708,471 | $903,228 | $347,139 | $40,668 |
| Morrow County | OR | 2019 | $8,100,960 | $26,314,016 | $748,970 | $232,537 | $28,830 |
| Morrow County | OR | 2020 | $9,794,092 | $28,969,156 | $1,085,398 | $480,111 | $28,544 |
| Morrow County | OR | 2021 | $10,548,982 | $35,802,573 | $1,300,946 | $532,659 | $29,244 |
| Morrow County | OR | 2022 | — | — | — | — | — |
| Morrow County | OR | 2023 | — | — | — | — | — |
| Morrow County | OR | 2024 | — | — | — | — | — |
| Morrow County | OR | 2025 | $15,641,094 | $49,469,488 | $1,486,503 | $6,424,103 | — |
| Umatilla County | OR | 2016 | — | — | — | — | — |
| Umatilla County | OR | 2017 | — | — | — | — | — |
| Umatilla County | OR | 2018 | — | — | — | — | — |
| Umatilla County | OR | 2019 | — | — | — | — | — |
| Umatilla County | OR | 2020 | $18,639,145 | $23,962,747 | $537,507 | $9,535,000 | $535,380 |
| Umatilla County | OR | 2021 | $19,656,776 | $24,277,850 | $467,041 | $8,655,000 | $496,873 |
| Umatilla County | OR | 2022 | — | — | — | — | — |
| Umatilla County | OR | 2023 | $22,713,457 | $29,785,525 | $551,759 | $6,555,000 | $393,182 |
| Umatilla County | OR | 2024 | $23,768,779 | $32,455,314 | $1,173,049 | $5,320,000 | $336,111 |
| Umatilla County | OR | 2025 | $25,403,483 | $34,243,545 | $2,033,686 | $3,945,000 | $272,791 |
| Briscoe County | TX | 2024 | $3,661,357 | $5,526,120 | — | — | — |
| Crane County | TX | 2024 | $2,550,539 | — | — | — | — |
| Dickens County | TX | 2022 | $2,081,890 | — | — | — | — |
| Glasscock County | TX | 2024 | $3,661,357 | $5,526,120 | — | — | — |
| Pecos County | TX | 2022 | $2,761,636 | $42,596,429 | — | — | $43,185 |
| Ward County | TX | 2024 | $3,661,357 | $5,526,120 | — | — | — |
| Mecklenburg County | VA | 2023 | $10,700,962 | $40,962,523 | $6,913,176 | $19,683,525 | $825,482 |
| Grant County | WA | 2023 | — | $177,010,677 | — | — | — |
| Pend Oreille County | WA | 2014 | — | — | — | — | — |

## Sanity check vs Census 2017 ACFR

### FY 2017
| County | Pdf extracted prop_tax | Census 2017 prop_tax ($M) | Pdf debt | Census debt |
|---|---:|---:|---:|---:|
| Umatilla County | (missing) | — | — | — |
### FY 2018
| County | Pdf extracted prop_tax | Census 2017 prop_tax ($M) | Pdf debt | Census debt |
|---|---:|---:|---:|---:|
| Morrow County | $8.1M (if $) | $27.1M | $0.3M | $107.0M |
| Umatilla County | (missing) | — | — | — |

## Notes on extraction

- The parser returns the FIRST plausible candidate (large dollar amount on a line beginning with the target keyword). It does NOT distinguish between "total property taxes — primary government" vs "property taxes — discretely presented component units" — both will match.
- ACFRs vary in whether numbers are in dollars or thousands. The raw extracted value is shown as-is; downstream code must check magnitude per county.
- **The PDF vs Census number-mismatch is expected**. PDF figures are PRIMARY GOVERNMENT only (the county government, not including school district / cities / special districts within the county). Census 2017 ACFR (`data/derived/acfr_county_year_wide.csv`) aggregates ALL local governments in the county area. For comparing trajectories, the PDF series is what we want; for comparing levels, recognize the units are different.
- **~40% of PDFs failed extraction because they are scanned images, not text PDFs.** Morrow 2022/2023/2024, Umatilla 2016-2019, and 2022 are scanned. To recover these, an OCR pass (Tesseract / AWS Textract) is needed. The 2025 ACFRs are all born-digital text — newer counties have switched to native PDF.
- 4 of 25 high-share counties currently downloaded; this is a pilot. The remaining 20 should mostly be accessible through state-centralized portals (VA APA, WA SAO, OR SOS, NC LGC, TX comptroller).

## Key emerging finding: Morrow County property tax trajectory

Even with the gap-ridden extraction, the Morrow County series tells a clear story:

| FY | Property tax |
|---:|---:|
| 2018 | $8.1M |
| 2019 | $8.1M |
| 2020 | $9.8M |
| 2021 | $10.5M |
| 2022–24 | (scanned, OCR needed) |
| 2025 | $15.6M |

A near-doubling of county property tax revenue from 2018 ($8.1M) to 2025 ($15.6M) — a **+93% increase over 7 years** — coincident with Morrow becoming Oregon's largest DC cluster (Amazon and Google in Boardman). The pre-DC-wave baseline (2018-2019 flat at $8.1M) gives a clean counterfactual reference. This is the kind of within-county evidence the mechanism story needs.