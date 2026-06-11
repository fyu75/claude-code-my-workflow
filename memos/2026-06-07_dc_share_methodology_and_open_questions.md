# DC Share Methodology — Formula, Units Bug, Multipliers, Open Questions

**Date:** 2026-06-07
**Context:** Discussion while deciding the three pending items (multipliers, 28 controls, KY). Surfaced a units bug and several methodology questions that need resolution before the DiD is re-run.
**Companion memo:** `memos/2026-06-07_acfr_integration_and_dc_share_update.md` (the A→E integration session that produced the files discussed here).

> **§7 below (added end of session 2) is the most important new material: the expanded 1:3 matched DiD AND the discovery that BOTH the MuniSpot v2 post-period data AND the Census 2017 baseline have state-systematic measurement errors. Read §7 first when resuming.**

---

## 1. How the 1% DC treatment is currently decided

**Script:** `scripts/python/15_dc_tax_share_distribution.py` → writes `data/derived/dc_tax_share_distribution.csv`.

```
DC tax contribution ($M) = (county latest operational MW) × $50,000/MW/year ÷ 1e6
DC share (%)             = 100 × DC tax contribution ÷ (county 2017 total property tax)
TREATED                  = DC share (mid scenario) ≥ 1%
```

| Component | Value / source | Assumption |
|---|---|---|
| MW | `mw_latest` (most recent operational MW, 2018–2025) | current DC footprint |
| $/MW/year | **$50,000** (mid); low $30k, high $100k | DC pays ~$50k property tax per MW *at standard rates* (no abatement) |
| Denominator | 2017 total county property tax (Census ACFR) | pre-boom fiscal baseline |

It is a **pure engineering proxy** — no county-specific tax record enters the naive treatment decision. Treatment is decided on the **mid** scenario only.

**Worked example — Morrow County OR:** ~1,004 MW × $50k = $50.2M; 2017 property tax $27.1M → share = 185% → treated.

---

## 2. ⚠ UNITS BUG (must fix before any DiD re-run)

The two share columns in `dc_tax_share_distribution.csv` are stored in **different units**:

| Column | Stored as | Morrow OR example |
|---|---|---|
| `dc_share_mid` (naive) | **percent** (ratio × 100) | `185.57` = 185.57% |
| `dc_share_mid_adjusted` | **fraction** (ratio, no ×100) | `1.855` = same 185.57% |

`scripts/python/39_add_pt_structure_state.py` line 86 computes the adjusted share as a raw fraction (`adj_tax / base`) while the naive share (script 15, line 62) is `100 × ratio`. They differ by a factor of 100.

**Consequence:** the `≥ 0.01` cut was applied to both, but means different things:
- naive **percent** column, `≥ 0.01` → really a **0.01% cut** → 348 counties
- adjusted **fraction** column, `≥ 0.01` → genuine **1% cut** → 109 counties

So the "**348 → 109 collapse**" reported in the companion memo is an **artifact**. The honest comparison at a consistent **true 1% cut**:

| Treatment definition | Treated counties (true 1% cut) |
|---|---|
| Naive | **125** |
| Adjusted (blanket multipliers) | **109** |
| Counties that actually drop | **16** |

The naive 1%-cut count of **125 matches the established treated set in CLAUDE.md** ("1% treatment cut", "54 of 125 treated counties"). The 348 was never real.

**Fix:** make `dc_share_*_adjusted` percent-scaled (×100) like the naive column, and apply `≥ 1.0` (not `≥ 0.01`) consistently. Re-export.

The 16 that drop under adjustment (all barely-over-1% in abated states): TX (8: Ellis, Reeves, Nueces, Andrews, Upton, Lamar), GA (4: Harris, Fulton, Jackson, Troup), SC (3: Union, Spartanburg, York), OH (2: Fairfield, Franklin), NV (1: Clark).

---

## 3. Multipliers = state-specific haircut on the $50k/MW rate

The "multiplier" is the **net-of-abatement** adjustment. Net-of-abatement share = the *same* formula with a state-adjusted effective $/MW:

| State structure | × | Effective $/MW |
|---|---|---|
| standard / VA-consolidated | 1.00 | $50,000 |
| SC-FILOT / NV-Switch | 0.50 | $25,000 |
| TX-Chapter-312 | 0.25 | $12,500 |
| GA-IDA-leasehold / OH-no-TPP | 0.20 | $10,000 |
| AL-abatement-heavy | 0.15 | $7,500 |
| KY-consolidated-with-PILOT | 0.90 | $45,000 |

Economic logic (sound): a 100%-abated DC contributes ~$0 to *current* property tax even with huge assessed value. Net-of-abatement is arguably the more honest "fiscal treatment intensity."

### Coverage — how well-grounded is each county's multiplier?

Of the **125** treated counties:

| Multiplier basis | Counties |
|---|---|
| `standard` / VA (×1.0, no change) | 72 |
| **Meaningful haircut** (×0.15–0.50) | **53** |

Of the **53** meaningfully adjusted:

| Evidence quality | Counties |
|---|---|
| Actual extracted ACFR property tax on hand | 27 |
| **Only an assumed state multiplier (no county check)** | **26** |
| Hard GASB-77 abatement disclosure (county-specific) | 4 (Jackson AL, Madison AL, Storey NV, Clark NV) |

### The "blanket assumption"

Assigning a county's multiplier **purely from its state**, without opening that county's ACFR to confirm the abatement happened. Example: every TX treated county gets ×0.25 *because it's in Texas* — but Chapter 312 is **opt-in per company, per jurisdiction**, so some TX counties may collect full freight. We assumed, didn't verify, for 26 of the 53.

---

## 4. $50,000/MW — provenance, validation, and DECISION

> **DECISION (2026-06-07, Frank): use $50,000/MW (the current `mid` scenario) for now.** Flagged as an **OPEN ISSUE for co-author discussion** (Henrik / Rui / Mitch) — the calibration is thin (one county) and the realistic gross range is wide. Do not treat $50k as settled; revisit before submission.

**Provenance:** calibrated from **one** county — Prince William County VA FY22 (~$36k/MW personal-property tax + some real-property tax), per the docstring of script 15. **Not** from literature.

**Lit-review verdict (full report: `quality_reports/lit_review_data_center_property_tax_per_mw.md`):** the peer-reviewed academic literature on DC *local fiscal impact* is **nearly empty** — four backends (OpenAlex, SSRN, Semantic Scholar, arXiv) surfaced no per-MW property-tax benchmark. This is a genuine **gap = novelty** for the paper, but means there is no academic number to cite. The usable evidence is government grey literature + news/industry (JLARC VA 2024; Loudoun & PWC county budgets; Tax Foundation 2025; Nevada example).

### Implied gross $/MW from real anchors (expanded with web/news search 2026-06-07)

| Source | Anchor | Implied gross $/MW | Read |
|---|---|---|---|
| Jackson AL | GASB-77 $971,910 ÷ ~80 MW | **~$12,000** | abated floor |
| Prince William VA | $69.07M (2023) ÷ ~1,760 MW | **~$39,000** | typical growth county (PP only) |
| Loudoun VA | $330M (FY20) ÷ ~2,000 MW | **~$165,000** | dense hub (PP only, outlier) |
| Loudoun VA | $1.37B (FY26 proj) ÷ ~5,330 MW | **~$257,000** | dense hub (outlier) |
| **Nevada (news)** | 12 MW DC → **$3.13M/yr before abatement** | **~$261,000** gross; ~$104k after 75% PP break | full-rate dense |
| **Tax Foundation 2025** | $1B model DC ($775M TPP), Loudoun-style TPP | **~$100–125k/MW** in taxing jurisdictions; **$0** in OH/IL (no TPP) | authoritative model |

**Key learning:** the realistic GROSS (no-abatement) rate is ~**$100k–260k/MW** for dense, fully-taxing jurisdictions, dropping to **$10–40k/MW** under heavy incentives / PP-only-with-breaks. The spread is driven by (a) equipment density ($/MW capex), (b) local millage, (c) depreciation schedule, (d) abatements — i.e., exactly the state-mechanism heterogeneity the multipliers try to capture. **This validates the multiplier *concept*** (same physical MW → wildly different tax by jurisdiction).

**Implication for $50k:** it is **conservative** — below the full-rate gross ($100k+), appropriate as a blended figure given most counties have *some* incentive. For treatment assignment (≥1% cut) a conservative rate means we **under-assign** treatment, which is the safe direction (lower bound on the treated set). The `$30k/$50k/$100k` band remains the headline sensitivity; a `$150k full-rate-dense` scenario could be added as an upper robustness.

