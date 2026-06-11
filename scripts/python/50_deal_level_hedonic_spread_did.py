"""
50_deal_level_hedonic_spread_did.py

Deal-level hedonic bond-SPREAD DiD — the referee-grade pricing test, and the proper
resolution of the county-year sign-flip found in scripts 16 vs 49.

Unit          : one muni deal (MASTER_DEAL_NO), spread over matched Treasury (bps).
Sample        : deals from ever-treated counties (DC property-tax share >= 1%, the 125 set)
                + never-DC-host control counties. Same universe as script 16.
Estimand      : treated_post = 1[ county is >=1% DC  AND  year >= its first-DC year ].
Hedonic ctrls : log(years-to-maturity), log(amount). (Rating/coupon deliberately EXCLUDED:
                rating is post-treatment / a bad control; coupon is collinear with spread.)
Fixed effects : county FE  (each county its own pre/post control -> removes the "which control
                group" fragility) + STATE x YEAR FE (differences out the rate cycle / 2022-23
                spread spike that contaminated the county-year design).
Inference     : SEs clustered on county.

Specs:
  A  county FE + year FE,                no hedonic ctrls      (closest to the old TWFE)
  B  county FE + state x year FE,        no hedonic ctrls
  C  county FE + state x year FE,        + hedonic ctrls       <- PREFERRED
  D  spec C on 2015+ issues only         (AI-hyperscale era)

NEGATIVE coefficient = spreads TIGHTEN after DC arrival = cheaper borrowing.

NOTE on estimator: this is two-way-FE generalized DiD. With staggered DC timing and
heterogeneous effects it can be biased (Goodman-Bacon); a Sun-Abraham / CS deal-level
version is the natural follow-up. Reported here first because the immediate question is
whether the -23bps survives bond-composition + rate-cycle controls at all.

Output: data/derived/deal_level_spread_did_results.md
"""
from pathlib import Path
import numpy as np, pandas as pd
import pyfixest as pf

ROOT = Path(__file__).resolve().parents[2]; D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)

# ---- deal-level spreads ----
d = pd.read_csv(D/"sdc_deal_spread.csv")
d["county_fips"] = fz(d["county_fips"].astype(int).astype(str))
d = d.dropna(subset=["spread_bps","par_wtd_yrs2mat","AMT"]).copy()
d = d[(d["par_wtd_yrs2mat"] > 0) & (d["AMT"] > 0)]

# ---- treatment universe + timing (from the main panel) ----
pan = pd.read_csv(D/"county_year_panel_v4.csv", dtype={"county_fips":str})
pan["county_fips"] = fz(pan["county_fips"])
g_map = pan.dropna(subset=["first_dc_year"]).groupby("county_fips")["first_dc_year"].min().astype(int)
never_host = pan.groupby("county_fips")["n_dc_cumulative"].max().pipe(lambda s: set(s[s==0].index))

tax = pd.read_csv(D/"dc_tax_share_distribution.csv", dtype={"county_fips":str})
tax["county_fips"] = fz(tax["county_fips"])
treated_set = set(tax[tax["dc_share_mid"] >= 1.0]["county_fips"])

# restrict to treated (>=1%) ∪ never-host
d = d[d["county_fips"].isin(treated_set | never_host)].copy()
d["treated_ever"] = d["county_fips"].isin(treated_set).astype(int)
d["g"] = d["county_fips"].map(g_map)
d["post"] = ((d["treated_ever"]==1) & (d["year"] >= d["g"])).astype(int)
d["treated_post"] = d["post"]                       # =1 only for treated counties after their DC year
d["state_year"] = d["STATECODE"].astype(str) + "_" + d["year"].astype(str)
d["log_mat"] = np.log(d["par_wtd_yrs2mat"])
d["log_amt"] = np.log(d["AMT"])

n_treated = d.loc[d["treated_ever"]==1,"county_fips"].nunique()
n_ctrl    = d.loc[d["treated_ever"]==0,"county_fips"].nunique()
n_post    = int(d["treated_post"].sum())

L = ["# Deal-Level Hedonic Bond-Spread DiD\n",
     "**Date:** 2026-06-10. Referee-grade pricing test; resolves the county-year sign-flip "
     "(script 16 CS −23bps vs script 49 matched +21bps). `scripts/python/50`.\n",
     "Unit = muni deal; outcome = spread over matched Treasury (bps). **Negative = tighten = "
     "cheaper borrowing.** treated_post = county is ≥1% DC and year ≥ its first-DC year. "
     "Hedonic ctrls = log(maturity), log(amount); rating/coupon excluded (bad control / collinear). "
     "County FE + state×year FE; SEs clustered on county.\n",
     f"## Sample",
     f"- Deals: **{len(d):,}** | treated-county deals {int((d['treated_ever']==1).sum()):,}, "
     f"control-county deals {int((d['treated_ever']==0).sum()):,}",
     f"- Counties: {n_treated} treated (≥1% DC), {n_ctrl} never-DC-host controls",
     f"- Post (treated × after DC year) deals: {n_post:,}",
     f"- Years: {int(d['year'].min())}–{int(d['year'].max())}", ""]

def run(formula, data, label):
    m = pf.feols(formula, data=data, vcov={"CRV1": "county_fips"})
    b = m.coef()["treated_post"]; se = m.se()["treated_post"]; p = m.pvalue()["treated_post"]
    n = int(m._N)
    sig = "***" if p<0.01 else "**" if p<0.05 else "*" if p<0.10 else ""
    return f"| {label} | **{b:+.2f}{sig}** | {se:.2f} | {p:.4f} | {n:,} |"

L += ["## Results — coefficient on treated_post (bps)", "",
      "| Spec | β (spread, bps) | SE | p | N deals |", "|---|---:|---:|---:|---:|"]
L += [run("spread_bps ~ treated_post | county_fips + year",                         d,           "A. county + year FE")]
L += [run("spread_bps ~ treated_post | county_fips + state_year",                   d,           "B. county + state×year FE")]
L += [run("spread_bps ~ treated_post + log_mat + log_amt | county_fips + state_year", d,         "C. + hedonic ctrls (PREFERRED)")]
L += [run("spread_bps ~ treated_post + log_mat + log_amt | county_fips + state_year", d[d["year"]>=2015], "D. spec C, 2015+ issues")]
L += ["", "*Stars: \\*\\*\\* p<0.01, \\*\\* p<0.05, \\* p<0.10.*", ""]

L += ["## Reading guide",
      "- Compare to: CS-vs-never-treated county-year (script 16) **−23.4 bps** (p<0.10); "
      "matched county-year (script 49) **+21 bps mean / ≈0 median** (no clear effect).",
      "- Spec C is preferred: bond composition controlled, rate cycle absorbed by state×year FE, "
      "county is its own pre/post control (no dependence on a chosen control group).",
      "- If C is negative & significant → the credit-quality repricing survives and the pricing "
      "channel is real. If C is ≈0 / wrong-signed → the −23bps was a composition/control-group "
      "artifact and the pricing channel is not established.",
      "- Caveat: TWFE generalized DiD; staggered timing + heterogeneity → a Sun-Abraham/CS "
      "deal-level version is the next robustness step.", ""]

(D/"deal_level_spread_did_results.md").write_text("\n".join(L))
print("\n".join(L))
print("Wrote data/derived/deal_level_spread_did_results.md")
