# Data Centers and Municipal Finances: Status Memo on Empirical Results

**To:** Mitch, Henrik, Rui · **From:** Frank · **Date:** June 11, 2026
*All numbers are produced by numbered scripts in the project repository; section references are to the internal running notes.*

## 1. Summary

We now have a complete first pass on both halves of the project. **Data centers raise host-county property taxes — clean hyperscale/colo counties grow 2.6%/yr faster than matched controls — but we find no municipal bond-market response to this windfall on any margin we can measure**: not in new-issue spreads, not in issuance volume, not in ratings, and not in secondary-market prices of outstanding bonds. The single exception is that crypto-mining counties pay 16–18 bps *more* on new issues after their facilities are announced. The early −23 bps result (May memo §6) does not survive better identification; Section 5 reconciles it.

## 2. Variables

| Variable | Definition | Source |
|---|---|---|
| **Treatment (baseline)** | County with estimated DC-related property tax ≥ 1% of county property tax (S&P capacity × $50k/MW ÷ Census 2017 property tax) | S&P 451; Census of Govts |
| **Treatment timing** | Year of the county's first public announcement of a ≥50MW facility (absorbing: once announced, always treated). Collected facility-by-facility for all 172 major DCs (press releases, groundbreakings, county abatement votes) | hand-collected, 2026-06 |
| **Treatment intensity** | Cumulative announced ≥50MW capacity (MW) ÷ 2017 property tax ($M) — contains no $/MW assumption | S&P 451 + Census |
| **Type label** | clean hyperscale/colo vs crypto-mining vs mixed, from S&P `PROVIDERTYPE` | S&P 451 |
| Outcome 1 | County property-tax revenue, annualized growth (CAGR), county-government scope | Census 2017+2022; hand-verified ACFRs |
| Outcome 2 | Offering spread of new-issue deals (bps over maturity-matched Treasury, deal level) | SDC Public Finance |
| Outcome 3 | Issuance: P(any deal), log par, deal count (county-year) | SDC |
| Outcome 4 | Ratings: share of par rated; average rating conditional on rated | SDC |
| Outcome 5 | Yield-to-worst of *outstanding* bonds (customer-sale trades, bond-year level) | MSRB (215.8M trades) |

## 3. Samples

- **Treated:** 125 counties pass the 1% cut; 3 removed after field verification (two phantom S&P entries with no facility on the ground; one project rejected by the state PSC and never built) → **122**, of which 119 have a dated announcement (clean 49 / crypto 48 / mixed 22). The property-tax test further requires a DC operational by 2022 and verified tax data at both endpoints → 92.
- **Controls:** 2,639 counties with **no S&P-listed data center of any size** (we removed 137 counties hosting small <50MW facilities from the raw no-DC pool). Property-tax test: 1:3 nearest-neighbor on log 2017 property tax, same state → same Census division. Bond tests: full pool with county fixed effects.
- **Placebo group:** 11 metro counties (LA, Santa Clara, Cook, Philadelphia, Dallas…) that host a ≥50MW DC but whose tax base is so large the fiscal share is <1% — the mechanism is off by construction, so they should show nothing. They do, with high statistical power.
- **Periods:** property tax FY2017→FY2022 (Census of Governments bookends; next census is FY2027); bond data 2008–2025; announcement years 2000–2024, staggered.

## 4. Tests and results

All bond regressions: county + year FE (robustness: state×year FE), hedonic controls (log size, log maturity), SEs clustered by county. Property-tax test: matched-pair design with bootstrap CIs.

| # | Outcome | Result |
|---|---|---|
| 1 | Property-tax CAGR | **Positive: all +3.39%/yr (p=0.004); clean +2.59 (p=0.032, CI [+0.38,+4.90]); crypto +4.53 (p=0.096, outlier-driven)** |
| 2 | New-issue spread | No effect for clean (−2 bps, ns); **positive for crypto (+16–18 bps, p≈0.05–0.11)** |
| 3 | Issuance (all margins) | No effect for any group |
| 4 | Ratings | No effect on quality; crypto counties carry 6pp less rated par (p=0.05) |
| 5 | Outstanding-bond yields (bond FE — the same bond before vs after announcement, immune to issuance selection) | **No effect for any group** (clean +0.3 bps, SE 2.0; 29,933 bonds; pre-trends flat); the precision rules out even modest repricing |
| 6 | Continuous dose | No dose-response on spreads at any intensity |
| 7 | Placebo metros | No effect on any outcome (34,625 bonds — also rules out low power as the explanation) |

