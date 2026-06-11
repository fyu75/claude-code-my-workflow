# DC Share Formula Refinement — Mechanism Corrections from ACFR Sprint

**Date:** 2026-06-07
**Authors:** dc-muni team
**Status:** Working memo for internal discussion (Henrik / Mitch / Frank)
**Context:** Tier 1-5 ACFR scrape sprint surfaced state-mechanism evidence that should reshape how we compute DC share and interpret the treated-set composition.

---

## Current DC share definition (for reference)

From the prior intensity-estimation work in `scripts/python/37_*` and outputs in `data/derived/dc_tax_share_distribution.csv`:

**DC share = (estimated DC property tax) / (2017 county property tax base) × 100%**

- **Numerator** = `MW_latest × $X per MW per year`, with three estimates (low / mid / high) capturing assumed assessed-value-per-MW × effective tax rate
- **Denominator** = `prop_tax_2017_M` from Census 2017 ACFR (county-government-only, type=1)
- **Treatment cut** = `dc_share_mid ≥ 1%` → 125 counties

The "$X per MW" estimates encode assumptions about:
1. Assessed value per MW: DC capex per MW (typically $7-15M/MW), assessment ratio (varies by state), asset depreciation schedule
2. Effective tax rate: county property tax mill rate × assessment ratio
3. The low/mid/high range captures uncertainty in both

---

## Where the new ACFR data would change things

> The current formula assumes DCs pay tax at the standard county property tax rate. Our new data shows this is wrong in several states. The most consequential corrections aren't to the MW or PT numbers — they're to the assumption that the standard rate even applies.

### 1. State-mechanism corrections (most impactful)

