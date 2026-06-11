"""
73_msrb_secondary_event_study.py

Phase 3: SECONDARY-MARKET yield event study around DC announcements — the
selection-free test of the pricing channel. Primary-market (SDC) results are
entangled with the county's CHOICE to issue; here the same outstanding bond
trades before and after the announcement, so a bond fixed effect absorbs all
time-invariant bond/issuer characteristics and identification is purely
within-bond.

Design:
  panel  = bond (9-char CUSIP) x year, par-weighted mean yield-to-worst
  filter = customer-sale trades (TRADE_TYPE_INDICATOR=='S', retail price
           discovery), PAR_TRADED >= $10k, YIELD present, not when-issued,
           remaining maturity >= 1yr at trade
  spec   = yield_bt ~ announced_{c(b),t} + log(remaining_maturity)
                      | CUSIP + year,  cluster = county
           announced = 1[year >= county first >=50MW announcement] (absorbing)
  event study version: binned event time, ref = -1
  groups = treated (clean_dc / crypto cuts) vs clean never-DC controls;
           PLACEBO = 11 big-DC metros (fiscal share <1%, mechanism off)

CUSIP6 -> county mapping: data/derived/msrb_cusip6_county_map.csv (SDC
ISSUECUSIP1 bridge; multi-county conduits dropped). Working slice from script 72.

Output: data/derived/msrb_secondary_event_study.md
"""
from pathlib import Path
import numpy as np, pandas as pd
import pyarrow.parquet as pq
import pyfixest as pf
import warnings; warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)
PHANTOM = {"47121", "54047", "21127"}

# ---------- load slice, filter, aggregate to bond-year ----------
sl = pq.read_table(ROOT / "data" / "msrb" / "msrb_working_slice.parquet",
                   columns=["CUSIP", "CUSIP6", "TRADE_DATE", "YIELD", "PAR_TRADED",
                            "TRADE_TYPE_INDICATOR", "MATURITY_DATE", "WHEN_ISSUED_INDICATOR"]).to_pandas()
print(f"slice: {len(sl):,} trades")
# SAS char columns survive as strings: PAR_TRADED carries "MM+" masking (par > $5M for
# 5 days post-trade), YIELD/dates char-typed -> coerce; "MM+" rows drop (institutional
# blocks lose par weight, acceptable: they re-appear unmasked in later disseminations)
sl["YIELD"] = pd.to_numeric(sl.YIELD, errors="coerce")
sl["PAR_TRADED"] = pd.to_numeric(sl.PAR_TRADED, errors="coerce")
sl = sl[(sl.TRADE_TYPE_INDICATOR == "S") & sl.YIELD.notna() & (sl.PAR_TRADED >= 10_000)
        & (sl.WHEN_ISSUED_INDICATOR != "Y")].copy()
sl["TRADE_DATE"] = pd.to_datetime(sl.TRADE_DATE, errors="coerce")
sl["MATURITY_DATE"] = pd.to_datetime(sl.MATURITY_DATE, errors="coerce")
sl["rem_mat"] = (sl.MATURITY_DATE - sl.TRADE_DATE).dt.days / 365.25
sl = sl[(sl.rem_mat >= 1) & sl.TRADE_DATE.notna()]
sl["year"] = sl.TRADE_DATE.dt.year
sl = sl[sl.year.between(2008, 2025) & sl.YIELD.between(-2, 20)]
print(f"after filters (S, >=10k, mat>=1yr, 2008-2025): {len(sl):,}")

sl["wy"] = sl.YIELD * sl.PAR_TRADED
by = (sl.groupby(["CUSIP", "CUSIP6", "year"])
        .agg(wy=("wy", "sum"), w=("PAR_TRADED", "sum"), rem_mat=("rem_mat", "mean"))
        .reset_index())
by["yield_pw"] = by.wy / by.w
by["log_rem_mat"] = np.log(by.rem_mat.clip(lower=0.25))
nyr = by.groupby("CUSIP")["year"].transform("nunique")
by = by[nyr >= 2]                                   # within-bond identification needs >=2 yrs
print(f"bond-year obs: {len(by):,} | bonds: {by.CUSIP.nunique():,}")

