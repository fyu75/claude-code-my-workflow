# MuniSpot Coverage — Quick Read

**To:** Mitch
**From:** Frank
**Date:** 2026-05-19
**Re:** Coverage and gaps in the MuniSpot Academic License delivery; questions to raise with Raj before we lock the panel

---

## What's in the delivery

| | |
|---|---|
| Source | Federal Audit Clearinghouse (Single Audit Act ACFRs) compiled by MuniSpot |
| Fiscal years | FY2016 – FY2024 (9 years, annual) |
| Files | 18 CSVs (9 income statements + 9 balance sheets), 4.33M rows total |
| Scope | **General Fund only** — no Special Revenue, Capital Projects, or Enterprise funds |
| Entity types | 23, of which **County-General Purpose Government** is the one we care about |

Headline:

- ~1,879 distinct county-government entities appear in at least one year
- 949 counties have both FY2017 and FY2024 (the 2-period window we'd use)
- 606 counties have all 9 years balanced

Out of 3,143 US counties, that's **60% any-year, 30% two-period, 19% balanced**.

---

## Four issues to flag

### Issue 1 — Not all counties are covered, and the gap is non-random

**State-level coverage is wildly uneven.** A few examples (county-government entities only):

| State | US counties | MuniSpot any-year | % | 2-period (17+24) |
|---|---:|---:|---:|---:|
| North Carolina | 100 | 101 ✱ | 101% | 88 |
| Wisconsin | 72 | 70 | 97% | 58 |
| Virginia | 134 | 92 | 69% | 84 |
| Texas | 254 | 155 | 61% | **60 (24%)** |
| Georgia | 159 | 119 | 75% | 32 (20%) |
| Washington | 39 | 19 | 49% | 9 (23%) |
| Kentucky | 120 | 32 | 27% | 1 (<1%) |
| Oklahoma | 77 | 2 | 3% | 1 (1%) |
| New Jersey | 21 | 0 | 0% | 0 |
| Connecticut | 8 | 0 | 0% | 0 |
| Alaska | 29 | 0 | 0% | 0 |

✱ NC has 101 records vs 100 actual counties — there's a spurious row to clean up.

**Notable patterns:**

- **Zero-coverage states (continental US):** CT, VT, NJ, SD, RI, AK. CT/VT/RI have effectively no county governments (abolished); SD/NJ/AK are real gaps.
- **Single-digit coverage:** OK 2.6%, AR 9%. Are these states filing under a different framework?
- **Mid-tier with poor 2-period coverage:** TX (61% → 24%), GA (75% → 20%) — counties appear in *some* years but not consistently across 2017 and 2024.

**Selection on county size.** Within our DC-relevant treated sample (125 counties with DC tax share ≥ 1%):

| | N | Median 2017 property tax |
|---|---:|---:|
| Covered in MuniSpot 2-period | 45 | $29.7M |
| Missing from MuniSpot | 80 | $13.2M |

So MuniSpot systematically under-represents the small rural counties — precisely the ones hosting hyperscale DCs (Morrow OR, Storey NV, Milam TX, Pend Oreille WA, etc.). Of the 23 counties where we hand-collected ACFRs (top-25 by DC tax share), **only 12 appear in MuniSpot at all**, and **only 5 have both 2017 and 2024 General Fund data**.

### Issue 2 — Even covered counties often miss years

For the 1,879 counties that appear at least once:

| Years observed | Counties |
|---:|---:|
| 1 | 230 |
| 2 | 149 |
| 3 | 134 |
| 4 | 127 |
| 5 | 125 |
| 6 | 117 |
| 7 | 142 |
| 8 | 249 |
| 9 | **606** |

Only 32% of covered counties have all 9 years. For another 13% only one year is observed — these are likely one-off filings.

### Issue 3 — Property tax appears thin, but it's mostly a labelling problem

Counties with a row explicitly tagged `class_1 == 'PROPERTY TAX REVENUES'`:

| | Counties |
|---|---:|
| With ≥ 1 PT row, any year | 808 of 1,879 (43%) |
| With PT row in all 9 years | 215 |
| With PT row in 2017 AND 2024 | 327 |
| **Treated ≥ 1%** with PT in 2017 AND 2024 | **17** of 87 covered |

That looks dire — but it's largely a labelling artifact. When I checked what the **1,071 counties without a `PROPERTY TAX REVENUES` row** actually report on the revenue side, the top categories are:

| `class_1` in the no-PT counties | Rows |
|---|---:|
| `MISCELLANEOUS` | 9,151 |
| `INTERGOVERNMENTAL REVENUE` | 7,361 |
| `LICENSES AND PERMITS` | 6,089 |
| `CHARGES FOR SERVICES` | 4,912 |
| **`TAX REVENUES`** | **4,815** |
| `FINES AND FORFEITURES` | 4,329 |
| `LOCAL REVENUE` | 1,980 |

The 4,815 rows tagged `TAX REVENUES` (a broader bucket) are the smoking gun: these counties **do** report tax revenue, MuniSpot just didn't break out the property-tax portion separately. Concrete state-level evidence:

| State | Counties in MS | With explicit `PROPERTY TAX REVENUES` | % |
|---|---:|---:|---:|
| Iowa | 70 | 70 | **100%** |
| Virginia | 92 | 91 | **99%** |
| New York | 53 | 52 | 98% |
| Ohio | 54 | 41 | 76% |
| Illinois | 72 | 53 | 74% |
| Texas | 155 | 97 | 63% |
| Michigan | 73 | 27 | 37% |
| Georgia | 119 | 39 | 33% |
| **California** | **53** | **5** | **9%** |
| **Minnesota** | 85 | 8 | 9% |
| **North Carolina** | 101 | 13 | 13% |
| **Tennessee** | 92 | 2 | 2% |
| Alabama | 32 | 0 | 0% |
| **All MS counties** | **1,879** | **808** | **43%** |

CA and TN have full property-tax systems — they obviously levy property tax. The 9% / 2% rates are inconsistent labelling, not absence of tax. Same likely true for NC, MN, MI, GA.

**For our treated sample**, accepting either label widens the 2-period coverage substantially:

| Has at least one row of... | Counties | 2017 AND 2024 both |
|---|---:|---:|
| `PROPERTY TAX REVENUES` | 36 | 17 |
| `TAX REVENUES` | 38 | 11 |
| Either (union) | 69 of 87 | **30** |
| Neither | 18 | — |

If we can convince MuniSpot to re-process the `TAX REVENUES` rows and extract the property-tax portion (an upstream ACFR parser task on their end, not ours), our treated 2-period PT sample roughly doubles (17 → 30). That's the single highest-leverage fix to ask for.

### Issue 4 — Scope is "General Fund only," not total county finances

This is in the README but worth flagging explicitly because it shapes what mechanisms we can test.

*(We verified the GF-only claim empirically: 99.95% of `County-General Purpose Government` rows are labelled "General Fund" or close variants like "General", "General Fund 001", "General Fund - County Wide", etc. A residual 0.05% (299 rows out of 625,539) slipped through with broader labels like "Total Governmental Funds" or "Capital Projects" — small enough to ignore.)*

US local governments keep separate books for ~5 fund types under GASB:

| Fund | What's in it | In MuniSpot? |
|---|---|---|
| **General Fund** | Day-to-day operations — police, fire, courts, administration, parks. Funded by property tax + sales tax + intergovernmental aid. | ✅ Yes — the entire delivery |
| Special Revenue Funds | Money legally restricted to a purpose (gas tax, federal grants, opioid settlement, **state DC-incentive pass-throughs**) | ❌ No |
| **Capital Projects Funds** | Money set aside for infrastructure — **new schools, roads, water plants, broadband** | ❌ No |
| Debt Service Funds | Money reserved for bond principal + interest | ❌ No |
| Enterprise Funds | Government activities run like a business (water utility, airport, transit) | ❌ No |

Mapped to our paper's mechanism map:

| Channel | Where the money lives | MuniSpot captures? |
|---|---|---|
| Property tax revenue ↑ | Mostly GF (sometimes Special Revenue if voter-restricted) | ✅ Yes (mostly) |
| Total operating revenue ↑ | GF | ✅ Yes |
| Operating expenditures (services) ↑ | GF | ✅ Yes |
| **Capex ("new roads & schools") ↑** | Capital Projects Fund | ❌ **Not directly** |
| Debt issued / debt service ↑ | Capital Projects + Debt Service | ❌ Not directly |
| **State DC-incentive pass-throughs** | Special Revenue | ❌ Not directly |

**The indirect read on capex:** GF accounting does give us one window — `INTERFUND TRANSFERS OUT`. When a county wants to fund a Capital Projects Fund expenditure, it moves money from GF → CPF via an interfund transfer. So higher GF transfers-out in DC counties **suggests** higher capex downstream, in proportion to the GF→CPF flow. It's a proxy, not the thing itself.

**Concrete example — Morrow County, OR (FY2024):**

| Source | Total Revenue FY2024 |
|---|---:|
| MuniSpot (GF only) | $31.9M |
| Our acquired PDF (total governmental funds) | $49.5M |
| Gap | $17.6M of non-GF activity that MuniSpot doesn't see |

That $17.6M gap is exactly the Special Revenue + Capital Projects + Debt Service activity tied to the DC build-out. So our v3 memo's "Morrow capex CAGR +28.6%" finding from the PDF data is **not** something MuniSpot would have shown us — it's only visible because we extracted the broader scope from the PDF.

The two datasets are complementary: MuniSpot for GF mechanisms across a broad county panel, PDFs for the full multi-fund picture on a smaller treated sample.

---

## Questions to raise with MuniSpot (Raj Chowdhury, info@munispot.com)

Recommend asking these in one email so we can finalize sample selection:

1. **Filing threshold.** Our working hypothesis is that this is driven by the Single Audit Act federal-awards-over-$750K threshold — small counties without federal grants don't file with the Federal Audit Clearinghouse. **Is that the binding constraint, or are there other filters (state-specific exemptions, MuniSpot's own quality gates, etc.) in play?**

