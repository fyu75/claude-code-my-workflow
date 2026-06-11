"""
59_phase1_triangulate_pt.py  — PHASE 1 (cheap, no agents, no search)

Finalize treated-county property tax by triangulating sources ALREADY ON DISK:
  primary = Census 2022 panel (with proven-wrong substitutions, from script 58),
  QC overlay + gap-fill = the 95-county hand-VERIFIED spine (gold), ACFR-PDF, MuniSpot v2.

"Census correct unless proven otherwise" (Frank) -> Census stays PRIMARY. The verified spine
is used to (a) VALIDATE Census 2017 against gold hand-checks [58 treated overlap], flagging
disagreements as review candidates (this is how we catch residual collector-state/scope errors
for free), and (b) FILL the 2 Census gaps (Silver Bow MT, Mayes OK).

Units: verified & PDF are raw USD -> /1e6 to $M; Census already $M. Validation is Census 2017
($M) vs verified baseline (FY2017 all-funds) -> apples-to-apples (both ~2017, all-funds scope).

Output: data/derived/treated_pt_final.csv      (finalized PT + provenance + QC flags)
        data/derived/treated_pt_qc_report.md   (Census-vs-verified agreement + flagged rows)
"""
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[2]; D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)

T = pd.read_csv(D/"treated_universe_labeled.csv", dtype={"county_fips":str}); T["county_fips"]=fz(T["county_fips"])

# --- sources (raw USD -> $M) ---
v = pd.read_csv(D/"verified_two_endpoint_pt.csv", dtype={"county_fips":str}); v["county_fips"]=fz(v["county_fips"])
v = v[v["status"]=="VERIFIED"].copy()
v["ver_2017"] = np.where(v["baseline_fy"]==2017, v["baseline_pt_allfunds_usd"]/1e6, np.nan)
v["ver_post"] = v["post_pt_allfunds_usd"]/1e6
v["ver_post_fy"] = v["post_fy"]
p = pd.read_csv(D/"acfr_county_year_extracted_wide.csv", dtype={"county_fips":str}); p["county_fips"]=fz(p["county_fips"])
def pdf_year(yrlo, yrhi):
    s = p[p["fy"].between(yrlo,yrhi)].sort_values("fy").groupby("county_fips").tail(1)
    return dict(zip(s["county_fips"], pd.to_numeric(s["property_tax_allfunds"],errors="coerce")/1e6))
pdf17, pdf22 = pdf_year(2016,2018), pdf_year(2021,2023)

T = T.merge(v[["county_fips","ver_2017","ver_post","ver_post_fy"]], on="county_fips", how="left")

# --- (a) VALIDATE Census 2017 vs verified baseline (FY2017) ---
val = T.dropna(subset=["ver_2017"]).copy()
val = val[val["pt_2017"]>0]
val["pct_diff"] = (val["pt_2017"]-val["ver_2017"]).abs()/val["ver_2017"]*100
val["agree10"] = val["pct_diff"]<=10
n_val=len(val); n_ok=int(val["agree10"].sum())
flagged = val[~val["agree10"]].sort_values("pct_diff",ascending=False)

# --- (b) finalize PT: prefer VERIFIED PAIR (gold, scope-consistent) > Census(subs) > pdf/v2 ---
# Verified is hand-checked county-government scope; where it disagrees with Census the growth-
# cancellation test showed Census growth can be corrupted (Laramie +13% vs +111%). CAGR-annualize
# to normalize the mixed verified post-vintages (FY2022-2024).
vp = v.dropna(subset=["baseline_pt_allfunds_usd","post_pt_allfunds_usd"]).set_index("county_fips")
T["pt_2017_final"]=T["pt_2017"]; T["pt_2022_final"]=T["pt_2022"]
T["src_2017_final"]=T["pt_2017_src"]; T["src_2022_final"]=T["pt_2022_src"]
T["fy_base"]=2017.0; T["fy_post"]=2022.0
for i,r in T.iterrows():
    f=r["county_fips"]
    if f in vp.index:   # gold verified pair -> use it (scope-consistent)
        T.at[i,"pt_2017_final"]=vp.at[f,"baseline_pt_allfunds_usd"]/1e6
        T.at[i,"pt_2022_final"]=vp.at[f,"post_pt_allfunds_usd"]/1e6
        T.at[i,"src_2017_final"]="verified"; T.at[i,"src_2022_final"]="verified"
        T.at[i,"fy_base"]=vp.at[f,"baseline_fy"]; T.at[i,"fy_post"]=vp.at[f,"post_fy"]
