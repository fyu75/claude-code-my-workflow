"""
63_bond_county_year_panel.py

County-YEAR bond panel with COUNTY + YEAR fixed effects (staggered TWFE): observe the within-county
change in bond features when a DC arrives. Treatment = treated_post (county is a DC host AND
year >= its first_op_year). Controls = never-DC-host. Crypto labeled (clean/crypto cut).

Two panels:
  BALANCED (all county-years 2008-2025, 0 for non-issuing years) -> issuance / probability-of-issuing.
  ISSUING-ONLY (county-years with >=1 deal) -> spread, rating (those need a deal to be observed).

Outcomes (~ treated_post | county + year, cluster county):
  par_wtd_spread_bps      spread over Treasury (− = cheaper)        [issuing]
  log1p(par_total_M)      total issuance volume                      [balanced]
  n_deals                 number of deals                            [balanced]
  is_issue                1 if county came to market that year       [balanced; extensive margin]
  any_rated_share         par share carrying a rating                [issuing]
  rated_avg_rating        avg rating | rated (lower=better)          [issuing]

Plus a binned EVENT STUDY (county+year FE) for spread and log(par): leads = pre-trend test, lags = path.

Output: data/derived/bond_county_year_panel.md
"""
from pathlib import Path
import numpy as np, pandas as pd
import pyfixest as pf

ROOT = Path(__file__).resolve().parents[2]; D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)
Y0,Y1 = 2008,2025

# treatment
T = pd.read_csv(D/"treated_universe_labeled.csv", dtype={"county_fips":str}); T["county_fips"]=fz(T["county_fips"])
opyear=dict(zip(T["county_fips"],T["first_op_year"])); cls=dict(zip(T["county_fips"],T["dc_class"]))
treated_all=set(T["county_fips"])
pan=pd.read_csv(D/"county_year_panel_v4.csv", dtype={"county_fips":str}); pan["county_fips"]=fz(pan["county_fips"])
never=pan.groupby("county_fips")["n_dc_cumulative"].max().pipe(lambda s:set(s[s==0].index))-treated_all

# deal-level -> county-year aggregates
d=pd.read_csv(D/"sdc_deal_spread.csv"); d["county_fips"]=fz(d["county_fips"].astype(int).astype(str))
d=d[d["county_fips"].isin(treated_all|never)&(d["AMT"]>0)&d["year"].between(Y0,Y1)].copy()
r=pd.read_csv(D/"sdc_deal_rating.csv"); r["MASTER_DEAL_NO"]=pd.to_numeric(r["MASTER_DEAL_NO"],errors="coerce").astype("Int64")
d["MASTER_DEAL_NO"]=pd.to_numeric(d["MASTER_DEAL_NO"],errors="coerce").astype("Int64")
d=d.merge(r[["MASTER_DEAL_NO","any_rated_share","rated_avg_rating"]],on="MASTER_DEAL_NO",how="left")
def pw(g,c):
    w=g.loc[g[c].notna(),"AMT"]; return (g.loc[g[c].notna(),c]*w).sum()/w.sum() if w.sum()>0 else np.nan
cyr=d.groupby(["county_fips","year"]).apply(lambda g: pd.Series({
    "par_total_M": g["AMT"].sum()/1e6, "n_deals": len(g),
    "par_wtd_spread_bps": pw(g,"spread_bps"), "any_rated_share": pw(g,"any_rated_share"),
    "rated_avg_rating": pw(g,"rated_avg_rating")})).reset_index()

# balanced panel (county x year), fill issuance 0
counties=sorted(set(d["county_fips"]))
bal=pd.MultiIndex.from_product([counties,range(Y0,Y1+1)],names=["county_fips","year"]).to_frame(index=False)
bal=bal.merge(cyr,on=["county_fips","year"],how="left")
bal["par_total_M"]=bal["par_total_M"].fillna(0); bal["n_deals"]=bal["n_deals"].fillna(0)
bal["is_issue"]=(bal["n_deals"]>0).astype(int); bal["log_par"]=np.log1p(bal["par_total_M"])
for df in (bal,cyr):
    df["treated_ever"]=df["county_fips"].isin(treated_all).astype(int)
    df["dc_class"]=df["county_fips"].map(cls); df["oy"]=df["county_fips"].map(opyear)

