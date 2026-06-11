# Continuous DC dose on the announcement clock — Test 3 (dose-response)

**Date:** 2026-06-10. `scripts/python/70`. dose = cumulative ANNOUNCED >=50MW capacity (MW) / baseline 2017 property tax ($M) — absorbing, assumption-free, in the investor information set. 1 MW/$M ~ 5pp of expected fiscal share under the $50k/MW working assumption. County+year FE, cluster county; clean never pool (2,639); phantoms excluded.

Dose panel: 74 counties; p50/p90/max dose at 2025 = 7.5 / 45.0 / 641 MW/$M.

| Outcome | Cut | (i) dose MW/$M (wins. 50) | (ii) log(1+dose) | (iii) announced x share |
|---|---|---|---|---|
| Spread (bps, deal hedonic) | ALL | +0.418 (0.617) p=0.498 | +0.597 (3.671) p=0.871 | -0.014 (0.197) p=0.943 |
| Spread (bps, deal hedonic) | clean_dc | +0.144 (0.945) p=0.879 | -1.953 (4.143) p=0.637 | -0.377 (0.309) p=0.224 |
| Spread (bps, deal hedonic) | crypto | +0.214 (0.941) p=0.820 | +4.857 (7.244) p=0.503 | +0.082 (0.290) p=0.778 |
| Rating ext (any-rated, deal) | ALL | -0.001 (0.001) p=0.390 | -0.015* (0.009) p=0.091 | +0.000 (0.000) p=0.414 |
| Rating ext (any-rated, deal) | clean_dc | -0.002 (0.003) p=0.427 | -0.008 (0.014) p=0.542 | +0.001 (0.001) p=0.333 |
| Rating ext (any-rated, deal) | crypto | -0.001 (0.002) p=0.444 | -0.027* (0.015) p=0.071 | +0.000 (0.000) p=0.732 |
| Issuance P(any deal) (cy) | ALL | +0.000 (0.001) p=0.675 | -0.005 (0.011) p=0.658 | +0.000 (0.000) p=0.269 |
| Issuance P(any deal) (cy) | clean_dc | -0.001 (0.002) p=0.551 | -0.017 (0.021) p=0.417 | +0.000 (0.000) p=0.882 |
| Issuance P(any deal) (cy) | crypto | +0.002 (0.001) p=0.141 | +0.006 (0.012) p=0.604 | +0.001 (0.000) p=0.153 |
| Issuance log(1+par) (cy) | ALL | -0.000 (0.003) p=0.971 | -0.028 (0.033) p=0.408 | +0.001 (0.001) p=0.241 |
| Issuance log(1+par) (cy) | clean_dc | -0.005 (0.007) p=0.481 | -0.078 (0.070) p=0.264 | +0.001 (0.001) p=0.632 |
| Issuance log(1+par) (cy) | crypto | +0.003 (0.003) p=0.426 | -0.003 (0.037) p=0.942 | +0.001 (0.001) p=0.272 |
| Spread par-wtd (cy) | ALL | +0.782 (0.555) p=0.159 | +7.523** (3.601) p=0.037 | +0.176 (0.200) p=0.379 |
| Spread par-wtd (cy) | clean_dc | +2.180* (1.169) p=0.062 | +11.574** (4.945) p=0.019 | -0.041 (0.343) p=0.906 |
| Spread par-wtd (cy) | crypto | +0.124 (0.594) p=0.835 | +3.562 (5.568) p=0.522 | +0.167 (0.251) p=0.506 |

## Verification appendix (run 2026-06-10, before trusting any cell)
- LINEAR dose is winsorized at 50 MW/$M: raw-dose crypto-spread -0.169*** was 100% Glasscock 48173 leverage (dose=641, documented artifact/oil county); winsorized -> +0.21 ns.
- cy par-wtd spread shows log-dose +12.7** for clean even after dropping dose>50 counties, but the PREFERRED deal-level hedonic spec is null (-2.0 ns, also null without hedonics; no dose-related shift in maturity/amount mix). Discrepancy = aggregation weighting: cy gives tiny, rarely-issuing high-dose counties (Morrow/Storey/Briscoe) equal county-year weight; deal-level weights by actual market activity. READ: no robust spread dose-response in either direction.

## Reading
- A priced fiscal channel requires beta significant AND monotone in dose. Flat dose-response on top of the dummy nulls (script 68/69) = the bond market does not price the DC fiscal windfall, at any dose.
- Crypto: if the spread-widening scales with dose, the risk interpretation sharpens (more mining capacity per $ of tax base -> wider spreads).
- Caveat: continuous-treatment DiD requires stronger parallel-trends (de Chaisemartin-D'Haultfoeuille); we read sign/magnitude, not structural ATTs.
- The dose regressor contains NO $/MW assumption; the $50k/MW translation is interpretation only.