# ---------- county mapping + treatment ----------
m = pd.read_csv(D / "msrb_cusip6_county_map.csv", dtype=str)
by = by.merge(m, left_on="CUSIP6", right_on="cusip6", how="inner")
by["county_fips"] = fz(by["county_fips"])
by = by[~by.county_fips.isin(PHANTOM)]

T = pd.read_csv(D / "treated_universe_labeled.csv", dtype={"county_fips": str}); T["county_fips"] = fz(T["county_fips"])
cls = dict(zip(T.county_fips, T.dc_class))
anc = pd.read_csv(D / "announcement_anchor_county.csv", dtype={"county_fips": str}); anc["county_fips"] = fz(anc["county_fips"])
cty = pd.read_csv(D / "dc_announcement_years.csv", dtype={"county_fips": str}); cty["county_fips"] = fz(cty["county_fips"])
A = (T[["county_fips"]].merge(anc[["county_fips", "ann_firstmaj"]], on="county_fips", how="left")
       .merge(cty[["county_fips", "announce_year"]], on="county_fips", how="left"))
A["A_firstmaj"] = A["ann_firstmaj"].fillna(A["announce_year"])
amap = dict(zip(A.county_fips, A.A_firstmaj))
# placebo metros: anchor = first >=50MW operational year (no announcements; symmetric is impossible,
# op-year is the available objective clock; lead is ~1yr so comparable)
cmp_ = pd.read_csv(D / "treatment_anchors_compare.csv", dtype={"county_fips": str})  # treated anchors
f50 = pd.read_csv(D / "big_dc_announcement_targets_capped.csv", dtype={"county_fips": str}) if False else None
# metros' first50 op year: rebuild tiny lookup from the property file
RAW = Path("/Users/fangyu/claude/datacenter/raw")
per = pd.read_sas(RAW / "dcpropertiesperiodic_latest.sas7bdat", encoding="latin-1")
per["pid"] = per["PROPERTYUNIQUEID"].astype(str).str.replace(r"\.0$", "", regex=True)
mwp = per.groupby("pid")["TOTALITPOWER"].max().div(1000).rename("mw_peak").reset_index()
prop = pd.read_csv(D / "dc_property_county_fips.csv")
prop["pid"] = prop["PROPERTYUNIQUEID"].astype("Int64").astype(str)
prop["county_fips"] = fz(prop["county_fips"].astype(str))
prop["oy"] = pd.to_numeric(prop["YEARFACILITYBECAMEOPERATIONAL"], errors="coerce")
bigall = prop.merge(mwp, on="pid"); bigall = bigall[bigall.mw_peak >= 50]
f50map = bigall.groupby("county_fips")["oy"].min().to_dict()

by["grp"] = by["group"]
by["AY"] = np.where(by.grp == "treated", by.county_fips.map(amap),
                    np.where(by.grp == "placebo_metro", by.county_fips.map(f50map), np.nan))
by = by[~((by.grp != "control") & by.AY.isna())]
by["dc_class"] = by.county_fips.map(cls)

def run_dummy(df, tset_label, ks=None):
    s = df[(df.grp == "control") | ((df.grp == tset_label) & (df.dc_class.isin(ks) if ks else True))].copy()
    s["announced"] = ((s.grp == tset_label) & (s.year >= s.AY)).astype(int)
    mm = pf.feols("yield_pw ~ announced + log_rem_mat | CUSIP + year", data=s, vcov={"CRV1": "county_fips"})
    b, se, p = mm.coef()["announced"], mm.se()["announced"], mm.pvalue()["announced"]
    st = "***" if p < .01 else "**" if p < .05 else "*" if p < .10 else ""
    nb = s.loc[s.grp == tset_label, "CUSIP"].nunique(); nc = s.loc[s.grp == tset_label, "county_fips"].nunique()
    return f"{b*100:+.1f}{st} bps ({se*100:.1f}) p={p:.3f} | {nb:,} bonds / {nc} counties"

