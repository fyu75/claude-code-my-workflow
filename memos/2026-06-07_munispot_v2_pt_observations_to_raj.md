# Email to Raj — MuniSpot v2 county property-tax observations

**Date drafted:** 2026-06-07
**Sender:** Frank Yu (CEIBS)
**Recipient:** Raj (MuniSpot)
**Context:** Follow-up after v2 interim delivery (Apr→Jun 2026). Four observations on county-level property-tax extraction in v2, ordered mechanical fixes first, scope expansions second.

**Audit history (2026-06-07 — five verification passes):**
- Opening: soft-dropped Raj's "+615" framing. Empirically the lift is ~+294 distinct county_fips (v1 1,903 → v2 2,197); Raj's "+615" counts distinct `auditee_ein`, which inflates because counties pick up new EINs when they change auditors.
- Point 2 — Geography corrected (original draft listed WV/OH as misbucket clusters, but those states' ad-valorem rows are correctly classified by Raj; the misbucketing concentrates in NC/LA/TX). County count corrected from 162 (the lift gain) to 169 (directly affected). NV added to single-digit list.
- Point 3 — Pattern + count corrected. Original ~960 / "all 91 TN counties show TAX REVENUES + 'Taxes' pattern" was wrong. TN actually uses LOCAL REVENUE + 'Local Taxes' (89 of 91 still-gap counties specifically; 90 of 91 use one of the two aggregate forms). Unified aggregate-pattern count is 892 still-gap counties (rounded to "about 890").
- Point 4 — Numbers corrected (38 → 39 VA cities, 45 → 46 total entities) and AK clause dropped (v2's AK handling is mixed: passes 12 of 15 organized boroughs).

**Underlying evidence:**
- v2 raw at `data/munispot/data v2/` (1.5 GB CSVs, FY2016–FY2026)
- v2 parquet at `data/munispot/parquet_v2/` (55 MB, Hive-partitioned)
- Classifier output: `data/derived/muni_property_tax_v2_classified_gf_only_FY2016_2026.parquet`
- Coverage map: `data/derived/munispot_county_equiv_coverage_v2.csv`
- Filter exclusions: `data/derived/munispot_filter_exclusions_v2.csv`
- Build scripts: `scripts/python/34_convert_munispot_v2_to_parquet.py`, `35_classify_munispot_property_tax.py`, `36_recover_county_equivalents_v2.py`

**Additional issue observed but NOT in email (would dilute the asks):** Raj's `county_coverage_map.csv` has a county-name-vs-municipality_name mapping bug — first row reads state=AK, county="Anchorage Municipality", municipality_name="Aleutians East Borough" (these are ~1,000 miles apart). Flag separately if it becomes load-bearing.

---

## Email body

Subject: MuniSpot v2 — four observations on county property-tax coverage

Hi Raj,

Thanks for getting v2 out so quickly. The coverage lift is real, and the rural fill from the state-portal supplementing is exactly where v1 was thinnest — that work shows. Got the files, converted to parquet, ran the same checks we did on v1. Four observations on the county-level property-tax side, ordered mechanical fixes first, bigger lifts second.

1. The class_1 = 'PROPERTY TAX REVENUES' bucket returns rows for 924 of the 2,055 covered counties (~45%) — points 2 and 3 below are what's driving the gap on the other 55%.

2. About 1,208 ad-valorem rows are misbucketed into MISCELLANEOUS, spread across 169 counties — concentrated in North Carolina (86), Louisiana (48), and Texas (25), with single-digit cases in SC, MS, OK, FL, GA, NV. The reported_stat values are unambiguous — "Ad valorem taxes", "Ad valorem property taxes", "Ad valorem" — but class_1 reads MISCELLANEOUS. A regex re-tag on reported_stat ("ad valorem" or "real estate tax" → PROPERTY TAX REVENUES) lifts strict-bucket coverage from 924 to ~1,086 counties. Likely a quick fix on your side.

3. About 890 counties report tax revenue as a single aggregate line with no breakdown — either class_1='TAX REVENUES' with reported_stat='Taxes', or class_1='LOCAL REVENUE' with reported_stat='Local Taxes' (the Tennessee pattern). Tennessee leads with 90 counties (almost all via the LOCAL REVENUE form); secondary clusters in GA (85), MN (78), WI/FL/MI (~54 each), CA (47), AL (41), KY (40), CO (39). The decomposition usually does exist in the ACFR, but in the notes to the financial statements rather than the governmental-funds statement itself — typical wording is "Note 4 — Taxes consisted of $X general property taxes, $Y sales and use, $Z local option…". If the pipeline can reach the notes, that's where most of the remaining property-tax coverage sits.

4. One consistency note on the county-equivalent filter: it passes Denver and Honolulu, but excludes Indianapolis-Marion, Louisville-Jefferson, Philadelphia, DC, Baltimore, St. Louis, Carson City, and all 39 VA independent cities (state 51, cfips 510-840) — 46 entities Census treats as county-equivalents.

Happy to send row-level evidence behind any of these — the ad-valorem misbucket list is a reported_stat grep on your end, and I can pass the geoids for (4) if useful. Glad to share our reported_stat classifier code too if it's helpful for cross-checking (1).

Best,
Frank
CEIBS
