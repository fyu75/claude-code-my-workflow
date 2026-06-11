"""
64_pt_timing_event_study.py

Tests Frank's construction-channel hypothesis: does a county's PROPERTY TAX start rising
BEFORE the DC's "operational" year (construction-in-progress assessment, land reassessment,
phased personal property)? If pre-operational coefficients (−2,−1) are positive, the operational
date is too late and the tax base responds during construction.

Annual log(property tax) from MuniSpot v2 (FY2016-2024); county + year FE; event time relative to
first_op_year, reference = −1. Finer (unbinned) resolution near 0. Never-DC controls.
HONEST: v2 covers ~31 treated -> underpowered; this is a directional/timing read.

Output: data/derived/pt_timing_event_study.md
"""
from pathlib import Path
import numpy as np, pandas as pd
import pyfixest as pf

ROOT = Path(__file__).resolve().parents[2]; D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)

v=pd.read_csv(D/"muni_property_tax_v2_classified_gf_only_FY2016_2026.csv",dtype={"county_fips":str},low_memory=False)
v["county_fips"]=fz(v["county_fips"]); v=v[(v.tier_strict==True)&(v.column_index==1)&v.fiscal_year.between(2016,2024)].copy()
v["val"]=pd.to_numeric(v["reported_value"],errors="coerce")*pd.to_numeric(v["value_multiplier"],errors="coerce").fillna(1)
cy=v.groupby(["county_fips","fiscal_year","report_id"])["val"].sum().reset_index().groupby(["county_fips","fiscal_year"])["val"].median().reset_index()
cy=cy[cy["val"]>0].copy(); cy["log_pt"]=np.log(cy["val"]); cy=cy.rename(columns={"fiscal_year":"year"})
ny=cy.groupby("county_fips")["year"].nunique(); cy=cy[cy["county_fips"].isin(ny[ny>=4].index)]

T=pd.read_csv(D/"treated_universe_labeled.csv",dtype={"county_fips":str}); T["county_fips"]=fz(T["county_fips"])
opy=dict(zip(T.county_fips,T.first_op_year)); cls=dict(zip(T.county_fips,T.dc_class)); treated=set(T.county_fips)
pan=pd.read_csv(D/"county_year_panel_v4.csv",dtype={"county_fips":str}); pan["county_fips"]=fz(pan["county_fips"])
never=pan.groupby("county_fips")["n_dc_cumulative"].max().pipe(lambda s:set(s[s==0].index))-treated
cy=cy[cy.county_fips.isin((treated&set(cy.county_fips))|(never&set(cy.county_fips)))].copy()
cy["treated_ever"]=cy.county_fips.isin(treated).astype(int); cy["dc_class"]=cy.county_fips.map(cls); cy["oy"]=cy.county_fips.map(opy)
cy["et"]=np.where(cy.treated_ever==1, cy.year-cy.oy, np.nan)
usable=set(cy[(cy.treated_ever==1)&cy.oy.between(2018,2023)].county_fips)
cy=cy[(cy.treated_ever==0)|(cy.county_fips.isin(usable))].copy()

def es(data,label):
    for k in [-3,-2,0,1,2,3]:
        data[f"e{k:+d}".replace('+','p').replace('-','m')]=((data.treated_ever==1)&(np.clip(data.et,-3,3)==k)).astype(int)
    ec=[c for c in data.columns if c.startswith("ep") or c.startswith("em")]
    m=pf.feols("log_pt ~ "+" + ".join(ec)+" | county_fips + year", data=data, vcov={"CRV1":"county_fips"})
    co,pv,se=m.coef(),m.pvalue(),m.se()
    out=[f"### {label}  (N treated cohorts: {data[(data.treated_ever==1)].county_fips.nunique()})"]
    out+=["| event time | coef (log pt) | SE | p | |","|---|---:|---:|---:|---|"]
    for k in [-3,-2,0,1,2,3]:
        c=f"e{k:+d}".replace('+','p').replace('-','m'); b=co.get(c,np.nan); s=se.get(c,np.nan); p=pv.get(c,np.nan)
        st="***" if p<.01 else "**" if p<.05 else "*" if p<.10 else ""
        tag="**pre-operational** (construction test)" if k<0 else ("**operational**" if k==0 else "post")
        out.append(f"| {k:+d} | {b:+.3f}{st} | {s:.3f} | {p:.3f} | {tag} |")
    out.append("| −1 | 0 (ref) | — | — | reference |")
    return out

L=["# Property-Tax Timing Event Study — does the tax base rise BEFORE operational?\n",
   "**Date:** 2026-06-10. `scripts/python/64`. log(county property tax), v2 annual, county+year FE, "
   "event time vs first_op_year, ref −1. Tests construction-in-progress assessment (Frank's hypothesis).\n",
   "**If coefficients at −2/−3 are POSITIVE & rising, the tax base responds DURING construction "
   "→ operational date is too late.**\n"]
L+=es(cy.copy(),"ALL treated")
L+=[""]+es(cy[(cy.treated_ever==0)|(cy.dc_class=="clean_dc")].copy(),"Clean hyperscale/colo only")
L+=["", "## Reading", "- Positive pre-operational (−2,−3) => construction/assessment channel (tax up before 'operational').",
    "- Flat pre + positive post => effect lags operational (assessment cycle AFTER completion).",
    "- v2 thin (~16-31 treated) -> directional; the announcement-dated re-timing (agent-feasible, ~75% hit) "
    "is the proper fix.", ""]
(D/"pt_timing_event_study.md").write_text("\n".join(L)); print("\n".join(L)); print("\nWrote pt_timing_event_study.md")
