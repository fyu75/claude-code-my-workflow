# MuniSpot V2 — What We Got, What's Wrong With It, and What It Can't Do for the Tests

**To:** Mitch
**From:** Frank
**Date:** 2026-06-10
**Re:** Honest accounting of Raj's V2 delivery — coverage, data-quality issues, and the gap between V2 and the property-tax DiD we're actually running. Base for our discussion.

---

## Bottom line up front

V2 is a real upgrade over V1, and the money was not wasted — but **it is not the dataset that produced our headline result, and it can't be on its own.** Three sentences:

1. **What improved:** V2 now covers all governmental funds (not just the General Fund), adds ~294 more counties, and extends the window to FY2026. That's worth having.
2. **What's still broken:** where V2 reports a property-tax number for one of our treated counties, it's *wrong often enough* — unit misfires, school-district sweep-in, single-levy under-capture, scope mismatches — that we cannot take any value at face value. It reaches 72% of our treated counties with *some* data but only **37%** with usable property tax.
3. **What it means for the paper:** the property-tax result came from **hand-read ACFRs**, not V2. V2's real, defensible role is (a) a **growth-rate cross-check** (its level errors cancel in within-V2 CAGRs), (b) a **handful of unique rescues** we couldn't get elsewhere, and (c) the **broad control panel** for the General-Fund outcomes. That's a supporting instrument, not the main one.

---

## 1. What V2 delivered (the upgrade over V1)

| Dimension | V1 (Apr 2026) | V2 (Jun 2026 interim) |
|---|---|---|
| Scope | **General Fund only** | **All governmental funds** (`column_index==-1` = Total Gov Funds; `==1` recovers GF for V1 comparability) |
| Fiscal years | FY2016–FY2024 | **FY2016–FY2026** (+2 post-period years) |
| Counties (distinct FIPS) | ~1,903 | ~2,197 (**+294**) |
| Rows | 4.33M | 4.04M (county-only, cleaner entity filter) |
| Entity scope | mixed (school districts + cities tagged with county FIPS — over-counted ~6×) | restricted to County-General Purpose Government |

Two of these are genuinely valuable for us:

- **All-funds scope** partially opens the **capex channel** we couldn't see in V1. Capital Projects Fund activity now sits inside "Total Governmental Funds." We have not yet mined this, but it's the first time a *panel* source touches the H1 (new roads/schools) mechanism rather than just the GF operating budget.
- **FY2025–FY2026** lengthens the post-period — directly useful for the DiD post window and for eventually testing parallel trends.

> **Note on Raj's "+615 counties" framing:** the real lift is **~+294 distinct counties**. The +615 counts distinct `auditee_ein`, which inflates because a county picks up a new EIN when it changes auditors. Not a criticism — just don't quote 615 to anyone.

---

## 2. What we've done with V2 on our end since delivery

So you can see where the effort went — this was not a "load it and run a regression" delivery. Three phases:

**a. Property-tax classification.** V2's property tax is scattered across inconsistent labels, so we wrote a classifier that recovers it in three tiers — strict (`PROPERTY TAX REVENUES`), extended (+ ad-valorem / real-estate keywords pulled out of MISCELLANEOUS), and PILOT-inclusive (+ payments-in-lieu-of-tax). This lifted V2-native county coverage from **927 → 1,092 counties (+18%)** before any hand work. (`scripts/python/35_*`.) We also built the coverage maps that produced every number in §3 and §4 below (`dc_treated_coverage_v2_vs_acfr.csv`, the county-equivalent recovery crosswalk).

**b. Verification against ground truth.** This is where most of the labor went. Because V2's values fail at the unit of analysis (§3), we hand-read the underlying ACFRs — using parallel research agents — for **~95 counties**, capturing *both* the FY2017 baseline and the post-period value with provenance, into a verified spine (`verified_two_endpoint_pt.csv`, 95 rows). We ran this as successive waves: initial treated recovery, then control-post recovery, then a Tennessee-specific wave (TN bundles in cash-basis filings but separates cleanly in the GAAP Comptroller reports — recovered all 10 TN treated + 7 TN controls), then a high-risk-county wave. Alongside, we built a **triangulation engine** (Census-2017 ≈ V2-2017 within ±10% → baseline auto-confirmed, no read needed; disagreement → flag for hand-verify), which auto-cleared ~58% of counties and is what let V2 carry real weight despite its level errors.

