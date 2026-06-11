"""
77_salience_verification.py

Main-thread verification of the script-76 salience result (the only significant
primary-market cell from the tier-1 heterogeneity round): mega-announcement counties
spread -24.9 (p=0.047), mega x post-2023 -29.1 (p=0.002).

Two checks before accepting:
1. PRIMARY-MARKET robustness: drop the 2 documented oil-confounded counties from the
   mega list (Williams ND 38105, Ward TX 48475) + leave-one-out over the remaining 10.
2. SECONDARY-MARKET confirmation (the same test that rejected the colo -46.5):
   identical mega cells in the MSRB bond-year panel, bond + year FE — if the
   primary-market effect is real repricing, the same outstanding bonds must show it.

Output: data/derived/salience_verification.md
"""
from pathlib import Path
import numpy as np, pandas as pd
import pyarrow.parquet as pq
import pyfixest as pf
import warnings; warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]; D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)
MEGA = {"53025", "48331", "13097", "41067", "13121", "37069", "38105", "41013",
        "48349", "48355", "45015", "48475"}                  # script-76 top decile
OIL = {"38105", "48475"}                                     # documented oil confounds
MX = MEGA - OIL

T = pd.read_csv(D / "treated_universe_labeled.csv", dtype={"county_fips": str}); T["county_fips"] = fz(T["county_fips"])
nm = dict(zip(T.county_fips, T.name))
anc = pd.read_csv(D / "announcement_anchor_county.csv", dtype={"county_fips": str}); anc["county_fips"] = fz(anc["county_fips"])
cty = pd.read_csv(D / "dc_announcement_years.csv", dtype={"county_fips": str}); cty["county_fips"] = fz(cty["county_fips"])
A = (T[["county_fips"]].merge(anc[["county_fips", "ann_firstmaj"]], on="county_fips", how="left")
       .merge(cty[["county_fips", "announce_year"]], on="county_fips", how="left"))
A["AY"] = A.ann_firstmaj.fillna(A.announce_year); amap = dict(zip(A.county_fips, A.AY))
never = set(pd.read_csv(D / "clean_never_dc_controls.csv", dtype=str)["county_fips"].pipe(fz))

# ---- primary market ----
d = pd.read_csv(D / "sdc_deal_spread.csv"); d["county_fips"] = fz(d["county_fips"].astype(int).astype(str))
d = d[(d.AMT > 0) & d.year.between(2008, 2025) & d.spread_bps.notna()].copy()
d["logamt"] = np.log(d.AMT); d["logmat"] = np.log(d.par_wtd_yrs2mat.clip(lower=0.25))
d = d.dropna(subset=["logmat"])

def prim(mset, era=None):
    s = d[d.county_fips.isin(mset | never)].copy()
    s["AY"] = s.county_fips.map(amap); s = s[~(s.county_fips.isin(mset) & s.AY.isna())]
    s["ann"] = ((s.county_fips.isin(mset)) & (s.year >= s.AY)).astype(int)
    if era == "post": s["ann"] = s["ann"] * (s.year >= 2023).astype(int)
    m = pf.feols("spread_bps ~ ann + logamt + logmat | county_fips + year", data=s, vcov={"CRV1": "county_fips"})
    return m.coef()["ann"], m.pvalue()["ann"]

L = ["# Salience-result verification (script 76's mega/era cells)\n",
     "**Date:** 2026-06-11. `scripts/python/77`. Primary-market spec = script 68; secondary = script 73.\n",
     "## 1. Primary market — oil-drop + leave-one-out", "| Variant | beta (bps) | p |", "|---|---:|---:|"]
b, p = prim(MEGA);      L.append(f"| mega 12 (script 76 cell) | {b:+.2f} | {p:.3f} |")
b, p = prim(MX);        L.append(f"| drop 2 oil counties (n=10) | {b:+.2f} | {p:.3f} |")
for f in sorted(MX):
    b, p = prim(MX - {f}); L.append(f"| LOO drop {nm.get(f, f)} | {b:+.2f} | {p:.3f} |")
b, p = prim(MX, era="post"); L.append(f"| mega-ex-oil x post-2023 | {b:+.2f} | {p:.3f} |")