2. **State exemptions.** CT, VT, RI presumably have no county-government filers because those states abolished operational county governments. **But what's the story for NJ (21 counties, 0 covered), SD (66/0), AK (29/0), and the OK/AR thin coverage? Are these state-specific filing pathways that go through a different system?**

3. **Year gaps within covered counties.** A county might appear in FY2017 but not FY2024 — is that because (a) it stopped filing, (b) the FY2024 ACFR hasn't been processed yet, or (c) it was filed but failed MuniSpot's normalization? **Is there a way to distinguish "not yet processed" from "did not file"?**

4. **Property tax decomposition.** 1,071 of 1,879 covered counties (57%) have no row tagged `class_1 == 'PROPERTY TAX REVENUES'`, but 4,815 of those rows are tagged with the broader `TAX REVENUES` label. State-level evidence (CA 9%, TN 2%, NC 13%, MN 9% all have universal property-tax systems but near-zero PT extraction) confirms this is a labelling pipeline issue, not absence of tax. **Can MuniSpot run a second pass on the `TAX REVENUES` rows and extract the property-tax sub-component? Or share the underlying ACFR line-item text so we can decompose ourselves?** This single fix would roughly double our usable 2-period treated PT sample (17 → 30) and is probably the highest-leverage change on the existing delivery.

