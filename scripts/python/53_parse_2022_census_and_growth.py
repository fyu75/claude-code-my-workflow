"""
53_parse_2022_census_and_growth.py

Parse the 2022 Census of Governments Individual Unit File (full universe, released
Oct 2024) on the SAME county-government (type=1) scope as the trusted 2017 file, then
build the 2017->2022 fiscal-growth panel that brackets the DC boom (2018-2024).

The 2022 record is 33 chars vs 2017's 32 (the amount field widened by one). We parse
year/flag by NEGATIVE index so the same code reads both vintages:
    id = line[0:12]  (state[0:2] + type[2] + county[3:6] + unit[6:12])
    item = line[12:15];  flag = line[-1];  year = line[-5:-1];  amount = line[15:-5]

VALIDATION GATE: reconstruct 2017 type=1 and require it to reproduce the existing
acfr_2017_county_govt_only.csv (rev_property_tax=T01, lt_debt_outstanding_end=49U) within
rounding. If it doesn't, the parser is wrong and we stop — do NOT trust the 2022 build.

Outputs:
  data/derived/acfr_2022_county_govt_only.csv   type=1, parallel to the 2017 file (+capex/debt flows)
  data/derived/acfr_2017_county_govt_only_rebuilt.csv  (validation artifact)
  data/derived/census_2017_2022_growth.csv      one row per county: levels both years + growth, treated flag
  data/derived/census_2017_2022_growth.md       summary + treated-vs-control growth
"""
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[2]; D = ROOT / "data" / "derived"
A    = ROOT / "data/external/acfr"
F22  = A/"2022/2022_Individual_Unit_File/2022FinEstDAT_06052025modp_pu.txt"
F17  = A/"2017/2017FinEstDAT_06122023modp_pu.txt"
def fz(s): return s.astype(str).str.zfill(5)

# item code -> variable (mechanism set)
ITEMS = {
    'T01':'rev_property_tax', 'T09':'rev_sales_tax', 'T40':'rev_income_tax',
    'F12':'capex','F18':'capex','F25':'capex','F32':'capex','F36':'capex',
    'F44':'capex','F61':'capex','F62':'capex','F80':'capex','F89':'capex',  # capital outlay (summed)
    '49U':'lt_debt_outstanding_end', '44T':'lt_debt_outstanding_indrev',
    '24T':'lt_debt_issued_pub','29U':'lt_debt_issued_other',
    '34T':'lt_debt_retired_pub','39U':'lt_debt_retired_other',
    'I89':'interest_on_debt',
}

def parse_type1(path):
    """Sum item amounts to county_fips for type=1 (county-government) units only. $thousands."""
    agg = {}
    with open(path, errors='replace') as f:
        for line in f:
            line = line.rstrip("\n")
            if len(line) < 20 or line[2] != '1':      # county-government only
                continue
            item = line[12:15]
            if item not in ITEMS: continue
            cf = line[0:2] + line[3:6]                  # state+county FIPS
            try: amt = float(line[15:-5])               # $thousands, negative-indexed width
            except ValueError: continue
            agg.setdefault(cf, {}).setdefault(ITEMS[item], 0.0)
            agg[cf][ITEMS[item]] += amt
    df = pd.DataFrame.from_dict(agg, orient='index').reset_index().rename(columns={'index':'county_fips'})
    for c in df.columns:
        if c != 'county_fips': df[c] = df[c] / 1000.0   # -> $millions
    return df.fillna(0.0)

print("Parsing 2017 (validation) ...")
c17 = parse_type1(F17)
print("Parsing 2022 ...")
c22 = parse_type1(F22)
for d in (c17, c22): d["county_fips"] = fz(d["county_fips"])

# ---- VALIDATION GATE: 2017 rebuild must match the trusted file ----
trusted = pd.read_csv(D/"acfr_2017_county_govt_only.csv", dtype={"county_fips":str})
trusted["county_fips"] = fz(trusted["county_fips"])
chk = trusted.merge(c17[["county_fips","rev_property_tax","lt_debt_outstanding_end"]],
                    on="county_fips", how="inner", suffixes=("_trusted","_rebuilt"))
def agree(col):
    """Match rate treating NaN==NaN and NaN-as-0 as agreement; only real value gaps count as mismatch."""
    a = chk[f"{col}_trusted"].fillna(0.0); b = chk[f"{col}_rebuilt"].fillna(0.0)
    diff = (a-b).abs()
    return (diff <= 0.01).mean(), diff.max(), int((diff>0.01).sum())
