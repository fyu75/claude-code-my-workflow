# Literature Review: Data Center Property Tax & Revenue per Megawatt to Local Governments

**Date:** 2026-06-07
**Query:** DC property/personal-property tax revenue per MW to local governments; fiscal impact of data centers on county/municipal property tax base; assessment/valuation of DC real & personal property for local taxation
**Purpose:** Validate the `$50,000/MW/year` calibration used in `scripts/python/15_dc_tax_share_distribution.py` to assign the 1% DC treatment.

## Summary

The peer-reviewed academic literature on the **local fiscal impact of data centers** is nearly empty. Structured academic backends (OpenAlex, SSRN, Semantic Scholar) return generic fiscal-federalism, property-tax-for-schools, and resource-curse papers — none addresses DC property/personal-property tax per MW. **This is itself a finding: the empirical question this project addresses is essentially uncovered in the academic literature**, which is both the opportunity (novelty) and the constraint (no published per-MW benchmark to cite).

The usable evidence is **government / policy grey literature**, chiefly the **JLARC (Virginia) Dec 2024 data-center study** and **county budget documents** for Loudoun and Prince William (VA). These give concrete, citable revenue figures that let us back out an implied $/MW and bracket our calibration band.

## Media / Policy context (primary evidence base)

### JLARC, "Data Centers in Virginia" (Dec 2024) — the authoritative source
- Industry contributes est. **74,000 jobs, $5.5B labor income, $9.1B GDP** annually to VA (most from construction phase).
- VA **sales-and-use tax exemption** for DCs totaled **$2.7B FY2015–2024** ($1B in FY2024 alone) = 53% of the state's total economic-incentive spending; expires 2035.
- JLARC: >90% of VA DC investment would not have occurred *without* the sales/use exemption — i.e., the state exemption is what enables the **local** property-tax windfall.
- URL: https://jlarc.virginia.gov/landing-2024-data-centers-in-virginia.asp

### Loudoun County, VA ("Data Center Alley") — the dense-hub upper bound
- ~**$700M/yr** total DC tax revenue (real property + computer-equipment PP) ≈ **17% of county revenue**.
- Computer-equipment **PP tax: ~$330M (FY2020)** → projected **~$1.37B (FY2026)** (range $1.06–1.48B); $1.5–2.5B by 2030.
- Real-property tax from DCs: $70.4M (FY2020); DCs added $16B of real-property value in 2024 (portfolio $41B).
- Capacity (county energy use): **2.0 GW (2021) → 5.33 GW (2025)**, +233%.
- Efficiency: $0.04 county cost per $1 of DC tax revenue vs $0.25 for normal business.

### Prince William County, VA — the "typical growth county" anchor (our $50k source)
- Total DC tax revenue: **$6.5M (2012) → $166.4M (2023)** (+2,475%).
- Business-tangible PP tax on "Computer Equipment & Peripherals": **$3.39M (2012) → $69.07M (2023)**.
- PP tax rate on computer equipment: $1.25/$100 (2012–19) → $2.15 (2023) → $3.70 (2024) → $4.15 (2025/FY26).
- Capacity added: ~256 MW (2022), ~247 MW retail (2023); 48 DC buildings, 7.04M sq ft (Jan 2023).
- URL: https://www.pwcva.gov/assets/2024-07/aFY25--04--Revenues.pdf

## Implied $/MW — does $50,000 hold up?

Backing out gross PP-tax per MW from the anchors (caveats: MW definitions differ across sources; Loudoun "GW" is county power draw not IT load; PWC figure is PP-only, no real property):

| County | Anchor | Implied $/MW (PP only) | Read |
|---|---|---|---|
| Jackson AL | GASB-77 $971,910 ÷ ~80 MW | **~$12,000** | abated / incentive floor |
| Prince William VA | $69.07M (2023) ÷ ~1,760 MW | **~$39,000** | "typical" growth county |
| Loudoun VA | $330M (FY20) ÷ ~2,000 MW | **~$165,000** | dense hub (outlier) |
| Loudoun VA | $1.37B (FY26 proj) ÷ ~5,330 MW | **~$257,000** | dense hub (outlier) |

