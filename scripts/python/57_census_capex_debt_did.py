"""
57_census_capex_debt_did.py

Rescue the capex & debt channels on the FULL Census 2022 universe. The MuniSpot-v2 capex
DiD was underpowered (N=41, "no usable signal") and gave only debt FLOWS (no stock).
Census 2022 gives clean both-year CAPITAL OUTLAY (ΣF-codes) for 93 treated and DEBT
OUTSTANDING STOCK (49U) for 97 treated — 2× the MuniSpot coverage, and a real debt STOCK
MuniSpot never had.

Design: REUSE the validated script-56 matched pairs (full_universe_matched_pairs.csv —
vetted treated × full clean Census controls, caliper-matched on baseline property tax).
Just swap the outcome to capex / debt. Mirror script 56's matched-pair estimator.

Outcomes (2017->2022): total % growth (winsorized p1/p99) and $M level change, for
  - capex (capital outlay)
  - lt_debt_outstanding_end (debt stock)
Plus intensity proxies scaled by property tax (capex-per-$PT, debt-per-$PT change), since
property tax is the one clean total we have.

Output: data/derived/census_capex_debt_did_results.md
"""
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]; D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)
rng = np.random.default_rng(20260516)

g = pd.read_csv(D/"census_2017_2022_growth.csv", dtype={"county_fips":str}); g["county_fips"]=fz(g["county_fips"])
# intensity proxies: capex/PT and debt/PT, change 2017->2022 (pp of property tax)
for k in ["capex","lt_debt_outstanding_end"]:
    g[f"{k}_perPT_17"] = np.where(g["rev_property_tax_17"]>0, g[f"{k}_17"]/g["rev_property_tax_17"], np.nan)
    g[f"{k}_perPT_22"] = np.where(g["rev_property_tax_22"]>0, g[f"{k}_22"]/g["rev_property_tax_22"], np.nan)
    g[f"{k}_perPT_chg"] = g[f"{k}_perPT_22"] - g[f"{k}_perPT_17"]
    g[f"{k}_lvl_chg"]   = g[f"{k}_22"] - g[f"{k}_17"]

P = pd.read_csv(D/"full_universe_matched_pairs.csv")
P["treated_fips"]=fz(P["treated_fips"].astype(int).astype(str)); P["control_fips"]=fz(P["control_fips"].astype(int).astype(str))

def col(name): return dict(zip(g["county_fips"], g[name]))

def matched_pair(outcome, winsor=False):
    M = col(outcome)
    if winsor:
        vals = pd.Series(list(M.values())).replace([np.inf,-np.inf],np.nan).dropna()
        lo,hi = np.percentile(vals,[1,99])
        M = {k:(np.nan if pd.isna(v) else min(max(v,lo),hi)) for k,v in M.items()}
    eff=[]
    for t,grp in P.groupby("treated_fips"):
        dt = M.get(t)
        if dt is None or pd.isna(dt): continue
        dc = [M.get(c) for c in grp["control_fips"] if M.get(c) is not None and not pd.isna(M.get(c))]
        if not dc: continue
        eff.append(dt - np.mean(dc))
    eff=np.array(eff)
    if len(eff)<5: return None
    boot=[rng.choice(eff,len(eff),replace=True).mean() for _ in range(10000)]
    lo,hi=np.percentile(boot,[2.5,97.5])
    nneg=int((eff<0).sum())
    return dict(n=len(eff), mean=eff.mean(), median=np.median(eff),
                tp=stats.ttest_1samp(eff,0).pvalue, wp=stats.wilcoxon(eff).pvalue,
                npos=len(eff)-nneg, ci=(lo,hi),
                sp=stats.binomtest(len(eff)-nneg,len(eff),0.5).pvalue)

def line(label, r, unit):
    if r is None: return f"| {label} | too few | — | — | — | — |"
    sig="***" if r['tp']<0.01 else "**" if r['tp']<0.05 else "*" if r['tp']<0.10 else ""
    return (f"| {label} | **{r['mean']:+.2f}{unit}{sig}** | {r['median']:+.2f} | t={r['tp']:.3f} / W={r['wp']:.3f} | "
            f"[{r['ci'][0]:+.2f},{r['ci'][1]:+.2f}] | {r['npos']}/{r['n']} pos |")

L=["# Census 2022 Capex & Debt DiD (full-universe matched, channel rescue)\n",
   "**Date:** 2026-06-10. `scripts/python/57`. Reuses the script-56 validated matched pairs "
   "(vetted treated × full clean Census controls); swaps outcome to capex / debt. Mirrors the "
   "script-56 matched-pair estimator. **Negative debt effect = DC counties deleverage MORE; "
   "positive capex = invest MORE.**\n",
   "| Outcome (matched-pair, treated − controls) | Mean effect | Median | t / Wilcoxon p | Boot 95% CI | sign |",
   "|---|---:|---:|---:|---:|---:|"]
L+=[line("Capex — % growth (winsorized)",          matched_pair("capex_growth_tot_pct", winsor=True), "pp")]
L+=[line("Capex — $M level change",                matched_pair("capex_lvl_chg"),                     "$M")]
L+=[line("Capex/PT intensity — change (pp of PT)", matched_pair("capex_perPT_chg"),                   "pp")]
L+=[line("Debt o/s — % growth (winsorized)",       matched_pair("lt_debt_outstanding_end_growth_tot_pct", winsor=True), "pp")]
L+=[line("Debt o/s — $M level change",             matched_pair("lt_debt_outstanding_end_lvl_chg"),   "$M")]
L+=[line("Debt/PT intensity — change (pp of PT)",  matched_pair("lt_debt_outstanding_end_perPT_chg"), "pp")]
L+=["", "## Reading guide",
    "- Coverage: 93 treated have both-year Census capex, 97 have debt o/s (vs MuniSpot capex N=41).",
    "- Compare to MuniSpot (scripts 47/48): capex 'no usable signal' (N=41); debt-service-burden clean NULL. "
    "Census adds a debt STOCK test MuniSpot couldn't do.",
    "- Property-tax-scaled intensity uses the one clean total we have; a full capex/totexp ratio needs "
    "total-expenditure parsing (enhancement).",
    "- Winsorized at p1/p99 (capex % growth is lumpy); median + sign test are the robust reads.", ""]
(D/"census_capex_debt_did_results.md").write_text("\n".join(L))
print("\n".join(L))
print("\nWrote census_capex_debt_did_results.md")
