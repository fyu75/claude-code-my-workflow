# Project Memo: Data Centers and Municipality Finances

**Date:** 2026-05-10
**Authors:** Cronqvist · Dai · Warachka · Yu
**Working title:** *Corporate Investment and Municipality Finances: Evidence from Data Centers*

---

## 1. One-paragraph elevator pitch

The U.S. data-center buildout is the largest concentrated corporate-investment shock in modern public-finance history — projected to reach **~1/5 of total U.S. capex in 2026** — and it lands on local governments through a channel we don't fully understand. Unlike a Toyota plant or an Amazon warehouse, a data center delivers an enormous **property and personal-property tax base** (Loudoun County, VA collected ~$900M from data centers in FY2025 — nearly its entire operating budget) without a meaningful labor shock (DCs employ very few workers and few complementary inputs beyond power and water). Using the S&P 451 Research Data Center Database, county ACFRs, MSRB EMMA, and credit-rating actions, we estimate the **elasticity of municipal tax revenue, capital spending, debt, ratings, and bond yields** to data-center investment. We adapt Greenstone–Hornbeck–Moretti's (JPE 2010) winner-vs-loser plant-opening design and we exploit migration of new data centers from wealthy DC hubs (Loudoun) toward poor / rural counties (San Bernardino-style) where the relative shock is largest. The closest existing precedent — Chava–Malakar–Singh's corporate-subsidy paper finding a 15.2 bps muni-spread effect — leaves the data-center setting unstudied, and the AI-driven inflection point (chip-replacement cycles, hyperscaler concentration, voter pushback over electricity and water) introduces risk dynamics that prior corporate-investment shocks lacked.

---

## 2. The phenomenon (magnitudes worth fixing in our heads)

| Fact | Source |
|---|---|
| DCs ≈ 1/5 of total U.S. capex in 2026 | Henrik note 2026-04-30 |
| Loudoun County, VA: ~$900M from DCs in FY2025 (≈ entire operating budget) | Bond Buyer / Civic IQ 2026 |
| Prince William County, VA: DC personal-property tax $2.9M (FY13) → $54.4M (FY22), 38.4% CAGR; DCs = 96% of FY22 computer-equipment personal-property tax | PWC FY22 Fiscal Impact Analysis |
| Georgia: 162 existing DCs + 285 planned (+176%); avg ~$28M/yr property tax per project | Civic IQ 2026 |
| DC assessed value: ~$858/sqft vs ~$258/sqft for general commercial | Civic IQ 2026 |
| AWS Richmond County NC: $10B investment with 50% property tax abatement + 65% personal property abatement, 20-year term | Civic IQ 2026 |
| Stargate (Texas + 5 sites): $400B+ planned capex | Civic IQ 2026 |
| 38 U.S. states currently offer dedicated DC tax incentives (sales-tax exemption, electricity exemption, property abatement); under reevaluation as voter pushback grows | NCSL "Subsidizing Servers" |

The "incentive vs revenue" tension is the central tradeoff. **What is happening on net at the county level?**

---

## 3. The research question(s)

### Primary RQ
> What is the causal effect of large data-center investment on a host county's fiscal position and municipal bond market outcomes?

### Five outcome channels (run in parallel; do not narrow prematurely)

