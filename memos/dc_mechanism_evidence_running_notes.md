# DC Mechanism Evidence — Running Notes

Findings surfaced during the Tier 1–4 ACFR-scrape sprint (June 2026). Each entry is a candidate for paper anecdote, presentation slide, or robustness check. Updated as agents complete.

**Source files**: `data/external/acfr_pdfs/<county>/raw_pdfs/*.pdf` and `.firecrawl/<county>_acfr.md`
**Master table**: `data/derived/acfr_county_year_extracted_wide.csv`

---

## 1. PILOT / FILOT — Direct DC fiscal-channel evidence

These are the cleanest mechanism-evidence findings: payments documented in county ACFRs that exist *because* of negotiated industrial / DC tax-incentive agreements.

### Racine County WI (55101) — FY2023 — Foxconn analog (cautionary case)
- **2017: County issued $110M Taxable GO Bonds for Foxconn megaproject** (Mount Pleasant)
- Bonds secured by special assessments on Foxconn-controlled properties — directly analogous to DC FILOT/PILOT structures
- FY2023 status: **partial defeasance underway** ($18.4M applied in 2023)
- **Special item FY2023: $28.8M proceeds from land sale** (used for debt service / defeasance) — Foxconn returning land
- **FEWI Development Corp (Foxconn entity) = #1 principal property taxpayer**: $1.23B taxable AV = 3.79% of total county AV (up from 2.40% in 2014)
- Foxconn project under-delivered on jobs → county now unwinding via land sale
- **Paper relevance — multi-purpose**:
  - **Natural-experiment analog**: this is the cleanest non-DC parallel to a DC mega-deal. Mega corporate investment + county-issued debt + special-assessment mechanism + (here) underperformance.
  - **Cautionary case study**: shows the downside path — what happens when the corporate investment doesn't materialize as promised. Counties that issued debt against expected DC growth could face similar unwinds.
  - **Methodological**: helps frame "what would the counterfactual look like" — Racine's debt issuance pattern, special-assessment mechanism, and 2017-2023 fiscal arc are all observable
- Stand-alone Section 2 candidate in the paper ("Comparable Mega-Deals: Lessons from Foxconn")

### Spartanburg County SC (45083) — FY2023 — best-documented FILOT mechanism in sample
- **FILOT abatements: $23,872,245** + **SSRC (Special Source Revenue Credits): $8,117,413** = **$31,989,658 total ED abatements**
- = 25% of GF property tax revenue ($94.2M)
- True gross PT absent FILOT would be ~$118M (instead of $94.2M)
- **Mechanism explicitly documented in ACFR**:
  - SC tiered assessment: real property 4-6% of market value; personal property normally 10.5% (incl. DC servers/equipment)
  - **FILOT reduces personal property assessment ratio from 10.5% to 6% or 4% (40-60% reduction)**
  - County millage FY2023: 110.9 mills (106.2 operating + 4.7 debt service)
- **Top taxpayer BMW Manufacturing**: 4.9% of assessed value = $75.4M AV, $27.0M taxes paid — on FILOT
- Milliken & other industrials also on FILOT
- **MD&A narrative explicit**: "increased fee-in-lieu-of-tax payments (~$1.5M)" drove FY2023 PT increase
- **Paper relevance**: this is the most cleanly documented FILOT mechanism in our sample. Better than Berkeley SC because (a) larger absolute amounts, (b) explicit MD&A narrative tying FILOT to PT growth, (c) top-taxpayer documentation, (d) explicit "counterfactual gross" quantification. **Use as the master FILOT case study in the paper's mechanism section.**

### Berkeley County SC (45015) — FY2023 — flagship anecdote
- **FILOT (Fee-In-Lieu-Of-Taxes): $20.7M in General Fund, $27.0M all-funds**
- Equals **53%** of GF property tax revenue, **55%** of all-funds PT
- Berkeley County is where Google's Goose Creek DC and Volvo plant sit
- SC's industrial-recruitment mechanism; the FILOT structure essentially redirects what would be standard PT into a negotiated long-term fee schedule
- **Paper relevance**: Berkeley SC is a cleanly DC-tied FILOT case — Google is one of the major FILOT counterparties. Complements Spartanburg as a paired-evidence pair (Spartanburg = mechanism master case, Berkeley = DC-specific example).

### Madison County AL (01089) — FY2024
- Tax abatement disclosure: **single IT company beneficiary received 90% property tax abatement worth $4,075,567**
- Almost certainly Meta or Google's Huntsville DC
- Auto manufacturer abatement: $888,250 (77%); industrial abatement: $2,835
- **Paper relevance**: Documented DC-specific tax abatement at $4M scale, in a county where Meta and Google have major DCs

### Douglas County GA (13097) — FY2023
- **$4,150,000 in property tax abatements in 2023** under county economic development incentive program (agent flagged as "likely includes DC-related personal-property tax abatements")
- **Paper relevance**: Quantified abatement that materially reduced county PT revenue — useful for showing fiscal cost of attracting DCs

### Marshall County KY (21157) — FY2023
- **In Lieu Tax Payments: $795,675** in General Fund
- KY regulatory-basis reporting; no counterparty named
- 43% DC share — almost certainly DC PILOT
- **Paper relevance**: Substantial PILOT for a $3M-property-tax county; ratio of PILOT to regular PT = 26%