**c. V2 audit of the hard cases + sample construction.** We queried V2 across every label/fund/year for the 23 treated counties still unresolved — confirming 15 are structurally dead for documented reasons (KY tax-bundling visible right in V2, TX-oil counties absent, OK/MO cash-basis) and rescuing **one** (Mecklenburg VA, Microsoft Boydton) that nothing else could resolve. We then assembled the matched-DiD sample: **101 of 125 treated counties usable, 1:3 matched, 303 pairs, 137 control counties** (same-state preferred, same-Census-division fallback).

**Net:** roughly a dozen processing/verification scripts (`34`–`45`) and ~95 hand-audited counties stand between Raj's raw V2 delivery and the analysis sample. V2 was the **starting point and the cross-check**, not the finished panel.

---

## 3. The data-quality issues we verified (this is the part that matters)

We ran the same verification battery on V2 that we ran on V1, plus hand-read the underlying ACFRs for ~95 counties as ground truth. The property-tax figures fail in **predictable, state-systematic ways**:

**Mechanical errors (wrong number, right concept):**
- **Unit misfires.** Prince William County VA shows up as **$1.23 *trillion*** (×1,000,000 error; true value $1.23B). Others are ×1000 off. These are catastrophic for a level comparison.
- **School-district sweep-in.** Venango PA's V2 property tax is **9.5× too high** because it absorbed overlapping school-district levies.
- **Fiscal-year mislabel.** Medina TX's "FY2017" row is actually FY2018.

**Structural / under-capture errors (concept itself incomplete):**
- **Single-levy capture.** V2 frequently grabs *one* sub-component, not the total — Arlington VA's V2 figure missed **86%** of real-estate tax (it took personal-property only). Verified wrong in **6 of 8** counties we spot-checked this way.
- **The aggregate-"Taxes" wall.** ~**890 counties** report tax as one undifferentiated line with no property-tax breakout — Tennessee (90 counties), Georgia (85), Minnesota (78) lead. The decomposition exists in the ACFR *notes*, but V2's pipeline doesn't reach the notes. These counties yield **zero** property tax from V2.
- **Ad-valorem misbucketing.** ~1,208 rows of obvious property tax ("Ad valorem taxes") are filed under `MISCELLANEOUS` instead of `PROPERTY TAX REVENUES` — 169 counties, concentrated in NC (86), LA (48), TX (25). This one is a quick regex fix on Raj's side (we've flagged it to him).

**The one redeeming property:** these level errors **mostly cancel in the within-V2 growth rate.** PWC's level is ×1,000,000 wrong, but its V2 CAGR matches the true CAGR (+6.8%) almost exactly. So **V2 growth is usable even when V2 levels are not** — validated to ±2pp in 7 of 10 checks. This is what makes V2 salvageable as a *cross-check* rather than a primary measure.

**Entity-filter inconsistency** (affects national-panel construction, not the PT result directly): V2 passes Denver and Honolulu but *excludes* Indianapolis-Marion, Louisville-Jefferson, Philadelphia, DC, Baltimore, St. Louis, Carson City, and all 39 VA independent cities — 46 consolidated city-counties Census treats as county-equivalents.

---

## 4. Coverage for *our* treated set (the only sample that matters for the paper)

Across our 125 DC-treated counties (DC tax share ≥ 1%):

| | Treated counties | % |
|---|---:|---:|
| V2 has *any* data | 90 | 72% |
| V2 has usable property tax (any tier) | **46** | **37%** |
| Our hand-collected ACFR PDFs | 23 | 18% |
| **PT from at least one source (V2 ∪ ACFR)** | **54** | **43%** |
| Neither V2 nor our PDFs | 25 | 20% |

And the gap is **non-random**: the treated counties V2 misses are the **small rural ones** — Morrow OR, Storey NV, Milam TX, and similar — which are precisely our headline DC-impact stories (hyperscale DC dropped into a tiny tax base). V2 over-represents large counties because they're the ones that reliably clear the Single Audit Act's $750K-federal-awards filing trigger.

---

## 5. The gap between V2 and the tests we intend to run

**The test we are running:** a 2017→post, 1:3 matched, two-period **property-tax growth DiD** — DC counties vs same-state (or same-Census-division) never-DC controls. The sample is now locked at **101 of 125 treated usable, 303 pairs, 130 control counties**, and the DiD has been run (`scripts/python/46_*`).

**Result:** DC counties' county-government property tax grows **~1.3–1.6 pp/yr faster** than matched controls — significant at p<0.01 across every specification:

