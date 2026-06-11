# Data Inventory Memo — DC × Muni Project

**Date:** 2026-05-16
**Author:** Frank Yu (CEIBS), with Claude
**Scope:** First inventory pass over (1) prior-project DC data, (2) new SDC Public Finance muni data, (3) new MSRB historical transaction data.
**Status:** Initial review; SDC data fully indexed at the column level, MSRB documented from WRDS spec only (raw file is 57 GB, not loaded).

---

## 0. Where things live

```
/Users/fangyu/claude/datacenter2/data/
├── datacenter -> /Users/fangyu/claude/datacenter/raw    # symlink to prior project's raw (23 S&P 451 SAS files)
├── sdc_muni/sdc_municipals/                              # 7 SAS files, ~1.7 GB total
├── msrb/                                                 # MSRB historical trades (large)
│   ├── msrb.sas7bdat            # 57.9 GB  ← do not open in memory
│   ├── msrb.zip                 #  6.8 GB
│   ├── msrb_lookup.sas7bdat     # 57 MB
│   └── MSRB_variables_02082022version.pdf
├── derived/  external/  intermediate/                    # empty, ready for pipeline output
```

The `data/datacenter` symlink exposes the same 23-file S&P / 451 Research database that anchored Project 1 (Cronqvist–Dai–Yu, "Data Center Capital Structure," April 2026). Re-using the same raw avoids duplication; analysis output for Project 2 should go to `data/derived/` and `output/` in **this** repo, not the prior one.

---

## 1. Data Center side — what Project 1 already established

The prior project (`/Users/fangyu/claude/datacenter/`) is a *firm-level* exercise on **DC ownership and capital structure**, drawing on `dcproperties_*`, `dcownership_*`, `dcprovider_*`, `dcclient_*` plus a Compustat/CIQ link. Key facts from `analysis/output/complete_report.md` that are load-bearing for **this** project:

| Year | US facilities | US IT power (MW) | # of distinct owners |
|---:|---:|---:|---:|
| 2018 | 2,792 | 12,931 | 562 |
| 2020 | 3,145 | 17,669 | 571 |
| 2022 | 3,432 | 25,190 | 588 |
| 2024 | 4,320 | 39,531 | 659 |
| 2025 | 4,551 | 43,990 | 671 |

CAGRs 2018→2025: **+7.2% facilities, +19.1% MW, +2.6% owners** — capacity is growing 2.6× faster than count (densification / hyperscale build-out), and the ownership base is barely widening. Public-firm capacity (8.9 → 29.7 GW) is the lion's share; private capacity (3.99 → 14.3 GW) is growing slightly faster in % terms.

**What we inherit for Project 2:**
- A property-level US panel 2018–2025 with MW capacity and operational status — directly usable to construct $\text{DC}_{c,t}$ and $\text{MW}_{c,t}$ at the county level.
- A vetted Compustat / CIQ link (`ccmlink2.sas7bdat`, ~109 firms / 92 mapped to GVKEY) — useful if we want to attribute DC investment to a publicly-traded parent.
- Geocoded property coordinates (`coords_us_power.csv`) — feeds the county FIPS join, which is the missing piece on our side and the key to the muni linkage.

**What is *not* in Project 1 and we have to add:** county FIPS for every property (Project 1 carries metro/NCREIF, not FIPS), the property-level *announcement* dates (for event-study windows; Project 1 used operational-status snapshots), and the link from property → host municipality / school district / utility district (the actual bond issuer is rarely the county itself).

---

## 2. SDC Public Finance (`data/sdc_muni/sdc_municipals/`)

Seven SAS files; full row counts confirmed by chunked read. Bond-level grain is **`MASTER_DEAL_NO × MUNITRANCHE`**.

