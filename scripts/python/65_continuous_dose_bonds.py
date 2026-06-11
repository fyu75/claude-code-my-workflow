"""
65_continuous_dose_bonds.py

Continuous-DOSE bond panel (Frank's idea): instead of a 0/1 treated dummy, use the county's
DC fiscal-intensity RATIO as the treatment magnitude — tests dose-response (does the effect
scale with how big the DC is relative to the county's tax base?).

dose_{c,t} = dc_share_mid_c  ×  buildout fraction_{c,t}
  where dc_share_mid = DC property tax / county property tax (%, the ratio Frank named),
  buildout fraction = (# of the county's DCs operational by year t) / (total # DCs) ∈ [0,1].
Step version (robustness): dose = dc_share_mid × 1[year ≥ first_op_year].
Controls (never-DC) have dose = 0 always.

Outcome ~ dose | county + year FE, cluster county. Coefficient = effect per +1 percentage-point
of DC fiscal share. County-year bond panel (script 63 construction).

Output: data/derived/continuous_dose_bonds.md
"""
from pathlib import Path
import numpy as np, pandas as pd
import pyfixest as pf

ROOT = Path(__file__).resolve().parents[2]; D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)
Y0,Y1=2008,2025

T=pd.read_csv(D/"treated_universe_labeled.csv",dtype={"county_fips":str}); T["county_fips"]=fz(T["county_fips"])
share=dict(zip(T.county_fips,T.dc_share_mid)); cls=dict(zip(T.county_fips,T.dc_class)); treated=set(T.county_fips)
pan=pd.read_csv(D/"county_year_panel_v4.csv",dtype={"county_fips":str}); pan["county_fips"]=fz(pan["county_fips"])
never=pan.groupby("county_fips")["n_dc_cumulative"].max().pipe(lambda s:set(s[s==0].index))-treated

# buildout: # DCs operational by year t per county
dc=pd.read_csv(D/"dc_property_county_fips.csv"); dc["county_fips"]=fz(dc["county_fips"].astype(str))
dc["oy"]=pd.to_numeric(dc["YEARFACILITYBECAMEOPERATIONAL"],errors="coerce")
tot=dc.groupby("county_fips")["oy"].size()
def frac_oper(f,yr):
    s=dc[dc.county_fips==f]["oy"].dropna()
    return (s<=yr).sum()/len(s) if len(s) else 0.0

# deal-level -> county-year (reuse script-63 aggregates)
d=pd.read_csv(D/"sdc_deal_spread.csv"); d["county_fips"]=fz(d["county_fips"].astype(int).astype(str))
d=d[d.county_fips.isin(treated|never)&(d.AMT>0)&d.year.between(Y0,Y1)].copy()
r=pd.read_csv(D/"sdc_deal_rating.csv"); r["MASTER_DEAL_NO"]=pd.to_numeric(r["MASTER_DEAL_NO"],errors="coerce").astype("Int64")
d["MASTER_DEAL_NO"]=pd.to_numeric(d["MASTER_DEAL_NO"],errors="coerce").astype("Int64")
d=d.merge(r[["MASTER_DEAL_NO","any_rated_share","rated_avg_rating"]],on="MASTER_DEAL_NO",how="left")
def pw(g,c):
    w=g.loc[g[c].notna(),"AMT"]; return (g.loc[g[c].notna(),c]*w).sum()/w.sum() if w.sum()>0 else np.nan
cyr=d.groupby(["county_fips","year"]).apply(lambda g: pd.Series({"par_total_M":g.AMT.sum()/1e6,"n_deals":len(g),
    "par_wtd_spread_bps":pw(g,"spread_bps"),"any_rated_share":pw(g,"any_rated_share"),"rated_avg_rating":pw(g,"rated_avg_rating")})).reset_index()
counties=sorted(set(d.county_fips))
bal=pd.MultiIndex.from_product([counties,range(Y0,Y1+1)],names=["county_fips","year"]).to_frame(index=False).merge(cyr,on=["county_fips","year"],how="left")
bal["par_total_M"]=bal.par_total_M.fillna(0); bal["n_deals"]=bal.n_deals.fillna(0); bal["log_par"]=np.log1p(bal.par_total_M)

# build dose (tv = share × buildout-fraction; step = share × 1[any operational by t])
fcache={}
def dose_tv(f,yr):
    if f not in treated: return 0.0
    if (f,yr) not in fcache: fcache[(f,yr)]=frac_oper(f,yr)
    return share.get(f,0.0)*fcache[(f,yr)]
for df in (bal,cyr):
    df["dc_class"]=df.county_fips.map(cls)
    df["dose"]=[dose_tv(f,y) for f,y in zip(df.county_fips,df.year)]

def stat(f,data,keep):
    data=data[(~data.county_fips.isin(treated))|(data.dc_class.isin(keep))].dropna(subset=[f.split('~')[0].strip()])
    try:
        m=pf.feols(f,data=data,vcov={"CRV1":"county_fips"})
        b=m.coef()["dose"];se=m.se()["dose"];p=m.pvalue()["dose"]
        s="***" if p<.01 else "**" if p<.05 else "*" if p<.10 else ""
        return f"**{b:+.4f}{s}** | {se:.4f} | {p:.3f} | {int(m._N):,}"
    except Exception as e: return f"— | — | {str(e)[:20]} | —"

CUTS=[("ALL",["clean_dc","crypto","mixed"]),("clean_dc",["clean_dc"]),("crypto",["crypto"])]
specs=[("par_wtd_spread_bps","Spread (bps/pp-share)",cyr),("log_par","log(1+par)",bal),
       ("n_deals","n deals",bal),("any_rated_share","any-rated share",cyr),("rated_avg_rating","avg rating|rated",cyr)]
L=["# Continuous-Dose Bond Panel (DC fiscal-share ratio as treatment magnitude)\n",
   "**Date:** 2026-06-10. `scripts/python/65`. dose = dc_share_mid (DC tax / county property tax, %) × "
   "buildout-fraction; outcome ~ dose | county + year FE, cluster county. β = effect per +1 percentage-"
   "point of DC fiscal share. Tests dose-response (does the effect scale with DC fiscal size?).\n",
   "| Outcome | Cut | β per pp-share | SE | p | N |","|---|---|---:|---:|---:|---:|"]
for outc,olab,base in specs:
    for nm,ks in CUTS:
        L+=[f"| {olab} | {nm} | "+stat(f"{outc} ~ dose | county_fips + year",base,ks)+" |"]
L+=["", "## Reading",
    "- dose-response: a significant β means bond features scale with the DC's fiscal share — stronger "
    "mechanism evidence than a 0/1 dummy, and harder to explain as a spurious trend.",
    "- Spread β<0 = bigger DC share -> tighter spreads. Rating-avg β<0 = better quality.",
    "- CAVEAT: continuous-treatment DiD (de Chaisemartin–D'Haultfœuille) subtleties; dose timing still "
    "anchored to OPERATIONAL year (anticipation not yet captured — needs announcement dates).", ""]
(D/"continuous_dose_bonds.md").write_text("\n".join(L)); print("\n".join(L)); print("\nWrote continuous_dose_bonds.md")
