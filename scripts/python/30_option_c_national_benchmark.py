"""
30_option_c_national_benchmark.py

Option C: 2017→latest within-county growth for treated DC counties,
benchmarked against US state-and-local nominal CAGR.

Outcomes:
  - Property tax revenue
  - Capital outlay (capex_total = sum of capex_* lines)
  - Long-term debt outstanding

(Total revenue dropped — Census ASLGF rev_* line items omit charges/fees,
so they systematically undercount and produce inflated growth rates vs PDF.)

Benchmark CAGRs (2017→2024, 7 years, nominal):
  Property tax:    5.85%  (BEA NIPA 3.21; Census ASLGF historical)
  Capital outlay:  5.07%  (BEA NIPA 3.21 state & local gross investment)
  Debt outstanding 1.74%  (Census state & local debt outstanding)

For each treated county we compute:
  treated CAGR = (latest / 2017_baseline) ^ (1/years) - 1
  excess CAGR  = treated CAGR - benchmark CAGR

A positive excess means the county grew its fiscal aggregate faster than
the national state+local trend.

Outputs:
  data/derived/option_c_excess_growth.csv
  data/derived/option_c_summary.md
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DERIVED = ROOT / "data" / "derived"

BENCHMARK_CAGR = {
    # Property tax: median per-county nominal CAGR (BLS/Census ASLGF; the
    # 5.85% BEA aggregate is dominated by big-state appreciation and is
    # not the right "typical-county" benchmark).
    "property_tax":         0.0340,
    "capital_outlay":       0.0507,
    "lt_debt_outstanding":  0.0174,
}

# Counties flagged as unreliable in prior session:
#  - Mecklenburg VA: 2023 PDF is county-government scope while Census 2017
#    re-aggregation might include consolidated entities (unit mismatch)
#  - Pecos / Ward / Crane TX: small oil counties whose 2017→2024 trajectory
#    is dominated by the 2014-16 oil price collapse, NOT DC investment.
#    Property tax declines of 20-30% reflect oil & gas mineral interest
#    valuation drop unrelated to data centers.
#  - Glasscock / Briscoe / Knox TX: tiny counties with patchy PDF data;
#    extracted values likely reflect parsing errors (shared 5.5M total
#    revenue values across multiple counties = a known parser bug).
UNRELIABLE_TREATED = {
    "51117",   # Mecklenburg VA (unit mismatch)
    "48371",   # Pecos TX (oil collapse)
    "48475",   # Ward TX (oil collapse)
    "48103",   # Crane TX (oil collapse)
    "48173",   # Glasscock TX (suspected parser dup)
    "48045",   # Briscoe TX (suspected parser dup)
}
OUTCOME_LABELS = {
    "property_tax":         "Property tax revenue",
    "capital_outlay":       "Capital outlay (capex)",
    "lt_debt_outstanding":  "Long-term debt outstanding",
}

# 1) 2017 county-government-only baselines (re-aggregate from long file)
print("Building 2017 baselines from acfr_2017_long.csv ...")
long_df = pd.read_csv(DERIVED / "acfr_2017_long.csv", low_memory=False)
long_df["county_fips"] = long_df["county_fips"].astype(str).str.zfill(5)
long_df["type"] = long_df["type"].astype(int)
cg = long_df[long_df["type"] == 1]   # county-government records only

# property_tax: rev_property_tax line per county
pt_2017 = (
    cg[cg["var_name"] == "rev_property_tax"]
    .groupby("county_fips")["amount_millions"].sum()
    .rename("property_tax_2017_M")
)

# capital_outlay: sum of capex_* lines per county
capex_lines = cg["var_name"].str.startswith("capex_", na=False)
co_2017 = (
    cg.loc[capex_lines]
    .groupby("county_fips")["amount_millions"].sum()
    .rename("capital_outlay_2017_M")
)

# debt outstanding (end of year): lt_debt_outstanding_end per county
debt_2017 = (
    cg[cg["var_name"] == "lt_debt_outstanding_end"]
    .groupby("county_fips")["amount_millions"].sum()
    .rename("lt_debt_outstanding_2017_M")
)

baselines = pd.concat([pt_2017, co_2017, debt_2017], axis=1).reset_index()
print(f"  Baselines built for {len(baselines)} counties")
print(baselines.describe())

# 2) Latest PDF extraction per treated county per outcome
ext = pd.read_csv(DERIVED / "acfr_county_year_extracted_wide.csv")
ext["county_fips"] = ext["county_fips"].astype(str).str.zfill(5)
ext["fy"] = ext["fy"].astype(int)

# Convert PDF values from dollars to millions to match baselines
out_map = {
    "property_tax":        "property_tax_2017_M",
    "capital_outlay":      "capital_outlay_2017_M",
    "lt_debt_outstanding": "lt_debt_outstanding_2017_M",
}

records = []
for fips, g in ext.groupby("county_fips"):
    base = baselines[baselines["county_fips"] == fips]
    if base.empty:
        continue
    state = g["state"].iloc[0]
    name  = g["county_name"].iloc[0]
    row = {"county_fips": fips, "county_name": name, "state": state}
    for outcome, base_col in out_map.items():
        baseline_M = base[base_col].iloc[0]
        mask = g[outcome].notna() & (g[outcome] > 0)
        if not mask.any() or pd.isna(baseline_M) or baseline_M <= 0:
            row[f"{outcome}_excess"] = np.nan
            continue
        sub = g.loc[mask].sort_values("fy").tail(1).iloc[0]
        latest_M = sub[outcome] / 1e6       # PDF in dollars → millions
        years = sub["fy"] - 2017
        if years < 1:
            continue
        treated_cagr = (latest_M / baseline_M) ** (1 / years) - 1
        excess       = treated_cagr - BENCHMARK_CAGR[outcome]
        row[f"{outcome}_baseline_M"] = baseline_M
        row[f"{outcome}_latest_M"]   = latest_M
        row[f"{outcome}_year"]       = sub["fy"]
        row[f"{outcome}_cagr"]       = treated_cagr
        row[f"{outcome}_excess"]     = excess
    records.append(row)

df = pd.DataFrame(records)
df.to_csv(DERIVED / "option_c_excess_growth.csv", index=False)
print(f"\nWrote option_c_excess_growth.csv: {len(df)} treated counties")

# 3) Summary stats per outcome
def t_test_one_sided(x):
    """One-sided t-test: H0 mean<=0 vs H1 mean>0."""
    from scipy import stats
    x = pd.Series(x).dropna().values
    if len(x) < 3:
        return np.nan, np.nan, np.nan, np.nan
    t, p_two = stats.ttest_1samp(x, 0)
    p_one = p_two / 2 if t > 0 else 1 - p_two / 2
    return len(x), x.mean(), t, p_one

df_full  = df
df_clean = df[~df["county_fips"].isin(UNRELIABLE_TREATED)]

def summarize(d, label):
    print(f"\n=== {label} (N total = {len(d)}) ===")
    print(f"{'Outcome':<32} {'N':>4} {'mean excess':>13} {'t-stat':>8} {'p (1-sided)':>12}")
    print("-"*72)
    rows = []
    for outcome in BENCHMARK_CAGR:
        col = f"{outcome}_excess"
        if col not in d.columns:
            continue
        n, m, t, p = t_test_one_sided(d[col])
        lab = OUTCOME_LABELS[outcome]
        print(f"{lab:<32} {n:>4} {m*100:>12.2f}% {t:>8.2f} {p:>12.4f}")
        rows.append((lab, n, m, t, p, BENCHMARK_CAGR[outcome]))
    return rows

full_rows  = summarize(df_full,  "FULL SAMPLE (incl. flagged-unreliable)")
clean_rows = summarize(df_clean, "CLEAN SAMPLE (drop Mecklenburg + TX oil + parser-dup)")

lines = ["# Option C: National-benchmark within-county growth",
         "",
         f"Treated counties extracted: {len(df_full)}; clean sample: {len(df_clean)} "
         f"(dropped {len(UNRELIABLE_TREATED)}: Mecklenburg VA, Pecos/Ward/Crane TX oil counties, Glasscock/Briscoe TX parser-suspected)",
         f"Benchmarks: property tax 3.4% (per-county median); capex 5.07% (BEA aggregate); debt 1.74% (Census ASLGF)",
         "",
         "## Excess CAGR — FULL SAMPLE",
         "",
         f"| Outcome | N | Mean excess | t-stat | p (1-sided) | Benchmark |",
         f"|---|---:|---:|---:|---:|---:|"]
for lab, n, m, t, p, bench in full_rows:
    lines.append(f"| {lab} | {n} | {m*100:.2f}% | {t:.2f} | {p:.4f} | {bench*100:.2f}% |")
lines += ["", "## Excess CAGR — CLEAN SAMPLE",
          "",
          f"| Outcome | N | Mean excess | t-stat | p (1-sided) | Benchmark |",
          f"|---|---:|---:|---:|---:|---:|"]
for lab, n, m, t, p, bench in clean_rows:
    lines.append(f"| {lab} | {n} | {m*100:.2f}% | {t:.2f} | {p:.4f} | {bench*100:.2f}% |")

lines += ["",
          "## Per-county detail",
          "",
          df[[c for c in df.columns
              if c in ("county_fips","county_name","state") or c.endswith("_cagr") or c.endswith("_excess")]]
            .to_markdown(index=False)]

(DERIVED / "option_c_summary.md").write_text("\n".join(lines))
print(f"\nWrote option_c_summary.md")