| File | Rows | Grain | Key fields |
|---|---:|---|---|
| `deals_data.sas7bdat` | **1,628,790** | deal × sequence (`MASTER_DEAL_NO`, `SEQ_NO`) | 64 columns — deal date (`DELDATE`, `wrds_first_sale_date`), use-of-proceeds (`MUNI_UOPCODE/AMT/NUMBER`), `AMT`, `YTM`, `TAXABLE`, `INSAMT`, `SECURITY`, `SPECREV`, `REFUNDED`, `BB_REGION_TRANS`, `ISSTYPE_TRANS`, `OFFTYPE`, `COMP`, `BANKQ`, `QZAB`, `NOTES1`, `CORPORATE_BACKED`, `GENERAL_TRANS` |
| `ratings.sas7bdat` | **912,128** | tranche | `FITCHRATING1`, `FITCHSHORT1`, `MOODY_RATING`, `MDSHORT`, `SP_RATING`, `SPSHORT` — coverage across all three agencies for the full file (nearly every tranche has a rating record, including `NR`) |
| `maturity.sas7bdat` | **912,128** | tranche | `AMTMATY`, `MATURITY`, `ENDSERIALMATY`, `ENDSERIALCOUPON`, `SPLIT` (serial-bond structure) |
| `calldata.sas7bdat` | **912,128** | tranche | `CALL_FLAG`, `CLDAT1` (call date), `CLPRC`, `PUTDATE`, `PUTFREQCODE`, `REFAMT`, `TAXABLECODE`, `DERIV`, `CALPAR` |
| `managers.sas7bdat` | 1,498,538 | deal × manager × role | `MANAGERNUMBER`, `MANAGERROLE` |
| `wrds_managers.sas7bdat` | 2,945,398 | deal × manager × role (denormalized) | adds `MANAGER_CODE`, `MANAGER_LONG` |
| `munimanager_lookup.sas7bdat` | 48,000 | manager dictionary | `MANAGERNUMBER ↔ MANAGER_CODE ↔ MANAGER_LONG` |

**Year coverage of `deals_data` by `DELDATE`** (delivery date):

| Window | N deals/seq |
|---|---:|
| 1991–1999 | sparse (single digits) |
| 2020 | 11,934 |
| 2021 | 11,239 |
| 2022 | 9,169 |
| 2023 | 7,199 |
| 2024 | 7,854 |
| 2025 | 11,197 |
| 2026 | 3,653 (forward-dated; refresh runs through Q1/Q2) |
| 2027–2030 | a handful (forward delivery / data entry) |

Mean `AMT` ≈ $26M per record (non-null on 537k of 1.63M rows — `AMT` populated at the deal level, not on every sequence row).

### 2a. Role of each of the 7 SDC files

After a full second-pass inspection (every file opened, column lists scanned, sample rows read), the 7 files break down as follows. **Only `deals_data` carries any geographic content** — the other six are deal-attribute extensions keyed on `MASTER_DEAL_NO` / `MUNITRANCHE`. There is no separate "issuer master" file shipping FIPS or county codes.