### Citable sources (grey literature; verify against primary PDFs before paper use)
- **JLARC, "Data Centers in Virginia," Dec 2024** — authoritative. https://jlarc.virginia.gov/landing-2024-data-centers-in-virginia.asp
- **Tax Foundation, "State Taxation of Data Centers," 2025** — models a $1B DC, TPP depreciation schedules (Loudoun 50%→10%; Santa Clara 73%→2%; Charlotte ~20%/yr); all-in effective rates 24% (Charlotte) to 80% (Santa Clara). https://taxfoundation.org/research/all/state/data-centers-taxation/
- **Prince William County TY2023 Data Center Tax Revenue Report** — source of the $50k mid. https://www.pwcva.gov/assets/2024-10/TY2023_Data%20Center%20Industry%20Tax%20Revenue%20Report_09.24.2024.pdf
- **Loudoun County** DC tax pages — dense-hub upper bound.
- **To do:** build internal implied-$/MW distribution from our own ACFR + GASB-77 extractions; report median + IQR as the empirical anchor for co-author discussion.

---

## 5. OPEN QUESTION: 2017 denominator vs same-year property tax

**Current:** denominator = 2017 total county property tax (fixed pre-period baseline).

**Why 2017 is correct for *treatment assignment* (recommend keep):**
1. **Exogeneity / no circularity.** Treatment is a ≥1% gate. A same-year (post-treatment) denominator would assign treatment partly on a post-treatment outcome — circular. A DC's own tax sits *inside* a contemporaneous denominator, mechanically shrinking the share.
2. **Standard practice.** Scaling a shock by *pre-existing* size (à la Greenstone-style designs) is the conventional, defensible choice.
3. **Coverage.** 2017 is available for all 125 treated counties (Census ACFR, 3,020 counties). Same-year (≥FY2020) ACFR PT exists for only **53 of 125** — using it would drop 58% of the treated set.

**Same-year as robustness:** feasible on the 53-county subset; useful as a sensitivity, *not* as the primary treatment-assignment scaler.

---

## 5b. Property tax incidence: state vs county, and scope consistency (discussion 2026-06-07)

**Who collects DC property tax?** Overwhelmingly **LOCAL, not state.** US property tax is almost entirely local; most states levy little/no statewide property tax. The state's fiscal relationship to DCs runs the *other* way — states mostly **forgo** revenue to attract DCs (sales/use-tax exemption on equipment: JLARC $2.7B in VA FY15–24, the single largest state incentive; corporate income tax minimal for standalone DCs). JLARC framing: *the state exemption enables the local property-tax windfall.* Vertical fiscal externality — state gives, locals receive.

**But "local" ≠ "county government."** Local property tax is split across overlapping jurisdictions, each with its own millage:

| Jurisdiction | Typical share of local property tax |
|---|---|
| School districts | often largest (~50–60%) |
| County government | ~15–30% |
| City / municipality | varies |
| Special districts (fire, water, hospital) | remainder |

A DC's property tax is **divided** — county government keeps only its millage share. In states with strong independent school districts (TX, GA), the county-government slice is small even when *total* local DC tax is large. **Virginia is the calibration exception**: VA counties are the dominant taxing authority and fund schools through the county budget, so Loudoun/PWC county figures ≈ most of local. That does **not** transfer cleanly to TX/GA.

**Scope-consistency issue (NEW, needs attention):**
- Our **denominator** = county-government property tax only (`acfr_2017_county_govt_only.csv`, type=1).
- The **$50k/MW numerator** was calibrated on VA (county ≈ all of local). Applied to TX/GA, it may represent *total local* DC tax while the denominator is only the *county-government* slice → **inflates the share** in non-VA states. This cuts the **same direction** as the abatement multipliers (both say "discount non-VA shares").
- **Two honest implications:** (1) the county-government outcome **understates the total local windfall** (schools get the biggest piece, unmeasured) — state this as scope, not a bug; muni bonds are issued by local govts so county-government finance is still the right lens. (2) Robustness idea: back out the **county-government millage share** of total local property tax per state and scale $50k accordingly. **OPEN ISSUE for co-authors.**

## 5c. Background facts for the paper (Tax Foundation 2025 report)