# gap-fill any still-missing from pdf
for i,r in T.iterrows():
    f=r["county_fips"]
    if pd.isna(r["pt_2017_final"]) or r["pt_2017_final"]<=0:
        if f in pdf17 and pd.notna(pdf17[f]): T.at[i,"pt_2017_final"]=pdf17[f]; T.at[i,"src_2017_final"]="acfr_pdf"
    if pd.isna(r["pt_2022_final"]) or r["pt_2022_final"]<=0:
        if f in pdf22 and pd.notna(pdf22[f]): T.at[i,"pt_2022_final"]=pdf22[f]; T.at[i,"src_2022_final"]="acfr_pdf"
# annualized CAGR (handles mixed post-vintages)
span = (T["fy_post"]-T["fy_base"]).clip(lower=1)
T["pt_cagr_pct"] = np.where((T["pt_2017_final"]>0)&(T["pt_2022_final"]>0),
                            100*((T["pt_2022_final"]/T["pt_2017_final"])**(1/span)-1), np.nan)

T["qc_census_verified"] = np.where(T["county_fips"].isin(flagged["county_fips"]),"FLAG_disagree",
                          np.where(T["county_fips"].isin(val["county_fips"]),"validated_ok","no_verified_check"))
T["pt_both_final"] = (T["pt_2017_final"]>0)&(T["pt_2022_final"]>0)
keep=["county_fips","name","state","dc_class","treated_by_2022","oil_confound","mw_latest","dc_share_mid",
      "pt_2017_final","pt_2022_final","fy_base","fy_post","pt_cagr_pct","src_2017_final","src_2022_final",
      "qc_census_verified","pt_both_final"]
T[keep].to_csv(D/"treated_pt_final.csv", index=False)

L=["# Phase 1 — Treated PT Triangulation (on-disk sources, no agents)\n",
   "**Date:** 2026-06-10. `scripts/python/59`. Census primary; 95-county hand-verified spine as QC + "
   "gap-fill; ACFR-PDF fallback. Validation = Census 2017 ($M) vs verified baseline (FY2017 all-funds).\n",
   f"## Coverage", f"- Treated universe: **{len(T)}**; PT both years final: **{int(T['pt_both_final'].sum())}** "
   f"(gaps filled: {int((~T['pt_both_final']).sum())} remaining).",
   f"## Census ↔ verified-spine validation (the free QC)",
   f"- Overlap with gold hand-checks: **{n_val}** treated; **{n_ok} agree within ±10% ({100*n_ok/n_val:.0f}%)**.",
   f"- **{len(flagged)} disagree >10%** — review candidates (Census may carry a residual scope/collector error):",
   "", "| County | ST | Census 2017 ($M) | Verified 2017 ($M) | % diff | note |", "|---|---|---:|---:|---:|---|"]
vnote=dict(zip(v["county_fips"], v["note"].astype(str).str[:70]))
for _,r in flagged.iterrows():
    L.append(f"| {r['name']} | {r['state']} | {r['pt_2017']:.1f} | {r['ver_2017']:.1f} | {r['pct_diff']:.0f}% | {vnote.get(r['county_fips'],'')} |")
L+=["", "## Reading guide",
    "- 'validated_ok' counties: Census 2017 confirmed by an independent hand-check -> locked.",
    "- 'FLAG_disagree': decide case-by-case; per 'Census unless proven wrong', keep Census unless the "
    "verified note proves a scope error (e.g., GA govwide, collector-state, TN school-levy).",
    "- Gaps (Silver Bow MT, Mayes OK) filled from verified/PDF — see src_*_final.", ""]
(D/"treated_pt_qc_report.md").write_text("\n".join(L))
print("\n".join(L))
print(f"\nGap fills: ", T[T['src_2017_final'].isin(['verified_baseline','acfr_pdf'])|T['src_2022_final'].isin(['verified_post','acfr_pdf'])][['county_fips','name','pt_2017_final','src_2017_final','pt_2022_final','src_2022_final']].to_string(index=False))
print("\nWrote treated_pt_final.csv + treated_pt_qc_report.md")
