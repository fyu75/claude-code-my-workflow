"""
62_bond_block_cleaned.py

Re-run the BOND BLOCK on the CLEANED treatment (today's foundation): treated = operating-by-2022,
crypto LABELED (clean/crypto/mixed cut), treatment timed to first_op_year (not first_dc_year).
Controls = never-DC-host. Directly comparable to the property-tax result; supersedes scripts 16/49/
50/51 (old contaminated ≥1% set with first_dc_year).

treated_post = treated_ever AND year>=first_op_year; SEs clustered on county.
  A. SPREAD (deal-level hedonic): spread_bps ~ treated_post + log_mat + log_amt | county + state×year
  B. ISSUANCE (county-year):      log(1+par_M), log(n_deals) ~ treated_post | county + year
  C. RATING (deal-level):         any_rated_share (extensive), rated_avg_rating (intensive)
Cuts: ALL / clean_dc / crypto / mixed (treated_post=1 only for that class; other classes dropped).

Output: data/derived/bond_block_cleaned.md
"""
from pathlib import Path
import numpy as np, pandas as pd
import pyfixest as pf

ROOT = Path(__file__).resolve().parents[2]; D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)

T = pd.read_csv(D/"treated_universe_labeled.csv", dtype={"county_fips":str}); T["county_fips"]=fz(T["county_fips"])
# NO treated_by_2022 filter for BONDS: SDC deal data runs to 2025, so staggered treated_post
# (year>=first_op_year) correctly times the late openers (2023-25). Dropping them would discard
# real post-DC bond variation (115 post-op deals across 20 counties). The 2022 cutoff applies only
# to the 2-period property-tax Census DiD (no PT data past 2022), NOT to the deal-level bond panel.
T = T.copy()
opyear=dict(zip(T["county_fips"],T["first_op_year"])); cls=dict(zip(T["county_fips"],T["dc_class"]))
treated_all=set(T["county_fips"])
pan=pd.read_csv(D/"county_year_panel_v4.csv", dtype={"county_fips":str}); pan["county_fips"]=fz(pan["county_fips"])
never=pan.groupby("county_fips")["n_dc_cumulative"].max().pipe(lambda s:set(s[s==0].index))-treated_all

d=pd.read_csv(D/"sdc_deal_spread.csv"); d["county_fips"]=fz(d["county_fips"].astype(int).astype(str))
d=d[d["county_fips"].isin(treated_all|never)&(d["AMT"]>0)].copy()
d["treated_ever"]=d["county_fips"].isin(treated_all).astype(int)
d["dc_class"]=d["county_fips"].map(cls); d["oy"]=d["county_fips"].map(opyear)
d["state_year"]=d["STATECODE"].astype(str)+"_"+d["year"].astype(str); d["log_amt"]=np.log(d["AMT"])

def post_for(data, keep):
    x=data[(data["treated_ever"]==0)|(data["dc_class"].isin(keep))].copy()
    x["treated_post"]=((x["treated_ever"]==1)&(x["year"]>=x["oy"])).astype(int)
    return x

def stat(formula, data):
    data=data.dropna(subset=[formula.split("~")[0].strip(),"treated_post"])
    try:
        m=pf.feols(formula, data=data, vcov={"CRV1":"county_fips"})
        return dict(b=m.coef()["treated_post"], se=m.se()["treated_post"], p=m.pvalue()["treated_post"], n=int(m._N))
    except Exception as e:
        return dict(err=str(e)[:30])

def fmt(r, dec=3):
    if "err" in r: return f"— | — | {r['err']} | —"
    s="***" if r["p"]<.01 else "**" if r["p"]<.05 else "*" if r["p"]<.10 else ""
    return f"**{r['b']:+.{dec}f}{s}** | {r['se']:.{dec}f} | {r['p']:.3f} | {r['n']:,}"