### Lawrence County KY (21127) — FY2022
- **In Lieu Tax Payments: $180,000** in General Fund
- **191% DC share — our highest-share treated county**
- Small county ($1.4M GF PT, $6.5M PT base 2017)
- **Paper relevance**: Likely DC PILOT for the highest-share county in our treated set. Headline candidate.

### McCracken County KY (21145) — FY2022
- **In Lieu Tax Payments: $926,467** in General Fund
- No named counterparty in audit notes
- 3% DC share — modest, so this PILOT may be partly non-DC industrial
- **Paper relevance**: Worth investigating whether $926K is mostly DC or other industrial

### Jackson County KY (21109) — FY2022 — small-county surprise
- **Personal property tax: budgeted $1,000, actual collected $167,849 — 168× the budget**
- Exact signature of a new DC's tangible-property hitting the rolls mid-year and surprising the county budget process
- Plus $83,219 in-lieu payment (unattributed)
- Caveat: audit had disclaimer of opinion due to 13 internal-control findings (use with quality caveat)
- **Paper relevance**: Striking small-county mechanism evidence — a county clearly unprepared for the magnitude of new DC assessment. Even if quality caveat applies, the budget-vs-actual delta is the story.

### Pike County KY (21195) — FY2022 — null finding
- In Lieu Tax Payments: $1,526 — de minimis
- Tax abatement disclosed: only an occupational tax abatement for MC Mining / Excel Mining at $16,547 (coal, not DC)
- **Paper relevance**: Useful as a low-DC-share comparison case (5% share, no DC-specific incentives surfaced)

### Calloway County KY (21035) — FY2021 — hospital PILOT, not DC
- In Lieu Tax Payments: $124,758 — agent identifies as likely Murray-Calloway County Hospital PILOT (standard KY DLG line)
- 9% DC share, so the PILOT is probably NOT data-center-related
- **Paper relevance**: Cautionary case — not every KY PILOT in our table reflects DC activity. Worth a robustness probe to disentangle DC vs hospital/utility PILOTs.

### Ellis County TX (48139) — FY2022 — TX Local Govt Code §312 abatement, DC-adjacent
- **$1,643,747 tax abatement FY2022** under TX Local Government Code **§312** (NOT Chapter 313; §312 is county-level abatement in reinvestment zones)
- Single named agreement: **Sharka LLC** under "**Midlothian Technology Commercial Industrial Tax Abatement Reinvestment Zone #14**"
- Terms: **85% improvement value + 100% personal property value abated for 10 years**
- **Paper relevance**: The wording is directly DC-adjacent — "Technology Commercial Industrial" reinvestment zone + "100% personal property value" abatement matches DC structures (server equipment is the personal property). This is a likely DC-related abatement under a different statutory name. Worth verifying Sharka LLC's business type via county economic development records.
- GF PT $53.3M / AF PT $69.4M (ratio 1.30×)

### Beaver County PA (42007) — FY2023 — abatement structure unclear
- Tax abatement programs listed: LERTA, KOZ, Clean and Green
- **No dollar amounts disclosed** — PA doesn't require GASB 77 disclosure unless material
- **Paper relevance**: Highlights a data limitation — some states' ACFRs don't surface the abatement dollar amounts even when programs exist

---

## 2. State PT-structure findings (analytical implications)

These shape how we aggregate property tax across counties and what coverage means.