5. **FY2025 and future updates.** README §6 says this is a one-time export. **What's the timing for an FY2025 ACFR pass-through, and can we get a refresh during the project at the academic rate?**

6. **Historical backfill.** Counties' ACFRs typically go back 10–20 years. **Is FY2010–FY2015 data available as an extension, even at reduced quality?** Pre-period data is what enables the parallel-trends test on our DC counties.

7. **Beyond the General Fund.** This delivery is GF-only, but the channel we most want to test — capex on new roads, schools, and DC-supporting infrastructure — lives in the Capital Projects Fund, not the GF. **Does MuniSpot extract the other governmental funds (Special Revenue, Capital Projects, Debt Service) in a parallel product?** Even a coarse "total revenue / total expenditures by fund type" would let us see the capex channel directly. If yes, please send pricing for an academic add-on.

8. **Specific list to spot-check.** Could MuniSpot tell us whether the following are missing because they're not in the FAC universe, or because they were filtered out at some downstream stage?
   - Morrow County, OR (FIPS 41049) — covered ✓
   - Umatilla County, OR (FIPS 41059) — NOT covered ✗
   - Grant County, WA (FIPS 53025) — NOT covered ✗
   - Lawrence County, KY (FIPS 21127) — NOT covered ✗
   - Marshall County, KY (FIPS 21157) — NOT covered ✗
   - Mayes County, OK (FIPS 40097) — NOT covered ✗
   - All 6 small TX DC counties (Briscoe, Crane, Dickens, Glasscock, Knox, Ward) — NOT covered ✗