def post(df, keep):
    x=df[(df["treated_ever"]==0)|(df["dc_class"].isin(keep))].copy()
    x["treated_post"]=((x["treated_ever"]==1)&(x["year"]>=x["oy"])).astype(int); return x

def stat(f,data):
    data=data.dropna(subset=[f.split('~')[0].strip(),"treated_post"])
    try:
        m=pf.feols(f,data=data,vcov={"CRV1":"county_fips"})
        b=m.coef()["treated_post"];se=m.se()["treated_post"];p=m.pvalue()["treated_post"]
        s="***" if p<.01 else "**" if p<.05 else "*" if p<.10 else ""
        return f"**{b:+.3f}{s}** | {se:.3f} | {p:.3f} | {int(m._N):,}"
    except Exception as e: return f"— | — | {str(e)[:22]} | —"

CUTS=[("ALL",["clean_dc","crypto","mixed"]),("clean_dc",["clean_dc"]),("crypto",["crypto"])]
L=["# Bond County-Year Panel — County + Year FE (staggered TWFE)\n",
   "**Date:** 2026-06-10. `scripts/python/63`. Within-county change in bond features when a DC arrives. "
   "treated_post = DC host AND year≥first_op_year; county FE + year FE; SEs clustered on county. "
   f"Window {Y0}-{Y1}; controls = never-DC-host.\n",
   f"Counties: treated {len(treated_all&set(counties))}, control {len(never&set(counties)):,}.\n"]
specs=[("par_wtd_spread_bps","Spread (bps, −=cheaper)","issue"),
       ("log_par","log(1+par $M) issuance","bal"),("n_deals","n deals","bal"),
       ("is_issue","P(issue this year)","bal"),
       ("any_rated_share","Any-rated par share","issue"),("rated_avg_rating","Avg rating|rated (−=better)","issue")]
L+=["| Outcome | Cut | β treated_post | SE | p | N |","|---|---|---:|---:|---:|---:|"]
for outc,olab,pn in specs:
    for nm,ks in CUTS:
        base = bal if pn=="bal" else cyr
        L+=[f"| {olab} | {nm} | "+stat(f"{outc} ~ treated_post | county_fips + year", post(base,ks))+" |"]

# ---- event study (spread + log_par), binned -5..+5, ref -1 ----
def event(df, outc, keep, pn):
    x=post(df,keep); x["et"]=np.where(x["treated_ever"]==1, x["year"]-x["oy"], np.nan)
    for k in [-5,-4,-3,-2,0,1,2,3,4,5]:
        x[f"e{k:+d}".replace('+','p').replace('-','m')]=((x["treated_ever"]==1)&(np.clip(x["et"],-5,5)==k)).astype(int)
    ec=[c for c in x.columns if c.startswith("ep") or c.startswith("em")]
    f=f"{outc} ~ "+" + ".join(ec)+" | county_fips + year"
    m=pf.feols(f,data=x.dropna(subset=[outc]),vcov={"CRV1":"county_fips"})
    return m.coef(), m.pvalue()
L+=["", "## Event study — ALL treated (binned, ref −1; pre = parallel-trends test)"]
for outc,olab in [("par_wtd_spread_bps","Spread (bps)"),("log_par","log(1+par)")]:
    co,pv=event(cyr if outc=="par_wtd_spread_bps" else bal, outc, ["clean_dc","crypto","mixed"], None)
    cells=[]
    for k in [-5,-4,-3,-2,0,1,2,3,4,5]:
        c=f"e{k:+d}".replace('+','p').replace('-','m'); b=co.get(c,np.nan); p=pv.get(c,np.nan)
        st="*" if p<.10 else ""
        cells.append(f"{k:+d}:{b:+.2f}{st}")
    L+=[f"- **{olab}**: "+"  ".join(cells)+"  (ref −1=0)"]
L+=["", "## Reading", "- County FE => identification is each county's bonds AFTER its DC vs BEFORE (and vs never-DC in same years).",
    "- Spread − = cheaper borrowing; issuance/n_deals/P(issue) + = more borrowing; rating extensive + = more rated.",
    "- Event-study pre-period (−5..−2) ≈ 0 => parallel trends; lags = dynamics. Staggered TWFE caveat -> "
    "Sun-Abraham/CS is the robustness.", ""]
(D/"bond_county_year_panel.md").write_text("\n".join(L))
print("\n".join(L)); print("\nWrote bond_county_year_panel.md")