| State | What the new data shows | Implication for DC share |
|---|---|---|
| **SC** (Berkeley, Spartanburg) | FILOT reduces personal property assessment from 10.5% to 4-6%. Berkeley FILOT $20.7M GF (53% of PT); Spartanburg FILOT+SSRC $32M (25% of PT, $118M counterfactual gross). | Current formula likely **overstates** SC DC share by ~50-60% |
| **GA** (Newton, Jackson GA, Douglas) | IDA leasehold bonds hold title to DC equipment → effectively tax-exempt at county level. Newton: no DC in top-10 taxpayers despite Meta/Takeda/Rivian; Jackson GA: personal property AV dropped $223M (2022→2023). | Current formula **massively overstates** GA DC share. Actual DC PT might be 10-30% of what the formula implies. |
| **AL** (Madison) | 90% property tax abatement disclosed in ACFR for IT-company taxpayer ($4.08M abated). | Current formula **overstates** AL DC share by ~10× for FILOT-style abatement targets |
| **TX** (Ellis, Ector) | Local Govt Code §312 abatement (85% improvement value + 100% personal property for 10 yrs). Ellis: Sharka LLC in Midlothian Technology RZ. | Current formula **overstates** TX DC share substantially for counties using §312 |
| **OH** (Licking, Franklin, Union OH, Fairfield) | (a) DC tax goes mostly to categorical levies (Dev Disabilities, Children's Services), NOT GF — AF/GF ratio 2.4-8.1×. (b) **CRITICAL**: OH abolished business tangible personal property (TPP) tax in 2005-2011. DCs in OH are taxed only on real property (building shell + land), NOT on the servers/cooling/generators (70-90% of DC asset value). | The "share" should use AF PT as denominator, not GF — current formula understates denominator. AND DC numerator should be cut by ~70-90% because OH cannot tax the personal property base. Two-direction correction. Affects 4 treated counties. |
| **KY** (Lawrence, Marshall, McCracken, Jackson KY) | KY "Taxes" line bundles ad valorem + occupational tax; DC PILOT shows up separately ($180K-$926K). | Denominator overstated; numerator should add PILOT |
| **MO** (Clay) | County retains only its own $0.31/$100 levy; schools/cities collect separately. | Current formula **overstates** MO DC share because numerator implicitly counted county-share only but denominator was county PT |

### 2. Denominator-year update

- Currently uses 2017 (Census ACFR baseline).
- We now have FY22-FY24 ACFR PT for many counties (~75 with both GF + AF).
- **Recommendation**: keep 2017 as the pre-treatment baseline (defensible for identification), but compute a parallel share using FY22-FY24 as a "current intensity" metric. The two would diverge most in fast-growing counties (Newton GA grew PT 12% YoY, named #1 fastest-growing GA county in FY2023).

### 3. Denominator scope (GF vs all-funds)

- The 2017 baseline from Census ACFR uses **all governmental funds** (Census aggregation).
- Our v2 GF-only PT classifier is the wrong column to compare against — apples-to-oranges.
- **Recommendation**: use the all-funds figure consistently. For counties without all-funds in our PDFs, use Census 2017 as the comparator. For Raj's v2 data, use `column_index = -1` (Total Governmental Funds).

### 4. Numerator refinement using observed DC PT

We have a few direct windows into DC fiscal impact from the ACFR sprint:

| County | Direct observation | Implication |
|---|---|---|
| Lawrence KY | $180K PILOT in a county with $1.43M GF PT | DC contribution ~13% of GF; much smaller than the 191% formula claim |
| Marshall KY | $795K PILOT / $3M GF PT | ~26% — closer to formula |
| Jackson KY | $168K personal property surprise / $313K total PT | ~54% — matches formula reasonably |
| Madison AL | $4M abatement (i.e., 10% of what would have been collected at gross) | DC is a real player; net contribution roughly 10% of pre-abatement gross |
| Spartanburg SC | $24M FILOT / $94M GF PT | 25% (FILOT as proxy for DC PT) |
| Berkeley SC | $20.7M FILOT / $38.7M GF PT | 53% (FILOT directly visible) |
| Newton GA | No DC in top-10 taxpayers despite Meta/Takeda/Rivian | DC effectively tax-exempt via IDA leasehold |
| Union OH | AWS $2B DC just started construction 2023, not yet on rolls | Future-period mechanism evidence only |

These cases suggest the **low estimate** in `dc_tax_share_distribution.csv` is probably closer to truth for FILOT/IDA-leasehold states; the **high estimate** may be closer for KY/VA/TX (no abatement, or partial via §312).

---

## Suggested refinements

### For paper purposes

1. **Add a `pt_structure_state` column** to `dc_tax_share_distribution.csv` capturing the dominant state mechanism:
   - `SC-FILOT` (Berkeley, Spartanburg)
   - `GA-IDA-leasehold` (Newton, Jackson GA, Douglas GA, Cook GA, Fulton GA, Whitfield GA, Harris GA)
   - `AL-abatement-heavy` (Madison AL, Jackson AL)
   - `OH-categorical-no-TPP` (Licking, Franklin, Union OH, Fairfield)
   - `TX-Chapter-312-abatement` (Ellis, Ector + ~10 other TX counties)
   - `KY-consolidated-with-PILOT` (Lawrence, Marshall, McCracken, Pike, Jackson KY)
   - `VA-consolidated` (Prince William, Loudoun, Fairfax, Henrico, etc.)
   - `NV-Switch-deals` (Storey, Clark)
   - `standard` (default)

   This becomes a categorical robustness control. Heterogeneity analysis runs DiD separately by structural category.

2. **Two-version DC share**:
   - `dc_share_naive_*` — current formula, useful as the "headline" intensity (preserved for compatibility)
   - `dc_share_adjusted_*` — apply state-mechanism multipliers:
     - FILOT states (SC): × 0.40-0.60
     - IDA-leasehold states (GA): × 0.10-0.30
     - AL abatement-heavy: × 0.10-0.20
     - OH no-TPP: × 0.10-0.30 (only building shell taxed)
     - TX §312 active: × 0.15-0.30
     - KY with PILOT: × 0.80-1.00 + add PILOT directly
     - standard: × 1.00

3. **Cross-check via observed values**: where we have a direct PILOT or abatement number from the ACFR, anchor the county's DC share against that directly rather than using the formula. Use these as "ground truth" cases for calibrating the state-mechanism multipliers above.

---

## What this means for the treated set (n=125)

> The 125-county treated set is probably stable in size, but with composition shifts that matter for the paper. Some "high-share" counties (Newton GA at 12%, Jackson GA at 1%) may drop out because the IDA-leasehold structure makes their de facto county-level DC PT very small. Some "low-share" counties (KY counties with substantial PILOT) may move up if we credit PILOT correctly. The KY/VA/TX-non-§313 counties stay roughly where they are. The most-affected segments are the GA cluster (six treated counties) and the OH cluster (four treated counties) — current shares may be overstated by 5-10× in each.

### Concrete suggested order of operations

1. Verify with the team (Henrik, Mitch) which structural adjustments are defensible
2. Build the `pt_structure_state` flag from the data we've gathered (running notes file `dc_mechanism_evidence_running_notes.md` is the working source)
3. Compute `dc_share_adjusted_mid` with state-mechanism multipliers
4. Re-run the within-county growth tests + DiD on both naive and adjusted definitions
5. If adjusted estimates pass the t-test, they become the primary; naive becomes the robustness check

This is exactly the kind of empirical refinement the new ACFR scrape was set up to enable. Tier 1-5 sprint makes this much more credible than it would have been with only v2 data.

---

## Raj's v2 data: GF vs all-funds — what's available and what to use

Raj's MuniSpot v2 has BOTH scopes via the `column_index` column:

| `column_index` | What it represents | Comparable to our PDF |
|---:|---|---|
| **1** | General Fund | `property_tax_gf` |
| **-1** | Total Governmental Funds (all-funds) | `property_tax_allfunds` |
| 2, 3, 4, 5, 6, 7 | Individual non-major funds (Road, Capital Projects, Debt Service, etc.) | breakdown components |

Our derived files split this for convenience:
- `data/derived/muni_property_tax_v2_classified_gf_only_FY2016_2026.parquet` — `column_index == 1` filter applied
- `data/derived/muni_property_tax_v2_classified_allfunds_FY2016_2026.parquet` — `column_index == -1` filter applied

### Important caveat from the coverage audit

The two column counts looked nearly identical (46 counties in our treated set for each), which masks a bigger picture: **where Raj has GF, he almost always has all-funds too.** That's because both columns come from the same parsed ACFR. The all-funds column adds *value* (richer measurement) but not *breadth* (extra counties). So switching from GF to all-funds for the paper is about measurement quality — especially for OH/IL/WA counties where AF is 2-8× GF — not about adding more counties to the sample.

### Coverage by scope (from the audit)

| | Counties classified PT |
|---|---:|
| v2 GF (`column_index == 1`, tier_with_pilot) | 1,092 |
| v2 All-Funds (`column_index == -1`, tier_with_pilot) | 1,081 |
| Intersection | ~1,075 (overlap is very high) |

### What this means practically

1. **For comparing v2 vs our PDFs**: use the matching column. Our `property_tax_gf` ↔ Raj's `column_index=1`. Our `property_tax_allfunds` ↔ Raj's `column_index=-1`.

2. **For the paper's main analysis**: per our Option C decision, the all-funds figure is the primary analytical column (better measurement). Use Raj's `column_index=-1` for counties where we don't have PDFs.

3. **For state-specific patterns**: where Raj's all-funds matters most:
   - **OH**: AF is 2.4-8.1× GF (categorical-dominated)
   - **IL**: AF is 1.5× GF
   - **WA**: AF is 1.5-2× GF (multi-fund levies)
   - **GA**: AF is 1.3-1.9× GF (SPLOST adjacent)
   - Where GF ≈ AF (KY, NE, AL, PA): either column is fine

4. **Limitations all-funds does NOT fix**:
   - Raj's `class_1='PROPERTY TAX REVENUES'` still misses ad-valorem rows in MISCELLANEOUS (1,208 rows in LA/NC/TX). Our `35_classify_munispot_property_tax.py` lifts this — but Raj's raw bucket doesn't.
   - **Aggregate "Taxes" / "Local Taxes" counties** (TN especially, also FL/GA/MI/WI/AL) — still unsolvable from Raj's data alone regardless of column_index. PT just isn't broken out at the source. Our Tier 5a TN-notes-mining sprint had to scrape source ACFRs to get this.
   - **Filter-excluded entities** (Philadelphia, DC, Baltimore, St. Louis, Carson City, Indianapolis, Louisville, 38 VA indep cities) — still excluded.

### Bottom line on Raj's data

When asked "should we use GF or all-funds from Raj?", the answer is **all-funds (`column_index=-1`)** as the primary analytical column, with GF (`column_index=1`) as the v2-audit-comparison column. But all the v2 data-quality limitations we've documented apply equally to both column choices — they're not solved by switching scope. The state-mechanism corrections in §1 above still apply to both Raj-source columns.

---

## Cross-references

- **Mechanism evidence file**: `memos/dc_mechanism_evidence_running_notes.md` — running list of state-specific findings, anecdote candidates, structural caveats
- **Coverage table**: `data/derived/dc_treated_coverage_v2_vs_acfr.csv` — one-row-per-treated-county matrix of what data we have
- **Master PT table**: `data/derived/acfr_county_year_extracted_wide.csv` — dual-column GF + all-funds for each county-year we've extracted
- **Source DC share file**: `data/derived/dc_tax_share_distribution.csv` — current definition
- **v2 (Raj's) PT data**: `data/munispot/parquet_v2/` partitioned by (statement_type, fiscal_year); `column_index = -1` for all-funds, `column_index = 1` for GF-only