### Ohio — categorical-levy structure + **business TPP abolished** (huge for DC share)
- **Licking OH**: GF PT only $5.8M of $37.6M total PT (15% in GF)
- **Franklin OH**: GF PT $65.8M of $531.8M total PT (12% in GF)
- **Union OH**: GF PT $8.06M of $19.6M total PT (41% in GF — smaller county)
- **Fairfield OH**: GF PT $13.5M of $49.8M total PT (27% in GF)
- OH counties route most PT to voter-approved categorical funds (Developmental Disabilities, Children's Services, Mental Health, Senior Services, Library, Roads)

**CRITICAL ADDITIONAL FINDING (from Union OH agent)**: **Ohio abolished business tangible personal property (TPP) tax in 2005-2011** (phased out over 6 years). Implication: **DCs in OH counties are taxed only on real property (building shell + land), NOT on the servers/cooling/generators that make up 70-90% of DC asset value.** This is structurally different from KY, VA, TX, AL, GA, NC etc.

- AWS $2B two-site DC in Jerome Township (Union OH) started construction 2023 — even when on tax rolls, will only pay PT on the buildings, not the equipment
- Implication for DC share formula: **OH counties' DC share should be cut by ~70-90% to reflect the missing personal-property tax base** that's available in other states
- This is one of the most consequential single-state corrections we've found. Applies to Licking, Franklin, Union OH, Fairfield (4 of our treated counties).
- **Implication for v2 GF-column**: still systematically undercounts true county-level PT by ~85% for OH categorical structure. All-funds figures essential.

### Missouri — fragmented levy structure
- **Clay MO**: county retains only its own ~$0.31/$100 levy
- Schools, cities, libraries each levy separately through the same collector but those don't flow through the county ACFR
- **Implication**: MO counties' fiscal exposure to DCs is structurally smaller than other states. The $287M DC base × DC share calculation overstates Clay MO's county-government fiscal exposure. Most DC PT goes to non-county recipients.

### Nebraska — clean consolidated
- **Sarpy NE**: GF $64.6M ≈ AF $67.3M (ratio 1.04×)
- NE counties keep most PT in GF; clean GASB format
- **Implication**: NE counties give cleanest measurement; useful as a structural anchor

### Alabama — clean consolidated
- **Madison AL**: AF ≈ GF (ratio 1.0×)
- AL counties use straightforward ad-valorem labels

### Kentucky — consolidated, BUT "Taxes" line is impure
- **Lawrence KY, Marshall KY, Pike KY, McCracken KY**: AF/GF ratio ~1.0-1.1× on PT line
- **IMPORTANT CORRECTION (from Calloway KY agent)**: the "Taxes" line in KY Fiscal Court regulatory-basis audits combines ad valorem property taxes AND occupational license taxes (payroll/net-profits). It is NOT pure property tax. Our KY entries currently overstate PT.
- The clean source for KY property tax specifically is the **Sheriff's Tax Settlement audit** (e.g., `2023CallowaySTS-audit.pdf`) at auditor.ky.gov — separate document from the Fiscal Court audit.
- **Action item**: For all KY counties in our master table, mark the property_tax figure as "Taxes line, includes occupational tax" and queue a follow-up sprint to pull Sheriff's Tax Settlement audits for clean PT decomposition.
- KY all-funds revenue ratio higher (2-3.5×) due to non-PT revenue in other funds

### Georgia — semi-split + **IDA leasehold-bond mechanism for DC abatement**
- **NEWTON GA**: County-wide tax digest grew **26% in FY2023 alone** + millage rolled back from 11.145 → 9.45 mills (digest-surge rollback policy)
- **CRITICAL FINDING from Newton GA agent**: Stanton Springs hosts Meta, Takeda, Rivian (per MD&A) but **no DC entities appear in top-10 taxpayers**. Top is Bard pharma at 1.46% of AV.
- Agent's interpretation: **Newton County Industrial Development Authority (IDA) issues leasehold revenue bonds that hold title to DC equipment, making the assets effectively tax-exempt at the county level**. DC tax benefit flows through IDA PILOT payments (in IDA separate financial statements), NOT through county direct levy.
- No GASB 77 disclosure in county ACFR — the IDA is a discretely presented component unit with separate financials
- **Paper relevance — GA mechanism**: This is the Georgia analog to SC FILOT. Different statutory wrapper (IDA leasehold bonds vs SC FILOT) but functionally equivalent: a public-authority structure that wraps the corporate asset and converts standard PT into a negotiated payment. Worth direct comparison in the paper's state-mechanism section.
- Other GA semi-split (SPLOST handling)
- **Cook GA**: GF $8.1M / AF $13.6M (1.7×)
- **Whitfield GA**: GF $20.1M / AF $30.9M (1.9×) — Special Fire District drives the gap
- **Douglas GA**: GF and AF both $112.5M (agent excluded Unincorporated Service Area millage; would push AF to $124.4M if included)
- **Fulton GA**: GF $646.6M / AF $697.5M
- **Implication**: GA SPLOST funds carry sales-tax revenue, NOT property tax — must distinguish

### Washington — mixed-levies
- **Pend Oreille WA**: GF $4.6M / AF $8.3M (1.8×)
- **Grant WA**: GF $21.4M / AF $32.6M (1.5×)
- WA BARS code 3111000 = property tax specifically; the broader "310 Taxes" aggregate includes sales/REET — must use 3111000 sum across funds for clean PT
- **Implication**: WA counties have multiple substantial fund levies (Road, Mental Health, Veterans, DD); GF undercount is meaningful (~30-50%)

### Illinois — semi-split with Replacement Tax exclusion
- **DeKalb IL**: GF $18.4M / AF $27.0M (1.5×)
- "Replacement Tax" (Personal Property Replacement Tax) is state corporate tax distributed to local govts — NOT property tax; must exclude

### Pennsylvania — consolidated
- **Beaver PA**: GF $57.4M ≈ AF $57.4M (1.0×) — all PT in GF
- **Luzerne PA**: GF $130.7M / AF $134.9M (1.03×) — nonmajor funds carry small debt-service PT
- PA uses "Real Estate Taxes" as the legal label
- **Implication**: PA is structurally close to consolidated

### Oklahoma — regulatory-basis quirk
- **Mayes OK**: "County General" receipts apportioned = $14.3M (proxy for PT, but not clean)
- OK regulatory cash basis doesn't break out PT from other receipts at fund level
- **Implication**: OK counties' figures are approximations; flag in analysis

### North Dakota — unified mill levy
- **Dickey ND**, **Stutsman ND**, **Grand Forks ND**: variable AF/GF ratios (1.5–2.3×) reflecting Road & Bridge fund separate millage
- **Williams ND** (Bakken): "Taxes" line bundles property tax with oil/gas extraction tax — extraction problem; agent couldn't isolate PT
- **Implication**: Most ND counties give clean PT (no county sales/income tax); Bakken counties contaminated

### Arizona — multiple blended districts
- **Maricopa AZ**: GF $658M + Flood Control $76M + Library $26M = $760M total PT
- AZ counties bundle multiple districts as blended component units
- **Implication**: All-funds PT requires summing the bundled districts

### Nevada — ad valorem clean, but watch Consolidated Tax
- **Clark NV**: GF ad valorem $423.7M / AF ad valorem $956.5M (ratio 2.26×)
- LVMPD (Las Vegas Metro Police Dept) has its own $188M ad valorem levy — included in AF
- **CRITICAL DISTINCTION**: GF "Taxes" line ($701M) bundles ad valorem + gaming tax + franchise + others. The clean property tax is the "Ad Valorem Taxes" sub-line ($423.7M) from the budgetary basis schedule.
- **Consolidated Tax** ($843M to GF) is state-distributed sales/gaming revenue, NOT property tax — correctly reported as Intergovernmental, not Taxes
- NV constitutional cap: $3.64/$100 AV combined; 3%/yr increase cap on owner-occupied residential, 8% on other

### Washington — confirmed mixed-levies; PT subset of "310 Taxes"
- **Grant WA, Douglas WA, Pend Oreille WA**: GF "310 Taxes" includes sales tax + REET + lodging — broader than property tax
- For clean PT, use **BARS code 3111000** sum across all funds that levy property tax
- Typical funds carrying separate PT levies: 001 General + 101/119 County Roads + 104 Veterans + 108 Mental Health + 125 DD Residential

### Indiana — circuit-breaker, LIT-PTR exclusion
- **St. Joseph IN**: GF PT $45.8M / AF PT $68.4M (1.49×)
- **CRITICAL**: LIT-PTR (Local Income Tax-Property Tax Replacement) shows up in custodial fund 6203 ($64.9M for St. Joseph). This is a state mechanism — Local Income Tax distributed to local governments as a property-tax replacement subsidy — and must be EXCLUDED from property tax line.
- Also: Settlement Fund (fund 6000) is a pure tax-distribution pass-through ($361M in St. Joseph) — exclude from all-funds revenue to avoid double-counting
- IN circuit-breaker caps PT at ~1-2% of AV by property class

---

## 3. Counties to use as analytical anchors (not DC-driven)

### Salt Lake County UT (49035) — robustness anchor
- GF PT $182.7M / AF PT $358.5M (huge county)
- **No DC operator appears in top-10 taxpayers**; Rio Tinto/Kennecott dominates at $3.55B taxable value
- 1% DC share is real but small relative to $189B county-wide assessed value
- **Use**: Robustness check; large county where DC is a tiny fraction. Tests whether our DC effects survive when a county's economy is dominated by other industries.

### Clark County NV (32003) — robustness anchor (gaming-dominated)
- GF ad valorem $423.7M / AF $956.5M (huge county)
- **No hyperscale DC in top-10 taxpayers**; casino REITs dominate (VICI $4.0B AV, Blackstone $1.99B AV)
- Switch Data Center (SwitchNAP) presence is real but absorbed into the $8.66B general personal property roll (7.2% of total AV)
- **Use**: Robustness check; county economy dominated by gaming + hospitality where DC is one of many large industrial users.

---

## 4. Coverage / data-quality caveats

### Williams County ND (38105) — extraction-blocked
- Bakken oil county; "Taxes" line bundles PT + oil extraction tax + production tax
- Agent could not disentangle PT cleanly from the gov-funds statement alone
- FY2021 is latest available (FY2022/2023 not posted to ND auditor portal)
- **Implication**: Williams ND should be marked as PT-uncertain in our master table; may need state PT distribution data to back out

### Dickey ND (38021) — anecdote claim can't be cross-validated from ACFR
- Our intensity data shows 145% DC share — highest in entire treated set
- ACFR has consolidated "Taxes" line ($1.5M GF, $3.4M AF) with no DC breakdown
- No PILOT, no abatement notes, no top-taxpayer disclosure pointing to a DC
- **Implication**: The 145% share claim depends on our intensity proxy (MW capacity-based) but isn't visible in the county's audited financial statements. Need to verify the DC's existence/scale via S&P 451 records before using as a headline anecdote.

### Audit-quality caveats
- Jackson KY: disclaimer of opinion (13 findings)
- Williams ND: material weakness flagged (no internal capacity to prepare GASB notes)
- Use these with caveats; quality varies sharply across small-county audits

---

## 5. Anecdote shortlist for paper / presentations

Ordered by storytelling power, given current evidence:

1. **Berkeley SC FILOT structure** — $20.7M GF FILOT (53% of PT). Strong, quantified, multi-DC, well-documented. Best new finding from this sprint.
2. **Lawrence KY** (191% DC share + $180K PILOT, tiny county) — the David-and-Goliath frame.
3. **Madison AL — Meta/Google 90% abatement worth $4M** — direct DC-specific corporate name attached (when verified via county economic development records).
4. **Jackson KY budget shock** — personal property tax actuals 168× budget. Storytelling power if the audit-quality caveat can be managed.
5. **Douglas GA $4.15M abatement** — quantified but DC-specific attribution unclear.

---

## 6. Treatment heterogeneity — real data centers vs. crypto miners (2026-06-10)

**The cleanest heterogeneity result in the project so far, and a paper-worthy finding in its own right.**

A treatment-validity audit (S&P 451 `PROVIDERTYPE`) revealed the "data center" treatment is two economically distinct populations: **hyperscale/colocation DCs** (Google/Microsoft/Meta/AWS-type — stable cloud-service tax base, permanent infrastructure) vs. **cryptocurrency-mining facilities** (Bitcoin miners — BTC-price-driven, often leased/abated, transient). Crypto dominates the *highest* DC-share counties (Dickens TX 181%, Milam 157%, Franklin NC 131%, Cook GA 122% — all crypto), because miners chase cheap rural power and so dominate small tax bases.

**Raw evidence (finalized treated PT, county-government scope, operating-by-2022, median annualized CAGR vs. ~3.4 %/yr matched-control benchmark):**

| Treatment type | n | Median PT CAGR | Excess vs benchmark |
|---|---|---|---|
| **Clean hyperscale/colo** | 39 | **+5.57 %/yr** | **+2.2 pp** |
| Crypto-mining | 35 | +3.84 %/yr | +0.4 pp |
| Mixed | 18 | +4.60 %/yr | +1.2 pp |

**Reading:** real data centers materially expand the host county's property-tax base; Bitcoin miners barely beat the benchmark. Consistent with the mechanism — hyperscale builds large taxable real + personal property (servers, cooling, generators, substations); miners are lighter, leased, frequently abated, and leave (Big Horn MT's Marathon operated ~2021, departed 2022).