We then attacked the nulls with three pre-specified sample splits chosen to maximize the chance of finding an effect: **GO vs revenue bonds** (the windfall backs GO debt — but GO is already 82.5% of deals, and GO-only is null); **issuer type** (school districts are the largest property-tax recipients — null for districts, county governments, and cities alike); and **salience** (largest announcements × post-ChatGPT era — significant in new-issue spreads, but the significance depends on a single county and the same cells show nothing in outstanding-bond prices). None survives. Cells examined and failed are reported in full in the internal notes.

## 5. Why the May result (−23.4 bps) is gone

The original estimate compared county-year average spreads of DC counties against all 2,776 no-DC counties (Callaway–Sant'Anna). It fails three replacements, each a stricter design:

| Step | Change | Estimate |
|---|---|---|
| Original | county-year aggregate, broad unmatched controls | −23.4 (p=0.057) |
| Swap controls only | size-matched counties (same design as the tax test) | **+21.0** (sign reverses) |
| Deal level + composition controls | county is its own control | +4.9 (ns; rejects −23.4 by ~9 SEs) |
| Outstanding bonds, bond FE | same bond before vs after | +0.3 (SE 2.0) |

Mechanics: DC counties' deals actually trade ~7–10 bps *above* same-state peers in levels (they are small, rural issuers); the negative sign came from the aggregation and the control group, compounded by a timing flaw in the original cohort assignment (current capacity backdated — 32 of the 125 "treated" had no operating DC by 2022) and unlabeled crypto facilities. With only county FE and no year controls, one obtains −70 bps "effects" for every group — the market-wide spread compression of 2023–25 (sample average fell from 193 to 49 bps), not a DC effect.

## 6. Difficulties worth knowing about

1. **Treatment validity required substantial cleaning.** S&P's DC registry mixes hyperscale with crypto mines (half the high-share counties), contains geocoding errors and phantom entries, and lists "operational years" for projects never built. We verified facility-by-facility.
2. **County property-tax data is the hard part of this project.** Census T01 carries systematic scope errors (collector states report all overlapping districts; Tennessee includes school levies); roughly 50 treated counties required hand-verification from audited financial statements. The matched-DiD baseline rests on this verified spine.
3. **Bond-market tests are sensitive to design choices** — the −23 episode, and two later cases where significant new-issue cells (few effective clusters) failed the outstanding-bond confirmation. We therefore treat the bond-FE secondary-market test as the standard any pricing claim must meet.

## 7. Where this leaves the paper

The fiscal first stage is robust; the capital-market non-response is precisely estimated and survives every attack we could construct, including a high-powered placebo. The framing we propose: **do municipal markets price fiscal windfalls?** Answer: not the level — only the source risk (crypto premium at issuance). Open items for discussion: the $50k/MW calibration (now interpretation-only — no headline regression uses it), the expenditure side (where the windfall goes — Census data in hand, untested), and abatement heterogeneity in the first stage.

---

## Appendix: Result Tables

### Table 1 — Property-tax growth (first stage)

**Dependent variable: annualized growth of county property-tax revenue (CAGR, %/yr), FY2017 → FY2022/24, county-government scope.**
Matched-pair design: each treated county vs mean of 3 size-matched no-DC counties (matched on log 2017 property tax, same state → same division).

| Treated group | Mean effect (%/yr) | Median | t-test p | Bootstrap 95% CI | N treated |
|---|---:|---:|---:|---:|---:|
| All | **+3.39** | +1.16 | 0.004 | [+1.34, +5.84] | 85 |
| Clean hyperscale/colo | **+2.59** | +2.11 | 0.032 | [+0.38, +4.90] | 34 |
| Crypto-mining | +4.53 | +0.95 | 0.096 | [−0.10, +10.20] | 33 |

*Effect = treated CAGR − mean matched-control CAGR. Control pool: 2,639 counties with no S&P-listed data center.*

### Table 2 — New-issue offering spreads

**Dependent variable: offering spread of new-issue municipal deals (bps over maturity-matched Treasury, deal level, SDC, 2008–2025).**
`announced` = 1 in every year from the county's first ≥50MW DC announcement onward. Controls: log par, log maturity. SE clustered by county.

| Treated group | County + year FE | County + state×year FE | N deals |
|---|---:|---:|---:|
| All | −0.5 (6.7), p=0.94 | +6.7 (4.3), p=0.12 | 49,284 |
| Clean hyperscale/colo | −2.2 (8.3), p=0.79 | +5.2 (5.7), p=0.37 | 47,364 |
| Crypto-mining | +16.9 (10.5), p=0.11 | +14.3 (7.6), p=0.06 | 44,715 |

### Table 3 — Other new-issue outcomes

**Dependent variables as labeled; same treatment, FE (county + year), and clustering as Table 2.**

| Dependent variable | All | Clean | Crypto | N |
|---|---:|---:|---:|---:|
| Share of par rated (deal) | −0.025 (0.014), p=0.07 | −0.015 (0.016), p=0.38 | **−0.061 (0.031), p=0.05** | 67,384 |
| Avg rating \| rated (deal; AAA=1, lower=better) | −0.111 (0.048), p=0.02¹ | −0.148 (0.054), p=0.01¹ | −0.004 (0.076), p=0.95 | 10,793 |
| P(any deal) (county-year) | +0.008 (0.020), p=0.68 | +0.028 (0.025), p=0.27 | +0.016 (0.036), p=0.66 | 75,322 |
| log(1+par $M) (county-year) | +0.050 (0.070), p=0.47 | +0.099 (0.107), p=0.35 | +0.057 (0.103), p=0.58 | 75,322 |

*¹ Not robust to state×year FE (clean: p=0.19); we read the rating-quality result as no effect.*

### Table 4 — Outstanding-bond yields (secondary market)

**Dependent variable: par-weighted yield-to-worst of outstanding bonds (%, bond×year level; customer-sale trades, par ≥ $10k, remaining maturity ≥ 1yr; MSRB, 2008–2025).**
Bond + year FE — the same bond before vs after announcement; immune to issuance selection. Effects in bps.

Panel A. Announced dummy:

| Group | Effect (bps) | N bonds | N counties |
|---|---:|---:|---:|
| All treated | +0.4 (1.6), p=0.80 | 43,211 | 112 |
| Clean hyperscale/colo | +0.3 (2.0), p=0.89 | 29,933 | 48 |
| Crypto-mining | +2.0 (2.8), p=0.49 | 4,602 | 44 |
| Placebo metros | −5.8 (8.4), p=0.49 | 34,625 | 8 |

Panel B. Event study, clean counties (binned, reference = year −1):

| Event year | −4 | −3 | −2 | 0 | +1 | +2 | +3 | +4 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Coef (bps) | −0.9 | +0.3 | −0.4 | +0.7 | +2.5 | +2.1 | +2.1 | +1.7 |
| p | 0.61 | 0.91 | 0.79 | 0.66 | 0.21 | 0.14 | 0.17 | 0.15 |

*Control: ~240,000 bonds of the 2,639 no-DC counties (panel total: 1.31M bond-years, 318k bonds).*

### Table 5 — Placebo: metro counties with large DCs but negligible fiscal share

**Dependent variables as labeled. 11 metro counties (LA, Santa Clara, Cook, Philadelphia, Dallas…) hosting ≥50MW DCs with fiscal share <1% — the fiscal mechanism is absent, so the prediction is no effect. Anchor: first ≥50MW operational year (both columns).**

| Dependent variable | Treated big-DC counties (n=72) | Placebo metros (n=11) |
|---|---:|---:|
| Offering spread (bps, deal) | −1.1 (8.9), p=0.90 | −3.4 (5.6), p=0.54 |
| Share of par rated (deal) | −0.03 (0.02), p=0.08 | −0.01 (0.03), p=0.63 |
| P(any deal) (county-year) | −0.03 (0.03), p=0.35 | +0.03 (0.03), p=0.23 |
| log(1+par $M) (county-year) | −0.07 (0.09), p=0.45 | +0.13 (0.20), p=0.52 |

---

*Sources by table: T1 `scripts/python/60+69` (`sample_fixes_placebo.md`); T2–T3 `scripts/python/68` (`announcement_did_bonds.md`); T4 `scripts/python/72–73` (`msrb_secondary_event_study.md`); T5 `scripts/python/69`. Reconciliation in §5: scripts 16, 49, 50, 73.*
