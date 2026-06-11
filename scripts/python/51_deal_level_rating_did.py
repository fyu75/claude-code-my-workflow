"""
51_deal_level_rating_did.py

Bond RATING as an OUTCOME, on the robust deal-level spec (script 50): county FE +
state x year FE, SEs clustered on county. This is the credit-quality question asked
directly — and it puts rating on the SAME identification that survived for spread,
rather than the fragile CS-vs-never-treated county-year design of script 21.

Rating is the right OUTCOME here (it must NOT be a control in the spread regression —
it sits on the DC -> credit -> spread path). Two margins:
  INTENSIVE : rated_avg_rating (par-weighted, rated tranches only; lower = better).
              "Among deals that get rated, does credit quality improve post-DC?"
  EXTENSIVE : any_rated_share (par share of the deal carrying any agency rating; all deals).
              "Are DC counties more likely to obtain a public rating post-DC?"
  + share_ig (>= BBB-/Baa3), share_aaa.

Sign: NEGATIVE coef on rating level = rating IMPROVES (toward Aaa=1). POSITIVE coef on
any_rated_share / share_ig / share_aaa = more / better-rated.

Data: ratings.sas7bdat + maturity.sas7bdat (tranche par) -> deal-level aggregates, merged
onto the deal universe in sdc_deal_spread.csv (MASTER_DEAL_NO -> county_fips, state, year, AMT).
Treatment timing from county_year_panel_v4. Universe = >=1% DC treated + never-DC-host.

Caveat: SDC rating coverage is sparse (~20% of tranches), and rated deals skew large; the
intensive margin is a selected subsample. The extensive margin (all deals) is better powered.

Output: data/derived/deal_level_rating_did_results.md
        data/derived/sdc_deal_rating.csv  (deal-level rating aggregates, reusable)
"""
from pathlib import Path
import numpy as np, pandas as pd
import pyfixest as pf

ROOT = Path(__file__).resolve().parents[2]; D = ROOT / "data" / "derived"
SDC  = ROOT / "data/sdc_muni/sdc_municipals"
def fz(s): return s.astype(str).str.zfill(5)

RATING_MAP = {
    'Aaa':1,'Aa1':2,'Aa2':3,'Aa3':4,'A1':5,'A2':6,'A3':7,'Baa1':8,'Baa2':9,'Baa3':10,
    'Ba1':11,'Ba2':12,'Ba3':13,'B1':14,'B2':15,'B3':16,'Caa1':17,'Caa2':18,'Caa3':19,'Ca':20,'C':21,
    'AAA':1,'AA+':2,'AA':3,'AA-':4,'A+':5,'A':6,'A-':7,'BBB+':8,'BBB':9,'BBB-':10,
    'BB+':11,'BB':12,'BB-':13,'B+':14,'B':15,'B-':16,'CCC+':17,'CCC':18,'CCC-':19,'CC':20,'D':22,
    'Aa':3,'Ba':12,'Baa':9,
}
def map_rate(x):
    if pd.isna(x): return np.nan
    s = str(x).strip()
    return np.nan if s in ('NR','WR','',' ') else RATING_MAP.get(s, np.nan)

# ---- 1. deal-level rating aggregates (build once, cache) ----
cache = D/"sdc_deal_rating.csv"
if cache.exists():
    deal = pd.read_csv(cache)
else:
    print("Building deal-level rating aggregates from SAS...")
    r = pd.read_sas(SDC/"ratings.sas7bdat", encoding='latin-1')
    for src, col in [('mn','MOODY_RATING'),('sn','SP_RATING'),('fn','FITCHRATING1')]:
        r[src] = r[col].map(map_rate)
    r['any_rated'] = r[['mn','sn','fn']].notna().any(axis=1).astype(int)
    r['avg_rating']= r[['mn','sn','fn']].mean(axis=1)
    r['best']      = r[['mn','sn','fn']].min(axis=1)
    t = pd.read_sas(SDC/"maturity.sas7bdat", encoding='latin-1')[['MASTER_DEAL_NO','MUNITRANCHE','AMTMATY']]
    t['amt'] = pd.to_numeric(t['AMTMATY'], errors='coerce')
    tr = t.merge(r[['MASTER_DEAL_NO','MUNITRANCHE','any_rated','avg_rating','best']],
                 on=['MASTER_DEAL_NO','MUNITRANCHE'], how='left')
    tr = tr[tr['amt']>0].copy()
    tr['is_aaa'] = (tr['best']==1).astype(float)
    tr['is_ig']  = ((tr['best']<=10)&tr['best'].notna()).astype(float)
    def pw(g, col, mask=None):
        m = g[col].notna() if mask is None else mask(g)
        w = g.loc[m,'amt']
        return (g.loc[m,col]*w).sum()/w.sum() if w.sum()>0 else np.nan
    g = tr.groupby('MASTER_DEAL_NO')
    deal = g.apply(lambda x: pd.Series({
        'any_rated_share':  (x.loc[x['any_rated']==1,'amt'].sum())/x['amt'].sum(),
        'rated_avg_rating': pw(x,'avg_rating'),
        'share_aaa':        (x.loc[x['is_aaa']==1,'amt'].sum())/x['amt'].sum(),
        'share_ig':         (x.loc[x['is_ig']==1,'amt'].sum())/x['amt'].sum(),
    })).reset_index()
    deal.to_csv(cache, index=False)
    print(f"  cached {len(deal):,} deals -> {cache.name}")