| Specification | Effect | Inference |
|---|---|---|
| Matched-pair effect (headline) | **+1.62 pp/yr** | bootstrap CI [+0.82, +2.41]; 68/101 positive |
| Pair-stacked OLS, clustered on county | +1.54 pp/yr | SE 0.52, p=0.003 |
| Unique-county OLS, state FE | +1.27 pp/yr | p=0.015 |
| Treated vs +3.40% national benchmark | excess +2.36 pp/yr | p<0.001 |

Robustness holds both directions: dropping the division-fallback pairs (strict same-state, N=97) gives +1.42 pp/yr (p=0.001); dropping the reuse-heavy East-South-Central division (N=86) *strengthens* to +1.91 pp/yr (p=0.0001). This is consistent with the earlier 74-pair read (+1.25 pp/yr) but now better-powered — a larger sample, not a regime change.

**Here is the uncomfortable fact:** that sample was built by **hand-reading ACFRs county-by-county** (≈95 counties, parallel agent + Firecrawl recovery), *not* from V2. V2's contribution to the result was:

1. **Growth-rate triangulation** — where Census-2017 ≈ V2-2017 within ±10%, the baseline auto-confirms with no ACFR read needed (~58% of counties). This saved real labor.
2. **A small number of unique rescues** — most importantly **Mecklenburg VA** (Microsoft Boydton), where V2's consistent FY2016→FY2024 series resolved a Census/scope conflict that nothing else could (independently confirmed against the VA APA report to the dollar: FY24 $113.7M). That's one treated county we'd have lost without V2.
3. **The broad General-Fund control panel** for the *non*-property-tax outcomes.

So the gap, stated plainly:

| What we need for the tests | Does V2 deliver it? |
|---|---|
| Reliable PT **level** per treated county | ❌ No — every value needs triangulation against Census + ACFR |
| PT **growth rate** per treated county | 🟡 Partial — usable where it exists (~37% of treated), errors cancel |
| The **small rural** treated counties (our story) | ❌ No — systematically missing |
| The ~25 structurally-dead counties (KY bundling, TX-oil, OK/MO cash-basis) | ❌ No — and *nothing* can; the audited financials themselves bundle property tax |
| Broad **control** counties for matching | ✅ Yes — V2's main contribution |
| **Capex / debt** channel | 🟡 Newly *possible* via all-funds scope; not yet mined |

---

## 6. The capex & debt channels — what V2 newly let us test

This is the part of the analysis that **only V2 could deliver** — and it's where V2 earned its keep beyond the control panel. V2's new all-governmental-funds scope carries clean GASB expenditure lines (capital outlay, debt-service principal + interest, new borrowing) that V1's General-Fund-only delivery never had. Coverage is ~10× better than property tax (1,041 counties for capex, 1,431 for debt service nationally) because these lines aren't bundled the way "Taxes" is. We mined them on the same 101-treated matched sample (`scripts/python/47–48`).

To sidestep V2's unit errors and capex's year-to-year lumpiness, we used **intensity ratios** (capex / total expenditure; debt service / total revenue), window-averaged FY2016–18 vs FY2022–25. Ratios are unit-free — a ×1000 error cancels top and bottom — and a handful of impossible ratios self-filter.

**Findings:**

| Channel | Effect | Read |
|---|---|---|
| **Debt-service burden** ((prin+int)/revenue) | **+0.18pp, p=0.84 (N=54)** | **Clean null — no leverage-up** |
| Capex intensity (capex/total exp) | −2 to −3pp, significant only in some specs (N=41) | Underpowered; *not* a usable claim |
| New borrowing (proceeds/total exp) | noise (N=11) | Too thin to use |

The headline here is the **debt-service null, and it's a real result, not a non-finding.** A standard worry about communities that host big speculative investments is that they **over-borrow against future tax revenue**. We find no such thing — DC counties' debt-service burden is statistically indistinguishable from their matched controls. Combined with the property-tax result, the fiscal picture is: **tax base up (+1.5pp/yr), debt flat.** That is exactly the profile that *strengthens* municipal credit and is consistent with the bond-spread tightening (−23bps) we found separately — higher coverage of unchanged debt.