Source: Jared Walczak, "State Taxation of Data Centers," Tax Foundation, 2025 (`.firecrawl/taxfoundation_dc.md`; https://taxfoundation.org/research/all/state/data-centers-taxation/). Usable as intro/data-section background and motivation.

1. **Thesis support (citable):** *"Localities in which data centers operate receive tax windfalls that reduce burdens on, and support additional benefits to, residents."* — an authoritative statement of exactly our DC→local-fiscal-windfall mechanism.
2. **Mechanism = local, property/TPP-driven:** burden dominated by (a) sales tax on equipment (usually exempted) and (b) tangible personal property (TPP) tax (often imposed). **TPP > 20% of total federal+state+local burden** across 12 jurisdictions. Backs "channel runs through property/personal-property tax, not income/sales."
3. **Pure-capex, minimal-labor (citable):** DC employment +60% (2016–2023) but "modest overall and particularly low in relation to capital." Supports the paper's core premise.
4. **State heterogeneity (validates multipliers):** all-in effective rates **24% (Charlotte) → 80% (Santa Clara)**; only 2 of 12 (Elk Grove IL, **Columbus OH**) impose no TPP — independently confirms our `OH-categorical-no-TPP`. Depreciation schedules differ wildly (Loudoun 50%→10%; Santa Clara 73%→2%; Charlotte ~20%/yr) → same equipment, very different assessed value.
5. **Model-DC density anchor:** $1B facility = **$775M TPP + $225M shell, 32 MW utilization, 40 acres**; servers = 75% of TPP on a **5-yr replacement cycle** (≈ $24M TPP/MW). Supports Mitch's short-asset-cycle → property-tax-volatility risk angle.
6. **Incentives conditional on targets:** SC (jobs held 3 yrs), TX ($500M capex + 20 MW + 40 jobs) — relevant to incentive-erosion risk and the endogeneity threat (incentives are conditional outcomes, not exogenous).
7. **Scale:** US DC investment projected >$1T over 5 years; hyperscalers +$1.8T by 2030.
8. **Real property tax is the "neutral" channel:** TF argues real-property tax on DCs is appropriate/broad-based (unlike discriminatory TPP/sales) — useful framing for why real-property tax is the cleanest fiscal channel.

## 6. The three decisions — full discussion

### Decision 1 — Multipliers / net-of-abatement (Frank prefers net-of-abatement)

- The units bug is now **FIXED** (script 39 re-run): both share columns are percent-scaled; cut is a true `>= 1.0`. Treated set = **125 naive → 109 adjusted**, 16 drop. The 16 are all barely-over-1% counties in abated states (TX 8, GA 4, SC 3, OH 2, NV 1 — see §2).
- **Coverage reality (§3):** the multiplier only "bites" on 53 of 125; of those, **only 4 have hard GASB-77 evidence** (Jackson/Madison AL, Storey/Clark NV); 27 have actual ACFR PT we could use instead; **26 rest on a pure state-blanket assumption.**
- **Lit-review (§4)** supports the underlying $/MW band but offers no academic basis for the *state multipliers* themselves — they remain internally-calibrated guesses.
- **Open sub-choice:** (a) pure blanket multipliers as primary [109], (b) evidence-first hybrid — use actual ACFR where available (27) + multiplier fallback (26), or (c) naive [125] primary + adjusted [109] as robustness.

**FINALIZATION (2026-06-07, working decision — flagged for co-author sign-off):**
- **Important feasibility note:** the "evidence-first hybrid" (b) does **not** fully work, because the ACFR gives *total* county property tax (the denominator), **not the DC-specific tax** (the numerator). DC-specific tax is only directly observed in **GASB-77 abatement notes (4 counties: Jackson/Madison AL, Storey/Clark NV)**. So the hybrid collapses in practice to **blanket state multipliers + GASB-77-informed county overrides** — which is exactly what `scripts/python/39_*` already computes (the AL ×0.15 and NV ×0.50 overrides are GASB-77-informed).
- **Working choice:** report **net-of-abatement adjusted share (109 treated) as the PREFERRED treatment definition** (per Frank's net-of-abatement preference), with **naive (125) as the robustness/headline-sensitivity companion**. Both columns already exist (units-fixed). $50k/MW locked (§4).
- **No new computation needed** — the data is ready. The genuine open items remain for co-authors: (i) is $50k right (§4); (ii) the county-vs-local scope mismatch that inflates non-VA shares (§5b); (iii) whether to validate/recalibrate multipliers against the GASB-77 dollar amounts. These are substantive, not mechanical.

### Decision 2 — 28 missing control counties (extraction IS partly possible)

Checked disk 2026-06-07. Of the 28 missing controls:

| Status | n | Counties |
|---|---|---|
| **PDF already downloaded → can extract now** | **9** | Early GA, Peach GA, Union GA, Fleming KY, Greenup KY, Harrison KY, Hopkins KY, Lincoln KY, Josephine OR |
| **No PDF on disk → need acquisition first** | **19** | Wilkinson GA; Eureka NV, Humboldt NV; Bottineau ND, Mountrail ND, Pembina ND; Armstrong TX, Bowie TX, Jack TX, Kenedy TX, Kimble TX, McMullen TX, Stonewall TX, Sutton TX; Asotin WA, Cowlitz WA, Lewis WA, Lincoln WA, Skamania WA |

- The 9 with PDFs can go through the existing agent-extraction wave immediately (reuses `extract_acfr_agent_outputs.py` + Tier 1-5 pattern).
- The 19 without PDFs are mostly **very small rural TX/WA/ND counties** — many may not publish a full ACFR at all (small counties often file only state-template financials, not GASB ACFRs). Acquisition success is uncertain.
- **Caveat linking to Decision 3:** 5 of the 9 extractable are **KY** counties → their property-tax extraction inherits the KY bundled-tax problem below.
- **Recommended:** extract the 9 now; attempt acquisition for the 19 but expect partial yield; drop whatever can't be found rather than block the DiD.

**RESULT (2026-06-07, Sonnet + firecrawl agent wave):**
- *The 9 with PDFs:* 5 KY (Fleming, Greenup, Harrison, Hopkins, Lincoln) → all **bundled, not separable** (same KY issue as D3; flag, don't use as property-only). 3 GA + 1 OR (Early, Peach, Union GA; Josephine OR) → still to be extracted from disk PDFs (not yet run).
- *The 19 without PDFs (firecrawl acquisition):* **found so far** — GA Wilkinson 13319 (GF PT $4.80M, FY2022); ND Bottineau 38009 (GF $2.66M / all-funds $4.20M, FY2023), Mountrail 38061 (GF $31.6k / all-funds $1.64M — Bakken, property tiny vs $72.8M oil-driven revenue), Pembina 38067 (GF $2.38M / all-funds $3.32M, FY2023); NV Eureka 32011 (GF ad-valorem $4.77M, FY2020; net proceeds of mines excluded), Humboldt 32013 (all-funds property $10.94M incl. net-proceeds-of-minerals, FY2023; GF not separable).
- *WA — all 5 found* (Asotin, Cowlitz, Lewis, Lincoln, Skamania). *TX — 5 of 8 found* (Armstrong, Bowie, Jack, McMullen, Sutton); **3 NOT_FOUND** (Kenedy, Kimble, Stonewall — tiny counties, no published audited ACFR; drop them).
- *3 GA + 1 OR disk PDFs extracted* (Early, Peach, Union GA — govwide-only; Josephine OR — fund-level).
- **INTEGRATED 2026-06-07** via `scripts/python/41_integrate_d2_controls.py`: 20 D2 control rows added → wide CSV now **131 rows, 112 counties, 102 with property tax**.
- **ND/NV/GA gotcha:** much county property tax sits in Special Revenue (Road/Bridge) funds → GF-only understates; use **all-funds** PT. GA counties report PT only on the government-wide Statement of Activities (fund "Taxes" bundled) → tagged `acfr_govwide_d2`, value in `property_tax_allfunds`, GF null. Oil counties' big revenue is intergovernmental oil-tax sharing (state tax), NOT property tax. NV Humboldt all-funds PT includes net-proceeds-of-minerals.

### Decision 3 — KY bundled-tax correction (elaboration)

**The problem:** Kentucky county ACFRs report a single top-line **"Taxes"** in the governmental-funds statement that **bundles ad valorem (property) + occupational license tax + other**. The occupational tax (a local payroll/wage tax) is often the *largest* local revenue source in KY — so a `property_tax_gf` pulled from the bundled line is **overstated**, not property-only.

**Current 7 KY rows in `acfr_county_year_extracted_wide.csv`:**

| FIPS | County | FY | property_tax_gf | source | flag |
|---|---|---|---|---|---|
| 21019 | Boyd | 2025 | $9.70M | munispot_v2_gf | check MuniSpot classification |
| 21127 | Lawrence | 2022 | $1.43M | ACFR | likely bundled |
| 21145 | McCracken | 2022 | **$19.95M** | ACFR | **suspiciously high for ~65k-pop county → almost certainly includes occupational tax** |
| 21157 | Marshall | 2023 | $3.04M | ACFR | likely bundled |
| 21195 | Pike | 2022 | $9.96M | ACFR | likely bundled |
| 21225 | Union | 2023 | (none) | ACFR | only total revenue |
| 21127 | Lawrence | 2024 | (none) | ACFR | empty |

**Smoking gun:** McCracken County (Paducah, ~65k pop) showing $19.95M "property tax" is implausibly high — Paducah has a sizeable occupational tax; the figure is bundled.

**Options:**
- **(a) Flag (non-destructive):** set `state_pt_structure = 'KY-combined-taxes-not-separable'` on these rows, keep the number; decide at analysis time. Reversible, no data lost.
- **(b) Null the PT:** set `property_tax_gf = NaN`; KY counties drop from PT-based tests. Cleaner but discards partial signal.
- **(c) Re-extract the property-only line:** some KY ACFRs *do* break out "Property taxes" separately in detailed statements — a targeted re-extraction could recover the true property-only number for some counties. Most effort, best data.
- **Recommended:** **(a) flag now** (cheap, reversible), and opportunistically try (c) for the high-value counties (McCracken, Pike) where the bundling distortion is largest.

**RESULT (2026-06-07, re-extraction attempted via Sonnet agent wave, option c):** A Sonnet agent read **every KY ACFR PDF on disk (13 counties)**. Finding: **12 of 13 use the KY Dept. for Local Government regulatory (cash) basis, which bundles ALL taxes under one "Taxes" line — property tax is structurally NOT separable** (confirmed against Statement of Receipts, budgetary schedules, and notes). Re-extraction (option c) is therefore **impossible** for those counties. Resolution applied via `scripts/python/40_fix_ky_bundled_taxes.py`:
- **5 nulled** (`KY-bundled-taxes-not-separable`): Boyd 21019, Lawrence 21127, McCracken 21145, Pike 21195, Union 21225. Bundled value preserved in new column `bundled_taxes_gf` (e.g. McCracken $19.95M was confirmed = bundled Taxes line, not property-only).
- **2 salvaged:** Marshall 21157 — occupational tax flows through a separate Occupational Tax Administrator Fund, so GF "Taxes" $3.04M is effectively ad-valorem-only (agent-inferred; flagged `KY-property-only-occ-in-separate-fund(inferred)`). Jackson KY 21109 — quarterly statement itemizes by revenue code → real property-only **$313,743** (added; flagged `KY-itemized-property-only(audit-disclaimer)`).
- **NEW data gotcha for CLAUDE.md:** KY county audits (DLG regulatory basis) bundle property + occupational + net-profits under one "Taxes" line; not separable from the financial statements. Only quarterly fund reports with revenue codes (e.g. Jackson 21109) or counties that route occupational through a separate fund (Marshall) yield property-only.

---

**Status of near-certain actions:** units bug — **DONE** (§2, script 39 re-run, 125→109). Lit-review — **DONE** (§4).

**Decision status (2026-06-07 — all three resolved at working level):**
- **D1 (multipliers / $/MW):** **FINALIZED (working).** $50k/MW locked; net-of-abatement adjusted share (109) = preferred treatment definition, naive (125) = robustness. Hybrid collapses to blanket+GASB-77 overrides (already computed). Substantive items (is $50k right; county-vs-local scope; multiplier recalibration) flagged for co-authors. No new computation needed.
- **D2 (28 controls):** **DONE.** 20 of 28 integrated (`script 41`); 5 KY bundled (unusable as property-only, see D3); 3 tiny TX have no published ACFR (dropped). Wide CSV: 131 rows, 112 counties, 102 with PT.
- **D3 (KY bundled tax):** **RESOLVED** — re-extraction impossible (structural bundling); script 40 nulled 5, salvaged Marshall + Jackson KY.

**Remaining (analysis, next session):** re-run within-county growth tests + DiD on the finalized panel — preferred treated set = adjusted 109, robustness = naive 125, controls = the expanded set (now 102 counties with PT). Use all-funds PT where GF understates (WA/ND/GA).

---

## 7. Expanded 1:3 matched DiD + the dual-source data-quality problem (end of session 2)

### 7.1 Expanded matching — DONE
`scripts/python/42_match_controls_full125.py` — 1:3 matching for ALL 125 treated (defined correctly from `dc_tax_share_distribution.csv` `dc_share_mid>=1%`, NOT from the wide CSV which now contains D2 controls). Output `data/derived/matched_controls_full125.csv`:
- **123 of 125 treated matched × 3 = 369 pairs, 304 unique controls.** (2 treated lack a 2017 Census baseline: 30093 Silver Bow MT consolidated, 40097 Mayes OK.)
- 318 pairs "OK" (control within 0.5–2× of treated 2017 PT), 51 "FALLBACK" (nearest, out of band).
- Matching is cheap (needs only 2017 Census). Running the DiD is gated by **post-period data quality** (below).

### 7.2 Expanded DiD scaffolding — `scripts/python/43_expanded_matched_did.py`
- Scope rule: 2017 Census = county-govt TOTAL property tax (all funds). Post MUST be all-funds too (GF-only understates).
- **Units bug fixed:** Census `rev_property_tax` is in **MILLIONS** (PWC=780.6 → $780.6M); post is in dollars. Multiply Census by 1e6. (First run produced +1.5-billion-% CAGRs from this.)
- Estimator: per-treated effect = treated CAGR − mean(matched-control CAGR); t-test/Wilcoxon/sign/bootstrap + pooled OLS (CAGR ~ treated + state FE). Plus treated-vs-benchmark (3.40%/yr).

### 7.3 ⚠ THE KEY FINDING: both post-period sources AND the 2017 baseline have state-systematic errors
QC: compare each source's value to the Census-2017 magnitude; role-aware bands (controls shouldn't grow >25%/yr; treated may grow fast). `data/derived/post_period_qc_both_sources.csv` + `data/derived/v2_value_qc.csv`. **22 of 427 matched-set counties flagged.**

**Online-verified 8 counties (Sonnet + firecrawl/google). Verified true values saved to `data/derived/post_period_verified_values.csv`. Examples (keep for reference):**

| County | Census-2017 | source-post (suspect) | **TRUE (verified)** | What's broken |
|---|---|---|---|---|
| Arlington VA (51013) | $863M ✓ | V2 $145M | **$1,083M** FY24 | V2 = personal-property line only; dropped real estate (86%) |
| Pecos TX (48371) | $19.9M | V2 $1.93M | **$33.6M** FY23 | V2 = minor sub-fund (~1/17). Oil county. |
| Lincoln NM (35027) | $11.1M ✓ | V2 $2.90M | **$16.9M** FY22 | V2 = one narrow levy (~1/6) |
| Box Elder UT (49003) | $16.4M | V2 $4.18M | **$13.5M** FY23 | V2 = county general levy only (~1/3) |
| **Madison IN (18095)** | **$55.2M ❌** | V2 $26.3M ✓ | **$28.0M** FY24 | **CENSUS wrong** — summed property+income tax (IN reports both as "Taxes"). V2 was right! |
| Oswego NY (36075) | $50.8M ✓ | V2 $16.8M | **$48.7M** FY23 | V2 captured "other property-tax items" only, missed core real-property line (NY bug) |
| **Missaukee MI (26105)** | **$13.6M ❌** | V2 $123.5M ❌ | **~$4.8–6.8M** | **BOTH wrong** — Census absorbed road/school (~3×); V2 FIPS collision (~18×) |
| Story IA (19169) | $26.6M ✓ | V2 $23.7M ✓ | $28.3M FY24 | both roughly fine (V2 ~ GF slice) |

**Lessons (state-systematic, bidirectional):**
- **MuniSpot v2 all-funds UNDER-captures** — grabs one levy bucket / sub-component, not the total (NY: misses real property; VA: misses real estate; UT: county general levy only). Verified wrong in ~6 of 8.
- **Census-2017 (ASLGF parser) OVER-captures in some states** — IN bundles income tax into "Taxes"; MI absorbs road/school district revenue. So the *baseline* is not a safe anchor either.
- Because the two sources err in **opposite directions**, mixing them manufactures spurious growth/decline. A clean 2-period growth number needs **both endpoints read from the actual ACFR statement** (hand-verified), per county.
- Clean ×1000 auto-fixes: PWC 51153 (V2 $1.23e12 → /1000 = $1.23B), Ashtabula OH 39007.
- Oil counties (McMullen 48311, Jack 48237, Mountrail 38061, Pecos): 2017 Census baseline anomalous (pre-boom or parser error) → growth undefined → drop from growth DiD (consistent with CLAUDE.md oil-county caveat).
- ACFR fragments found (need true value, NOT yet verified): Fulton GA 13121 ($697k vs $529M), Franklin OH 39049 ($531k vs $417M).

### 7.4 Scripts + files created this session-arc
| File | Purpose |
|---|---|
| `scripts/python/42_match_controls_full125.py` | 1:3 matching all 125 treated → `matched_controls_full125.csv` |
| `scripts/python/43_expanded_matched_did.py` | expanded 2-period matched DiD (ACFR-only post; V2 disabled via `USE_V2=False`) |
| `data/derived/matched_controls_full125.csv` | 369 pairs, 123 treated, 304 controls |
| `data/derived/post_period_qc_both_sources.csv` | QC of ACFR vs V2 post values vs 2017, role-aware bands |
| `data/derived/v2_value_qc.csv` | V2 ×1000 / out-of-band flags |
| `data/derived/post_period_verified_values.csv` | **8 hand-verified true values (reuse — don't re-verify)** |
| `data/derived/expanded_matched_did_{panel.csv,results.md}` | current (ACFR-only, N too small) DiD output |

### 7.5 DECISION PENDING for next session — A / B / C
The expansion-to-125 via *Census-2017 baseline + V2/single-source post* is **NOT reliable** as-is (§7.3). Three paths:
- **A — Clean spine only:** restrict growth DiD to counties with hand-verified ACFR on BOTH endpoints (small but trustworthy; ~the original 22 + verified). *Recommended as the publishable result now.*
- **B — Verify both endpoints incrementally:** keep agent-verifying both 2017 and post for flagged counties; grow the clean panel over time (8 done; 5+4 queued). *Recommended as a background campaign.*
- **C — Consistent re-scrape:** hand-scrape a uniform pre-period (FY2017/18) ACFR for all treated+controls so both endpoints share one verified source (most defensible, biggest effort).

**Verification still queued (interrupted):** treated batch (Fulton GA 13121, Franklin OH 39049, Washington GA 13303, Warren IN 18153, Valencia NM 35061) + control-B (Austin TX 48015, Crosby TX 48107, Throckmorton TX 48447, Benton WA 53005).

**Frank to choose A/B/C at next session start before running the growth DiD.**

### 7.6 Decision = **B**. Queued 9 counties verified (2026-06-08)

Frank chose **B**. Dispatched 9 parallel Sonnet+firecrawl agents (one per county, each with an ~8-call escape hatch). **8 of 9 now have usable two-endpoint data; 1 structurally failed.** All true values + provenance saved to **`data/derived/verified_two_endpoint_pt.csv`** (the new gold-standard spine — both endpoints, not just post; supersedes the post-only `post_period_verified_values.csv` for these 9).

| County | role | dc_share_mid | FY17 baseline | post | impl. PT CAGR | status |
|---|---|---:|---:|---:|---:|:--|
| Fulton GA 13121 | treated | 1.2% | $558.945M | $765.662M (FY24) | +4.6%/yr | VERIFIED |
| Franklin OH 39049 | treated | 1.4% | $432.379M | $531.792M (FY23) | +3.5%/yr | VERIFIED |
| Washington GA 13303 | treated | **52%** | $8.591M | $8.826M (FY23) | **+0.4%/yr** | VERIFIED |
| Valencia NM 35061 | treated | 49% | $12.455M | $17.822M (FY24) | +5.3%/yr | VERIFIED |
| Sullivan IN 18153 | treated | 16% | — | — | — | **FAILED** |
| Austin TX 48015 | control | — | $15.277M | $21.725M (FY22) | +7.3%/yr | VERIFIED |
| Crosby TX 48107 | control | — | $1.366M | $2.735M (FY24) | +10.4%/yr | VERIFIED* |
| Throckmorton TX 48447 | control | — | $1.665M | $1.903M (FY22) | +2.7%/yr | PARTIAL (levy) |
| Benton WA 53005 | control | — | $28.651M | $32.078M (FY21) | +2.9%/yr | VERIFIED |

\* Crosby baseline = Census (confirmed plausible, no FY17 PDF online); all others have audited both-endpoints.

**Findings worth carrying forward:**
1. **The "fragments" were a UNITS bug, not fragments.** Fulton's $697,487 was the *FY2023* value (misattributed to FY17); Franklin's $531,792 was the *correct FY23 all-funds* value but in **$000s** read as dollars. **Large counties report ACFRs in thousands** — the wide-table extractor mis-scaled them. **Action:** audit `acfr_county_year_extracted_wide.csv` for any county whose true PT is ≥ ~$100M but whose stored value looks like ~$X00,000 (likely ×1000 too small).
2. **Sullivan IN is unrecoverable from published audits** — Indiana SBOA regulatory basis bundles property tax + local income tax under one "Taxes" line per fund; needs DLGF County Abstract / Gateway Detailed Receipts (firecrawl can't reach the JS forms). Census $22.97M over-captures (all-taxing-units settlement + LIT). Drop from clean PT growth panel or source the Abstract manually. Same futility class as KY/TN bundling.
3. **§5b denominator-scope evidence (new):** the treatment-share denominator `dc_tax_share_distribution.csv → prop_tax_2017_M` is systematically **2–4× larger** than Census county-govt-only PT (Fulton $2,070M vs $529M; Washington GA $21.2M vs $8.6M; Valencia $42.3M vs $13.2M). That denominator is a **broader (all-taxing-units / county-wide levy) scope**, which deflates `dc_share` and is exactly the county-vs-local scope inconsistency flagged for co-authors. **The treatment cut and the DiD outcome are computed on different PT scopes** — reconcile before finalizing.
4. **Washington GA 13303 is a substantive anomaly:** nominal dc_share_mid = 52% yet county-govt PT grew only +0.4%/yr — either the DC isn't yet on the tax base, the 52% is a denominator-scope artifact (point 3), or it's a genuine counter-example. Inspect individually.

**Clean spine after B (this round):** 7 fully-audited two-endpoint counties (4 treated: Fulton, Franklin, Washington GA, Valencia; 3 control: Austin, Crosby, Benton) + Throckmorton (levy-based, usable with ±3% flag). Combined with the original 8 post-verified counties, the clean DiD panel is now large enough to re-run §7.2 sourcing the baseline from `verified_two_endpoint_pt.csv` first, then ACFR-allfunds, then Census.

**Next:** wire `verified_two_endpoint_pt.csv` into `43_expanded_matched_did.py` as the top-priority source for BOTH endpoints (above Census 2017 and ACFR-wide), drop Sullivan IN, re-run. Then continue B over remaining flagged counties.

### 7.7 Second B wave (5 remaining QC-flagged) + first clean test + units audit (2026-06-08)

Verified the last 5 QC-flagged counties (all flagged cells in `post_period_qc_both_sources.csv` are now resolved). Appended to `verified_two_endpoint_pt.csv` (now 14 rows).

| County | role | FY17 baseline | post | status | QC-flag verdict |
|---|---|---:|---:|:--|:--|
| **Prince William VA 51153** | treated | $780.642M | $1.234B (FY24) | VERIFIED | `x1000_high` was REAL unit error ($1,233,906k → $1.23T). Census $780.6M EXACT. DC personal-prop tax $124M→$283M (+128%), ACFR names data centers. |
| Mountrail ND 38061 | control | $4.12M (Census) | $1.661M (FY23) | PARTIAL | `INCONSISTENT` was a YEAR-MISMATCH — PT genuinely declined (oil cycle); both endpoints internally consistent. |
| Ashtabula OH 39007 | control | $17.348M | $17.949M (FY23) | VERIFIED | `div1000_low` was a MISCLASSIFICATION (v2 grabbed PILOT line $14,677), not ÷1000. |
| Jack TX 48237 | control | NA (unverifiable) | $6.587M (FY22) | PARTIAL→DROP | post solid; no FY17 audit, Census $2.04M is ASLGF undercount → dropped from growth DiD. |
| McMullen TX 48311 | control | $12.765M (FY18) | $14.721M (FY22) | VERIFIED | `x1000_high` was REAL (Eagle Ford, $2.83B taxable, ~$21k PT/capita). Census $180k is the error. |

**META-LESSON — QC flags diagnose poorly; verification is mandatory.** Of 5 heuristic flags, only 1 (PWC) was the error the flag named. The rest: year-mismatch (real decline), wrong-row misclassification, and a genuinely large oil levy. **Never auto-correct by the flag (×1000 / ÷1000) — always read the source.** Drives DROP list in script 43.

**First clean test — `43_expanded_matched_did.py` re-run with verified spine** (`verified_two_endpoint_pt.csv` as top-priority both-endpoint source; DROP={Sullivan 18153, Jack 48237}; CAGR now uses the actual baseline FY, e.g. McMullen 2018). Output `expanded_matched_did_results.md`:
- PRIMARY matched effect (N=6 clean treated): mean **+4.60%/yr** (t p=0.25), median +3.02%/yr, 5/6 positive.
- Treated CAGR mean **+6.50%/yr** vs 3.40% benchmark = **+3.10%/yr excess** (p=0.42).
- **Pooled OLS (CAGR ~ treated + state FE, N=58): treated coef +3.84%/yr, SE 2.04%, p=0.060** — the headline; marginally significant, direction consistent.
- All effects POSITIVE (DC counties' county-govt property tax grows faster) but **underpowered**.

**⚠ THE BINDING CONSTRAINT IS CONTROL POST-COVERAGE, not treated.** Diagnostic on the panel:
- **35** treated have a clean own post; but only **6** also have ≥1 clean matched control.
- **29 treated are blocked PURELY by missing clean controls** — including the flagship verified four (PWC 51153, Fulton 13121, Franklin 39049, Valencia 35061) whose same-state controls lack post data.
- **281 of 304** unique matched controls still need a clean post value.
- **Next B wave = scrape post-period ACFR for the matched CONTROLS of the 29 blocked treated.** Each blocked treated needs only ≥1 of its 3 same-state controls → lifts usable treated 6 → up to 35 (6×). This is the single highest-leverage cleaning task left.

**Units-bug audit (step 3) — `data/derived/wide_table_units_audit.csv`.** Scanned the whole wide table for the thousands-misread (×1000-too-small) pattern vs Census×1e6. Result: **only 3 cells flagged, all Fulton (×2 cols) + Franklin — both already fixed via the verified file.** No other county contaminated. Remaining flags (McMullen ×2 high, Mountrail GF low) are real oil-county levels / GF-only fragments, already verified. **The ×1000 bug was isolated to exactly 2 large counties; wide-table units integrity confirmed.**

### 7.8 Control-post wave (third B wave) + powered re-run (2026-06-08)

Diagnostic in §7.7 showed the binding constraint was control-post coverage (35 treated had clean own post, only 6 had a clean control). Dispatched 22 Sonnet+firecrawl agents for the rank-1 same-state control of each of the 23 targetable blocked treated (6 TN/KY/IN treated skipped — controls equally bundled). **19 VERIFIED both-endpoint, 3 PARTIAL.** Appended to `verified_two_endpoint_pt.csv` (now 36 rows, 33 both-endpoint usable). Notable: **Arlington VA 51013 baseline obtained ($854.0M FY17 → $1,082.6M FY24)**, completing PWC's pair.

**Two matching-integrity problems surfaced (Census used for matching is itself unreliable):**
- **Texas County MO 29215**: audited county PT = **$271k** (MO cash-basis; only GR+SB40 funds levy PT, Road is sales-tax). Census $8.97M = **33× over-capture** → its match to Clay MO is invalid. Added to DROP. Implies **MO Census ASLGF is systematically unreliable**; **Clay MO 29047** (treated) also DROPPED (its baseline is MO-Census, untrustworthy; its only clean control is the dropped Texas MO).
- **Pickens SC 45077**: agent mixed bases (govwide baseline $27.1M, fund post $63.1M → spurious +133%). Corrected to **govwide both** ($27.1M→$46.9M, +73%).

**Powered re-run — `43_expanded_matched_did.py` (DROP now {18153, 48237, 29215, 29047}):**
| metric | N=6 (pre-wave) | **N=28 (post-wave)** |
|---|---|---|
| matched effect mean | +4.60%/yr (p=0.25) | **+1.92%/yr (t p=0.086)** |
| sign test | 5/6 pos | 19/28 pos (p=0.087) |
| treated CAGR vs 3.40% benchmark | +3.10% (p=0.42) | **+2.69%/yr (p=0.011)** ✅ |
| pooled OLS treated coef (+ state FE) | +3.84%/yr (p=0.060) | **+2.21%/yr, SE 1.20%, p=0.065, N=78** |
| bootstrap 95% CI | [-1.6%, +11%] | [-0.08%, +4.05%] |

**Interpretation:** usable treated 6→28 (4.7×). Effect size shrank (+3.84%→+2.21%) as the small sample's overstatement washed out — the reliable read is **DC-treated county-government property tax grows ~2 pp/yr faster** than matched controls; direction robust (19/28 positive), magnitude modest, significance marginal-to-significant. Cleanest significant result: **treated CAGR +6.09%/yr vs national 3.40% benchmark, excess +2.69%/yr, p=0.011.**

**Still open:** (a) each unblocked treated has only 1 clean control (rank-1); adding controls 2&3 would tighten the matched estimate. (b) Jackson AL (Russell AL baseline missing) and the 6 TN/KY/IN treated remain unaddressable via control scraping. (c) MO counties need source-audit baselines (Census unusable).

### 7.9 Treated-recovery wave 1 + re-run (2026-06-08)

The 123→34 treated attrition was traced (post-period source): 36 clean post, **43 v2-post-only (lost only because v2 disabled), 44 no-post** — all 87 keep a 2017 baseline, so recoverable by reading the post from the ACFR. Dispatched 13 agents for the top dropped treated by DC share (skipping 7 documented exclusions: Lawrence KY bundled; Pecos/Crane/Ward TX oil-collapse; Glasscock/Briscoe TX dup-unreliable; Mecklenburg VA scope).

**9 recovered** (added to `verified_two_endpoint_pt.csv`, now 45 rows): Morrow OR ($8.70M→$15.58M), Crook OR ($7.87M→$13.48M, Census baseline DOR-validated), Umatilla OR ($16.41M→$22.71M), Storey NV ($11.81M FY16→$22.77M), Dickens TX ($2.06M→$3.67M), Franklin NC ($46.79M→$62.69M; Census was 2.8× undercount), Cherokee NC ($18.47M→$21.79M), Wilkes GA ($4.95M→$4.88M flat), McDowell WV ($3.96M→$3.78M decline). **Dropped** (no usable FY17 baseline): Williams ND (Census $14.13M overstated vs true ~$11M → false decline), Childress TX (only FY19/20). **Not found** (audits exist offline): Milam TX, Knox TX.

**Two substantive findings:**
- **Abatement routing (OR SIP/enterprise-zone):** DC fiscal contribution arrives as **in-lieu / PILOT payments reported OUTSIDE the property-tax line** (Morrow FY24 SIP in-lieu = $11.7M, separate from the $15.6M PT line). A pure property-tax outcome understates DC impact in SIP states — measurement point for the paper.
- **High-share-but-flat counties recur:** Wilkes GA (37% share, PT flat) and McDowell WV (decline) join Washington GA — high nominal DC-share ≠ realized PT growth (abatement shielding), explaining the modest average effect.

**Re-run (N=28 → N=31 usable treated):**
| metric | N=28 | **N=31** |
|---|---|---|
| matched effect mean | +1.92%/yr (p=0.086) | **+1.90%/yr (p=0.094)** |
| treated CAGR vs 3.40% benchmark | +2.69% (p=0.011) | **+2.69%/yr (p=0.0067)** ✅ stronger |
| pooled OLS treated coef | +2.21% (p=0.065) | **+1.92%/yr, SE 1.16%, p=0.097, N=87** |
| bootstrap 95% CI | [-0.08, +4.05] | [-0.13, +4.03] |

**Constraint is still controls.** Adding 9 treated lifted usable only 28→31 because newly-recovered treated mostly lack a clean control. Current state: 43 treated have clean own data but only 31 are usable (12 control-blocked); 44 of 304 matched controls are clean. The treated-vs-benchmark result (p=0.0067) is the robust headline; the matched/OLS estimate (~+1.9%/yr, p≈0.09) will only tighten once controls fill in.

### 7.10 Measurement-error profile of Census 2017 baseline (for the paper's data section)

Empirical error rate from 42 hand-verified counties (verified ACFR value vs the Census 2017 ASLGF value we would otherwise use):

| Error band | Share of counties |
|---|---:|
| ≤5% (Census ~right) | 50% |
| 5–10% | 26% |
| 10–25% | 12% |
| 25–100% | 5% |
| >100% (gross) | 7% |

- **Median |error| = 4.9%** — the typical county's Census value is fine.
- **24% off by >10%, 12% by >25%, 7% catastrophically (>2×).** Errors are roughly symmetric (20 under, 18 over) → they do NOT cancel; they add noise plus a few bombs.
- **The fat tail is predictable by county type** (so verification can be targeted, not universal):
  - *Tiny TX oil/mineral counties* — Census wildly UNDERSTATES: McMullen +6,992%, Throckmorton +372% (ASLGF barely samples them).
  - *MO / NE small counties* — Census OVERSTATES: Texas MO −97%, Thayer NE −85% (cash-basis / scope mixing).
  - *Annual-sample-survey states (e.g., NC)* — Census UNDERCOUNTS: Franklin NC +180% (true $46.8M vs Census $16.7M).
  - *Large metro/suburban counties* — Census RELIABLE: PWC exact, Fulton −5%, most within 10%.
- **The post side (MuniSpot v2) is worse than the baseline** — v2 systematically under-captures (wrong in 6 of 8 flagged), so an unverified post is riskier than an unverified Census baseline.

**Implication:** Census-as-is is ~50/50 within 5% and ~3-in-4 within 10% — acceptable for a cross-section *average* but UNSAFE for any single county's growth ratio, because a 1-in-13 gross error manufactures a fake CAGR that dominates small-N estimates. Verification rule going forward: **always verify high-risk types (small oil/mineral/wind counties, MO/NE, sample-survey states); large normal counties may lean on Census.**

### 7.11 High-risk treated wave + REFINED error answer (2026-06-08)

Verified 16 high-risk-type treated (NC×3, GA×3, SC×3, AL, MS, OH, OK, SD, NE, TN-probe). **14 added** (verified file now 59 rows); **dropped** Monroe OH (Rover/REX natural-gas PIPELINE drove its PT surge, not DCs — confound) and Muskogee OK (cash/regulatory basis, ad valorem not isolable as clean all-funds). DROP now 8 counties.

**KEY UPDATE to the measurement-error answer — verifying the *predicted-high-risk* batch mostly REASSURED rather than corrected:**
- This batch: **83% within 5% of Census**, median |error| 0.9%. The NC sample-survey hypothesis was largely WRONG — Rutherford/Caldwell/Catawba NC were near-EXACT; only Franklin NC (earlier) was the 2.8× outlier.
- The two apparent "errors" are **scope/definition differences, not data errors**: Montgomery TN −28% (Census includes the school levy the county commission levies; we use county-only) and Jackson GA −16% (Census uses GROSS levy, ACFR is NET of GA LOST credit).
- Across all 49 independently-verified baselines: 53% within 5%, 75% within 10%, 12% off >25%. The >25% tail is **concentrated and predictable**: tiny counties (McMullen, Throckmorton, Texas MO, Thayer) + the one sample-survey outlier (Franklin NC). Mid-to-large counties in *every* state (including the "high-risk South") are reliable.
- **Revised guidance:** the dangerous cases are (a) very small counties and (b) state-specific scope/netting conventions (TN school levy, GA LOST) — NOT broad geography. Verify tiny counties and document the scope conventions; large counties can lean on Census.

**Re-run (N=33 usable treated):**
- Matched effect **+2.00%/yr (p=0.062), bootstrap 95% CI [+0.10%, +4.06%] — now EXCLUDES ZERO**; 22/33 positive.
- Treated CAGR vs 3.40% benchmark: **+2.94%/yr, p=0.0023** (strengthening as N grows).
- Pooled OLS: +1.75%/yr, SE 1.04%, p=0.093, N=101.

The estimate is stabilizing around **DC counties' property tax growing ~2 pp/yr faster**, and the matched-effect CI just crossed to exclude zero at N=33.

---

# 8. RESULT: the property-tax growth effect is regional, not DC-specific, once properly matched

**Bottom line for co-authors.** After expanding the verified sample to a credible size (41 treated, 65 matched controls), the 2017→latest growth in **county-government all-funds property tax** is **not robustly higher in DC counties than in their same-state matched controls.** DC counties do outgrow the *national* benchmark (+2.1%/yr, p=0.001), but that gap is largely a **state/regional** phenomenon: once we compare to same-state non-DC counties (matching) or absorb state fixed effects, the DC-specific differential collapses to ~+0.5%/yr and is statistically indistinguishable from zero. The earlier "+2–4%/yr" readings were a small-sample artifact.

## 8.1 The two estimates, side by side

| Estimate | Small verified sample (N≈33) | **Triangulated EXPANDED (41 treated / 65 controls)** |
|---|---:|---:|
| Treated CAGR vs **national** 3.40% benchmark | +2.9%/yr (p=0.002) | **+2.12%/yr (p=0.001)** ✅ significant |
| **Matched** effect vs same-state controls | +2.0%/yr (p=0.06) | **+0.68%/yr (p=0.33)** — not significant |
| Pooled OLS, treated + **state FE** | +1.75%/yr (p=0.09) | **+0.46%/yr (p=0.49)** — not significant |

The benchmark comparison and the matched/state-FE comparison disagree, and **the disagreement is the finding.** 2017–2024 was a high property-value era nationwide; same-state non-DC counties grew nearly as fast (~+4.8–5%/yr) as DC counties (~+5.5%/yr). The ~0.7 pp residual is what is plausibly DC-attributable, and it is not distinguishable from noise at this sample size.

## 8.2 Why we now trust the smaller number

- **Sample size.** The +2–4% figures came from ≤6–33 counties dominated by a few high-growth cases. The matched control group was the binding constraint (only 6 usable treated at one point). Expanding controls — the correct comparison group — is what pulled the estimate down.
- **Triangulation (Census × MuniSpot v2 level agreement).** For each county we have up to three independent FY2017 measures (Census ASLGF, v2, hand-read ACFR). Where Census-2017 and v2-2017 **agree within ±10%**, the baseline is corroborated by two independent sources — validated against hand-read truth in **6 of 6** test cases. Where they disagree, the level gap flags the county for hand-verification (it catches both v2 unit bugs, e.g. PWC ×1000, and Census sample-survey errors, e.g. Franklin NC −64%). This let us confirm ~⅔ of treated and many control baselines without reading every ACFR.
- **Measurement-error discipline.** Of 25 independently hand-verified treated baselines, only 1 (Franklin NC) was a genuine >25% data error; ~76% were within 10% of Census. The gross errors are predictable (tiny counties; state scope conventions like the TN school levy and GA LOST netting), so verification was targeted, not blanket.

## 8.3 Important caveats before concluding "no effect"

1. **Abatement routing.** In SIP / enterprise-zone states (OR, and similar), the DC fiscal contribution arrives as **in-lieu / PILOT payments reported *outside* the property-tax line** (e.g., Morrow OR: $11.7M FY24 in-lieu, separate from the PT line). A pure property-tax outcome **mechanically understates** the DC effect where abatements dominate — which is most large DC deals. A PILOT-inclusive revenue outcome could restore an effect. *Recommended next test.*
2. **High-share-but-flat counties.** Several high-DC-share counties show flat/declining PT (Washington GA, Wilkes GA, McDowell WV) — consistent with abatements shielding the base. This drags the average toward zero but is itself a substantive result (abatements neutralize the near-term property-tax channel).
3. **Coverage selection.** 70 treated are Census-only (no v2), excluded from the expanded test — these skew rural/small. The expanded sample tilts toward counties with v2 coverage.
4. **Outcome scope.** This concerns *level/growth of county-government property tax* only. It does **not** overturn the earlier bond-spread result (−23 bps) or the cross-sectional mechanism evidence; those use different identification.

## 8.4 What this means for the paper

The clean, defensible statement is: **"Using a same-state matched-control design on hand-verified and triangulated county financials, we find DC counties' property-tax growth is not statistically distinguishable from comparable non-DC counties in the same state over 2017–2024, despite outgrowing the national average — a gap driven by regional trends. The near-term property-tax channel appears muted, consistent with the prevalence of abatements that route DC contributions into PILOT/in-lieu revenue outside the property-tax line."** This is a more honest and arguably more interesting story than a mechanical "DCs raise property taxes," and it sets up the abatement/PILOT and bond-market channels as where the action is.

**Files:** `scripts/python/44_triangulated_did.py`, `data/derived/triangulated_did_results.md`, `data/derived/triangulated_baseline_status.csv` (per-county provenance: VERIFIED / CONFIRMED / CONFLICT / SINGLE_census).

### 8.5 Triangulation v2 (CENSUS_TRUST tier) + CONFLICT resolution + a new Census error mode (2026-06-08)

Added a **CENSUS_TRUST** tier: accept a single-source Census-2017 baseline for LOW-RISK counties (Census reliable there), gating HIGH-RISK ones (KY/TN bundling; TX Census<$6M oil; any Census<$3M) for hand-verification. Post from hand-ACFR / ACFR-wide / gated v2. Three tiers: PRIMARY (hand-both) ⊂ EXPANDED (+triangulation-confirmed) ⊂ FULL (+census-trust).

**Resolved all 6 CONFLICT treated by reading the ACFR — and found a NEW Census error mode:**
- **Census OVER-counts in "collector" states.** Iowa counties are the tax collector for cities/schools, so Census ASLGF lumps those in: Polk IA Census $209.8M vs true **$149.2M** (+41%); Dallas IA $26.5M vs **$22.3M** (+19%); Nueces TX $108.9M vs **$80.2M** (+36%, hospital-district levy mis-attributed). v2 was RIGHT in all three.
- **v2 over-counts when it sweeps in school districts:** Venango PA v2 $106.7M vs true **$11.1M** (9.5×); Census right.
- Medina TX: v2's "FY2017" was FY2018 mislabeled; v2 post $55M is a data error (true FY23 $25.9M).
- **The triangulation gate caught every one** — they surfaced as CONFLICT precisely because the two sources diverged. Residual risk: SINGLE_census counties in collector states with no v2 to flag them (silently over-counted). Since an over-counted baseline *understates* growth, the FULL effect is if anything a **lower bound**.

This complements §7.10's "Census under-counts small/sample-survey counties": Census errors are **bidirectional** — under-counts tiny/sample counties, over-counts collector-state counties. Both are caught by Census×v2 triangulation; only SINGLE_census (no v2) is exposed.

**Updated result (5 conflicts added; verified file 64 rows):**
| Sample | matched N | matched effect | OLS (+state FE) |
|---|--:|--:|--:|
| PRIMARY (hand-both) | 5 | +1.53% (n.s.) | — |
| EXPANDED (+confirmed) | 29 | +0.56% (n.s.) | — |
| **FULL (+census-trust)** | **70** | **+1.31%/yr, p=0.026** | **+1.35%/yr, p=0.020, N=208** |
| Treated CAGR vs 3.40% bench | — | +2.27%/yr (p<0.001) | — |

**Synthesis:** the matched DiD effect is **modest (~+1.3 pp/yr) and statistically significant in the full triangulated sample**, but the smaller most-verified subsample (EXPANDED, N=29) is underpowered and not significant. The point estimate is consistently positive and small — well below the +2–4% the early ≤6–33-county samples implied. Honest headline: **DC counties' county-government property tax grows ~1.3 pp/yr faster than matched same-state controls (p≈0.02); the effect is real but modest, and much of the raw gap vs the national benchmark is regional trend.** Usable treated now 78 (matched 70); the remaining ~38 are mostly structural dead-ends (KY/TN bundling, TX oil) — the practical ceiling.

### 8.6 Full treated recovery — 97/123 usable; result converged (2026-06-08)

Pushed to maximize treated: added 20 recovered counties → **usable treated 78 → 97** (verified_two_endpoint_pt.csv = 84 rows).
- **EASY 10** (low-risk, baseline trusted, needed only a post): all recovered incl. Clark NV ($622M→$1,067M), Washington OR/Intel, Salt Lake UT, Racine WI/Microsoft, Laramie WY ($13.3M→$28.0M), Pottawattamie IA/Google, Luzerne PA, Montrose CO. (Cass MI via v2; Big Horn MT no post online.)
- **TN re-probe — ALL 10 recovered.** Earlier "KY/TN bundled = dead" was WRONG for TN: large TN counties file GAAP Comptroller AFRs whose "Schedule of Detailed Revenues" separates *Current Property Tax* (only the small regulatory/cash-basis filers bundle). Recorded **county-only** (excl discretely-presented school CU); Census for TN ≈ county+school (~2×). KY (7) remains truly bundled (dead).
- No-baseline: Silver Bow MT recovered (not yet in matched design); Mayes OK failed (OK cash-basis, ad valorem not separable).

**Result CONVERGED:** despite usable treated growing 65→74 matched, the estimate barely moved:
| Sample | matched N | matched effect | OLS |
|---|--:|--:|--:|
| EXPANDED (most-verified) | 29 | +0.56% (n.s.) | — |
| **FULL** | **74** | **+1.25%/yr, p=0.025** | **+1.26%/yr, SE 0.56, p=0.025, N=227** |
| Treated vs 3.40% bench | — | +2.14%/yr (p<0.001) | — |

**Final headline:** DC-treated counties' county-government property tax grows **~1.25 pp/yr faster** than matched same-state controls (p≈0.025, bootstrap CI [+0.2, +2.3]); robust to state FE; stable as the sample grew from 6 → 74 matched treated. Modest, real, far below early small-sample +2–4%. **Practical ceiling reached: 97/123 usable; remaining ~26 are mostly structural dead-ends (KY bundling, TX oil, scope-drops).** Two scope notes for co-authors: TN figures are county-only (Census doubles via school levy); collector-state Census over-count (IA/WY) handled by triangulation.

---

# 9. Maximizing the matched sample: V2 audit of the unused, and Census-division matching (2026-06-08)

Two moves this session push usable treated to **101** and let **all 101 enter the matched DiD at 1:3**.

## 9.1 V2 audit of the 23 still-unused treated — 1 genuine recovery, the rest confirmed dead

Queried Raj's **MuniSpot v2** parquet (all `class_1` buckets, all `column_index`, all FY) for every one of the 23 unused treated FIPS, to ask: does V2 hold *anything* we can use, even rows our narrow `tier_with_pilot` filter rejects?

- **8 of 23 have V2 rows; 15 are absent entirely** (9 TX-oil counties, 4 small KY, Muskogee OK, Martin IN — V2 simply never extracted them).
- Of the 8 with rows, V2 **confirms why most are dead rather than rescuing them:** the three KY counties (Lawrence/McCracken/Pike) show only a single bundled `TAX REVENUES → "Taxes"` line — the property-tax-occupational-net-profits bundling, visible in the vendor's own normalized extract. Clay MO, Big Horn MT, Williams ND show bundled/oil-contaminated tax lines with no separable property-tax revenue. Monroe OH has a clean PT line but only to FY2020 and is a gas-infrastructure confound, not a DC.
- **The one real win: Mecklenburg County VA (51117)** — home of Microsoft's **Boydton** data-center campus. It had been stuck in CONFLICT (Census $29.7M vs V2 $54.2M — the CLAUDE.md "scope mismatch" gotcha). V2 carries a clean, internally-consistent `PROPERTY TAX REVENUES` series **FY2016→FY2024 ($43.9M → $113.7M)**. An independent pull of the **Virginia APA Comparative Report** (Exhibit B, "Total General Property Taxes") **matched FY2024 to the dollar ($113,716,079)** and confirmed the scope is county-government, locality-wide (excludes school board + towns) — exactly right. **74% of the base is Personal-Property-General ($84.1M)**: Boydton's servers taxed as business personal property. Added to `verified_two_endpoint_pt.csv` (FY2017 $54.17M → FY2024 $113.72M, +11.2%/yr). This resolves the old "drop Mecklenburg" instruction: that was a symptom of lacking a consistent-entity series, which V2 supplies.

**Takeaway for co-authors:** the search has bottomed out. Every remaining unused treated is dead for a *documented structural reason* (KY bundling shown in V2; TX-oil absent + confounded; OK/MO cash-basis), not for lack of effort — and no other source (ACFR PDF, state portal) will isolate a property-tax-only number where the audited financials themselves bundle it. Usable treated = **101 / 123**.

## 9.2 Why we relax matching from same-state to same-Census-division

Same-**state** matching (the strict design) nets out state-specific shocks — property-tax caps, statewide reassessment cycles, state-aid formulas — the cleanest counterfactual. But 24 usable treated couldn't fill 1:3 because their state had too few verified never-DC controls. To use all 101, we fall back **one notch** to the **Census division** (state preferred; division fills the remaining slots). Division matching still removes broad regional trends (Sun-Belt growth, Rust-Belt decline) but admits cross-state differences in tax law — a real loosening, so we keep `match_tier` per pair and can report state-only and state+division samples side by side.

The US Census Bureau's **9 divisions** (state FIPS in parentheses):

| Division | States |
|---|---|
| New England | CT (09) ME (23) MA (25) NH (33) RI (44) VT (50) |
| Middle Atlantic | NJ (34) NY (36) PA (42) |
| East North Central | IL (17) IN (18) MI (26) OH (39) WI (55) |
| West North Central | IA (19) KS (20) MN (27) MO (29) NE (31) ND (38) SD (46) |
| South Atlantic | DE (10) DC (11) FL (12) GA (13) MD (24) NC (37) SC (45) VA (51) WV (54) |
| East South Central | AL (01) KY (21) MS (28) TN (47) |
| West South Central | AR (05) LA (22) OK (40) TX (48) |
| Mountain | AZ (04) CO (08) ID (16) MT (30) NM (35) NV (32) UT (49) WY (56) |
| Pacific | AK (02) CA (06) HI (15) OR (41) WA (53) |

Implemented in `scripts/python/45_division_matched_sample.py` (matching ladder: same-state nearest-3 by |log baseline-PT|, then same-division to fill to 3; with replacement; output `data/derived/division_matched_pairs.csv`).

## 9.3 Resulting sample composition (after the TN-control recovery in §9.4)

| | Count |
|---|--:|
| Usable treated entering at 1:3 | **101 / 101** (0 partial) |
| Filled same-state only | 80 |
| Needed ≥1 division control | 21 |
| Pairs total (state / division) | 303 (270 / 33) |
| Unique controls used | 130 / 137 usable |
| Matches within 0.5×–2× PT band | 74% (median \|log ratio\| 0.18) |

By division — usable treated / usable controls / treated needing fallback:

| Division | Treated | Controls | Need fallback |
|---|--:|--:|--:|
| Middle Atlantic | 5 | 7 | 0 |
| East North Central | 10 | 12 | 3 |
| West North Central | 13 | 14 | 4 |
| South Atlantic | 27 | 37 | 0 |
| East South Central | 15 | 10 | 4 |
| West South Central | 13 | 31 | 0 |
| Mountain | 10 | 9 | 10 |
| Pacific | 8 | 17 | 0 |

**Residual fragility to carry into the tests.** Max control reuse is now **8×** (Bedford TN, Coffee TN — mid-size controls anchoring several mid-size TN treated), down from 15× before the TN-control wave; reuse is otherwise flat (50 controls used once, median twice). The **Mountain** division remains thin (10 treated / 9 controls, all needing some cross-state fallback) because DC-treated Western counties (NV, AZ) sit in states with few verified never-DC controls — a candidate for a later recovery wave if we want it fully same-state. **Implications for the tests:** (i) cluster SEs on the control county, (ii) show an ESC-dropped robustness column, (iii) read the division-relaxed estimate as a robustness layer over the strict same-state result. Tests not yet run — sample built and reviewed only.

## 9.4 TN-control recovery wave — dissolving the East-South-Central bottleneck (2026-06-08)

The first division-matched build had a real defect: East South Central held 15 usable treated (mostly the recovered TN counties) but only **3 usable controls** (Russell AL, Baldwin AL, one MS), because TN's own controls looked bundling-dead. Those 3 were reused ~15× and would have driven the ESC counterfactual single-handedly. Rather than test on that, we fixed it at the source.

**Insight:** if TN *treated* baselines were recoverable from the TN Comptroller GAAP AFRs (their "Schedule of Detailed Revenues" separates *Current Property Tax*), then TN *controls* are recoverable the same way. V2 confirmed it couldn't help — no TN control candidate has a clean V2 property-tax line (all bundled "Taxes"). So we ran 8 Sonnet+firecrawl agents on never-DC TN counties spanning the treated size range, pulling **county-primary-government-only** Current Property Tax (excluding the discretely-presented School Department CU).

**7 of 8 recovered** (added to `verified_two_endpoint_pt.csv` as controls):

| County | FIPS | Baseline | Post | CAGR |
|---|---|---|---|--:|
| Coffee | 47031 | FY17 $14.14M | FY24 $16.68M | +2.4% |
| Bedford | 47003 | FY17 $13.33M | FY24 $22.92M | +8.0% |
| Sevier | 47155 | FY18 $32.65M | FY24 $45.05M | +5.5% |
| Sullivan | 47163 | FY18 $44.74M | FY23 $52.94M | +3.4% |
| Cheatham | 47021 | FY18 $14.71M | FY24 $21.73M | +6.7% |
| Blount | 47009 | FY18 $47.00M | FY23 $56.62M | +3.8% |
| Stewart | 47161 | FY16 $5.04M | FY24 $6.60M | +3.4% |

Anderson (47001) was dropped — only an imprecise FY2017 baseline was available, and an overstated control baseline would bias the treated-minus-control gap *upward*, the wrong direction to fudge. Two data notes: (a) the TN Comptroller web archive starts at **FY2018** (FY2017 PDFs mostly 404), so 5 of 7 anchor at the earliest clean year (FY2016/2018) — fine in an annualized-CAGR design, and consistent with the file's existing mixed-baseline practice; (b) Census ≈ county + school (~2×), so these county-only figures are roughly half the Census line — the correct scope, matching the TN treated. Result: usable controls 130 → **137**, ESC controls 3 → **10**, max reuse 15× → 8×, in-band match quality 68% → 74%.
