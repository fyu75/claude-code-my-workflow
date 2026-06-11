# GO vs Revenue Bond Split — Pre-Specified Heterogeneity Test

**Date:** 2026-06-11. `scripts/python/74`. Mirrors script 68 spec exactly.
**Treatment:** `announced = 1[year >= A_firstmaj]`, county + year FE, cluster county.
**Period:** 2008–2025. **Controls:** clean never-DC counties (2,259).
**Phantoms excluded:** {47121, 54047, 21127}.

## A. Sample Description

| Item | Count |
|---|---|
| Treated counties (all classes, phantom-free) | 116 |
| — clean_dc | 48 |
| — crypto | 48 |
| — mixed | 20 |
| Control counties (clean never-DC) | 2,259 |
| Total deals in panel (AMT>0, 2008–2025, treated+control universe) | 59,884 |
| Deals with SECURITY non-missing (treated+ctrl universe) | 59,884 (100.0%) |
| GO share among SECURITY-matched deals | 82.5% |
| All SDC deals pre-geo-filter (AMT>0, 2008–2025) | 129,311 |
| SECURITY match rate (full SDC universe) | 100.0% |

## B. Spread Regressions: GO vs Revenue Splits

**Spec:** `spread_bps ~ announced + logamt + logmat | county_fips + year`, CRV1(county_fips).
Robustness column uses `county_fips + STATECODE^year` FE.

### 1. Spread — GO deals only (SECURITY == 'GO')

| Subsample | Cut | beta_announced | SE | p | N_deals | N_treated | beta(+state×year FE) | p |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| GO only | ALL | -1.98 | 8.24 | 0.810 | 34,789 | 111 | +1.17 | 0.812 |
| GO only | clean_dc | -2.19 | 10.23 | 0.831 | 33,270 | 47 | -1.47 | 0.830 |
| GO only | crypto | +14.59 | 13.37 | 0.275 | 31,289 | 44 | +11.64 | 0.192 |

### 2. Spread — Revenue deals only (SECURITY == 'RV')

| Subsample | Cut | beta_announced | SE | p | N_deals | N_treated | beta(+state×year FE) | p |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| RV only | ALL | +8.74 | 6.26 | 0.163 | 8,056 | 85 | +14.34* | 0.065 |
| RV only | clean_dc | +4.93 | 7.09 | 0.487 | 7,677 | 41 | +13.55 | 0.144 |
| RV only | crypto | +41.34** | 20.08 | 0.040 | 6,997 | 27 | +11.73 | 0.504 |

### 3. Spread — GO & Tax-Exempt only (SECURITY == 'GO' AND TAXABLE == 'E')

| Subsample | Cut | beta_announced | SE | p | N_deals | N_treated | beta(+state×year FE) | p |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| GO & tax-exempt | ALL | -3.49 | 9.11 | 0.702 | 32,078 | 111 | -1.26 | 0.814 |
| GO & tax-exempt | clean_dc | -3.62 | 11.39 | 0.751 | 30,678 | 47 | -4.73 | 0.524 |
| GO & tax-exempt | crypto | +13.30 | 12.02 | 0.269 | 28,874 | 44 | +13.16 | 0.145 |

### 4. Rating Extensive (any_rated_share) — GO and RV splits

| Subsample | Cut | beta_announced (any_rated_share) | SE | p | N_obs | N_treated | beta(+state×year FE) | p |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| GO only | ALL | -0.03 | 0.02 | 0.106 | 49,168 | 113 | -0.04*** | 0.010 |
| GO only | clean_dc | -0.01 | 0.02 | 0.693 | 47,108 | 47 | -0.05** | 0.012 |
| GO only | crypto | -0.07** | 0.03 | 0.012 | 44,861 | 46 | -0.03* | 0.088 |
| RV only | ALL | -0.03 | 0.03 | 0.198 | 10,053 | 88 | +0.01 | 0.827 |
| RV only | clean_dc | -0.05* | 0.03 | 0.074 | 9,598 | 42 | -0.01 | 0.810 |
| RV only | crypto | +0.02 | 0.07 | 0.763 | 8,747 | 28 | +0.03 | 0.708 |

### 5. Maturity Gradient — Full Sample
**Spec:** `spread_bps ~ announced + announced:logmat + logamt + logmat | FE`

| Cut | beta_announced | SE | p | beta(ann×logmat) | SE | p | N | N_treated | beta_ann(+state×yr) | p |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ALL | -0.03 | 6.55 | 0.996 | +0.56 | 2.49 | 0.822 | 43,318 | 114 | +5.54 | 0.187 |
| clean_dc | -1.62 | 8.11 | 0.841 | +1.59 | 3.07 | 0.603 | 41,409 | 48 | +3.69 | 0.510 |
| crypto | +16.27 | 10.81 | 0.133 | -1.81 | 5.81 | 0.756 | 38,749 | 46 | +13.30* | 0.094 |

### 6. SANITY CHECK — Pooled GO+RV Spread (reference: script 68 ALL ~+4.9/-0.5 ns, clean ~-2 ns)

| Subsample | Cut | beta_announced | SE | p | N_deals | N_treated | beta(+state×year FE) | p |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Pooled (all SECURITY) | ALL | +0.10 | 6.86 | 0.988 | 43,318 | 114 | +5.79 | 0.183 |
| Pooled (all SECURITY) | clean_dc | -1.17 | 8.50 | 0.890 | 41,409 | 48 | +4.32 | 0.459 |
| Pooled (all SECURITY) | crypto | +15.94 | 10.69 | 0.136 | 38,749 | 46 | +12.58* | 0.098 |

**Reference from script 68 (spread, deal panel):**
- ALL: +4.9 bps (ns); clean_dc: ~-0.5 bps (ns)
  *(script 68 Reading: 'clean_dc NULL')*

## C. Pre-Specified Prediction Evaluation

**Pre-specified prediction:** GO-only beta should be MORE NEGATIVE than RV-only beta
if the DC tax windfall is priced in GO bonds.

*(See data rows above; evaluation filled in from regression output.)*

**Maturity gradient prediction:** announced:logmat interaction should be negative
(longer maturity → larger spread compression if long-run tax base expectations matter).
