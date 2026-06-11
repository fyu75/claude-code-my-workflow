"""
78_colo_dose_secondary.py

The missing apples-to-apples confirmation for the colo result (memo §11): the primary-
market negative spread effect was estimated in DOSE form (log colo-MW per $ of baseline
tax, jointly with hyperscale/crypto doses — script 71 §3, -46.5 per log-point, op clock),
but the §12 secondary-market rejection used a county-level DUMMY. Here: the same joint
DOSE specification inside the MSRB bond-year panel.

  yield_pw (par-weighted YTW of outstanding bonds, %, bond x year)
      ~ ld_{clock}_colo + ld_{clock}_hyp + ld_{clock}_cry + ld_{clock}_oth + log_rem_mat
      | CUSIP + year,  cluster = county
  doses: cumulative >=50MW capacity by category (per-DC PROVIDERTYPE) on the operational
  clock (primary) and announcement clock (robustness), / 2017 property tax ($M), log1p.

If colo-dose is negative and significant here, the multi-tenant-diversification pricing
story survives; if not, the §11 colo cell is settled as a footnote.

Output: data/derived/colo_dose_secondary.md
"""
from pathlib import Path
import numpy as np, pandas as pd
import pyarrow.parquet as pq
import pyfixest as pf
import warnings; warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
RAW = Path("/Users/fangyu/claude/datacenter/raw")
D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)
PHANTOM = {"47121", "54047", "21127"}

# ---------- per-DC category doses (script 71 construction) ----------
pv = pd.read_sas(RAW / "dcprovider_latest.sas7bdat", encoding="latin-1")
pv["pid"] = pv["PROPERTYUNIQUEID"].astype(str).str.replace(r"\.0$", "", regex=True)
ptypes = pv.groupby("pid")["PROVIDERTYPE"].apply(lambda x: set(x.dropna()))
def _cat(ts):
    if any("Cryptocurrency" in t for t in ts): return "cry"
    if "Hyperscale" in ts: return "hyp"
    if ts & {"Retail", "Wholesale", "Telco", "Hosting", "Reseller"}: return "colo"
    return "oth"
pid_cat = ptypes.apply(_cat)
per = pd.read_sas(RAW / "dcpropertiesperiodic_latest.sas7bdat", encoding="latin-1")
per["pid"] = per["PROPERTYUNIQUEID"].astype(str).str.replace(r"\.0$", "", regex=True)
mw = per.groupby("pid")["TOTALITPOWER"].max().div(1000).rename("mw_peak").reset_index()
prop = pd.read_csv(D / "dc_property_county_fips.csv")
prop["pid"] = prop["PROPERTYUNIQUEID"].astype("Int64").astype(str)
prop["county_fips"] = fz(prop["county_fips"].astype(str))
prop["oy"] = pd.to_numeric(prop["YEARFACILITYBECAMEOPERATIONAL"], errors="coerce")
m = prop.merge(mw, on="pid"); m["cat"] = m.pid.map(pid_cat).fillna("oth")
T = pd.read_csv(D / "treated_universe_labeled.csv", dtype={"county_fips": str}); T["county_fips"] = fz(T["county_fips"])
treated = set(T.county_fips) - PHANTOM
big = m[(m.mw_peak >= 50) & m.county_fips.isin(treated)].dropna(subset=["oy"]).copy()
a = pd.read_csv(D / "dc_dc_level_announcements.csv", dtype={"county_fips": str}); a["county_fips"] = fz(a["county_fips"])
a = a[a.announce_year.notna()][["county_fips", "dcname", "announce_year"]]
nm = per.dropna(subset=["DATACENTERNAME"]).groupby("pid")["DATACENTERNAME"].first().rename("dcname").reset_index()
big = big.merge(nm, on="pid", how="left").merge(a, on=["county_fips", "dcname"], how="left")
cty = pd.read_csv(D / "dc_announcement_years.csv", dtype={"county_fips": str}); cty["county_fips"] = fz(cty["county_fips"])
cmap = dict(zip(cty.county_fips, cty.announce_year))
big["ann"] = big["announce_year"].fillna(big.county_fips.map(cmap)).fillna(big["oy"] - 1)

