# MSRB secondary-market yield event study — the selection-free pricing test

**Date:** 2026-06-11. `scripts/python/73`. Bond(CUSIP)-year panel of par-weighted customer-sale yield-to-worst; bond + year FE; cluster county; control = clean never-DC counties' bonds. `announced` absorbing. Identification = the SAME outstanding bond before vs after announcement (no issuance selection). Yields in %, effects reported in bps.

Universe: 1,307,777 bond-year obs, 318,200 bonds, 2,301 counties.

## Absorbing announced dummy (bps)
| Cut | effect |
|---|---|
| Treated ALL | +0.4 bps (1.6) p=0.798 | 43,211 bonds / 112 counties |
| Treated clean_dc | +0.3 bps (2.0) p=0.886 | 29,933 bonds / 48 counties |
| Treated crypto | +2.0 bps (2.8) p=0.485 | 4,602 bonds / 44 counties |
| Treated mixed | -0.7 bps (2.8) p=0.808 | 8,676 bonds / 20 counties |
| **PLACEBO metros** (op-yr anchor) | -5.8 bps (8.4) p=0.493 | 34,625 bonds / 8 counties |
| **Colo-capacity counties** (8, whisper arbiter) | +4.9* bps (2.6) p=0.062 | 12,535 bonds / 7 counties |

## Event study (binned, ref −1; bps)

### Treated clean_dc
| evt | coef (bps) | p |
|---|---:|---:|
| -4 | -0.9 | 0.611 |
| -3 | +0.3 | 0.914 |
| -2 | -0.4 | 0.792 |
| +0 | +0.7 | 0.660 |
| +1 | +2.5 | 0.211 |
| +2 | +2.1 | 0.137 |
| +3 | +2.1 | 0.173 |
| +4 | +1.7 | 0.148 |

### Treated crypto
| evt | coef (bps) | p |
|---|---:|---:|
| -4 | +8.3 | 0.261 |
| -3 | +6.8 | 0.413 |
| -2 | +3.5 | 0.524 |
| +0 | -0.2 | 0.963 |
| +1 | +6.4 | 0.194 |
| +2 | +4.4 | 0.283 |
| +3 | +4.9 | 0.175 |
| +4 | +6.9 | 0.151 |

### Placebo metros
| evt | coef (bps) | p |
|---|---:|---:|
| -4 | +1.1 | 0.556 |
| -3 | +7.8 | 0.167 |
| -2 | +4.4 | 0.350 |
| +0 | +11.7** | 0.042 |
| +1 | +5.8 | 0.200 |
| +2 | +0.8 | 0.818 |
| +3 | -2.2 | 0.668 |
| +4 | -6.7*** | 0.000 |

### Colo-capacity counties (whisper arbiter)
| evt | coef (bps) | p |
|---|---:|---:|
| -4 | -1.7 | 0.472 |
| -3 | +6.1*** | 0.000 |
| -2 | +2.0* | 0.097 |
| +0 | +3.8 | 0.153 |
| +1 | +7.5** | 0.015 |
| +2 | +5.3 | 0.112 |
| +3 | +6.0* | 0.091 |
| +4 | +3.1*** | 0.002 |

## Reading
- This is the arbiter test (memo §11): bond FE kills issuance selection — if the fiscal windfall is priced, the SAME bond's yield should fall after announcement relative to control bonds.
- clean_dc null here + primary-market null = airtight non-pricing. crypto positive = risk premium on volatile tax base, now selection-free. Placebo metros must be null (mechanism off).
- Filters: customer-sale (S) trades, par>=10k, rem. maturity>=1yr, yields in [-2,20], bond observed >=2 years. log(remaining maturity) controls the mechanical roll-down.