**Why keep crypto in (labeled, not dropped):** the physical infrastructure is repurposable even when the miner exits — Dickens TX's "Helios" Bitcoin mine is being converted to a CoreWeave/NVIDIA **AI** data center. Crypto counties are not noise to discard; the *contrast* is the result. Carry an `is_crypto` / `dc_class` label and report clean / crypto / mixed cuts.

**Supporting catch (data-quality, paper footnote material):** the US Census of Governments property-tax series (item T01) carries systematic county-government-scope errors that a gold hand-verified spine corrected — collector-state over-counts (Laramie WY, Polk/Dallas IA, Nueces TX), TN school-levy inclusion (Loudon, Scott), GA government-wide reporting. **Laramie WY (Microsoft Cheyenne)** is the sharp example: raw Census growth was a misleading +13 % (all-overlapping-districts, mostly canceling), while the county-government-only series shows **+111 %** — a real, large DC fiscal effect the unaudited Census number would have buried. Lesson for the data section: county-government property tax must be scope-checked, not taken from Census T01 at face value in collector / levy-pooling states.

**Status / caveat:** these are **raw median CAGRs**, not the matched DiD estimate (Phase 2). Provenance: `data/derived/treated_pt_final.csv` (124/125 finalized; 50 gold-verified, 70 Census, 5 state-source), `dc_crypto_classification.csv`, scripts `python/56,58,59`.