On capex, the honest read is **no usable signal.** Decomposing the levels: DC counties' capital outlay *did* grow (+10%/yr, 29 of 40 rose) — they are not cutting capital spending — but their matched controls grew capex even faster (+14.8%/yr), and on N≈40 nothing is significant in the headline specification. So we **cannot** claim DC counties out-invest in roads and schools, nor that they under-invest. The most likely substantive story — and a genuinely interesting one if it holds up with more data — is that **data centers are fiscally "light" on the host**: the campus brings its own power, fiber, and access roads (often via the developer or a special tax district), so the county collects the tax revenue *without* a matching capital obligation on its own budget. That would explain tax-up / county-capex-flat / debt-flat together. We flag it as a hypothesis, not a result — capex coverage in our treated set is too thin (N=41 vs 101 for PT) to settle it.

**Bottom line for the channels:** property tax is the solid mechanism; the debt-service null is a clean, paper-worthy secondary finding that supports the credit-quality story; capex is suggestive of "fiscally light" but underpowered. The capex gap is precisely the argument for the paid all-funds extraction in §7b — more treated counties with capital-outlay coverage is what would turn that hypothesis into a test.

---

## 7. What the money bought — and the discussion question for you

Net assessment, so we're aligned before you talk to Raj:

- **V2 did not produce the property-tax result.** Hand-read ACFRs did. If we'd had only V2, we'd have ~37% treated coverage with unreliable levels and would not have a defensible headline.
- **V2 still earned its place** as (i) a labor-saving cross-check that auto-confirmed more than half our baselines, (ii) the source of at least one otherwise-unrecoverable treated county, and (iii) the only broad-panel route to the General-Fund and (newly) the capex/all-funds outcomes for the controls and the secondary mechanisms.
- **The single highest-leverage thing Raj could still do for us** is reach the **ACFR notes** to decompose the aggregate-"Taxes" line (~890 counties, incl. the entire Tennessee block). That alone would roughly double our V2-native treated PT coverage and reduce our hand-reading burden going forward. We've asked; it's a pipeline change on his end, not ours.

### 7a. Status of asks already with Raj

I sent Raj four observations on 2026-06-07. So you know what's pending vs. what's new to negotiate:

| Ask | Status with Raj | Leverage |
|---|---|---|
| **Decompose the aggregate "Taxes" line via the ACFR notes** (~890 counties, incl. all of TN) | ✅ Raised (Point 3) | **Highest** — roughly doubles V2-native treated PT coverage; pipeline change on his end |
| **Ad-valorem regex re-tag** (MISCELLANEOUS → PROPERTY TAX; 169 counties NC/LA/TX) | ✅ Raised (Point 2) | High, cheap — lifts strict-bucket coverage 924 → ~1,086 |
| Strict PT bucket only ~45% of covered counties | ✅ Raised (Point 1, as framing) | — |
| Entity-filter inconsistency (46 consolidated city-counties excluded) | ✅ Raised (Point 4) | Low for PT; matters for national-panel work |

**What Raj has *not* been told, and could be used as leverage:**

- **His present PT values fail our verification.** The 06-07 email was scoped to *coverage* (why counties are missing), not *accuracy* (why the values that are present are wrong — the ×1,000,000 PWC misfire, Venango's school-district sweep-in, Arlington's 86% under-capture, Medina's FY mislabel). Raj currently thinks he owes us *more rows*; he doesn't know the rows he has don't reconcile to the audited financials. If we want him to prioritize the notes-decomposition pass, this is the lever — a reliability problem is more compelling than a coverage gap.
- **The all-funds / capex extraction is not yet on the table.** V2's new all-governmental-funds scope makes the Capital Projects Fund (capex — the H1 "new roads and schools" channel) reachable for the first time in a panel source, but the 06-07 email didn't ask him to surface capital-outlay line items. This is the natural *paid next deliverable*.
- **One known bug held in reserve:** `county_coverage_map.csv` maps Anchorage Municipality to Aleutians East Borough (~1,000 mi apart). Minor; flag only if it becomes load-bearing.

### 7b. Discussion question

Given that the PT mechanism is carried by hand-collected ACFRs and V2's real value is on the *broader* outcomes (all-funds, capex proxy, control panel), do we:

- **(a)** push Raj on the notes-decomposition + ad-valorem regex for a stronger V2-native PT panel,
- **(b)** negotiate the all-funds capex extraction as the next deliverable since that's the channel V2 newly *can* reach, or
- **(c)** treat V2 as locked and put remaining effort into the ACFR hand-collection that's actually moving the result?

My lean is **(b)+(a)**: the property-tax fight is mostly won by hand; V2's marginal value is now highest on the capex/all-funds channel we haven't exploited.