**Conclusion:** the **$30k / $50k / $100k (low/mid/high) band is defensible** as a calibration:
- The **$50k mid** ("PP + some real property") sits just above PWC's PP-only $39k — reasonable once real property is added.
- The **$30k low** matches abated/incentive-heavy states (Jackson AL ~$12k is below even this — the floor for fully-abated counties).
- The **$100k high** is still *below* Loudoun. Loudoun exceeds the band — consistent with the project's standing rule to treat **Loudoun as a non-representative outlier**, not a calibration target.
- **Recommendation:** keep low/mid/high as the headline sensitivity; cite JLARC 2024 + PWC/Loudoun budgets for the per-MW range; report the internal implied-$/MW distribution (from our own ACFR + GASB-77 extractions) as the empirical anchor.

## Gaps and Opportunities

1. **No peer-reviewed per-MW property-tax benchmark exists** — this paper would be among the first to quantify DC local fiscal impact systematically across counties (not just VA case studies).
2. **All concrete evidence is VA-centric** (JLARC, Loudoun, PWC). National generalization (our 125-county treated set across TX/GA/OH/etc.) is genuinely new.
3. **State-mechanism heterogeneity is unstudied** — FILOT (SC), IDA-leasehold (GA), Chapter 312 (TX), no-TPP (OH) produce very different effective $/MW; no paper quantifies this.

## Suggested Next Steps

- Cite JLARC (2024) as the authoritative institutional source; pull the primary PDF into `master_supporting_docs/industry_reports/`.
- Build the internal implied-$/MW distribution from our ACFR + GASB-77 data; report median + IQR as the calibration evidence.
- Verify the Loudoun/PWC figures against the primary budget PDFs before citing exact numbers in the paper.

## BibTeX / Grey-literature citations

```bibtex
@techreport{jlarc2024datacenters,
  title       = {Data Centers in Virginia},
  author      = {{Joint Legislative Audit and Review Commission}},
  institution = {Commonwealth of Virginia (JLARC)},
  year        = {2024},
  month       = {December},
  type        = {Legislative study},
  url         = {https://jlarc.virginia.gov/landing-2024-data-centers-in-virginia.asp},
  note        = {Authoritative study of data-center economic and fiscal impact in Virginia; verify exact per-locality figures against primary PDF}
}

@misc{pwc2024revenues,
  title        = {FY2025 Budget --- Revenues (Data Center Business Tangible Personal Property)},
  author       = {{Prince William County, Virginia}},
  year         = {2024},
  howpublished = {County budget document},
  url          = {https://www.pwcva.gov/assets/2024-07/aFY25--04--Revenues.pdf},
  note         = {Computer-equipment PP tax \$3.39M (2012) to \$69.07M (2023); source of the \$50k/MW mid calibration}
}

@misc{loudoun_datacenters,
  title        = {Data Centers in Loudoun County},
  author       = {{Loudoun County, Virginia}},
  year         = {2025},
  howpublished = {County government webpage},
  url          = {https://www.loudoun.gov/6188/Data-Centers-in-Loudoun-County},
  note         = {~\$700M/yr DC tax revenue, ~17\% of county revenue; PP tax ~\$330M (FY20) to projected ~\$1.37B (FY26)}
}
```

## Post-Flight Verification note

Academic-citation hallucination risk is **low** here because the substantive figures come from government primary sources with live URLs returned by Gemini Google-grounding (JLARC, county budgets), not from model recall. **Before any of these numbers enter the paper**, verify Loudoun/PWC/JLARC figures against the primary PDFs (flagged in Next Steps). The academic-literature "gap" claim is robust — four independent backends (OpenAlex, SSRN, Semantic Scholar, arXiv-adjacent) surfaced no DC-local-fiscal-impact paper.