| # | File | Cols | Key | Role | Geo content? |
|---|---|---:|---|---|---|
| 1 | `deals_data` | 64 | `MASTER_DEAL_NO` (one row per deal in 2005+ subset) | **Main deal table** — delivery date, par, coupon, use-of-proceeds, taxable status, issuer name, state code | Only `STATECODE` (2-letter) + `BB_REGION_TRANS` (Bloomberg region) + `ISSUER` (free-text string). No county or FIPS. |
| 2 | `ratings` | 8 | (`MASTER_DEAL_NO`, `MUNITRANCHE`) | Three-agency ratings at issuance (Moody's, S&P, Fitch — long codes + abbreviations) | None. "SHORT" fields are rating abbreviations (`AAA`, `AA+`, `NR`), not place codes. |
| 3 | `maturity` | 7 | (`MASTER_DEAL_NO`, `MUNITRANCHE`) | Maturity ladder — maturity date, amount-at-maturity, serial-bond structure | None. |
| 4 | `calldata` | 12 | (`MASTER_DEAL_NO`, `MUNITRANCHE`) | Call / put provisions — call flag, call date, call price, refunding amount | None. |
| 5 | `managers` | 3 | (`MASTER_DEAL_NO`, `MANAGERNUMBER`) | Underwriter assignment — which investment banks managed the deal, in what role | None. |
| 6 | `wrds_managers` | 5 | Same as `managers` + name fields | Denormalized join of `managers` + `munimanager_lookup` (convenience file) | None. |
| 7 | `munimanager_lookup` | 3 | `MANAGERNUMBER` | **Underwriter dictionary** — manager number → manager code → manager long name | None. The names here are *investment banks* (e.g., "A.D. Jack and Company", "Morgan Stanley") — i.e., the broker-dealers who underwrite munis, *not* the muni governments who issue them. |

**Comparison to other muni databases.** SDC Public Finance is light on issuer-side metadata relative to alternatives:

| Database | Has issuer master? | County FIPS provided? |
|---|---|---|
| SDC Public Finance (this dataset) | No | No — must parse from `ISSUER` string |
| Mergent MBSD (separate WRDS product) | Yes | Yes (partial coverage) |
| MSRB EMMA (free public web) | Yes (one profile page per CUSIP) | Partial — issuer registered address |

If WRDS happens to carry Mergent MBSD on the same subscription, a CUSIP-6 join (SDC `ISSUECUSIP1` ↔ Mergent issuer CUSIP) would bypass most of the parsing work. Worth asking Rui as a one-line add-on to the existing draft reply.

**What SDC gives us cleanly:**
- **Primary-market issuance.** Every new muni issue: par, coupon, maturity ladder, use-of-proceeds (UOP), insurance, taxable flag, GO vs revenue, issuer location (encoded via `BB_REGION_TRANS` + state fields in the broader deal record), syndicate composition. This is the right object for the **issuance-cost** outcome.
- **Three-agency ratings at issuance.** All ~912k tranches carry Moody's/S&P/Fitch fields; missing-vs-NR distinction needs to be checked at clean stage.
- **Use-of-proceeds breakdown.** `MUNI_UOPCODE / MUNI_UOPAMT / MUNI_UOPNUMBER` lets us split capex purposes (schools, water/sewer, transportation, general municipal) — important for the "what does the DC-driven revenue actually fund" angle.
- **Call/put structure.** Lets us control for embedded optionality cleanly when modelling yields.

**What SDC does *not* give us:**
- **No secondary-market trades.** SDC is issuance-side only. Spread evolution after issuance is MSRB's job.
- **No CUSIP-level outstanding-bond yield.** YTM in `deals_data` is the offering YTM at sale, not a running secondary-market yield.
- **County FIPS.** State and region are there; county is sometimes embeddable from the issuer-name string but not a clean field. Geocoding the issuer's name to a county is the planned join key on the DC side.
- **Issuer hierarchy.** Municipal issuers in SDC are often special districts (school, water, transit, redevelopment authority) whose geographic footprint is *not* the county — must be reconstructed.

**Immediate next steps for SDC:**
1. `01_import.do` — convert all seven SAS files to `.dta`, keep `MASTER_DEAL_NO × MUNITRANCHE` as the join key.
2. `02_clean.do` — apply US-firm/US-issuer filter at this stage (INV-4); de-duplicate `deals_data` to one row per tranche (figure out what `SEQ_NO > 1` means — likely amendment / restated records).
3. `03_descriptive.do` — issuance counts by state × year × UOP category, par-weighted; replicate the 2018–2025 issuance trend to sanity-check the file against MSRB aggregates and standard practitioner tables.

---

## 3. MSRB historical transactions (`data/msrb/`)

**Size discipline.** `msrb.sas7bdat` is **57.9 GB** uncompressed. Do not load in memory anywhere. The intended use pattern is (a) one filter pass in Stata or Python to extract a CUSIP universe relevant to our DC counties, save to a small `.dta` in `data/intermediate/`; (b) all subsequent analysis runs against that filtered file.

The `msrb_lookup.sas7bdat` (57 MB) almost certainly carries CUSIP-level static fields (issuer, state, sector) — that's the file to use to build the CUSIP filter list before touching the trades file. Have not opened it yet to avoid spending time before the SDC side is ingested.

### Variable schema (from `MSRB_variables_02082022version.pdf`, WRDS-curated)

Bond/trade identifiers:
- `RTRS_CONTROL_NUMBER` — trade-level ID, unique within a 10-year window (re-used across decades — keep this in mind).
- `CUSIP` — 9-char security ID. WRDS warns that `SECURITY_DESCRIPTION`, `DATED_DATE`, `MATURITY_DATE` may differ across reports for the same CUSIP; pick one authoritative source at clean stage.
- `(RTRS_CONTROL_NUMBER, CUSIP, TRADE_DATE)` is the recommended unique-trade key.

Trade attributes:
- `TRADE_TYPE_INDICATOR` — D (inter-dealer), P (purchase from customer), S (sale to customer). The customer-side trades (P/S) are the right surface for retail-spread analysis; D for liquidity.
- `TRADE_DATE`, `TIME_OF_TRADE` (HHMMSS), `SETTLEMENT_DATE` / `ASSUMED_SETTLEMENT_DATE` (use the former when both populated).
- `PAR_TRADED` — note: par > $5M is masked as "MM+" for the first five days. Means even-coarser censoring than TRACE's $5M cap on corporates.
- `DOLLAR_PRICE`, `YIELD` (yield-to-worst, MSRB-calculated; missing on variable-rate securities).

Bond attributes (carried on each trade):
- `COUPON`, `MATURITY_DATE`, `DATED_DATE`, `SECURITY_DESCRIPTION` (free-text).

Flags:
- `WHEN_ISSUED_INDICATOR`, `BROKERS_BROKER_INDICATOR`, `WEIGHTED_PRICE_INDICATOR`, `OFFER_PRICE_TAKEDOWN_INDICATOR` (primary-market list-price flag), `UV_DOLLAR_PRICE_INDICATOR`, `ATS_INDICATOR` (≥ Jul 2016), `NTBC_INDICATOR` (≥ Jul 2016).

Administrative:
- `RTRS_PUBLISH_DATE / TIME`, `VERSION_NUMBER`.

### Strengths and known gotchas

**Strengths.** MSRB RTRS is the regulatory tape for the muni market — universe coverage of customer-side and inter-dealer trades. Lets us build (a) at-issuance offering yields (via `OFFER_PRICE_TAKEDOWN_INDICATOR = Y`), (b) secondary-market spreads and effective bid-ask, (c) post-event price impact in event studies around DC announcements.

**Gotchas to flag in advance:**
1. **Par-size masking ("MM+")** for the first five business days on trades > $5M — distorts par-weighted aggregates if not cleaned.
2. **Yield calculated by MSRB**, sometimes missing for variable-rate / structured securities. We cannot back-fill these without a separate yield-engine pass.
3. **`RTRS_CONTROL_NUMBER` only unique within 10 years** — use the full triple `(RTRS_CONTROL_NUMBER, CUSIP, TRADE_DATE)`.
4. **No issuer geography on the trade record** — must be joined from `msrb_lookup` or, better, from SDC via CUSIP. This is the chokepoint and the reason to ingest SDC first.
5. **ATS / NTBC indicators only exist post-Jul 2016.** Any panel that crosses 2016 must handle the structural break.
6. **Dated-date vs. settlement-date discrepancies** between MSRB and SDC for the same CUSIP — pick one and stick with it (recommend SDC's `DATDAT` as authoritative for primary-market characteristics, MSRB for post-issuance trades).

### Recommended ingestion plan (deferred until after SDC `01–03`)

```
Stage 0: read msrb_lookup → write data/intermediate/msrb_cusip_universe.dta
Stage 1: build target CUSIP set = CUSIPs whose issuer maps to a DC-host county
         (county-list comes from S&P 451 properties geocoded to FIPS)
Stage 2: stream msrb.sas7bdat in chunks (Python/pyreadstat or Stata's
         `infile using` against a CSV export), keep only target CUSIPs
         → data/intermediate/msrb_trades_dc.dta  (expected: 1–5% of raw, manageable size)
Stage 3: all spread / liquidity analysis runs against the filtered file
```

Single-pass filter against the 57 GB file is the most expensive single step in the whole pipeline; we should do it once, cache aggressively, and version the filter-list so re-runs are deterministic.

---

## 4. Dependency graph (what feeds what)

```
S&P 451 properties + coords      ─┐
   (already in data/datacenter)   ├─→  property×county FIPS panel  ─┐
US Census county shapefile (TODO) ─┘                                 │
                                                                     ├─→  DC-host county list
SDC msrb_lookup (CUSIP ↔ issuer ↔ state) ─→  issuer×county crosswalk ┤
                                                                     │
SDC deals_data + ratings + maturity ──→  primary-market sample ──────┤
                                                                     │
MSRB filter pass (CUSIP universe) ──→  filtered trades file ─────────┤
                                                                     │
ACFR (county financials, TODO) ──────────────────────────────────────┘
   │
   ▼
analysis-ready county-year panel (revenue, capex, debt, ratings, yields, spreads)
```

The only piece *blocking* SDC ingestion is whether we want to filter to US issuers up-front (INV-4 says yes, do it in `02_clean.do`).

---

## 5. Open questions for the team

1. **SDC `SEQ_NO > 1`.** What does it represent? Restatement, refunding sequence, or a denormalization artefact? Rui likely knows from his WRDS work.
2. **MSRB year coverage** in this delivery — the WRDS spec is dated 02/08/2022; does our 57 GB file run through 2025 or stop earlier? Confirm before filter-pass design.
3. **County FIPS on SDC issuers.** Is there a WRDS auxiliary that gives issuer-level FIPS, or do we have to geocode issuer names? (Project 1's `coords_us_power.csv` is property-side, not muni-issuer-side.)
4. **Filter list versioning.** Recommend storing the DC-host county FIPS list as a committed `csv` in `master_supporting_docs/data_documentation/` so the MSRB filter pass is auditable.
5. **Do we want SDC's `wrds_managers` (denormalized) or `managers + lookup` (normalized)?** Denormalized is faster for descriptive work; normalized is cleaner for joins. Default to normalized in `02_clean.do`.

---

## 6. What this memo does *not* cover

- ACFR ingestion (county financials) — separate plan.
- NCSL state DC incentives — separate plan.
- Ratings agency PDFs (Moody's, S&P, Fitch 2026 DC pieces) — to be filed under `master_supporting_docs/industry_reports/`.
- The actual identification design (winner-vs-loser, staggered DiD, event-study) — that lives in `notes/2026-05-10_project_memo.md` §§4–5 and is unchanged by this inventory.

---

## 7. Sample design: cutoff, issuer scope, and what "muni" actually contains

Discussion follow-up, same day. Two design decisions locked in.

### 7.1 Par-amount cutoff: $1M

Distribution of `AMT` for 2005+ deals (units = $M, coverage 100%):

| pctile | value |
|---|---:|
| min | $0.001M |
| p25 | $2.65M |
| **median** | **$7.59M** |
| p75 | $23.83M |
| p90 | $74.43M |
| p99 | $459.59M |
| max | $10,000M |
| mean | $34.70M |

Cutoff sensitivity:

| Cutoff | Deals kept | Par kept | Unique issuers | Issuer count vs no-cutoff |
|---|---:|---:|---:|---:|
| none | 258,854 | 100.0% | 34,683 | — |
| **$1M** | **231,967 (89.6%)** | **99.8%** | **32,300** | **−7%** |
| $5M | 157,808 (61.0%) | 97.6% | 23,950 | −31% |
| $10M | 108,035 (41.7%) | 93.5% | 16,728 | −52% |

**Decision: $1M cutoff.** Matches the published-literature standard (Gao-Lee-Murphy 2020 JFE; Adelino-Cunha-Ferreira 2017 RFS; Cornaggia-Cornaggia-Israelsen 2018 RFS; Chava-Malakar-Singh 2023; Goldsmith-Pinkham-Gustafson-Lewis-Schwert 2022 JF — all use $1M deal-level). Drops 10% of deals, only 0.2% of par. $5M is held as a robustness check (more standard in liquidity / secondary-market work).

**Counter-intuitive sub-finding.** Raising the cutoff does *not* improve the regex parser's county-resolvable rate — it actually drops it slightly. Reason: large deals are disproportionately state-level (California, Texas, NJ Transportation Trust Fund, etc.). Pushing the cutoff up shifts the deal mix toward state-named mega-issuers, which we want to drop anyway. The real lever for "less parser work" is the issuer-type filter (§7.3), not the par cutoff.

### 7.2 Are all SDC issues muni bonds? Yes, with sub-flavors

SDC's product split:

- **SDC Public Finance** (← what we have): the universe of US municipal-bond new issues. Everything here is a muni instrument.
- **SDC New Issues / Corporate**: corporate bonds, equities, M&A. Separate WRDS product.

Within Public Finance, three SDC-native fields classify the bond:

**`ISSTYPE_TRANS` — issuer type** (2005+, $1M+, n = 231,967):

| Type | Deals | Share | Sample tier |
|---|---:|---:|---|
| District (school + special) | 85,315 | 36.8% | **A (main)** |
| City, Town, Village | 70,113 | 30.2% | **A (main)** |
| Local Authority | 26,498 | 11.4% | **A (main)** |
| State Authority | 26,418 | 11.4% | C (excluded) |
| County / Parish | 14,887 | 6.4% | **A (main)** |
| State / Province | 4,362 | 1.9% | C (excluded) |
| College or University | 3,782 | 1.6% | B (mostly C — public universities are state-controlled) |
| Direct Issuer | 503 | 0.2% | edge case |
| Indian Tribe / Co-op | 89 | 0.0% | edge case |

This field makes the regex-based "is this state-level or local?" classification unnecessary — SDC tells us directly. The regex parser's only remaining job is *extracting the county name* from the ISSUER string, restricted to the Tier A subset (~196,800 deals, 84.7% of the $1M+ sample).

**`CORPORATE_BACKED` — conduit / private-activity flag**:

| Value | Deals | Share |
|---|---:|---:|
| No (government credit) | 208,703 | 90.0% |
| **Yes (conduit / corporate-backed)** | **23,264** | **10.0%** |

Conduit bonds (a.k.a. private-activity bonds, IDA bonds, healthcare conduit bonds) are issued by a muni shell — typically a county Industrial Development Authority or a state Healthcare Facilities Authority — on behalf of a corporate or non-profit borrower (hospital chain, private university, manufacturer using IDA financing, low-income housing developer). The issuer is muni; the *credit* is corporate. The yield reflects the underlying corporate borrower, not the local government's tax base, so the DC-investment mechanism (property tax → muni revenue → muni yield) does not apply.

**Main sample restriction: `CORPORATE_BACKED == 'No'`.**

**`TAXABLE` — tax status of the bond**:

| Code | Meaning | Deals | Share |
|---|---|---:|---:|
| E | Tax-exempt (federal) | 205,668 | 88.7% |
| T | Taxable | 21,714 | 9.4% |
| A | AMT-subject | 4,585 | 2.0% |

All three are still muni instruments; the field describes federal tax treatment of the coupon. The taxable bucket (T) is dominated by 2009-2010 Build America Bonds (a federal subsidy program) and by pension obligation bonds — both flag-worthy externalities to handle in robustness.

### 7.3 Why state-level issuers are out of the main sample

State-level bonds (State Authority + State/Province ≈ 13% of $1M+ deals, but a larger share of par) are excluded from main-regression sample for four reasons:

1. **Treatment-intensity dilution.** California has 600+ DCs, Wyoming has 2. Both state's GO bonds become "treated" if any DC operates in-state, but the per-budget impact differs by orders of magnitude. The treatment variable is not well-defined at state level.
2. **State-by-year fixed effects absorb the variation.** The clean identification (Greenstone-Hornbeck-Moretti template, also Chava-Malakar-Singh 2023) is *within-state, across-counties* — DC-host vs non-DC-host counties in the same state, same year. State-level bonds collide with the FE.
3. **The mechanism is local.** Property tax (the primary channel) flows almost entirely to county / city / school district / special district treasuries — not to state treasuries. State income tax does flow to the state, but DC payrolls are tiny (≈40-60 workers per 100 MW); state sales/use tax on DC equipment is often statutorily exempted (NCSL: 38 states currently offer dedicated DC tax incentives).
4. **Signal-to-noise.** State-level bond yields are driven by pension liabilities, federal aid, Medicaid spending, recession risk, and 50 other fiscal factors. The DC signal sits inside that noise.

**Tier C is not discarded entirely.** State-level bonds are used for:

- **Falsification test.** If state-level yields respond significantly to within-state DC investment, that is a *warning sign* — it suggests a confounder is moving both DCs and broader fiscal conditions. The expected null is what we want.
- **Heterogeneity probe (optional).** High-DC-concentration states vs low-concentration states, state-level yield response. Likely weak by point 4, but referees will ask.

### 7.4 Subtle case — conduit / JPA issuers with state-level names

A handful of state-named issuers are not really "state-level" in our sense — they are **conduits**: state-chartered joint-powers authorities (JPAs) or special-purpose vehicles that issue bonds on behalf of a specific local project. Examples seen in the data:

- California Statewide Communities Development Authority (CSCDA)
- New Jersey Educational Facilities Authority
- Idaho Housing & Finance Association (when financing local single-family housing)
- Many state Health & Educational Facilities Authorities (HEFA structures)

For these, the *issuer* is state-level but the *use of proceeds* (`MUNI_UOPCODE` + `MUNI_UOPAMT`) ties to a specific local project. A second-version analysis could re-attribute these bonds to the underlying local geography using the UOP description text and Census place-matching. For the first-pass main regression, they remain in Tier C (excluded). Flag the issue, defer the work.

### 7.5 Updated workflow

With $1M cutoff + `CORPORATE_BACKED == 'No'` + `ISSTYPE_TRANS` Tier A only:

| Step | Input | Output |
|---|---|---|
| 1. Apply filters | 258,854 → 231,967 ($1M+) → 208,703 (non-conduit) → ~177,000 (Tier A only) | filtered sample |
| 2. State FIPS join | 2-letter STATECODE × 50-row crosswalk | 100% coverage |
| 3. Pass-3 regex parser on ISSUER | ~177k deals, ~27k unique issuers | county-name extraction, target ≥ 85% on Tier A |
| 4. Census county FIPS join | (state, county_name) | 5-digit FIPS |
| 5. Census place→county crosswalk | (state, place_name) for city/town/village | 5-digit FIPS |
| 6. EMMA lookup for residual special districts | ~1,500 issuers | optional; runs async; target ≥ 95% overall |

Expected main-sample size in the county-year panel: **~150,000–170,000 deal observations across 2005–2025**, covering roughly **2,000–2,500 unique counties** out of 3,143 US counties. This is comfortably above the precedent papers (Chava-Malakar-Singh 2023 reports n ≈ 80,000 on a similar deal-level cut).

### 7.6 What this does not change

- All other sections of this memo (DC data §1, MSRB §3, dependency graph §4) are unchanged.
- The DC-side spatial join (lat/lon → county FIPS) is unaffected; runs the same.
- The match level remains **county × year**, not bond × DC.

---

## 9. Implementation: parser pipeline + final coverage

What we built and ran today, in execution order. All scripts in `scripts/python/`, all derived outputs in `data/derived/`, all intermediate lookups in `data/external/`. Nothing committed.

### 9.1 SDC issuer → county FIPS pipeline

The fundamental problem: SDC's `ISSUER` field is free text, no FIPS provided. The pipeline extracts a county name (or place name as a fallback) from the string, then resolves it against three Census reference tables. Five layers ran in sequence; each builds on the previous.

**Sample frame (Tier A only):**

```
deals_data
  └─ DELDATE year ≥ 2000
  └─ AMT ≥ $1M
  └─ CORPORATE_BACKED == 'No'
  └─ ISSTYPE_TRANS ∈ {District, City-Town-Vlg, Local Authority, County/Parish}
       → 233,689 deals
       → 33,165 unique (ISSUER, STATECODE) pairs
       → $5,099B total par
```

**Pass-by-pass coverage (deal-weighted, full population):**

| Pass | What it does | Issuers | Deals | Par |
|---|---|---:|---:|---:|
| Pass-2 | Regex (county/city/township/borough suffix patterns) | 38.7% | — | — |
| Pass-3 | + Census Place crosswalk (spatial join place centroid → county) | 67.8% | — | — |
| Pass-4 | + cousub (MCD) crosswalk; + state-aware boro rule (NJ/PA → place, AK → county); + school-paren regex ("XX (YY) CSD") | 69.3% | 81.9% | 70.0% |
| Round-1 override | 60 hand-curated top-par residuals → county_override / multi_county / state_conduit / metro_excluded | 69.4% | 82.9% | 77.5% |
| Round-2 override | +60 more big residuals | 69.4% | 82.9% | 75.5% (NYC dropped) |
| **v3** (after NYC re-tag) | 120-entry override table, NYC tagged metro_excluded | **69.5%** | **83.0%** | **77.1%** |

**v3 by issuer type:**

| ISSTYPE_TRANS | Issuers | Issuer % resolved | Deal % | Par % |
|---|---:|---:|---:|---:|
| County/Parish | 1,984 | 98.4% | 99.3% | 99.3% |
| City, Town, Vlg | 7,867 | 97.0% | 98.6% | 98.8% |
| District | 17,110 | 66.2% | 78.6% | 79.0% |
| Local Authority | 6,204 | 34.4% | 38.1% | 37.2% |

County/Parish and City/Town/Vlg are effectively complete; District is at 79%; Local Authority is the holdout at 37%. The Local Authority residual is dominated by special-purpose entities (water districts, tollway authorities, port commissions, school finance corps) where the county is not in the name and would require EMMA-style lookup.

### 9.2 The override table

`data/external/sdc_issuer_overrides.csv` — 120 rows, four categories:

| `override_type` | N | Action | Logic |
|---|---:|---|---|
| `county_override` | 57 | Assign single FIPS | Single-county clean attribution (LA USD → 06037, Philly SD → 42101, etc.) |
| `multi_county_authority` | 34 | Flag, no FIPS | Genuine multi-county service area (BART, MARTA, SoCal Metro Water, etc.) — excluded from main county-year panel by design |
| `state_conduit` | 22 | Flag, no FIPS | State-level financing shell (gas prepayment SPVs, tobacco securitizations, state university authorities) — outside Tier A |
| `metro_excluded` | 7 | Flag, no FIPS | NYC consolidated multi-county fiscal unit (4 NYC entities) plus other unallocable metros |

**Construction rule:** override applies only to issuers that the regex pipeline left unresolved. It does not overwrite the 22,984 issuers that the regex resolved correctly. Multi-county and state-conduit entries do not get a FIPS assigned — they are annotated for explicit exclusion, not lost.

### 9.3 NYC decision

A specific design call worth documenting because the same logic would apply to any other multi-county metropolitan fiscal unit we encounter.

**Problem:** NYC has 5 boroughs = 5 county-FIPS, but issues bonds through citywide entities (NYC Municipal Water Fin Auth, NYC Housing Dev Corp, NYC Health & Hosp Corp, NYC IDA, NYC Sales Tax Asset Rec Corp, Hudson Yards Infra, Battery Park City Authority). No "primary borough" exists — Brooklyn has the largest population (31%), but the fiscal authority is unified. Assigning all NYC debt to Manhattan (where the city HQ sits, 19% of population) would invert the population-weighted exposure.

**Empirical check (run 2026-05-16):** of 4,507 US DCs in S&P 451, **63 are in NYC boroughs** (1.4% of US sample), 58 of those in Manhattan — almost certainly small carrier-hotel facilities at the well-known network meet-me-room buildings (60 Hudson, 111 8th Avenue, 32 AoA). Not hyperscale. For comparison: NJ tri-state DC counties (Bergen, Hudson, Essex, Middlesex, Union, Morris, Passaic) hold 93 DCs combined; Loudoun County VA alone holds 302.

**Decision:** drop NYC from main sample (tag = `metro_excluded`). Rationale: (a) NYC's $90B+ budget is dominated by pension, MTA, federal aid, real-estate-tax-from-skyscrapers — DC fiscal effects are noise on this scale; (b) the actual NY-metro DC cluster is in NJ, not NYC proper; (c) standard move in the muni-fiscal literature (Chava-Malakar-Singh and Adelino-Cunha-Ferreira drop NYC); (d) cost is 1.4% of DC sample, 7 issuers, ~$108B of par. Reversible: any user can edit the override CSV to re-include NYC under a different convention if desired.

**Other multi-county US cities — checked, no issue:** Houston, Dallas, Atlanta, Kansas City, Oklahoma City, Tulsa, Columbus, Portland are all >85-95% concentrated in their primary county, and the Census Place crosswalk assigns them to the plurality county correctly. NYC is unique because no borough is dominant.

### 9.4 DC-side spatial join

Independent of the SDC parser, every US DC property in S&P 451 needs a county FIPS for the eventual panel join. This is simpler — coordinates are clean, the operation is a single deterministic point-in-polygon spatial join.

**Script:** `scripts/python/04_dc_property_to_county.py`
**Input:** `data/datacenter/dcproperties_latest.sas7bdat` (4,543 US rows; 4,507 have lat/lon = 99.2%)
**Reference layer:** `data/external/cb_2023_us_county_500k/` — Census TIGER/Line county polygons, 1:500k generalized
**Output:** `data/derived/dc_property_county_fips.csv` (4,507 rows)

**Result: 4,507/4,507 = 100% matched.** Every US DC with coordinates resolved to a county. The 36 US properties without coordinates (0.8% of the US universe) will be handled via ZIP or geocoded address in a follow-up.

**Top 20 DC-host counties (by property count, all years):**

| FIPS | County | DCs |
|---|---|---:|
| 51107 | Loudoun, VA | 302 |
| 04013 | Maricopa, AZ | 219 |
| 51153 | Prince William, VA | 164 |
| 06085 | Santa Clara, CA | 144 |
| 48113 | Dallas, TX | 135 |
| 17031 | Cook, IL | 121 |
| 39089 | Licking, OH | 96 |
| 13121 | Fulton, GA | 88 |
| 06037 | Los Angeles, CA | 87 |
| 51059 | Fairfax, VA | 65 |
| 36061 | New York (Manhattan), NY | 58 |
| 53033 | King, WA | 57 |
| 41067 | Washington, OR | 53 |
| 39049 | Franklin, OH | 53 |
| 51117 | Mecklenburg, VA | 48 |
| 37119 | Mecklenburg, NC | 48 |
| 32003 | Clark, NV | 44 |
| 13097 | Douglas, GA | 43 |
| 17043 | DuPage, IL | 43 |
| 48201 | Harris, TX | 40 |

**517 unique US counties have at least one DC** (16.4% of 3,143 US counties). The treatment is concentrated — three Northern Virginia counties hold 531 DCs (~12% of the US sample) — but spread enough to support county-level cross-sectional variation.

### 

### 9.6 Honest assessment of where we are

**On the SDC side:** 83% deal-weighted, 77% par-weighted county FIPS coverage on the Tier A main sample. Another 5% of par is explicitly classified as multi-county / state conduit / metro-excluded (not lost — flagged for separate handling). True residual needing EMMA-style lookup: ~16% par-weighted, concentrated in 10,061 mid-size special-purpose districts.

**On the DC side:** 100% county FIPS coverage of all DCs with coordinates. 36 US DCs (0.8%) lack coordinates and need ZIP/address geocoding follow-up.

**What this is enough for:** building a county-year panel with treatment (DC count, MW capacity by county-year) and outcome (issuance par-weighted spread, count of deals) for ~2,000-2,500 DC-relevant counties × 26 years. This is the standard form for the Greenstone-Hornbeck-Moretti / Chava-Malakar-Singh identification.

**What still needs to happen before regression:**

1. ACFR data (county-year fiscal variables — revenue, expenditure, debt) — not yet ingested.
2. The 36 US DCs without coordinates need geocoding.
3. EMMA scrape (or skip — work with 83% coverage in the first round).
4. Treasury benchmark for spread calculation (FRED or WRDS Bondview).
5. Apply SDC issuer mapping to the deals_data table itself to produce a deal-level table with `county_fips` filled in.

Steps 1-5 are independent and can run in parallel.

---