These 12 are operationally important to our paper because they're the rural-county DC stories.

---

## What we can still do with this data

Even with the gaps, MuniSpot is a real upgrade over what we had:

- **Before:** 2017 Census ACFR cross-section + 23 hand-collected PDFs for select treated counties + national BEA aggregates as benchmark.
- **Now:** 9-year General-Fund panel on ~45 of our 125 treated counties (≥ 1% DC tax share) with ~720 never-DC-host control counties also in the 2-period window.

This makes a proper **2017 → 2024 two-period DiD on General Fund outcomes** feasible — but on a *narrower set of outcomes* than the full mechanism map:

| What MuniSpot lets us test cleanly | What it does NOT |
|---|---|
| Total GF revenue ↑ in DC counties | Capex on roads / schools — the H1 mechanism (Capital Projects Fund) |
| GF operating expenditures (services) ↑ | Total debt issued / debt service (Debt Service Fund) |
| Property tax revenue ↑ — when itemized | State DC-incentive pass-throughs (Special Revenue) |
| Intergovernmental revenue (control for federal/state shock) | Enterprise / utility activity (Enterprise Fund) |
| Interfund Transfers Out (proxy for capex) | |

**Sample is biased toward larger treated counties** — we should address that explicitly in the paper with a per-capita normalization and a size-matched control selection.

For the **property-tax channel specifically**, our hand-collected PDFs (23 counties) remain the better data source — the MuniSpot PT coverage is too thin for that mechanism. For the **capex channel**, the PDFs are necessary because GF data doesn't see it directly. The two datasets are complementary, not redundant.

---

## Suggested next steps

1. **Frank emails Raj** with the questions above this week (I can draft if useful). The state-exemption and property-tax labelling questions are the highest-priority — they may unlock additional rows from the existing delivery without a new acquisition.
2. **Frank builds** the merged county-year panel (MuniSpot × DC presence × SDC bond issuance) and runs preliminary 2-period DiD on the 45-treated / 720-control sample. Will report back before pushing further.
3. **Mitch / Henrik:** any flags on whether we should also reach out to MuniSpot via Chapman channels (since the license is in Mitch's name) about a re-delivery option for FY2025 + earlier years?

---

*References:*

- Raw delivery: `data/muni/` (gitignored, license-restricted)
- Parquet conversion: `data/muni/parquet/` (gitignored)
- Pre-filtered subsets: `data/derived/muni_{property_tax,total_revenue,total_expenditures}_*` (gitignored)
- Coverage script: `scripts/python/32_convert_muni_csv_to_parquet.py`
- README: `data/muni/README.md`
