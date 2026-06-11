"""
60_phase2_final_matched_did.py  — PHASE 2

Matched property-tax DiD on the FINALIZED treated foundation (treated_pt_final.csv, Phase 1):
gold-verified-where-available + Census + state-source, county-government scope, CAGR-annualized
(handles mixed post-vintages). Controls = full clean Census never-DC-host universe. Crypto KEPT
and reported as a labeled cut (clean_dc / crypto / mixed), per Frank.

Outcome = annualized property-tax CAGR (%/yr). Matched-pair effect = treated CAGR - mean(matched
control CAGR). 1:3 caliper match (0.5 log-pt) on log baseline PT, same-state -> same-Census-division
fallback. Estimators mirror scripts 46/56: matched-pair (t/Wilcoxon/sign/bootstrap).

Cuts reported: ALL operating-by-2022 | clean_dc | crypto | mixed | + oil-confound-dropped robustness.

Output: data/derived/phase2_final_matched_did.md
"""
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]; D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)
rng = np.random.default_rng(20260516)

DIV = {}  # state FIPS -> census division
for d,states in {1:["09","23","25","33","44","50"],2:["34","36","42"],3:["17","18","26","39","55"],
  4:["19","20","27","29","31","38","46"],5:["10","11","12","13","24","37","45","51","54"],
  6:["01","21","28","47"],7:["05","22","40","48"],8:["04","08","16","30","32","35","49","56"],
  9:["02","06","15","41","53"]}.items():
    for s in states: DIV[s]=d

# --- treated (finalized) ---
T = pd.read_csv(D/"treated_pt_final.csv", dtype={"county_fips":str}); T["county_fips"]=fz(T["county_fips"])
T = T[(T["treated_by_2022"]==True) & (T["pt_both_final"]==True) & T["pt_cagr_pct"].notna()].copy()
T["st"]=T["county_fips"].str[:2]; T["div"]=T["st"].map(DIV); T["logb"]=np.log(T["pt_2017_final"])

# --- controls: never-DC-host, clean Census both years, annualized CAGR ---
g = pd.read_csv(D/"census_2017_2022_growth.csv", dtype={"county_fips":str}); g["county_fips"]=fz(g["county_fips"])
pan = pd.read_csv(D/"county_year_panel_v4.csv", dtype={"county_fips":str}); pan["county_fips"]=fz(pan["county_fips"])
never = pan.groupby("county_fips")["n_dc_cumulative"].max().pipe(lambda s:set(s[s==0].index))
DROP_CTRL={"27053","18129","29069"}
C = g[g["county_fips"].isin(never-DROP_CTRL) & (g["rev_property_tax_17"]>0) & (g["rev_property_tax_22"]>0)
      & g["rev_property_tax_cagr_pct"].notna()].copy()
C["st"]=C["county_fips"].str[:2]; C["div"]=C["st"].map(DIV); C["logb"]=np.log(C["rev_property_tax_17"])
C=C.rename(columns={"rev_property_tax_cagr_pct":"cagr"})

def build_pairs(treated, k=3, caliper=0.5):
    rows=[]; reuse={}
    for _,t in treated.iterrows():
        cand=C[(C["st"]==t["st"]) & ((C["logb"]-t["logb"]).abs()<=caliper)].copy(); tier="state"
        if len(cand)<k:
            div=C[(C["div"]==t["div"]) & (C["st"]!=t["st"]) & ((C["logb"]-t["logb"]).abs()<=caliper)]
            cand=pd.concat([cand,div]); tier="division" if len(cand)>len(C[(C["st"]==t["st"])&((C["logb"]-t["logb"]).abs()<=caliper)]) else "state"
        cand=cand.assign(d=(cand["logb"]-t["logb"]).abs()).sort_values("d").head(k)
        for _,c in cand.iterrows():
            rows.append({"treated_fips":t["county_fips"],"t_cagr":t["pt_cagr_pct"],"dc_class":t["dc_class"],
                         "oil":t["oil_confound"],"control_fips":c["county_fips"],"c_cagr":c["cagr"],"tier":tier})
    return pd.DataFrame(rows)

P = build_pairs(T)

def effect(pairs):
    eff=[]
    for tf,grp in pairs.groupby("treated_fips"):
        eff.append(grp["t_cagr"].iloc[0]-grp["c_cagr"].mean())
    eff=np.array(eff)
    if len(eff)<5: return None
    boot=[rng.choice(eff,len(eff),replace=True).mean() for _ in range(10000)]
    nneg=int((eff<0).sum())
    return dict(n=len(eff),mean=eff.mean(),med=np.median(eff),tp=stats.ttest_1samp(eff,0).pvalue,
               wp=stats.wilcoxon(eff).pvalue,npos=len(eff)-nneg,
               sp=stats.binomtest(len(eff)-nneg,len(eff),.5).pvalue,ci=np.percentile(boot,[2.5,97.5]))

def row(label,P):
    r=effect(P)
    if r is None: return f"| {label} | n<5 | — | — | — | — |"
    sig="***" if r['tp']<.01 else "**" if r['tp']<.05 else "*" if r['tp']<.10 else ""
    return (f"| {label} | **{r['mean']:+.2f}{sig}** | {r['med']:+.2f} | {r['n']} | "
            f"t={r['tp']:.3f}/W={r['wp']:.3f} | [{r['ci'][0]:+.2f},{r['ci'][1]:+.2f}] |")

L=["# Phase 2 — Final Matched PT DiD (CAGR, finalized treated foundation)\n",
   "**Date:** 2026-06-10. `scripts/python/60`. Outcome = annualized property-tax CAGR (%/yr). Treated = "
   "finalized scope-consistent PT (Phase 1, gold-verified where available); controls = full clean Census "
   "never-DC-host universe; 1:3 caliper match. Matched-pair effect vs matched controls.\n",
   f"Treated operating-by-2022 w/ final PT: **{len(T)}** | control pool: **{len(C):,}** | pairs: {len(P):,}\n",
   "| Cut | Mean effect (%/yr) | Median | N treated | t / Wilcoxon p | Boot 95% CI |","|---|---:|---:|---:|---:|---:|"]
L+=[row("ALL (operating by 2022)", P)]
L+=[row("Clean hyperscale/colo", P[P["dc_class"]=="clean_dc"])]
L+=[row("Crypto-mining", P[P["dc_class"]=="crypto"])]
L+=[row("Mixed", P[P["dc_class"]=="mixed"])]
L+=[row("Clean + Mixed (non-pure-crypto)", P[P["dc_class"]!="crypto"])]
L+=[row("ALL, oil-confound dropped", P[~P["oil"].astype(bool)])]
L+=[row("Clean, oil-confound dropped", P[(P["dc_class"]=="clean_dc")&(~P["oil"].astype(bool))])]
L+=["", "*Stars: \\*\\*\\* p<.01, \\*\\* p<.05, \\* p<.10. Effect = treated CAGR − mean matched-control CAGR.*",
    "", "## Reading guide",
    "- Hypothesis (memo §6): clean hyperscale/colo DCs raise PT growth; crypto miners barely beat benchmark.",
    "- vs raw medians (clean +5.6 / crypto +3.8 / control bench ~3.4 %/yr): the matched effect nets out region/size.",
    "- N is small per cut (clean ~39, crypto ~35) -> the 2-period design is power-limited; the event-study "
    "(Phase 4) is the power fix. Report point estimates + CIs, not just stars.", ""]
(D/"phase2_final_matched_did.md").write_text("\n".join(L))
print("\n".join(L))
print("\nWrote phase2_final_matched_did.md")
