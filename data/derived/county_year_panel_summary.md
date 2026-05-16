# County-Year Panel — Coverage and Power Diagnostics

*Built 2026-05-16. Source: `scripts/python/05_build_county_year_panel.py`.*

## Panel dimensions
- **Counties**: 3,143 (50 states + DC, all US)
- **Years**: 2000–2025 (26 years)
- **County-year cells**: 81,718
- **DC-host counties** (≥1 DC opened 2000–2025 or earlier): 367

## Treatment exposure
- Treated county-year cells (post-first-DC, inclusive): 4,621 (5.7%)
- Pre-treatment cells for DC-host counties: 4,921

## SDC issuance coverage
- County-year cells with ≥1 SDC deal: 37,177 (45.5%)
- Counties with any SDC deal 2000–2025: 2,858 / 3,143 (90.9%)
- **DC-host counties with ≥1 SDC deal**: 360 / 367 (98.1%) ← critical
- Total deals in panel (resolved to FIPS): 188,307
- Deals in DC-host counties: 99,637 (52.9%)

## DC-host coverage by entry cohort
| First-DC year | # counties first treated |
|---|---:|
| 2000 | 30 |
| 2001 | 16 |
| 2002 | 9 |
| 2003 | 9 |
| 2004 | 3 |
| 2005 | 4 |
| 2006 | 12 |
| 2007 | 1 |
| 2008 | 16 |
| 2009 | 4 |
| 2010 | 13 |
| 2011 | 19 |
| 2012 | 7 |
| 2013 | 55 |
| 2014 | 17 |
| 2015 | 13 |
| 2016 | 5 |
| 2017 | 6 |
| 2018 | 6 |
| 2019 | 12 |
| 2020 | 4 |
| 2021 | 21 |
| 2022 | 31 |
| 2023 | 19 |
| 2024 | 19 |
| 2025 | 16 |

## Top 20 DC counties — issuance summary 2000-2025
| FIPS | County | State | #DC | 1st DC yr | # deals (2000-25) | par ($B) | mean par-wtd YTM |
|---|---|---|---:|---:|---:|---:|---:|
| 51107 | Loudoun County | VA | 206 | 2000 | 99 | $6.8 | 20.16% |
| 04013 | Maricopa County | AZ | 83 | 2001 | 1130 | $61.3 | 17.91% |
| 06085 | Santa Clara County | CA | 74 | 2000 | 798 | $40.0 | 21.49% |
| 51153 | Prince William County | VA | 72 | 2003 | 41 | $1.4 | 18.26% |
| 48113 | Dallas County | TX | 65 | 2000 | 1109 | $49.5 | 20.89% |
| 17031 | Cook County | IL | 57 | 2000 | 2668 | $99.6 | 22.02% |
| 39049 | Franklin County | OH | 31 | 2001 | 607 | $19.2 | 19.43% |
| 06037 | Los Angeles County | CA | 31 | 2000 | 2062 | $225.6 | 16.55% |
| 19153 | Polk County | IA | 30 | 2013 | 686 | $8.6 | 14.57% |
| 13121 | Fulton County | GA | 30 | 2001 | 192 | $21.4 | 15.74% |
| 53025 | Grant County | WA | 30 | 2008 | 77 | $3.2 | 21.65% |
| 41067 | Washington County | OR | 28 | 2002 | 127 | $5.8 | 18.79% |
| 51059 | Fairfax County | VA | 27 | 2001 | 119 | $13.3 | 20.24% |
| 41049 | Morrow County | OR | 25 | 2011 | 6 | $0.1 | 18.70% |
| 51117 | Mecklenburg County | VA | 25 | 2012 | 0 | $0.0 | nan% |
| 48029 | Bexar County | TX | 22 | 2000 | 630 | $52.2 | 24.06% |
| 37119 | Mecklenburg County | NC | 21 | 2000 | 204 | $17.9 | 19.60% |
| 42003 | Allegheny County | PA | 21 | 2013 | 973 | $20.9 | 21.08% |
| 39089 | Licking County | OH | 20 | 2016 | 158 | $1.2 | 17.47% |
| 41059 | Umatilla County | OR | 20 | 2012 | 32 | $0.4 | 18.67% |

## Power calculation (rough)
- DC-host counties with issuance: 360
- Mean deals/county-year among DC-host counties with any issuance: 13.4
- Median par/deal: $15.3M

## Files
- `data/derived/county_year_panel.csv` — balanced county-year panel (81,718 rows × 15 cols)
- `data/derived/county_year_panel_summary.md` — this report