CUTS=[("ALL",["clean_dc","crypto","mixed"]),("clean_dc",["clean_dc"]),("crypto",["crypto"]),("mixed",["mixed"])]
L=["# Bond Block — CLEANED treatment (operating-by-2022, crypto labeled, op-year timing)\n",
   "**Date:** 2026-06-10. `scripts/python/62`. Supersedes 16/49/50/51. treated_post = treated AND "
   "year≥first_op_year; cluster county. Controls = never-DC-host (2,498).\n",
   ""]
_iss=d[d["treated_ever"]==1]["county_fips"].unique()
_n=lambda c: sum(1 for f in _iss if cls.get(f)==c)
L+=[f"Treated issuing bonds: **{len(_iss)}** (clean {_n('clean_dc')} / crypto {_n('crypto')} / "
    f"mixed {_n('mixed')}); controls {len(never):,}. Timing = first_op_year (staggered, deals to 2025).\n"]

# A. SPREAD
ds=d[d["par_wtd_yrs2mat"]>0].copy(); ds["log_mat"]=np.log(ds["par_wtd_yrs2mat"]); ds=ds.dropna(subset=["spread_bps"])
L+=["## A. Deal-level hedonic spread — β on treated_post (NEGATIVE = tighter/cheaper)","",
    "| Cut | β (bps) | SE | p | N |","|---|---:|---:|---:|---:|"]
for nm,ks in CUTS:
    L+=[f"| {nm} | "+fmt(stat("spread_bps ~ treated_post + log_mat + log_amt | county_fips + state_year", post_for(ds,ks)),2)+" |"]

# B. ISSUANCE (county-year)
cy=d.groupby(["county_fips","year"]).agg(par_M=("AMT",lambda s:s.sum()/1e6),n_deals=("AMT","size")).reset_index()
cy["treated_ever"]=cy["county_fips"].isin(treated_all).astype(int); cy["dc_class"]=cy["county_fips"].map(cls)
cy["oy"]=cy["county_fips"].map(opyear); cy["log_par"]=np.log1p(cy["par_M"]); cy["log_n"]=np.log(cy["n_deals"])
L+=["", "## B. Issuance, county-year — β on treated_post (POSITIVE = issue more)","",
    "| Cut | log(1+par $M) | log(n deals) |","|---|---|---|"]
for nm,ks in CUTS:
    sub=post_for(cy,ks)
    a=fmt(stat("log_par ~ treated_post | county_fips + year", sub))
    b=fmt(stat("log_n ~ treated_post | county_fips + year", sub))
    L+=[f"| {nm} | {a} | {b} |"]

# C. RATING
r=pd.read_csv(D/"sdc_deal_rating.csv"); r["MASTER_DEAL_NO"]=pd.to_numeric(r["MASTER_DEAL_NO"],errors="coerce").astype("Int64")
dd=d.copy(); dd["MASTER_DEAL_NO"]=pd.to_numeric(dd["MASTER_DEAL_NO"],errors="coerce").astype("Int64")
dr=dd.merge(r[["MASTER_DEAL_NO","any_rated_share","rated_avg_rating"]],on="MASTER_DEAL_NO",how="left")
L+=["", "## C. Rating — β on treated_post (extensive +=more rated; intensive −=better quality)","",
    "| Cut | extensive (any-rated share) | intensive (avg rating\\|rated) |","|---|---|---|"]
for nm,ks in CUTS:
    sub=post_for(dr,ks)
    a=fmt(stat("any_rated_share ~ treated_post + log_amt | county_fips + state_year", sub))
    b=fmt(stat("rated_avg_rating ~ treated_post + log_amt | county_fips + state_year", sub))
    L+=[f"| {nm} | {a} | {b} |"]

L+=["", "## vs OLD (contaminated) results",
    "- OLD: spread −23bps (artifact→+4.9 ns); issuance NULL; rating intensive NULL, extensive −7pp.",
    "- KEY: does clean_dc differ from crypto? Real infrastructure (clean) is where any pricing/issuance/"
    "credit effect should concentrate; crypto is transient/leased.", ""]
(D/"bond_block_cleaned.md").write_text("\n".join(L))
print("\n".join(L)); print("\nWrote bond_block_cleaned.md")