def run_es(df, tset_label, ks=None):
    s = df[(df.grp == "control") | ((df.grp == tset_label) & (df.dc_class.isin(ks) if ks else True))].copy()
    s["et"] = np.where(s.grp == tset_label, s.year - s.AY, np.nan)
    out = []
    for k in [-4, -3, -2, 0, 1, 2, 3, 4]:
        s[f"k{k}".replace("-", "m")] = ((s.grp == tset_label) & (np.clip(s.et, -5, 5) == k)).astype(int)
    ec = [c for c in s.columns if c.startswith("k") and c not in ("CUSIP",)]
    ec = [c for c in ec if c.startswith("km") or c.startswith("k")]
    ec = [f"k{k}".replace("-", "m") for k in [-4, -3, -2, 0, 1, 2, 3, 4]]
    mm = pf.feols("yield_pw ~ " + " + ".join(ec) + " + log_rem_mat | CUSIP + year",
                  data=s, vcov={"CRV1": "county_fips"})
    co, pv = mm.coef(), mm.pvalue()
    for k in [-4, -3, -2, 0, 1, 2, 3, 4]:
        c = f"k{k}".replace("-", "m")
        b, p = co.get(c, np.nan), pv.get(c, np.nan)
        st = "***" if p < .01 else "**" if p < .05 else "*" if p < .10 else ""
        out.append(f"| {k:+d} | {b*100:+.1f}{st} | {p:.3f} |")
    return out

L = ["# MSRB secondary-market yield event study — the selection-free pricing test\n",
     "**Date:** 2026-06-11. `scripts/python/73`. Bond(CUSIP)-year panel of par-weighted customer-sale "
     "yield-to-worst; bond + year FE; cluster county; control = clean never-DC counties' bonds. "
     "`announced` absorbing. Identification = the SAME outstanding bond before vs after announcement "
     "(no issuance selection). Yields in %, effects reported in bps.\n",
     f"Universe: {len(by):,} bond-year obs, {by.CUSIP.nunique():,} bonds, "
     f"{by.county_fips.nunique():,} counties.\n",
     "## Absorbing announced dummy (bps)",
     "| Cut | effect |", "|---|---|"]
L.append("| Treated ALL | " + run_dummy(by, "treated") + " |")
L.append("| Treated clean_dc | " + run_dummy(by, "treated", ["clean_dc"]) + " |")
L.append("| Treated crypto | " + run_dummy(by, "treated", ["crypto"]) + " |")
L.append("| Treated mixed | " + run_dummy(by, "treated", ["mixed"]) + " |")
L.append("| **PLACEBO metros** (op-yr anchor) | " + run_dummy(by, "placebo_metro") + " |")
# colo-whisper arbitration: the 8 treated counties holding >=50MW COLO capacity (script 71 §3
# found suggestive -46.5 bps primary-market tightening on ~6-8 clusters; this is the arbiter)
COLO = {"04013", "13121", "32029", "45091", "49035", "51107", "51153", "53025"}
byc = by.copy(); byc.loc[(byc.grp == "treated") & ~byc.county_fips.isin(COLO), "grp"] = "drop"
byc = byc[byc.grp != "drop"]
L.append("| **Colo-capacity counties** (8, whisper arbiter) | " + run_dummy(byc, "treated") + " |")

L += ["", "## Event study (binned, ref −1; bps)", "", "### Treated clean_dc",
      "| evt | coef (bps) | p |", "|---|---:|---:|"]
L += run_es(by, "treated", ["clean_dc"])
L += ["", "### Treated crypto", "| evt | coef (bps) | p |", "|---|---:|---:|"]
L += run_es(by, "treated", ["crypto"])
L += ["", "### Placebo metros", "| evt | coef (bps) | p |", "|---|---:|---:|"]
L += run_es(by, "placebo_metro")
L += ["", "### Colo-capacity counties (whisper arbiter)", "| evt | coef (bps) | p |", "|---|---:|---:|"]
L += run_es(byc, "treated")

L += ["", "## Reading",
      "- This is the arbiter test (memo §11): bond FE kills issuance selection — if the fiscal windfall "
      "is priced, the SAME bond's yield should fall after announcement relative to control bonds.",
      "- clean_dc null here + primary-market null = airtight non-pricing. crypto positive = risk premium "
      "on volatile tax base, now selection-free. Placebo metros must be null (mechanism off).",
      "- Filters: customer-sale (S) trades, par>=10k, rem. maturity>=1yr, yields in [-2,20], bond observed "
      ">=2 years. log(remaining maturity) controls the mechanical roll-down.", ""]
(D / "msrb_secondary_event_study.md").write_text("\n".join(L))
print("\n".join(L)); print("\nWrote msrb_secondary_event_study.md")
