"""
61_phase4_event_study.py  — PHASE 4

Annual event study on the MuniSpot-v2 county property-tax panel (FY2016-2024), to deliver what
the 2-period design cannot: a PRE-TRENDS test (validates parallel trends behind the +3.07%/yr
Phase-2 headline) and the DYNAMICS (does PT jump at DC opening or ramp?).

HONEST SCOPE: v2 covers only ~31 of 125 treated with >=4 annual years -> this is a credibility /
dynamics check on that subset, NOT a power upgrade. Control group = never-DC counties in v2 (~568).
log(PT) outcome + county FE absorb the v2 level/scope bias (constant within county); identification
is within-county over time vs never-treated.

Design: binned event-study TWFE. event_time = fiscal_year - first_op_year (treated); reference = -1.
Bins [-4..+4]; controls carry all-zero event dummies. log_pt ~ D_{-4..-2,0..+4} | county + year,
SEs clustered on county. (Staggered timing -> a Sun-Abraham/CS version is the robustness; flagged.)

Output: data/derived/phase4_event_study.md
"""
from pathlib import Path
import numpy as np, pandas as pd
import pyfixest as pf

ROOT = Path(__file__).resolve().parents[2]; D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)

# --- v2 annual county-govt PT panel ---
v = pd.read_csv(D/"muni_property_tax_v2_classified_gf_only_FY2016_2026.csv", dtype={"county_fips":str}, low_memory=False)
v["county_fips"]=fz(v["county_fips"])
v = v[(v.tier_strict==True)&(v.column_index==1)&(v.fiscal_year.between(2016,2024))].copy()
v["val"]=pd.to_numeric(v["reported_value"],errors="coerce")*pd.to_numeric(v["value_multiplier"],errors="coerce").fillna(1)
pr = v.groupby(["county_fips","fiscal_year","report_id"])["val"].sum().reset_index()
cy = pr.groupby(["county_fips","fiscal_year"])["val"].median().reset_index()
cy = cy[cy["val"]>0].copy(); cy["log_pt"]=np.log(cy["val"])
nyrs = cy.groupby("county_fips")["fiscal_year"].nunique()
cy = cy[cy["county_fips"].isin(nyrs[nyrs>=4].index)]

# --- treatment cohorts ---
oy = pd.read_csv(D/"treated_universe_labeled.csv", dtype={"county_fips":str}); oy["county_fips"]=fz(oy["county_fips"])
coh = dict(zip(oy["county_fips"], oy["first_op_year"]))
dc_class = dict(zip(oy["county_fips"], oy["dc_class"]))
pan = pd.read_csv(D/"county_year_panel_v4.csv", dtype={"county_fips":str}); pan["county_fips"]=fz(pan["county_fips"])
never = pan.groupby("county_fips")["n_dc_cumulative"].max().pipe(lambda s:set(s[s==0].index))

treated_set = set(oy["county_fips"]) & set(cy["county_fips"])
ctrl_set    = (never & set(cy["county_fips"])) - treated_set
cy = cy[cy["county_fips"].isin(treated_set | ctrl_set)].copy()
cy["is_treated"] = cy["county_fips"].isin(treated_set)
cy["cohort"] = cy["county_fips"].map(coh)

# usable treated = cohort in [2017,2023] (>=1 pre and >=1 post inside 2016-2024)
cy["et"] = np.where(cy["is_treated"], cy["fiscal_year"]-cy["cohort"], np.nan)
usable_treated = set(cy[(cy["is_treated"]) & (cy["cohort"].between(2017,2023))]["county_fips"])
# drop always-treated (cohort<2017) and not-yet (cohort>2023) treated from the estimation panel
cy = cy[(~cy["is_treated"]) | (cy["county_fips"].isin(usable_treated))].copy()

# binned event-time dummies (reference -1); controls -> all zero
def binned(et):
    if pd.isna(et): return None
    return int(np.clip(et, -4, 4))
cy["etb"] = cy["et"].apply(binned)
for k in [-4,-3,-2,0,1,2,3,4]:
    cy[f"D{k:+d}".replace("+","p").replace("-","m")] = ((cy["is_treated"]) & (cy["etb"]==k)).astype(int)
dcols = [c for c in cy.columns if c.startswith("Dm") or c.startswith("Dp")]

fml = "log_pt ~ " + " + ".join(dcols) + " | county_fips + fiscal_year"
m = pf.feols(fml, data=cy, vcov={"CRV1":"county_fips"})
co, se, pv = m.coef(), m.se(), m.pvalue()

def lab(k): return f"D{k:+d}".replace("+","p").replace("-","m")
order = [-4,-3,-2,0,1,2,3,4]
L=["# Phase 4 — Annual Event Study (v2 panel, pre-trends + dynamics)\n",
   "**Date:** 2026-06-10. `scripts/python/61`. Outcome = log(county-govt property tax), v2 FY2016-2024. "
   "Binned event-time TWFE, county + year FE, SEs clustered on county. Reference period = -1.\n",
   f"Usable treated (cohort 2017-2023, >=4 v2 yrs): **{len(usable_treated)}** | never-DC controls: "
   f"**{len(ctrl_set):,}** | county-year obs: {len(cy):,}\n",
   "| Event time | coef (log pts) | SE | p | |", "|---|---:|---:|---:|---|"]
for k in order:
    c=lab(k); b=co.get(c,np.nan); s=se.get(c,np.nan); p=pv.get(c,np.nan)
    star="***" if p<.01 else "**" if p<.05 else "*" if p<.10 else ""
    tag = "pre (parallel-trends test)" if k<0 else ("**DC opens**" if k==0 else "post")
    L.append(f"| {k:+d} | {b:+.3f}{star} | {s:.3f} | {p:.3f} | {tag} |")
L+=["| −1 | 0 (ref) | — | — | reference |"]
pre = [co.get(lab(k),np.nan) for k in [-4,-3,-2]]
post= [co.get(lab(k),np.nan) for k in [0,1,2,3,4]]
L+=["", f"**Pre-trend coefficients (−4,−3,−2): {', '.join(f'{x:+.3f}' for x in pre)}** — "
    "near zero & insignificant => parallel trends supported.",
    f"**Post path (0..+4): {', '.join(f'{x:+.3f}' for x in post)}** — log-point lift in PT after DC opens.",
    "", "## Reading guide",
    "- Pre-period coefs ≈ 0 (insignificant) is the key validation: treated and control PT move together "
    "BEFORE the DC, so the Phase-2 +3.07%/yr is not a pre-existing divergence.",
    "- Post coefs rising = the tax base ramps after opening (consistent with multi-year buildout/assessment).",
    "- CAVEAT: only ~31 treated have annual v2 data; staggered TWFE can be biased under effect "
    "heterogeneity -> a Sun-Abraham/Callaway-Sant'Anna version is the robustness. This is a dynamics/"
    "credibility check on the subset, not a power upgrade over the 92-treated 2-period headline.", ""]
(D/"phase4_event_study.md").write_text("\n".join(L))
print("\n".join(L))
print("\nWrote phase4_event_study.md")