tp = pd.read_csv(D / "treated_pt_final.csv", dtype={"county_fips": str}); tp["county_fips"] = fz(tp["county_fips"])
g = pd.read_csv(D / "census_2017_2022_growth.csv", dtype={"county_fips": str}); g["county_fips"] = fz(g["county_fips"])
pt17 = {**dict(zip(g.county_fips, g.rev_property_tax_17)), **dict(zip(tp.county_fips, tp.pt_2017_final))}

rows = []
for f in sorted(set(big.county_fips)):
    sub = big[big.county_fips == f]; p = pt17.get(f, np.nan)
    for y in range(2008, 2026):
        r = {"county_fips": f, "year": y}
        for clock, col in [("op", "oy"), ("ann", "ann")]:
            known = sub[sub[col] <= y]
            for c in ("hyp", "colo", "cry", "oth"):
                mwv = known.loc[known.cat == c, "mw_peak"].sum()
                r[f"ld_{clock}_{c}"] = np.log1p(mwv / p) if (p and p > 0) else 0.0
        rows.append(r)
dose = pd.DataFrame(rows); dmap = dose.set_index(["county_fips", "year"])
DV = [c for c in dose.columns if c.startswith("ld_")]

# ---------- MSRB bond-year panel (script 73 construction) ----------
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
by = by[(by.group == "control") | (by.county_fips.isin(treated))].copy()
idx = pd.MultiIndex.from_arrays([by.county_fips, by.year])
for c in DV: by[c] = dmap[c].reindex(idx).values
by[DV] = by[DV].fillna(0.0)

L = ["# Colo-dose confirmation in the secondary market — the apples-to-apples test\n",
     "**Date:** 2026-06-11. `scripts/python/78`. Dependent variable: par-weighted yield-to-worst of "
     "OUTSTANDING bonds (%, bond x year; MSRB customer-sale trades, 2008-2025). Joint category doses "
     "(log1p cum >=50MW MW / 2017 PT $M), bond + year FE, cluster county. Coefficients x100 = bps per "
     "log-point of dose. Primary-market reference (script 71 §3, new-issue spreads): colo -46.5 (p=0.024) "
     "on the operational clock.\n",
     "| Clock | colo-dose | hyperscale-dose | crypto-dose |", "|---|---|---|---|"]
for clock in ["op", "ann"]:
    xs = [f"ld_{clock}_colo", f"ld_{clock}_hyp", f"ld_{clock}_cry", f"ld_{clock}_oth"]
    mm = pf.feols("yield_pw ~ " + " + ".join(xs) + " + log_rem_mat | CUSIP + year",
                  data=by, vcov={"CRV1": "county_fips"})
    cells = []
    for x in xs[:3]:
        b, se, p = mm.coef()[x] * 100, mm.se()[x] * 100, mm.pvalue()[x]
        st = "***" if p < .01 else "**" if p < .05 else "*" if p < .10 else ""
        cells.append(f"{b:+.1f}{st} ({se:.1f}) p={p:.3f}")
    L.append(f"| {clock} | " + " | ".join(cells) + " |")
ncolo = by[by[f"ld_op_colo"] > 0].CUSIP.nunique()
L += ["", f"Bonds in colo-dose>0 counties: {ncolo:,}; full panel {len(by):,} bond-years, "
      f"{by.CUSIP.nunique():,} bonds, {by.county_fips.nunique():,} counties.",
      "", "## Conclusion",
      "- If colo-dose here is null or positive: the §11 primary-market colo estimate is settled as NOT "
      "confirmed (footnote). If negative and significant: the multi-tenant-diversification pricing story "
      "survives the selection-free test and re-enters the paper.", ""]
(D / "colo_dose_secondary.md").write_text("\n".join(L))
print("\n".join(L)); print("\nWrote colo_dose_secondary.md")