# ---- 2. deal universe + geography + timing (from sdc_deal_spread) ----
u = pd.read_csv(D/"sdc_deal_spread.csv")[["MASTER_DEAL_NO","county_fips","STATECODE","year","AMT"]]
u["county_fips"] = fz(u["county_fips"].astype(int).astype(str))
u["MASTER_DEAL_NO"]    = pd.to_numeric(u["MASTER_DEAL_NO"], errors="coerce").astype("Int64")
deal["MASTER_DEAL_NO"] = pd.to_numeric(deal["MASTER_DEAL_NO"], errors="coerce").astype("Int64")
d = u.merge(deal, on="MASTER_DEAL_NO", how="left")

pan = pd.read_csv(D/"county_year_panel_v4.csv", dtype={"county_fips":str}); pan["county_fips"]=fz(pan["county_fips"])
g_map = pan.dropna(subset=["first_dc_year"]).groupby("county_fips")["first_dc_year"].min().astype(int)
never_host = pan.groupby("county_fips")["n_dc_cumulative"].max().pipe(lambda s:set(s[s==0].index))
tax = pd.read_csv(D/"dc_tax_share_distribution.csv", dtype={"county_fips":str}); tax["county_fips"]=fz(tax["county_fips"])
treated_set = set(tax[tax["dc_share_mid"]>=1.0]["county_fips"])

d = d[d["county_fips"].isin(treated_set | never_host) & (d["AMT"]>0)].copy()
d["treated_ever"] = d["county_fips"].isin(treated_set).astype(int)
d["g"] = d["county_fips"].map(g_map)
d["treated_post"] = ((d["treated_ever"]==1)&(d["year"]>=d["g"])).astype(int)
d["state_year"] = d["STATECODE"].astype(str)+"_"+d["year"].astype(str)
d["log_amt"] = np.log(d["AMT"])

# ---- 3. run ----
def run(formula, data, label):
    data = data.dropna(subset=[formula.split("~")[0].strip()])
    try:
        m = pf.feols(formula, data=data, vcov={"CRV1":"county_fips"})
        b=m.coef()["treated_post"]; se=m.se()["treated_post"]; p=m.pvalue()["treated_post"]; n=int(m._N)
        sig="***" if p<0.01 else "**" if p<0.05 else "*" if p<0.10 else ""
        return f"| {label} | **{b:+.4f}{sig}** | {se:.4f} | {p:.4f} | {n:,} |"
    except Exception as e:
        return f"| {label} | — | — | {str(e)[:30]} | — |"

n_post = int(d["treated_post"].sum())
nr_post = int(d.loc[(d["treated_post"]==1)&d["rated_avg_rating"].notna()].shape[0])
L = ["# Deal-Level Rating DiD (robust spec)\n",
     "**Date:** 2026-06-10. Bond RATING as outcome on the script-50 spec (county FE + state×year "
     "FE, cluster county) — the design that survived for spread. `scripts/python/51`.\n",
     "**Sign:** rating level lower = better (Aaa=1); NEGATIVE coef on a rating-level outcome = "
     "credit IMPROVES. POSITIVE coef on any_rated_share / share_ig / share_aaa = more/better-rated.\n",
     f"## Sample",
     f"- Deals: **{len(d):,}** | post (treated×after-DC) {n_post:,}; of those rated {nr_post:,}",
     f"- Treated (≥1% DC) {d.loc[d['treated_ever']==1,'county_fips'].nunique()}, "
     f"never-host {d.loc[d['treated_ever']==0,'county_fips'].nunique()}",
     f"- Overall any-rated par share (mean): {d['any_rated_share'].mean():.3f}", "",
     "## Results — coefficient on treated_post", "",
     "| Outcome (spec: county + state×year FE) | β | SE | p | N |", "|---|---:|---:|---:|---:|"]

L += [run("any_rated_share ~ treated_post | county_fips + state_year",            d, "Extensive: any-rated par share (all deals)")]
L += [run("any_rated_share ~ treated_post + log_amt | county_fips + state_year",  d, "  + log(amount) control")]
L += [run("rated_avg_rating ~ treated_post | county_fips + state_year",           d, "Intensive: avg rating | rated (lower=better)")]
L += [run("share_ig ~ treated_post | county_fips + state_year",                   d, "Share investment-grade (≥BBB-)")]
L += [run("share_aaa ~ treated_post | county_fips + state_year",                  d, "Share AAA/Aaa")]
L += [run("rated_avg_rating ~ treated_post | county_fips + state_year",  d[d["year"]>=2015], "Intensive rating, 2015+ issues")]
L += ["", "*Stars: \\*\\*\\* p<0.01, \\*\\* p<0.05, \\* p<0.10.*", ""]

L += ["## Reading guide",
      "- Compare to county-year CS (script 21): there, avg-rating ATT was +0.065 (ratings WORSEN, ns) "
      "on the same fragile design that gave the −23bps spread. This deal-level spec is the robust check.",
      "- Extensive margin uses ALL deals (well-powered); intensive uses only rated deals (~20%, "
      "selected toward larger issues — interpret with care).",
      "- A credit-quality story needs rating to IMPROVE (negative level coef) and/or the extensive "
      "/ IG / AAA shares to RISE. A null here is consistent with the spread null: no pricing-relevant "
      "credit improvement detectable.",
      "- Same TWFE staggered-timing caveat as script 50.", ""]

(D/"deal_level_rating_did_results.md").write_text("\n".join(L))
print("\n".join(L))
print("Wrote data/derived/deal_level_rating_did_results.md")
