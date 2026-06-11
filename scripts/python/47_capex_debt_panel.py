"""
47_capex_debt_panel.py

Extract the CAPEX and DEBT-SERVICE channels from MuniSpot v2 all-governmental-funds
(income statement, column_index == -1, County-General Purpose Government), FY2016-2026,
and build per-county outcomes for the matched DiD (script 48).

WHY ratios, not levels:
  v2 dollar levels are unreliable (x1000 / x1e6 unit misfires; duplicate mis-extracted
  rows -- e.g. county 01129 capital outlay appears as both $26M and $267M). Capex is also
  lumpy year to year (one school built per decade). Both problems vanish if we use
  INTENSITY RATIOS averaged over windows:
    - capex intensity      = CAPITAL OUTLAY / TOTAL EXPENDITURES
    - debt-service burden  = (PRINCIPAL + INTEREST) / TOTAL REVENUES
    - new-borrowing intens.= PROCEEDS FROM CAPITAL DEBT / TOTAL EXPENDITURES
  A x1000 error cancels in the ratio (numerator and denominator share it); an impossible
  ratio (>1 or <0) flags a corrupted county-year and is dropped by the [0,1] gate.

Outcome per county = (post-window mean) - (baseline-window mean) of each intensity, i.e.
the change in capex/debt intensity. Baseline = FY2016-2018, post = FY2022-2025 (means over
available years). Capex LEVEL CAGR is also emitted as a gated secondary outcome.

DEBT STOCK is intentionally absent: v2's balance sheet is the GOVERNMENTAL-FUNDS balance
sheet, which under GASB carries no long-term debt (that lives in the government-wide
statements v2 does not parse). We capture debt FLOWS (service + new issuance) only.

This script builds the panel + outcomes only; the DiD is script 48.
Output:
  data/derived/capex_debt_county_outcomes.csv
  data/derived/capex_debt_panel_long.csv   (county x fy intensities, for audit)
"""
from pathlib import Path
import numpy as np, pandas as pd, glob

ROOT = Path(__file__).resolve().parents[2]; D = ROOT / "data" / "derived"
PQ = ROOT / "data" / "munispot" / "parquet_v2"
def fz(s): return s.astype(str).str.zfill(5)

BUCKETS = {
    "TOTAL EXPENDITURES":                      "totexp",
    "TOTAL REVENUES":                          "totrev",
    "CAPITAL OUTLAY":                          "capex",
    "DEBT SERVICE, ANNUAL PRINCIPAL PAYMENT":  "prin",
    "DEBT SERVICE, INTEREST EXPENDITURE":      "interest",
    "PROCEEDS FROM CAPITAL DEBT":              "proceeds",
}
BASE_YRS = [2016, 2017, 2018]
POST_YRS = [2022, 2023, 2024, 2025]

# ---- 1. load county-gov all-funds rows for the 6 buckets, all FY ----
frames = []
for fy in range(2016, 2027):
    fs = glob.glob(str(PQ/f"statement_type=income_statement/fiscal_year={fy}/*.parquet"))
    if not fs: continue
    d = pd.read_parquet(fs[0], columns=["county_fips","municipality_type","column_index",
                                        "report_id","class_1","reported_value","value_multiplier"])
    d = d[(d["municipality_type"]=="County-General Purpose Government") &
          (d["column_index"]==-1) & (d["class_1"].isin(BUCKETS))].copy()
    d["fy"] = fy
    frames.append(d)
raw = pd.concat(frames, ignore_index=True)
raw["county_fips"] = fz(raw["county_fips"])
raw["val"] = raw["reported_value"].astype(float) * raw["value_multiplier"].astype(float)
raw["item"] = raw["class_1"].map(BUCKETS)

# ---- 2. collapse to one value per (county, fy, report_id, item): sum itemized rows ----
g = (raw.groupby(["county_fips","fy","report_id","item"])["val"].sum()
        .unstack("item"))
for c in BUCKETS.values():
    if c not in g.columns: g[c] = np.nan
g = g.reset_index()

# ---- 3. pick ONE report per (county, fy): the one with totexp & totrev present and the
#         most of the 6 buckets; tiebreak on larger totrev (the consolidated filing) ----
g["n_present"] = g[list(BUCKETS.values())].notna().sum(axis=1)
g["has_denoms"] = g["totexp"].notna() & g["totrev"].notna()
g = g.sort_values(["county_fips","fy","has_denoms","n_present","totrev"],
                  ascending=[True,True,False,False,False])
panel = g.drop_duplicates(["county_fips","fy"], keep="first").copy()

# ---- 4. intensities, with [0,1] sanity gates that drop corrupted county-years ----
def gated(num, den):
    r = num / den
    return r.where((r >= 0) & (r <= 1))   # impossible ratio -> NaN (e.g. dup mis-extraction)
panel["capex_share"]   = gated(panel["capex"], panel["totexp"])
panel["ds_burden"]     = gated(panel["prin"].fillna(0) + panel["interest"].fillna(0), panel["totrev"])
panel["newdebt_share"] = gated(panel["proceeds"], panel["totexp"])

panel[["county_fips","fy","totexp","totrev","capex","prin","interest","proceeds",
       "capex_share","ds_burden","newdebt_share"]].to_csv(D/"capex_debt_panel_long.csv", index=False)

# ---- 5. per-county baseline vs post window means -> change outcomes ----
def window_mean(df, col, yrs):
    s = df[df["fy"].isin(yrs)].groupby("county_fips")[col].mean()
    return s
OUTC = {"capex_share":"capex intensity (capex/totexp)",
        "ds_burden":"debt-service burden ((prin+int)/totrev)",
        "newdebt_share":"new-borrowing intensity (proceeds/totexp)"}
out = pd.DataFrame(index=sorted(panel["county_fips"].unique()))
for col in OUTC:
    b = window_mean(panel, col, BASE_YRS); p = window_mean(panel, col, POST_YRS)
    out[f"{col}_base"] = b; out[f"{col}_post"] = p
    out[f"{col}_chg"]  = p - b            # change in intensity (pp of the ratio)

# secondary: capex LEVEL CAGR (gated for lumpiness), baseline-mean -> post-mean of $ capex
cb = window_mean(panel.assign(capex=panel["capex"]), "capex", BASE_YRS)
cp = window_mean(panel, "capex", POST_YRS)
span = (np.mean(POST_YRS) - np.mean(BASE_YRS))
cagr = (cp / cb) ** (1/span) - 1
out["capex_level_cagr"] = cagr.where((cagr >= -0.30) & (cagr <= 0.60))   # gate extreme lumps

out.index.name = "county_fips"
out = out.reset_index()
out.to_csv(D/"capex_debt_county_outcomes.csv", index=False)

# ---- 6. coverage report ----
print(f"Counties in panel: {panel['county_fips'].nunique()}  | county-years: {len(panel)}")
print(f"Dropped county-years by ratio gate (capex_share NaN where capex present): "
      f"{int(panel['capex'].notna().sum() - panel['capex_share'].notna().sum())}")
for col, lab in OUTC.items():
    n = out[f"{col}_chg"].notna().sum()
    print(f"  {lab:48s}: {n} counties with baseline+post change")
print(f"  capex level CAGR (gated)                        : {out['capex_level_cagr'].notna().sum()} counties")
print("Wrote capex_debt_county_outcomes.csv + capex_debt_panel_long.csv")