# ---- secondary market (script-73 panel construction) ----
sl = pq.read_table(ROOT / "data" / "msrb" / "msrb_working_slice.parquet",
                   columns=["CUSIP", "CUSIP6", "TRADE_DATE", "YIELD", "PAR_TRADED",
                            "TRADE_TYPE_INDICATOR", "MATURITY_DATE", "WHEN_ISSUED_INDICATOR"]).to_pandas()
sl["YIELD"] = pd.to_numeric(sl.YIELD, errors="coerce"); sl["PAR_TRADED"] = pd.to_numeric(sl.PAR_TRADED, errors="coerce")
sl = sl[(sl.TRADE_TYPE_INDICATOR == "S") & sl.YIELD.notna() & (sl.PAR_TRADED >= 10_000)
        & (sl.WHEN_ISSUED_INDICATOR != "Y")].copy()
sl["TRADE_DATE"] = pd.to_datetime(sl.TRADE_DATE, errors="coerce"); sl["MATURITY_DATE"] = pd.to_datetime(sl.MATURITY_DATE, errors="coerce")
sl["rem_mat"] = (sl.MATURITY_DATE - sl.TRADE_DATE).dt.days / 365.25
sl = sl[(sl.rem_mat >= 1) & sl.TRADE_DATE.notna()]
sl["year"] = sl.TRADE_DATE.dt.year; sl = sl[sl.year.between(2008, 2025) & sl.YIELD.between(-2, 20)]
sl["wy"] = sl.YIELD * sl.PAR_TRADED
by = (sl.groupby(["CUSIP", "CUSIP6", "year"]).agg(wy=("wy", "sum"), w=("PAR_TRADED", "sum"),
        rem_mat=("rem_mat", "mean")).reset_index())
by["yield_pw"] = by.wy / by.w; by["log_rem_mat"] = np.log(by.rem_mat.clip(lower=0.25))
nyr = by.groupby("CUSIP")["year"].transform("nunique"); by = by[nyr >= 2]
mmap = pd.read_csv(D / "msrb_cusip6_county_map.csv", dtype=str)
by = by.merge(mmap, left_on="CUSIP6", right_on="cusip6", how="inner"); by["county_fips"] = fz(by["county_fips"])

def sec(mset, era=None):
    s = by[(by.group == "control") | (by.county_fips.isin(mset))].copy()
    s["AY"] = s.county_fips.map(amap); s = s[~(s.county_fips.isin(mset) & s.AY.isna())]
    s["ann"] = ((s.county_fips.isin(mset)) & (s.year >= s.AY)).astype(int)
    if era == "post": s["ann"] = s["ann"] * (s.year >= 2023).astype(int)
    m = pf.feols("yield_pw ~ ann + log_rem_mat | CUSIP + year", data=s, vcov={"CRV1": "county_fips"})
    nb = s.loc[s.county_fips.isin(mset), "CUSIP"].nunique()
    return m.coef()["ann"] * 100, m.pvalue()["ann"], nb

L += ["", "## 2. Secondary market (MSRB, bond + year FE) — confirmation test",
      "| Variant | beta (bps) | p | mega bonds |", "|---|---:|---:|---:|"]
for label, ms, era in [("mega-ex-oil, announced", MX, None), ("mega-ex-oil x post-2023", MX, "post"),
                       ("drop Nueces, announced", MX - {"48355"}, None),
                       ("drop Nueces, x post-2023", MX - {"48355"}, "post")]:
    b, p, nb = sec(ms, era); L.append(f"| {label} | {b:+.1f} | {p:.3f} | {nb:,} |")

L += ["", "## Conclusion",
      "- Primary market: point estimate stable across oil-drop and LOO (-20 to -39 bps) but significance "
      "depends on Nueces TX (drop it: p=0.405) -> inference rests on one county.",
      "- Secondary market: NO effect in the same cells (announced +0.7 p=0.75; x post-2023 -0.8 p=0.62; "
      "5,331 outstanding bonds, well-powered). The same bonds do not reprice.",
      "- CONCLUSION: the script-76 salience cells are NOT confirmed — primary-market-only, single-county-"
      "dependent inference, threshold-sensitive (>=300MW cut p=0.149). Same failure pattern as the colo "
      "-46.5. Record as: no confirmed effect for mega-announcement counties or the post-2022 era.", ""]
(D / "salience_verification.md").write_text("\n".join(L))
print("\n".join(L)); print("\nWrote salience_verification.md")