---

## 7. The credit / bond block — capital markets stay passive (2026-06-10)

**Companion to §6. Estimated on the same cleaned treatment** (operating-by-2022 set, crypto labeled, treatment timed to each county's first operational year), deal-level SDC muni data through 2025, vs. never-DC-host control counties (2,498). Treatment timing is staggered (`treated_post = year ≥ first_op_year`), so late-opening counties enter with their post-2023/24/25 deals — no county is dropped for timing (deals run to 2025, unlike the property-tax Census which stops at 2022).

**Results (β on treated_post; clusters on county):**

| Outcome | Clean hyperscale/colo | Crypto | All |
|---|---|---|---|
| **Spread** (bps; − = cheaper) | **+1.3 (p=0.76, null)** | +15.7 (p=0.08, *widens*) | +4.9 (p=0.12) |
| **Issuance** (log par; log n deals) | ≈0 ; −0.10 ns | ≈0 ; +0.07 ns | ≈0 ; −0.05 ns |
| **Rating — extensive** (any-rated par share) | **−0.08 (p<0.01)** | −0.05 (p=0.01) | −0.07 (p<0.001) |
| **Rating — intensive** (quality \| rated) | null | null | null |

**Reading:** a data center expands the host county's property-tax base (§6, +2–3 %/yr) but the county's **capital-markets behavior does not change** — no cheaper borrowing (clean-DC spread null), no extra issuance, no rating-quality improvement, and *less* of its debt carries a public rating (−7 pp). If anything, **crypto-mining counties' spreads widen** (+15.7 bps), consistent with Bitcoin-mining's volatile, transient tax base raising perceived risk — whereas real data centers are pricing-neutral.

**Important correction (supersedes earlier drafts):** an earlier "−23 bps cheaper borrowing" result was a **bond-composition + control-group artifact** — it flips sign under matched controls and vanishes (+4.9 bps, ns) under the proper deal-level hedonic spec with county + state×year fixed effects. **Do not claim DCs lower borrowing costs.** The pooled spread estimate (+4.9 bps) reproduces exactly across specifications, confirming the null.

**Unifying frame for the paper:** *"fiscally light inflow, fiscally quiet financing"* — DC investment makes a county fiscally **stronger** (tax base) but capital-markets **passive** (no leverage-up, no repricing, no rating gain). The two halves (§6 tax base, §7 credit) are estimated on one validated treatment.

**Caveat:** deal-level TWFE/staggered timing → a Sun-Abraham / Callaway–Sant'Anna deal-level robustness is the natural follow-up (won't rescue the spread). Provenance: `scripts/python/62`, `data/derived/bond_block_cleaned.md`.

---