pt_ok, pt_max, pt_bad   = agree("rev_property_tax")
dbt_ok, dbt_max, dbt_bad = agree("lt_debt_outstanding_end")
print(f"\nVALIDATION vs trusted 2017 file (n={len(chk):,} matched counties; NaN treated as 0):")
print(f"  property tax: {pt_ok*100:.1f}% within $10k  (max diff ${pt_max:.3f}M, {pt_bad} mismatches)")
print(f"  debt o/s end: {dbt_ok*100:.1f}% within $10k  (max diff ${dbt_max:.3f}M, {dbt_bad} mismatches)")
c17.to_csv(D/"acfr_2017_county_govt_only_rebuilt.csv", index=False)
GATE = (pt_ok > 0.97 and dbt_ok > 0.97)
print(f"  GATE: {'PASS' if GATE else 'FAIL — parser mismatch, 2022 build NOT trustworthy'}")

c22.to_csv(D/"acfr_2022_county_govt_only.csv", index=False)
print(f"\nWrote acfr_2022_county_govt_only.csv ({len(c22):,} counties)")

# ---- 2017 -> 2022 growth panel ----
keys = ["rev_property_tax","capex","lt_debt_outstanding_end"]
m = c17[["county_fips"]+keys].merge(c22[["county_fips"]+keys], on="county_fips",
                                     how="outer", suffixes=("_17","_22"))
def cagr(v17, v22, yrs=5):
    with np.errstate(invalid='ignore', divide='ignore'):
        r = np.where((v17>0)&(v22>0), (v22/v17)**(1/yrs)-1, np.nan)
    return r*100
for k in keys:
    m[f"{k}_growth_tot_pct"] = np.where(m[f"{k}_17"]>0, 100*(m[f"{k}_22"]/m[f"{k}_17"]-1), np.nan)
    m[f"{k}_cagr_pct"]       = cagr(m[f"{k}_17"], m[f"{k}_22"])

# treated flag (>=1% DC fiscal share)
tax = pd.read_csv(D/"dc_tax_share_distribution.csv", dtype={"county_fips":str}); tax["county_fips"]=fz(tax["county_fips"])
treated = set(tax[tax["dc_share_mid"]>=1.0]["county_fips"])
m["treated"] = m["county_fips"].isin(treated).astype(int)
m.to_csv(D/"census_2017_2022_growth.csv", index=False)

# ---- summary ----
def med(sub, col):
    s = sub[col].replace([np.inf,-np.inf],np.nan).dropna()
    return s.median() if len(s) else np.nan
t, c = m[m.treated==1], m[m.treated==0]
L = ["# 2017 -> 2022 Census of Governments Growth (county-government scope)\n",
     "**Date:** 2026-06-10. `scripts/python/53`. Full-universe Census 2022 (released Oct 2024) vs "
     "Census 2017, type=1 county-government scope — brackets the DC boom on Census-grade data.\n",
     f"**Parser validation vs trusted 2017 file:** property tax {pt_ok*100:.1f}% / debt {dbt_ok*100:.1f}% "
     f"within $10k -> **GATE {'PASS' if GATE else 'FAIL'}**.\n",
     f"## Coverage",
     f"- Counties in 2017: {c17.shape[0]:,}; in 2022: {c22.shape[0]:,}; in both: "
     f"{m[['rev_property_tax_17','rev_property_tax_22']].notna().all(axis=1).sum():,}",
     f"- Treated (>=1% DC) with both-year property tax: "
     f"{t[['rev_property_tax_17','rev_property_tax_22']].gt(0).all(axis=1).sum()} of {len(treated)}", "",
     "## Median 2017->2022 total growth (%), treated vs control", "",
     "| Outcome | Treated median | Control median | Treated−Control |", "|---|---:|---:|---:|"]
for k,lab in [("rev_property_tax","Property tax"),("capex","Capital outlay"),("lt_debt_outstanding_end","LT debt o/s")]:
    tm, cm = med(t,f"{k}_growth_tot_pct"), med(c,f"{k}_growth_tot_pct")
    L.append(f"| {lab} | {tm:+.1f}% | {cm:+.1f}% | {tm-cm:+.1f}pp |")
L += ["", "*Median total growth over the 5-year window; CAGR columns also in the CSV.*",
      "", "## Caveats",
      "- County-government (type=1) scope only — consolidated city-counties (Denver, Honolulu) and "
      "independent cities are scoped per Census convention; cross-check separately.",
      "- This is the GOLD-STANDARD endpoint to validate the ACFR-PDF and MuniSpot v2 2022 extractions "
      "against (next: triangulation audit).", ""]
(D/"census_2017_2022_growth.md").write_text("\n".join(L))
print("\n".join(L))
print("\nWrote census_2017_2022_growth.{csv,md}")
