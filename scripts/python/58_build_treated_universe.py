"""
58_build_treated_universe.py

Build the full ~125-county TREATED UNIVERSE with labels (keep everything, drop nothing —
Frank 2026-06-10). Each county carries flags so any analysis spec can slice instead of the
dataset hard-dropping counties:
  - is_crypto / dc_class   : S&P 451 PROVIDERTYPE 'Cryptocurrency Mining/Hosting' over ALL the
                             county's DCs (clean_dc / crypto / mixed / none). Crypto KEPT + labeled
                             (DCs get repurposed: Dickens 'Helios' -> CoreWeave/NVIDIA AI).
  - first_op_year / treated_by_2022 : earliest YEARFACILITYBECAMEOPERATIONAL; treated_by_2022 =
                             >=1 DC operational by 2022 (the 2-period-DiD-eligible flag).
  - oil_confound           : documented Permian-oil counties (tax base ~ oil price, not DC).
  - pt_2017 / pt_2022 (+ src): Census 2022 values, with ONLY PROVEN-WRONG values substituted by
                             today's state-source recoveries ("Census correct unless proven otherwise").

Proven-wrong substitutions (state-source, from 2026-06-10 agents):
  40101 Muskogee OK  2022: Census $54.4M = all-districts -> $11.40M county-only (OK Tax Commission)
  18153 Sullivan IN  2017: Census $22.97M = all-districts -> $6.83M county-unit (IN DLGF certified)
  48045 Briscoe TX, 48075 Childress TX, 48275 Knox TX, 48461 Upton TX : Census-imputed -> TX Comptroller
  (48003 Andrews TX: Census matches Comptroller within 2% -> KEEP Census.)

Output: data/derived/treated_universe_labeled.csv  (one row per treated county, all labels)
"""
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[2]; D = ROOT / "data" / "derived"; R = ROOT / "data/datacenter"
def fz(s): return s.astype(str).str.zfill(5)

# 1. base treated set (dc_share_mid >= 1)
tax = pd.read_csv(D/"dc_tax_share_distribution.csv", dtype={"county_fips":str}); tax["county_fips"]=fz(tax["county_fips"])
T = tax[tax["dc_share_mid"]>=1][["county_fips","name","state","mw_latest","dc_share_mid"]].copy()

# 2. crypto + operational-timing labels over ALL the county's DCs
pv = pd.read_sas(R/"dcprovider_latest.sas7bdat", encoding="latin-1")[["PROPERTYUNIQUEID","PROVIDERTYPE"]]
pv["pid"]=pd.to_numeric(pv["PROPERTYUNIQUEID"],errors="coerce"); pv["PROVIDERTYPE"]=pv["PROVIDERTYPE"].astype(str)
pv["is_crypto"]=pv["PROVIDERTYPE"].str.contains("Cryptocurrency",na=False)
pcry = pv.groupby("pid")["is_crypto"].max().rename("is_crypto")
dc = pd.read_csv(D/"dc_property_county_fips.csv"); dc["county_fips"]=fz(dc["county_fips"].astype(str))
dc["oy"]=pd.to_numeric(dc["YEARFACILITYBECAMEOPERATIONAL"],errors="coerce")
dc["pid"]=pd.to_numeric(dc["PROPERTYUNIQUEID"],errors="coerce")
dc=dc.merge(pcry,on="pid",how="left"); dc["is_crypto"]=dc["is_crypto"].fillna(False)
lab = dc.groupby("county_fips").agg(n_dc=("pid","size"), n_crypto=("is_crypto","sum"),
        first_op_year=("oy","min"), n_oper_by_2022=("oy",lambda s:int((s<=2022).sum()))).reset_index()
lab["dc_class"]=np.where(lab.n_crypto==0,"clean_dc",np.where(lab.n_crypto==lab.n_dc,"crypto","mixed"))
T = T.merge(lab, on="county_fips", how="left")
T["treated_by_2022"] = (T["n_oper_by_2022"].fillna(0) >= 1)

# 3. oil-confound documented set
OIL = {"48371","48475","48103","48173","48389","48135"}  # Pecos,Ward,Crane,Glasscock,Reeves,Ector
T["oil_confound"] = T["county_fips"].isin(OIL)

# 4. PT values: Census, then proven-wrong substitutions
g = pd.read_csv(D/"census_2017_2022_growth.csv", dtype={"county_fips":str}); g["county_fips"]=fz(g["county_fips"])
T = T.merge(g[["county_fips","rev_property_tax_17","rev_property_tax_22"]], on="county_fips", how="left")
T = T.rename(columns={"rev_property_tax_17":"pt_2017","rev_property_tax_22":"pt_2022"})
T["pt_2017_src"]="census"; T["pt_2022_src"]="census"
SUBS = {  # fips: (pt_2017, pt_2022, src) ; None = keep Census for that year
  "40101": (None, 11.404, "OK_TaxCommission_county_only"),
  "18153": (6.834, None, "IN_DLGF_certified_levy"),
  "48045": (1.109, 2.698, "TX_Comptroller"),
  "48075": (2.850, 3.087, "TX_Comptroller"),
  "48275": (1.697, 2.083, "TX_Comptroller"),
  "48461": (13.545, 28.281, "TX_Comptroller"),
}
for f,(p17,p22,src) in SUBS.items():
    m = T["county_fips"]==f
    if p17 is not None: T.loc[m,"pt_2017"]=p17; T.loc[m,"pt_2017_src"]=src
    if p22 is not None: T.loc[m,"pt_2022"]=p22; T.loc[m,"pt_2022_src"]=src
T["pt_growth_pct"] = np.where(T["pt_2017"]>0, 100*(T["pt_2022"]/T["pt_2017"]-1), np.nan)

T = T.sort_values("dc_share_mid", ascending=False)
T.to_csv(D/"treated_universe_labeled.csv", index=False)

# ---- verification report ----
print(f"TREATED UNIVERSE: {len(T)} counties (target ~125)\n")
print("dc_class:", T["dc_class"].value_counts(dropna=False).to_dict())
print("treated_by_2022:", T["treated_by_2022"].value_counts().to_dict())
print("oil_confound:", int(T["oil_confound"].sum()))
print("PT both years present:", int((T["pt_2017"]>0).mul(T["pt_2022"]>0).sum()),
      "| missing PT:", int(T["pt_2017"].isna().sum() + (T["pt_2017"]==0).sum()))
print("substitutions applied:", int((T["pt_2017_src"]!="census").sum() + (T["pt_2022_src"]!="census").sum()))
print("\n-- analysis-ready cuts --")
print("  full universe:", len(T))
print("  treated_by_2022 (2-period eligible):", int(T["treated_by_2022"].sum()))
print("  by_2022 & clean_dc:", int((T["treated_by_2022"]&(T["dc_class"]=="clean_dc")).sum()))
print("  by_2022 & crypto:", int((T["treated_by_2022"]&(T["dc_class"]=="crypto")).sum()))
print("\n-- counties with NO DC operational by 2022 (kept, flagged; event-study uses their op-year) --")
print(T[~T["treated_by_2022"]][["county_fips","name","state","dc_class","first_op_year"]].to_string(index=False))