## 8. DC size distribution & treatment intensity (2026-06-10)

**The "data center" label spans four orders of magnitude — and the economically meaningful ones are a sliver.** Per-DC IT power from S&P 451 `dcpropertiesperiodic.TOTALITPOWER` (kW, **97% populated** — the *periodic* table; the static `dcproperties` field is empty; derived `data/derived/dc_county_year_mw.csv`).

**Per-DC US distribution (4,358 of 4,507 with power data):**

| Threshold | # DCs | % of US DCs |
|---|---:|---:|
| median facility | **0.84 MW** | — |
| ≥ 10 MW | 1,016 | 22.5% |
| ≥ 50 MW | 188 | 4.2% |
| **≥ 100 MW** | **48** | **1.1%** |
| ≥ 300 MW | 9 | 0.2% |

**County-level MW is equally Pareto:** the top **41 counties (≥300 MW) hold ~67%** of US DC capacity; the top **14 (≥600 MW) hold 41%**. Of the 14 in the 600+ tier, **11 are already treated**; 24 of 27 in the 300–600 tier are treated.

**Paper implications:**
1. **Facility size, not DC count, is the right intensity measure** — a county with one 300 MW campus is fiscally nothing like one with twenty 1 MW colos. Supports the continuous-dose / size-weighted treatment direction.
2. **The fiscal story is driven by ~50 giant facilities**, which sit overwhelmingly in the treated set — so the treatment cut (dc_share ≥ 1%) already captures the high-impact DCs.
3. **Control validity (referee-proofing):** of 2,776 never-DC controls, 137 actually host a DC in S&P — but **every one is < 50 MW** (biggest: Warren OH, 15 MW; all < 0.3% fiscal share). No *big* DC sits in a control county; the big DCs are all treated or sub-1% metros (correctly excluded). Action: drop the 137 tiny-DC "controls" for cleanliness (economically trivial, but tightens the "are your controls DC-free?" answer).

---

## 9. Sample fixes + metro placebo — clean-DC effect firms up; maturity result demoted (2026-06-10)

**Two referee-proofing fixes (`scripts/python/69`):** (1) purged 137 tiny-DC hosts from the control pool (clean pool = 2,639, `clean_never_dc_controls.csv`); (2) dropped 3 phantom/cancelled "treated" (Meigs TN, McDowell WV — no verifiable facility; Lawrence KY — crypto project rejected by KY PSC, never built; `treated_exclusions_phantom.csv`).

**Effect on the PT headline (matched CAGR %/yr):**

| Cut | Baseline | Purged + phantom drop |
|---|---|---|
| ALL | +3.07 (p=0.007) | **+3.39 (p=0.004)** |
| **Clean hyperscale/colo** | +1.87 (p=0.092) | **+2.59 (p=0.032), CI [+0.38,+4.90] excludes zero** |
| Crypto | +4.31 (p=0.093, outlier-driven) | +4.53 (p=0.096) |

The fixes **strengthen** the result — notably the clean-DC cut crosses into significance once contaminated controls are removed. Bond results are unchanged under both fixes (all stable to 2 decimals).

**Metro placebo (mechanism test):** 11 counties host a ≥50MW DC but have huge tax bases (LA, Santa Clara, Cook, Philadelphia, Dallas, Bexar…) → fiscal share <1%, mechanism off, predicted null. Anchor for both groups = first ≥50MW operational year (symmetric).

| Outcome | Treated big-DC (n=72) | Placebo metros (n=11) | Verdict |
|---|---|---|---|
| Spread (deal hedonic) | null | null | pass (null is real, not power — metros have huge deal counts) |
| Rating extensive | −3pp* | null | pass (weak) |
| Issuance (any / par) | null | null | pass |
| **Maturity (par-wtd yrs)** | −0.36*** | **−1.00***** | **FAIL — metros shorten MORE** |

**Honest consequence:** the maturity-shortening result **fails the placebo** — it appears (even stronger) where the fiscal mechanism is off, so it is NOT a fiscal-channel effect (likely a secular/urban issuance trend). **Demote it from the paper's mechanism claims**; keep at most as a descriptive footnote. The spread/issuance/rating nulls and the crypto contrasts survive. This is the placebo doing exactly its job — and it makes the surviving results more credible.

---

## 10. Test 3 — continuous dose on the announcement clock: the fiscal channel is not priced at any dose (2026-06-10)

**New continuous measure** (`scripts/python/70`, `dc_dose_announced_mw_panel.csv`): `dose = cumulative ANNOUNCED ≥50MW capacity (MW) / baseline 2017 property tax ($M)` — absorbing (capacity stays in the investor information set once announced), assumption-free (no $/MW multiplier in the regressor), and scaled by fiscal size. Spans Loudoun 1.1 → Dickens 87 MW/$M (median 7.5). Under the $50k/MW working assumption, 1 MW/$M ≈ 5pp of expected fiscal share — interpretation only.

**Result: NO dose-response on spread.** Deal-level hedonic (preferred): clean −2.0 ns, crypto +0.2 ns (winsorized), ALL +0.6 ns — across linear, log, and static-share specs. Rating-extensive shows a mild dose-consistent retreat (−1.5pp per log-point ALL, crypto −2.7pp*), in line with the dummy results. Issuance null.

