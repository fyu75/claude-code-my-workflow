# Issuer-type heterogeneity: DC announcement effect on bond spreads

**Script:** `scripts/python/75_issuer_type_split.py`  
**Date:** 2026-06-11  
**Spec:** `spread_bps ~ announced + logamt + logmat | county_fips + year`, cluster county  
**Years:** 2008–2025  
**Treatment construction:** mirrors script 68 exactly — phantoms {47121,54047,21127} removed; anchor = A_firstmaj (DC-level firstmaj, county-level fallback); treated = 122 counties, controls = 2,776 clean never-DC counties.  

---

## A. Composition of deals in TREATED counties by issuer type

Total treated-county deals in sample (2008–2025): 25,725  
Total par ($M): 790,977

| ISSTYPE_TRANS | N deals | Par share (%) | Notes |
|---|---:|---:|---|
| District | 2,961 | 10.1 | school=640 (22%), other=2321 |
| City, Town Vlg | 2,684 | 7.7 |  |
| County/Parish | 749 | 4.3 |  |
| Local Authority | 290 | 1.6 |  |

---

## B. Spread regression by issuer type — cut: ALL treated

| Issuer type | beta (announced) | SE | p | N | N treated counties | N treated deals | Underpowered? |
|---|---:|---:|---:|---:|---:|---:|---|
| (a) District — all | -3.111 | 10.827 | 0.774 | 23,494 | 92 | 2,313 |  |
| (b) School district | -6.396 | 11.787 | 0.588 | 6,425 | 38 | 535 |  |
| (c) County/Parish | -15.528 | 13.612 | 0.254 | 5,223 | 88 | 614 |  |
| (d) City, Town Vlg | +2.272 | 3.904 | 0.561 | 17,784 | 79 | 2,185 |  |
| (e) ALL types (sanity) | +2.801 | 6.810 | 0.681 | 231,330 | 114 | 5,341 |  |

## C. Spread regression by issuer type — cut: clean_dc only

| Issuer type | beta (announced) | SE | p | N | N treated counties | N treated deals | Underpowered? |
|---|---:|---:|---:|---:|---:|---:|---|
| (a) District — all | -6.560 | 13.862 | 0.636 | 22,675 | 38 | 1,488 |  |
| (b) School district | +0.162 | 9.495 | 0.986 | 6,155 | 14 | 263 | ⚠ underpowered |
| (c) County/Parish | -20.181 | 15.146 | 0.183 | 5,027 | 39 | 406 |  |
| (d) City, Town Vlg | +2.644 | 4.033 | 0.512 | 16,986 | 38 | 1,378 |  |
| (e) ALL types (sanity) | -0.160 | 7.578 | 0.983 | 222,240 | 48 | 3,429 |  |

---

## D. Sanity check — pooled all-issuer-types vs script 68 baseline

Script 68 (ALL cut, county+year FE) reports spread_bps NULL for clean_dc.
Expected range: approximately −0.5 to +4.9 (ns).

| Cut | This script (all types) |
|---|---|
| ALL | +2.801 (SE=6.810, p=0.681, N=231,330) |
| clean_dc | -0.160 (SE=7.578, p=0.983, N=222,240) |

---

## E. Rating extensive (any_rated_share) by school-district vs county/parish

| Issuer type | beta (announced) | SE | p | N | N treated counties |
|---|---:|---:|---:|---:|---:|
| (b) School district | -0.038 | 0.026 | 0.144 | 8,065 | 38 |
| (c) County/Parish | +0.001 | 0.023 | 0.960 | 6,788 | 89 |

---

## F. Pre-specified hypothesis evaluation

**Prediction:** school-district spread beta more negative than county-government beta if DC property-tax  
windfall is priced in school/special-district bonds.

- **ALL cut:** School-district beta = -6.396 (p=0.588); County/Parish beta = -15.528 (p=0.254). Direction INCONSISTENT WITH hypothesis (school more negative than county). School-district estimate NOT significant at 10%.
- **clean_dc cut:** School-district beta = +0.162 (p=0.986); County/Parish beta = -20.181 (p=0.183). Direction INCONSISTENT WITH hypothesis (school more negative than county). School-district estimate NOT significant at 10%.

**school_district_cusip6.csv:** 127 unique (county_fips, cusip6) pairs across 38 treated counties — available for secondary-market MSRB run.