| # | Channel | Sign expected | Open empirical question |
|---|---|---|---|
| O1 | **Tax-revenue elasticity** — $ tax collected per $ DC investment | Positive | How big? Who captures it net of incentives? |
| O2 | **Muni capex / public-services investment** | Positive (with leakage) | Pass-through rate from revenue to spending |
| O3 | **Debt level / paydown** | Negative (de-leveraging) | Or do munis lever up against new capacity? |
| O4 | **Credit ratings** (Moody's / S&P / Fitch) | Positive (mostly), with nuance | Concentration-risk caveat eventually flips sign? |
| O5 | **Bond yields / spreads / liquidity** | Negative (lower borrowing cost) | And: announcement vs anniversary effects |

### Heterogeneity that matters (per Mitch + Henrik)
- **Rural / poor counties** (San Bernardino-style) vs. wealthy DC hubs (Loudoun) — relative shock is much larger in the former.
- **Tax-incentive intensity** — abatement-heavy deals may neutralize the fiscal benefit entirely.
- **Tenant type** — hyperscaler (AWS / Azure / GCP / Meta) vs. colocation vs. enterprise — different counterparty and concentration risk.
- **Pre-AI vs. post-AI buildout** — post-2022 DCs are larger, more power-intensive, more concentrated in a few tenants.

---

## 4. Why this is interesting (and uncrowded — for now)

Henrik flagged that **Giroud, Rauh, Chava, Gao, etc.** are increasingly active in the muni space. The DC angle is unusually open because:

1. **Scale is unprecedented.** 1/5 of U.S. capex is not a niche shock; it is the dominant corporate-investment shock of the decade.
2. **Pure capex, no labor.** This is rare. Almost every prior corporate-investment shock (Million Dollar Plant, Amazon HQ2, shale gas) has a labor channel that confounds the public-finance channel. DCs let us isolate the property/personal-property tax channel cleanly.
3. **Asset cycle is short and getting shorter.** Chip refresh cycles (~3–5 years) mean the property-tax base is more volatile than land-and-structures shocks. **This is genuinely new** and Mitch's intuition points at a real discontinuity.
4. **Risk angle is bilateral.** Fiscal benefit AND concentration risk live in the same data. We can run the upside (Loudoun in 2025) and downside (prison-bond-style unwind story) in one paper or one paper pair.
5. **Institutional validation already exists.** Moody's now has a DC credit-risk department. S&P Global Ratings published "Everywhere, All At Once" (2026) flagging DC growth as a muni risk factor. Rating agencies treating it as material is *evidence we should be working on it*, not a deterrent.

---

## 5. Identification strategy

### Primary: Million Dollar Plant winners-vs-losers (Greenstone–Hornbeck–Moretti, JPE 2010)

For each major DC siting, identify the **runner-up county** that lost out. Compare fiscal trajectories of winner vs runner-up.

- **Pro:** Gold-standard identification; selection on observables defensible because both counties wanted the project.
- **Con:** Runner-up identification requires RFP / state competition data; not all DC sitings have a clear loser.
- **Closest precedent:** **Chava, Malakar & Singh (2023)** — same design, broader corporate-subsidy setting. They find **15.2 bps yield-spread effect on winners vs losers**. Our DC effect should be similar in shape; magnitude likely larger because of the property-tax-intensive nature of DCs.

### Backup A: Construction-company press releases (Ravenpack)

Henrik's idea. A small set of construction firms builds the bulk of large DCs. Use their press releases (groundbreaking, milestone, completion) as the shock-timing instrument. **High-frequency identification** off bond trades.

### Backup B: Staggered DiD with heterogeneity-robust estimators

Panel of all U.S. counties × year, treatment defined by first-DC operational status. Use Callaway–Sant'Anna or de Chaisemartin–D'Haultfœuille — naïve TWFE is a red flag post-2020.

### Backup C: Pre-AI vs. post-AI structural break

Treat the 2022–2023 generative-AI inflection as exogenous to county fiscal fundamentals. Compare pass-through rates pre and post.

### Threats to address explicitly

- **Selection.** Munis seek out DCs (Henrik flagged this). Address by (a) winner-vs-loser, (b) instruments grounded in fiber / power-grid / land cost.
- **Tax incentive endogeneity.** Abatements are themselves negotiated outcomes, not exogenous prices. Pre-incentive ATTs are not the right object; we need to separate gross from net effects.
- **Federal subsidies (CHIPS-Act-adjacent).** Confound with state-level DC incentives.
- **Co-located energy infrastructure.** New DCs trigger transmission and generation upgrades that themselves change local economic activity.

---

## 6. Data architecture

> **Note on muni-bond data sources** (clarified by Rui 2026-05-10): municipal bonds are *not* on FINRA TRACE. Trade reporting goes through the MSRB Real-Time Transaction Reporting System (RTRS), surfaced publicly via EMMA and licensed for research via WRDS-MSRB. Primary-market issuance is a separate product — the standard sources are Mergent MBSD or SDC Public Finance.

| Source | Status | Coverage | Use |
|---|---|---|---|
| **S&P 451 Research DC Database** | ✅ Have (23 SAS files at `data/raw`) | Property-level: location, owner, operator, tenant, MW, status, cooling/power redundancy, certifications, periodic updates | The unit-of-analysis backbone |
| **County ACFRs** | ☐ Need to collect | County financials: revenue by source, expenditure, debt, fund balance | Outcomes O1–O3 |
| **WRDS-MSRB (Municipal Securities Transaction Data)** | ✅ via Rui (Wharton WRDS) | Trade-level secondary-market: price, yield, par, dealer/customer flag — every muni trade since 2005, 15-min reporting | Outcome O5 (yields, spreads, liquidity) |
| **SDC Public Finance** (LSEG) | ✅ via Rui | Primary-market issuance: amount, coupon, maturity, callability, use of proceeds, underwriter, negotiated/competitive | Sample frame + issue-level controls (O5) |
| **EMMA scrape** *(planned — Plan 3)* | ☐ Planned: 2018+, DC-host counties only | Documents only — official statements, continuing disclosure filings, material event notices, rating-action history. **Not** trades (those come from WRDS-MSRB). | Document supplement to WRDS-MSRB. Polite rate-limited scraper, identified user-agent, aggressive local caching, ToS-aware. Validate against MSRB Continuing Disclosure / Primary Market Data Sets if WRDS has them. |
| **Moody's / S&P / Fitch ratings actions** | ☐ Need to source | Rating changes, watch-list events | Outcome O4 |
| **NCSL state DC tax incentives** | ☐ Need to download | 38-state taxonomy of incentive types | Treatment intensity, robustness |
| **silicondata.com** *(via Rui's lead)* | ☐ Need to evaluate (commercial subscription; available on Bloomberg / Refinitiv) | GPU/server price series across A100, H100, B200; up to 8 years history, daily refresh; SiliconNavigator™ (rental/resale prices), SiliconIndex™, GPU forward curve | **DC asset-cycle volatility, depreciation modeling** (risk-angle paper, §9 #4); chip-replacement-cycle proxy for personal-property-tax base dynamics |
| **Ravenpack press releases** *(optional)* | ☐ Optional | Construction-company DC announcements | Backup identification (Henrik's idea) |
| **PWC VA fiscal-impact PDFs / similar case studies** | ☐ Need to collect | Stylized facts, motivation | Lead anecdote in Section 1 of paper |

---

## 7. Literature anchor (annotated, ~20 papers)

### A. Identification template (Million Dollar Plant family)

- **Greenstone, Hornbeck & Moretti (2010, JPE)** — winners-vs-losers, the canonical design. *"Identifying Agglomeration Spillovers."*
- **Gupta & Rodriguez (2024, JUE)** — "Firms for Funding": same design, school-finance outcomes. Very close cousin to our project.
- **Garin & Rothbaum (2024 WP, NBER-pipeline)** — "The Long-Run Impacts of Public Industrial Investment: Evidence from World War II" — finds $1,200/yr long-run earnings gain from WWII plant openings; relevant for the "what happens 30 years later when DCs decay?" question.
- **Slattery & Zidar (2020, JEP)** — "Evaluating State and Local Business Tax Incentives" — overview of place-based incentives; should be cited prominently.

### B. Closest precedent on muni-bond impact

- **Chava, Malakar & Singh (2023, SSRN; Henrik flagged)** — winners vs losers in $40B of corporate subsidies → **15.2 bps muni-spread increase** for winners. Effect is larger when jobs multiplier is low or debt capacity is constrained. **This is our nearest neighbor; we differentiate by (a) the DC setting, (b) the multi-channel framework, (c) the post-AI structural break.**
- **Chava, Malakar & Singh (2024, SSRN)** — "Communities as Stakeholders: Corporate Bankruptcies on Local Governments." Same trio, downside-shock setting. We should track this — it may be the disposable mirror of our paper.

### C. Muni-bond pricing & risk (the literature we plug into)

- **Adelino, Cunha & Ferreira (2017, RFS)** — Moody's 2010 muni rating recalibration → ~70 bps yield decline → boosted public investment / employment. Establishes the rating channel.
- **Cornaggia, Cornaggia & Israelsen (2018, RFS)** — Credit ratings drive muni borrowing costs through investor risk-weights, not just default probabilities.
- **Cornaggia, Hund & Nguyen (2022, JFM)** — Investor attention shapes muni returns; relevant to DC announcement-window event studies.
- **Goldsmith-Pinkham, Gustafson, Lewis & Schwert (2022, NBER)** — "Sea Level Rise Exposure and Municipal Bond Yields." Methodologically the closest paper to our setup: a county-level exposure metric → muni yields. **We can imitate their empirical structure**, swapping SLR for DC exposure.
- **Ambrose, Gustafson, Valentin & Ye (2025, Management Science)** — "Voter-Induced Municipal Credit Risk." TCJA SALT shock → **8.3 bps muni yield spread** in jurisdictions where voters faced higher costs of public goods. *Direct relevance:* DC pushback (water, electricity ratepayer concerns) creates voter-driven credit risk that our risk-angle paper can exploit.
- **Dagostino & Nakhmurina (2026, JAR)** — "Partisan Cities": state-local political alignment → 9 bps borrowing cost difference. *Implication:* our state-level DC incentive variation correlates with partisan alignment; need to control or exploit.
- **Wilson (2024, Macroeconomic Dynamics)** — "Municipal Government Channel of Monetary Policy": 100 bp monetary shock → 26 bp muni yield response. Useful baseline for sizing our effect (15 bps from Chava et al. is ~60% of the typical monetary impulse response).
- **Jiang, Jing & Zhang (2024, SSRN)** — "The Pricing of Property Tax Revenues." Relevant for our O1 → O5 channel; how does the muni market price the property-tax stream?

### D. Comparable industry-specific fiscal shocks

- **Newell & Raimi (2015, NBER WP 21542)** — "Shale Public Finance": local government revenues / costs of oil & gas. Directly comparable — natural-resource-style fiscal shock with extraction-cycle risk.
- **Chirakijja (2024, REStat)** — "The Local Economic Impacts of Prisons." Mitch's reference: prison bonds were a fiscal positive that turned junk as inmate populations declined. **Strongest analog for the risk angle: short-cycle asset class can flip from boon to burden.**
- **Cunningham (2024, Minnesota PhD WP)** — "Local Labor Market Effects of Amazon." Useful for differentiating: warehouses *do* have a labor channel, DCs largely don't.

### E. Information channel & local fiscal monitoring

- **Gao, Lee & Murphy (2020, JFE)** — "Financing Dies in Darkness: Newspaper Closures and Public Finance." Newspaper closure → 5–11 bps muni borrowing-cost increase. Henrik's reference. *Implication for us:* test whether DC effect is amplified in counties with diminished local-media monitoring.

### F. Climate / disaster / risk methodology cousins

- **Capuno, Corpuz & Lordemus (2024, JEBO)** — "Natural Disasters and Local Government Finance: Typhoon Haiyan." Local-fiscal-shock methodology template.
- **Mishra et al. (2026)** — "Physical Climate Risk Creates Challenges and Opportunities in U.S. Municipal Finance." Fresh framework for risk pricing.
- **Hanley (2026)** — "The Fiscal Fracture: Property Tax Erosion" — boomer-asset thesis on property-tax-base erosion; conceptually parallel to chip-cycle erosion of DC tax base.

### G. Industry / institutional signal (cite as evidence the question matters)

- **NCSL (2026)** — *Subsidizing Servers* — 38-state DC incentive census.
- **S&P Global Ratings (2026)** — *Everywhere, All At Once: How the Growth of Data Centers Could Carry Risks for U.S. Local Governments.*
- **Moody's (2026)** — Data Center credit-risk hub.
- **Nuveen (2026)** — *Data Centers Impact Muni Issuers: Risk and Reward.*
- **Rogers, Ota, Burola & Piquado (2026, arXiv)** — "Infrastructure Equation: Water, Energy, and Community Policy for Georgia's Data Center Boom." *Adjacent literature, not a competitor — they ask infrastructure / governance questions; we ask the muni-finance question.*
- **Prince William County, VA (2022)** — Data Center Fiscal Impact Analysis. Stylized fact source.

---

## 8. Candidate sub-papers (if scope expands)

The project naturally generates **2–3 papers**, not just one. Possible split:

| Paper | Focus | DV | Identification |
|---|---|---|---|
| **A: Fiscal benefit** | Tax revenue elasticity + muni response | O1 + O2 + O3 | Winner-vs-loser; staggered DiD |
| **B: Asset-pricing response** | Bond ratings + yields + spreads | O4 + O5 | Event study around DC announcements; Goldsmith-Pinkham-style exposure |
| **C: Risk angle** | Concentration risk; voter pushback; chip-cycle volatility | Yield variance, downgrade probability | Tenant-concentration HHI; voter-pushback indicator a la Ambrose et al. |

Frank's view: start as **one paper** (A + B together — fiscal effect *and* market response). Spin off **C** as a follow-up if the risk angle has its own momentum. Don't pre-commit to three papers; let the data tell us.

---

## 9. additions / extensions

Things not in Henrik's or Mitch's notes that I'd flag:

1. **The "bid-up" angle.** When word gets out that a hyperscaler is shopping for sites, do all candidate counties' muni yields move in anticipation? This is parallel to the M&A bid-target premium. Tests whether muni markets pre-price DC investment — Cornaggia–Hund–Nguyen (2022) suggests they're attention-driven enough that this is plausible.

2. **The "only game in town" angle.** Yonker (Cornell) wrote on monopsony in muni issuance ("only game in town" idea). For poor / rural counties, a single hyperscaler may become >50% of the property-tax base. This is **monopsony from the muni's side**. The hyperscaler can extract incentive concessions over time as counties lock in their dependence. Implication: long-run incentive escalation should be visible in renewal cycles.

3. **Tenant heterogeneity matters more than ownership.** The S&P 451 data lets us distinguish hyperscaler-owned (AWS/MS/Google build their own) vs colocation (Equinix, Digital Realty) vs enterprise. Hyperscaler-owned facilities have different lease structures and different counterparty risk — Anthropic / OpenAI as tenants in someone else's data center is a different fiscal animal than Microsoft owning the building. Worth a heterogeneity table.

4. **The "AI bust" stress test.** What happens to muni bond yields in counties heavily exposed to a single hyperscaler if that hyperscaler downgrades capex guidance? We can simulate using a counterfactual (Chava-Malakar-Singh's "Communities as Stakeholders" mirror logic). This is the prison-bond unwind story, applied prospectively.

5. **Federal preemption / CHIPS Act interactions.** The 2022 CHIPS Act doesn't directly cover DCs, but federal-state-local incentive stacking is real. We should at minimum control for federal-grant proximity.

6. **Property-tax rate response.** Counties may adjust millage rates after a DC arrives — either because the new base allows lower rates (capture by residents) or because political pressure leads to abatement renewals. ACFR data should let us decompose Δrevenue into Δbase × Δrate.

7. **Election-cycle endogeneity.** Per Ambrose et al. (2025), voter sentiment matters for muni pricing. DC siting decisions in years t–1 may correlate with election outcomes in t. Worth a robustness check excluding election years.

8. **Climate / power-grid co-shock.** Texas DCs cluster in ERCOT; the 2021 Texas grid failure is a natural experiment for DC operational risk pricing into local munis. May be worth as a vignette / robustness.

---

## 10. Open questions / decision points (for the team)

1. **Scope boundary:** one paper covering A + B, or two-paper plan from the outset?
2. **Sample period:** start at 2008 (post-FCRA muni reform; Cornaggia et al baseline)? Or 2010 (post-Dodd-Frank)? Or earlier for pre-period?
3. **Geographic unit:** county? Census tract? Issuer? S&P 451 data is property-level; ACFR is county-level; MSRB is issue-level. A county-year panel is the obvious common denominator.
4. **Pure-incentive deals:** include or exclude properties that received 100% abatement? They are the most-covered cases but the cleanest "no fiscal benefit" cases.
5. **International comparison:** any role for non-U.S. data centers? Probably not — focus US, leverage S&P 451 US coverage.
6. **Pre-registration:** worth filing on AsPredicted given how fast this space is moving? Cheap insurance against post-hoc looking.
7. **Replication-package authorship:** start clean from day one (we have the infrastructure for `/audit-reproducibility` already).

---

## 11. Stylized facts to nail in the first month

Before we run any regressions, the team needs these in hand:

1. **Geographic distribution of DCs** — county-level: rural vs urban classification; per-state; top-N by count and MW capacity. **(Plan 2 — next analysis task)**
2. **Time-series of DC operationalizations** — by year, by tenant type, by state. Is the post-AI inflection visible?
3. **Replication of the PWC VA stylized fact** — using S&P 451 + a few other fast-growing DC counties (Loudoun, Mesa AZ, Hillsboro OR). Show the figure.
4. **Tenant concentration HHI by county** — for poor / rural DC-host counties, what fraction of the property-tax base is from a single tenant?
5. **State incentive overlay** — which DC properties sit in which incentive regimes? Cross from S&P 451 location to NCSL incentive map.

These are mechanical and they earn us the right to claim insight before we build a model.

---

## 12. Working-paper outline (sketch, ~40-page target)

1. Introduction — magnitude of the shock, the puzzle, our finding
2. Institutional setting — what is a DC, how is it taxed, what is an ACFR
3. Data — S&P 451 + ACFR + MSRB + ratings + NCSL incentives
4. Stylized facts — Section 11 above
5. Identification — winner-vs-loser; threats; robustness
6. Results — five outcome channels (O1–O5); heterogeneity
7. Risk angle — concentration, asset cycle, voter pushback
8. Discussion — comparison with Chava et al; implications for muni investors and rating agencies
9. Conclusion

---

## 13. Next steps

1. ☐ **Plan 2 (next):** county-level descriptive analysis of US DC owners / providers / clients + geographic distribution. Foundation for #1 stylized fact.
2. ☐ **Plan 3 (parallel):** download external sources — NCSL, Mo
3. ody's 2026 DC hub, S&P Global Ratings 2026 piece, PWC VA FY22 fiscal report, and 5 comparable case-study PDFs. Save under `master_supporting_docs/`.
4. ☐ **Mitch's ACFR lead:** scope the ACFR collection. Munispot.com guide is the starting reference. Decide manual-pull vs. scraping.
5. ☐ **Henrik's lit list:** push the bibliography from the 20 in this memo to ~50 via `/lit-review` as background; do not hold up empirical work for it.
6. ☐ **Decision: scope (one paper vs two)** — kick this around at the next team call.
7. ☐ **Decision: pre-registration** — AsPredicted draft once design firms up.

---

## 