**Two artifacts caught by verification (documented in the output's appendix):** (i) the raw linear crypto-spread coefficient (−0.17***) was 100% Glasscock 48173 leverage (dose=641, documented artifact county) — winsorize at 50 kills it; (ii) the county-year aggregate shows clean log-dose +11.6**, but this is aggregation weighting (tiny, rarely-issuing high-dose counties get equal county-year weight), not composition or outliers — the deal-level estimate, weighted by actual market activity, is null.

**Chain complete:** strong first stage (+3.39%/yr, clean +2.59**) → reduced-form null (dummy) → **no dose-response** → placebo passes (metros null with high power). The bond market does not price the DC fiscal windfall at any dose. "Fiscally light inflow, fiscally quiet financing" now rests on all four legs.

**Addendum — clock + type-split refinements (`scripts/python/71`):** (i) Re-running the dose battery on the **operational clock** ("county begins collecting revenue") changes nothing — spreads stay null, crypto patterns marginally stronger (rating-ext −3.7pp* vs −2.7pp*); the market neither reacts to the news nor to the cash-flow arrival. (ii) **Type-split dose** (per-DC PROVIDERTYPE: each county's capacity split into crypto-MW vs hyperscale-MW, both in one regression): the rated-market retreat is **crypto-capacity-specific and now significant at 5% on both clocks** (crypto-dose −2.3pp**/−2.9pp** per log-point; hyperscale-dose flat ~0). Spread: crypto-dose positive / hyperscale negative, neither significant. (iii) New stylized fact: **zero treated counties host both a ≥50MW crypto and a ≥50MW hyperscale DC — major-DC counties fully specialize** (48 of 171 big DCs are crypto, in disjoint counties). Useful for the paper: the clean/crypto comparison is across-county by construction, not confounded within-county.

---

## 11. The risk-gradient interpretation — what the muni market actually prices (2026-06-10)

**The category-split dose results (script 71 §3) organize the whole bond block into one sentence: the market's response orders by the RISK of the new tax base, not its SIZE.**

| Capacity type | Tax-base character | Market response |
|---|---|---|
| **Crypto-mining** (48 big DCs, 50% of treated MW) | volatile, BTC-price-driven, transient, single-source | **negative effect on rated share** (−2.3/−2.9pp per log-point, 5%, both clocks); spread point-estimates positive, ns |
| **Hyperscale** (93 big DCs, 37% of MW) | large, durable, but single-company concentration | **no effect** on spread/rating/issuance at any dose, on both clocks (the headline result) |
| **Colocation** (27 big DCs, 11.5% of MW, 8 counties) | diversified multi-tenant, established markets | **negative spread effect in primary market** (−46.5 bps per log-point, p=0.02, operational clock; survives leave-Loudoun-out) — NOT confirmed in secondary market, see §12 |

**Magnitudes for the colo cell** (β × each county's log-dose; sample mean spread = 120 bps): Loudoun −31 bps, PWC/Salt Lake −16, Fulton −11 — economically large (~10–25% of the mean spread). The tiny-county extrapolations (Storey −117 bps) are implausible, which is itself a caution: with ~6–8 effective clusters and significance on one clock only, **the colo cell is SUGGESTIVE, not a headline** — and §12's secondary-market test does not confirm it.

**Why this frame is paper-worthy:** "do munis price fiscal windfalls?" becomes "munis price the *quality/volatility* of a new tax base while ignoring its *level*" — a sharper, positive characterization than a null, and directly testable with more power in the MSRB secondary-market panel (bond FE around announcement/operational dates, no issuance selection). MSRB is the designated confirmation test for both the hyperscale null and the colo primary-market result.

**Clock definitions used throughout** (for co-authors): *announcement clock* = capacity enters the dose the year the project is first publicly announced (information event; "investors know"); *operational clock* = capacity enters the year the facility becomes operational per S&P (cash-flow event; "county begins collecting revenue"). Median gap ≈ 1 year; all headline results are robust to either clock.

---

## 12. MSRB secondary-market results — no effect for any DC type; colo primary-market result not confirmed (2026-06-11)

**The confirmation test §11 called for, executed.** `scripts/python/72` (slice: 215.8M trades → 35.1M for treated/placebo/control counties via the SDC `ISSUECUSIP1` CUSIP6→county bridge, 21,294 issuers, 116/122 treated counties) + `scripts/python/73` (bond×year panel: par-weighted customer-sale yield-to-worst, **bond FE + year FE**, cluster county, log-remaining-maturity control). Identification = the SAME outstanding bond before vs after the county's first ≥50MW DC announcement — **no issuance selection possible**. 1.3M bond-year obs, 318k bonds, 2,301 counties.

| Cut | Secondary-market effect (same bond, post-announcement) | Reading |
|---|---|---|
| **Clean hyperscale/colo counties** | **+0.3 bps (SE 2.0), p=0.886**, 29,933 bonds; pre-trends −0.9/+0.3/−0.4 ≈ exactly zero | **No effect, precisely estimated** — CI ≈ [−3.6,+4.2] bps excludes even modest repricing |
| Crypto counties | +2.0 bps ns (4,602 bonds) | Direction consistent with primary +17bps but not significant → crypto premium lives in **new-issue pricing**, not outstanding-bond repricing |
| Placebo metros | −5.8 ns (34,625 bonds, high power) | No effect (as predicted) — also rules out the low-power explanation for the other nulls |
| **Colo-capacity counties (8)** | **+4.9 bps (p=0.062, positive sign)** + significant PRE-trend (+6.1*** at −3) | **Primary-market −46.5 NOT confirmed** — opposite sign, pre-trend violated; treat as a small-cluster artifact; read colo as NO effect |

**Dose-form confirmation (script 78, closes the dummy-vs-dose asymmetry):** the primary-market colo estimate was in DOSE form, so the strict apples-to-apples secondary test puts the same joint category doses into the bond-FE panel. Result: colo-dose **−1.3 bps per log-point (SE 4.8, p=0.79)** on the operational clock (+3.7 ns on announcement); 5,436 colo-county bonds. Rejects −46.5 by ~9 SEs.

**Primary-market robustness (2026-06-11, follow-up to Frank's question):** the −46.5 itself is not robust within the primary market either — under county + **state×year** FE it flips to **+18.3 (SE 27.4, p=0.51)**. The 8 colo counties cluster in a few states (VA/GA/UT/NV/WA) whose muni-rate environments diverge from the national year effect; county+year FE mis-attributed that state-level variation to the colo dose — the same mechanism that produced the original −23.4. Full record for the colo cell: significant only under county+year FE × operational clock; sign flips under state×year FE; ns on the announcement clock; no effect in outstanding bonds under either functional form. **Settled: does not enter the paper as a result; at most a tested-and-rejected line in a robustness appendix.**

**Final summary (supersedes §11's third row):** crypto — positive spread effect at issuance only (+16–18 bps, no secondary-market repricing); hyperscale — no effect on any outcome; colo — no effect (primary-market negative estimate not confirmed). **No negative spread effect (cheaper borrowing) for any DC type; the only significant pricing margin is the positive crypto spread effect on new issues.**

**Paper status:** the empirical core is complete — first stage (+3.39%/yr, clean +2.59**), primary-market nulls (dummy/dose/placebo), and now the selection-free secondary-market null with 2bps precision. Infrastructure: `msrb_cusip6_county_map.csv` (reusable issuer→county map), `msrb_working_slice.parquet` (35M trades, instant re-analysis). Gotcha for replication: MSRB `PAR_TRADED` is char-typed with "MM+" masking for >$5M blocks in the first 5 days — coerce numeric, masked rows drop.

---

## 13. Tier-1 heterogeneity round — three pre-specified splits, none confirmed (2026-06-11)

**Purpose:** before accepting the across-the-board no-effect results (§12), test the three sample splits with the strongest a-priori case that an effect was being DILUTED. Each had a one-directional prediction written down in advance; all were run with the script-68 spec, mandatory sanity checks (pooled must reproduce script 68 — all passed), and the standard sample-definition block. Scripts 74–77.

| Split | Pre-specified prediction | Result | Confirmed? |
|---|---|---|---|
| **GO vs revenue bonds** (74) | Property-tax windfall backs GO bonds → GO beta more negative than RV | GO clean −2.2 (p=0.83); RV clean +4.9 (p=0.49). Note: GO = **82.5%** of deals, so pooling was never diluting much | No — no effect either type |
| **Maturity gradient** (74) | Long bonds embed long-run tax base → negative announced×log(maturity) | +1.6 (p=0.60), opposite sign | No |
| **Issuer type: school district vs county govt vs city** (75) | Schools are the largest PT recipient → school-district beta most negative | School −6.4 (p=0.59, 38 counties); county govt −15.5 (p=0.25); city +2.3 (p=0.56). ISSTYPE populated for only 26% of deals | No — no effect any type |
| **Salience: mega-announcements × post-2022 era** (76) | Attention story → effect in top-decile-MW counties, post-ChatGPT | Primary market: mega −24.9 (p=0.047), mega-ex-oil −32.5 (p<0.001), ×post-2023 −29.1 (p=0.002). **Verification (77): significance depends on one county** (drop Nueces TX → p=0.41), threshold-sensitive (≥300MW cut p=0.15), and **secondary market shows no effect in the same cells** (announced +0.7 p=0.75; ×post-2023 −0.8 p=0.62; 5,331 outstanding bonds) | No — same failure pattern as the colo −46.5 (§12) |

**Reading:** the no-effect results survive the three strongest economically-motivated attacks available in the data. Two methodological notes for the paper: (i) the GO-share fact (82.5%) preempts the "you pooled away the GO effect" referee comment; (ii) the salience episode is the second instance (after colo) where a significant primary-market cell with few effective clusters failed secondary-market confirmation — supporting the design choice of treating the MSRB bond-FE test as the confirmation standard for any pricing claim.

**Multiple-testing note:** 4 hypotheses × ~3 cuts were examined in this round; one cell at p=0.047 and one at p=0.002 appeared and did not survive verification — about what false-discovery arithmetic predicts. All cells are reported above, including the failures.

---

## Process notes

- Append new entries when agents land; reorganize by category as the list grows.
- After Tier 4 + 5 wraps, do a verification pass on the top-5 anecdotes — confirm the PILOT counterparties via county economic development authority records and the S&P 451 Research DC database.
- For the v3-author memo to Mitch / Henrik: synthesize sections 1, 2, 5 above into a short brief.
