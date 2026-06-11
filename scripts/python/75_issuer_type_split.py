"""
75_issuer_type_split.py

Pre-specified heterogeneity test: issuer-type split of bond-spread DiD.

Hypothesis: DCs generate property-tax windfalls mainly for SCHOOL DISTRICTS
(largest PT recipient in most states), not county governments. If so, the
announcement effect on spread should be most negative for school/special
districts, not county-government issuers.

Mirrors script 68 exactly for treatment construction, sample, and estimator.
Splits the deal-level spread regression by ISSTYPE_TRANS:
  (a) District — all
  (b) School districts only (ISSUER contains school keywords)
  (c) County/Parish
  (d) City, Town Vlg

Outputs:
  data/derived/issuer_type_split.md
  data/derived/school_district_cusip6.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pyfixest as pf
import warnings
warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "data" / "derived"
SDC_DIR = ROOT / "data" / "sdc_muni" / "sdc_municipals"

def fz(s):
    return s.astype(str).str.zfill(5)

Y0, Y1 = 2008, 2025
PHANTOMS = {"47121", "54047", "21127"}

# ── school-district keyword pattern ──────────────────────────────────────────
SCHOOL_KW = r'(?i)\b(sch|school|isd|usd|unif|unified|elem|high\s+school|community\s+unit|cu\s*sd|c\.u\.s\.d|c\.s\.d|local\s+sch|lsd|cusd|k-12)\b'

# =============================================================================
# 1. Treatment construction — mirror script 68 exactly
# =============================================================================
T = pd.read_csv(D / "treated_universe_labeled.csv", dtype={"county_fips": str})
T["county_fips"] = fz(T["county_fips"])
T = T[~T.county_fips.isin(PHANTOMS)]
treated = set(T.county_fips)

anc = pd.read_csv(D / "announcement_anchor_county.csv", dtype={"county_fips": str})
anc["county_fips"] = fz(anc["county_fips"])
cty = pd.read_csv(D / "dc_announcement_years.csv", dtype={"county_fips": str})
cty["county_fips"] = fz(cty["county_fips"])

A = (T[["county_fips", "dc_class"]]
     .merge(anc[["county_fips", "ann_firstmaj"]], on="county_fips", how="left")
     .merge(cty[["county_fips", "announce_year"]], on="county_fips", how="left"))
A["A_firstmaj"] = A["ann_firstmaj"].fillna(A["announce_year"])
amap = dict(zip(A.county_fips, A.A_firstmaj))
cls_map = dict(zip(A.county_fips, A.dc_class))

# Controls: clean never-DC counties from panel
pan = pd.read_csv(D / "county_year_panel_v4.csv", dtype={"county_fips": str})
pan["county_fips"] = fz(pan["county_fips"])
never = (pan.groupby("county_fips")["n_dc_cumulative"].max()
           .pipe(lambda s: set(s[s == 0].index)) - treated)

def add_treat(df):
    df = df[df.county_fips.isin(treated | never)].copy()
    df["A"] = df.county_fips.map(amap)
    df = df[~(df.county_fips.isin(treated) & df.A.isna())].copy()
    df["announced"] = ((df.county_fips.isin(treated)) & (df.year >= df.A)).astype(int)
    df["dc_class"] = df.county_fips.map(cls_map)
    return df

# =============================================================================
# 2. Load SDC deals — chunked, keep needed cols only
# =============================================================================
KEEP_COLS = ["MASTER_DEAL_NO", "ISSTYPE_TRANS", "ISSUER", "ISSUECUSIP1"]

print("Loading SDC deals (chunked)…")
chunks = []
for chunk in pd.read_sas(SDC_DIR / "deals_data.sas7bdat",
                          encoding="latin-1", chunksize=200_000):
    chunks.append(chunk[KEEP_COLS].copy())
raw = pd.concat(chunks, ignore_index=True)
print(f"  SDC raw rows: {len(raw):,}")

# Harmonise MASTER_DEAL_NO to Int64 (matches sdc_deal_spread.csv)
raw["MASTER_DEAL_NO"] = raw["MASTER_DEAL_NO"].astype(str).str.strip()

# =============================================================================
# 3. Load spread + rating; merge with treatment construction
# =============================================================================
d = pd.read_csv(D / "sdc_deal_spread.csv")
r = pd.read_csv(D / "sdc_deal_rating.csv")

for df in (d, r):
    df["MASTER_DEAL_NO"] = pd.to_numeric(df["MASTER_DEAL_NO"], errors="coerce").astype("Int64")

d = d.merge(r, on="MASTER_DEAL_NO", how="left")
d = d[(d.AMT > 0) & d.year.between(Y0, Y1)].copy()
d["logamt"] = np.log(d.AMT)
d["logmat"] = np.log(d.par_wtd_yrs2mat.clip(lower=0.25))
d["county_fips"] = fz(d["county_fips"].astype(int).astype(str))
d = add_treat(d)

# Merge issuer-type info from SDC
# SDC MASTER_DEAL_NO is a string; convert for join
raw["MASTER_DEAL_NO_int"] = pd.to_numeric(raw["MASTER_DEAL_NO"], errors="coerce").astype("Int64")
d = d.merge(raw[["MASTER_DEAL_NO_int", "ISSTYPE_TRANS", "ISSUER", "ISSUECUSIP1"]],
            left_on="MASTER_DEAL_NO", right_on="MASTER_DEAL_NO_int", how="left")
d.drop(columns=["MASTER_DEAL_NO_int"], inplace=True)

# Decode bytes if needed
for col in ["ISSTYPE_TRANS", "ISSUER", "ISSUECUSIP1"]:
    if d[col].dtype == object:
        d[col] = d[col].apply(lambda x: x.decode("latin-1") if isinstance(x, bytes) else x)

# School-district flag
d["is_school_dist"] = (
    (d["ISSTYPE_TRANS"].str.strip() == "District") &
    d["ISSUER"].fillna("").str.contains(SCHOOL_KW, regex=True)
)

print(f"  Deals after treatment merge: {len(d):,}")
print(f"  Deals with ISSTYPE_TRANS: {d['ISSTYPE_TRANS'].notna().sum():,}")
print(f"  School-district deals: {d['is_school_dist'].sum():,}")

# =============================================================================
# 4. Composition table — treated counties only
# =============================================================================
tr_deals = d[d.county_fips.isin(treated)].copy()
total_par_tr = tr_deals["AMT"].sum()

comp_rows = []
for isstype, grp in tr_deals.groupby("ISSTYPE_TRANS"):
    n = len(grp)
    par_share = grp["AMT"].sum() / total_par_tr * 100
    if isstype == "District":
        n_school = grp["is_school_dist"].sum()
        n_other = n - n_school
        frac_school = n_school / n * 100 if n else 0
        comp_rows.append({
            "ISSTYPE_TRANS": isstype,
            "n_deals": n,
            "par_share_pct": par_share,
            "note": f"school={n_school} ({frac_school:.0f}%), other={n_other}"
        })
    else:
        comp_rows.append({
            "ISSTYPE_TRANS": isstype,
            "n_deals": n,
            "par_share_pct": par_share,
            "note": ""
        })

# Sort by n_deals descending
comp_df = pd.DataFrame(comp_rows).sort_values("n_deals", ascending=False).reset_index(drop=True)

# =============================================================================
# 5. Regression helper — mirror script 68 one()
# =============================================================================
def one(df, y, ctrl, fe, vcov_col="county_fips"):
    sub = df.dropna(subset=[y] + ([c.strip() for c in ctrl.split("+") if c.strip()] if ctrl else []))
    formula = f"{y} ~ announced" + (f" + {ctrl}" if ctrl else "") + f" | {fe}"
    m = pf.feols(formula, data=sub, vcov={"CRV1": vcov_col})
    b = m.coef()["announced"]
    se = m.se()["announced"]
    p = m.pvalue()["announced"]
    N = int(m._N)
    return b, se, p, N

def stars(p):
    return "***" if p < .01 else "**" if p < .05 else "*" if p < .10 else ""

# =============================================================================
# 6. Run regressions for each issuer-type cut × ALL-treated cut
# =============================================================================
# Cuts: ALL treated (all dc_class) vs clean_dc only
cuts = {
    "ALL": lambda df: df,
    "clean_dc": lambda df: df[df.dc_class.isin(["clean_dc"]) | df.county_fips.isin(never)],
}

issuer_cuts = {
    "(a) District — all":    lambda df: df[df["ISSTYPE_TRANS"].str.strip() == "District"],
    "(b) School district":   lambda df: df[df["is_school_dist"]],
    "(c) County/Parish":     lambda df: df[df["ISSTYPE_TRANS"].str.strip() == "County/Parish"],
    "(d) City, Town Vlg":    lambda df: df[df["ISSTYPE_TRANS"].str.strip() == "City, Town Vlg"],
    "(e) ALL types (sanity)":lambda df: df,
}

results = []
for cut_label, cut_fn in cuts.items():
    for issuer_label, issuer_fn in issuer_cuts.items():
        sub = issuer_fn(cut_fn(d)).copy()
        sub = sub[sub.spread_bps.notna() & sub.logamt.notna() & sub.logmat.notna()]
        n_tr_counties = sub[sub.county_fips.isin(treated)]["county_fips"].nunique()
        n_tr_deals = sub[sub.county_fips.isin(treated)]["MASTER_DEAL_NO"].nunique()
        underpowered = (n_tr_counties < 20) or (n_tr_deals < 200)
        try:
            b, se, p, N = one(sub, "spread_bps", "logamt + logmat", "county_fips + year")
            results.append({
                "cut": cut_label,
                "issuer_type": issuer_label,
                "beta": b, "se": se, "p": p, "N": N,
                "n_tr_counties": n_tr_counties,
                "n_tr_deals": n_tr_deals,
                "underpowered": underpowered,
                "err": None,
            })
        except Exception as e:
            results.append({
                "cut": cut_label,
                "issuer_type": issuer_label,
                "beta": np.nan, "se": np.nan, "p": np.nan, "N": 0,
                "n_tr_counties": n_tr_counties,
                "n_tr_deals": n_tr_deals,
                "underpowered": underpowered,
                "err": str(e)[:60],
            })

res_df = pd.DataFrame(results)

# =============================================================================
# 7. Any-rated share for school-district and county/parish
# =============================================================================
rated_rows = []
for issuer_label, issuer_fn in [
    ("(b) School district", lambda df: df[df["is_school_dist"]]),
    ("(c) County/Parish",   lambda df: df[df["ISSTYPE_TRANS"].str.strip() == "County/Parish"]),
]:
    sub = issuer_fn(d).copy()
    sub = sub[sub.any_rated_share.notna()]
    n_tr = sub[sub.county_fips.isin(treated)]["county_fips"].nunique()
    try:
        b, se, p, N = one(sub, "any_rated_share", "", "county_fips + year")
        rated_rows.append({"issuer_type": issuer_label, "beta": b, "se": se, "p": p, "N": N,
                            "n_tr_counties": n_tr, "err": None})
    except Exception as e:
        rated_rows.append({"issuer_type": issuer_label, "beta": np.nan, "se": np.nan, "p": np.nan,
                            "N": 0, "n_tr_counties": n_tr, "err": str(e)[:60]})

rated_df = pd.DataFrame(rated_rows)

# =============================================================================
# 8. Save school-district CUSIP6 for treated counties
# =============================================================================
school_tr = d[d.is_school_dist & d.county_fips.isin(treated)].copy()
# Explode slash-separated CUSIPs
cusip_rows = []
for _, row in school_tr.iterrows():
    cusip_raw = str(row["ISSUECUSIP1"]) if pd.notna(row["ISSUECUSIP1"]) else ""
    cusips = [c.strip()[:6] for c in cusip_raw.split("/") if len(c.strip()) >= 6]
    for c6 in cusips:
        cusip_rows.append({
            "county_fips": row["county_fips"],
            "cusip6": c6,
            "issuer": row["ISSUER"],
        })

cusip_df = pd.DataFrame(cusip_rows).drop_duplicates().reset_index(drop=True)
cusip_df.to_csv(D / "school_district_cusip6.csv", index=False)
print(f"  school_district_cusip6.csv: {len(cusip_df):,} rows, "
      f"{cusip_df.county_fips.nunique()} treated counties")

# =============================================================================
# 9. Format markdown output
# =============================================================================
n_treated = len(treated)
n_never = len(never)

lines = [
    "# Issuer-type heterogeneity: DC announcement effect on bond spreads",
    "",
    "**Script:** `scripts/python/75_issuer_type_split.py`  ",
    "**Date:** 2026-06-11  ",
    "**Spec:** `spread_bps ~ announced + logamt + logmat | county_fips + year`, cluster county  ",
    "**Years:** 2008–2025  ",
    f"**Treatment construction:** mirrors script 68 exactly — phantoms {{47121,54047,21127}} removed; "
    f"anchor = A_firstmaj (DC-level firstmaj, county-level fallback); "
    f"treated = {n_treated} counties, controls = {n_never:,} clean never-DC counties.  ",
    "",
    "---",
    "",
    "## A. Composition of deals in TREATED counties by issuer type",
    "",
    f"Total treated-county deals in sample (2008–2025): {len(tr_deals):,}  ",
    f"Total par ($M): {total_par_tr:,.0f}",
    "",
    "| ISSTYPE_TRANS | N deals | Par share (%) | Notes |",
    "|---|---:|---:|---|",
]
for _, row in comp_df.iterrows():
    lines.append(
        f"| {row['ISSTYPE_TRANS']} | {int(row['n_deals']):,} | {row['par_share_pct']:.1f} | {row['note']} |"
    )
lines += [
    "",
    "---",
    "",
    "## B. Spread regression by issuer type — cut: ALL treated",
    "",
    "| Issuer type | beta (announced) | SE | p | N | N treated counties | N treated deals | Underpowered? |",
    "|---|---:|---:|---:|---:|---:|---:|---|",
]
for _, row in res_df[res_df.cut == "ALL"].iterrows():
    if row["err"]:
        lines.append(f"| {row['issuer_type']} | ERR | | | | {row['n_tr_counties']} | {row['n_tr_deals']} | {'⚠' if row['underpowered'] else ''} |")
    else:
        st = stars(row["p"])
        flag = "⚠ underpowered" if row["underpowered"] else ""
        lines.append(
            f"| {row['issuer_type']} | {row['beta']:+.3f}{st} | {row['se']:.3f} | {row['p']:.3f} | "
            f"{int(row['N']):,} | {row['n_tr_counties']} | {row['n_tr_deals']:,} | {flag} |"
        )
lines += [
    "",
    "## C. Spread regression by issuer type — cut: clean_dc only",
    "",
    "| Issuer type | beta (announced) | SE | p | N | N treated counties | N treated deals | Underpowered? |",
    "|---|---:|---:|---:|---:|---:|---:|---|",
]
for _, row in res_df[res_df.cut == "clean_dc"].iterrows():
    if row["err"]:
        lines.append(f"| {row['issuer_type']} | ERR | | | | {row['n_tr_counties']} | {row['n_tr_deals']} | {'⚠' if row['underpowered'] else ''} |")
    else:
        st = stars(row["p"])
        flag = "⚠ underpowered" if row["underpowered"] else ""
        lines.append(
            f"| {row['issuer_type']} | {row['beta']:+.3f}{st} | {row['se']:.3f} | {row['p']:.3f} | "
            f"{int(row['N']):,} | {row['n_tr_counties']} | {row['n_tr_deals']:,} | {flag} |"
        )

# Sanity block
all_sanity = res_df[(res_df.cut == "ALL") & (res_df.issuer_type == "(e) ALL types (sanity)")]
clean_sanity = res_df[(res_df.cut == "clean_dc") & (res_df.issuer_type == "(e) ALL types (sanity)")]

def fmt_row(r):
    if r.empty:
        return "N/A"
    r = r.iloc[0]
    if r["err"]:
        return f"ERR: {r['err']}"
    return f"{r['beta']:+.3f}{stars(r['p'])} (SE={r['se']:.3f}, p={r['p']:.3f}, N={int(r['N']):,})"

lines += [
    "",
    "---",
    "",
    "## D. Sanity check — pooled all-issuer-types vs script 68 baseline",
    "",
    "Script 68 (ALL cut, county+year FE) reports spread_bps NULL for clean_dc.",
    "Expected range: approximately −0.5 to +4.9 (ns).",
    "",
    f"| Cut | This script (all types) |",
    f"|---|---|",
    f"| ALL | {fmt_row(all_sanity)} |",
    f"| clean_dc | {fmt_row(clean_sanity)} |",
    "",
    "---",
    "",
    "## E. Rating extensive (any_rated_share) by school-district vs county/parish",
    "",
    "| Issuer type | beta (announced) | SE | p | N | N treated counties |",
    "|---|---:|---:|---:|---:|---:|",
]
for _, row in rated_df.iterrows():
    if row["err"]:
        lines.append(f"| {row['issuer_type']} | ERR | | | | {row['n_tr_counties']} |")
    else:
        st = stars(row["p"])
        lines.append(
            f"| {row['issuer_type']} | {row['beta']:+.3f}{st} | {row['se']:.3f} | {row['p']:.3f} | "
            f"{int(row['N']):,} | {row['n_tr_counties']} |"
        )

# Evaluation of the pre-specified hypothesis
school_all = res_df[(res_df.cut == "ALL") & (res_df.issuer_type == "(b) School district")]
county_all = res_df[(res_df.cut == "ALL") & (res_df.issuer_type == "(c) County/Parish")]
school_clean = res_df[(res_df.cut == "clean_dc") & (res_df.issuer_type == "(b) School district")]
county_clean = res_df[(res_df.cut == "clean_dc") & (res_df.issuer_type == "(c) County/Parish")]

def eval_hypothesis(s_row, c_row):
    if s_row.empty or c_row.empty:
        return "Cannot evaluate — missing results."
    s, c = s_row.iloc[0], c_row.iloc[0]
    if s["err"] or c["err"]:
        return f"Cannot evaluate — errors in estimation."
    direction_ok = s["beta"] < c["beta"]
    s_sig = s["p"] < 0.10
    c_sig = c["p"] < 0.10
    b_school = f"{s['beta']:+.3f}{stars(s['p'])} (p={s['p']:.3f})"
    b_county = f"{c['beta']:+.3f}{stars(c['p'])} (p={c['p']:.3f})"
    verdict = "CONSISTENT WITH" if direction_ok else "INCONSISTENT WITH"
    return (f"School-district beta = {b_school}; County/Parish beta = {b_county}. "
            f"Direction {verdict} hypothesis (school more negative than county). "
            f"School-district estimate {'significant' if s_sig else 'NOT significant'} at 10%.")

lines += [
    "",
    "---",
    "",
    "## F. Pre-specified hypothesis evaluation",
    "",
    "**Prediction:** school-district spread beta more negative than county-government beta if DC property-tax  ",
    "windfall is priced in school/special-district bonds.",
    "",
    f"- **ALL cut:** {eval_hypothesis(school_all, county_all)}",
    f"- **clean_dc cut:** {eval_hypothesis(school_clean, county_clean)}",
    "",
    f"**school_district_cusip6.csv:** {len(cusip_df):,} unique (county_fips, cusip6) pairs across "
    f"{cusip_df.county_fips.nunique()} treated counties — available for secondary-market MSRB run.",
    "",
]

out_text = "\n".join(lines)
(D / "issuer_type_split.md").write_text(out_text)
print("\n" + out_text)
print("\nWrote issuer_type_split.md and school_district_cusip6.csv")
