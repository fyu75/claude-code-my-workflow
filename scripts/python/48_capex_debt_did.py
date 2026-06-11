"""
48_capex_debt_did.py

Matched DiD on the CAPEX and DEBT-SERVICE channels, reusing the locked 101-treated /
1:3 division-matched sample (script 45 `division_matched_pairs.csv`) and the same
estimators as the property-tax DiD (script 46). Outcomes come from script 47.

Outcomes (per county; "change" = post-window mean - baseline-window mean of the intensity):
  capex_share_chg    change in capex / total-expenditure         (H1: new roads & schools)
  ds_burden_chg      change in debt service / total-revenue       (debt burden)
  newdebt_share_chg  change in new borrowing / total-expenditure  (financing the build-out)
  capex_level_cagr   annualized growth of $ capex (gated)         (secondary, lumpy)

Estimators (per outcome): (1) matched-pair effect = outcome_treated - mean(outcome controls),
one-sample t / Wilcoxon / sign / bootstrap; (2) pair-stacked OLS, SEs clustered on county;
(3) unique-county OLS, state FE, HC1. Robustness: STATE-ONLY pairs, ESC-DROPPED treated.

Output: data/derived/capex_debt_did_results.md
"""
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[2]; D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)
rng = np.random.default_rng(20260516)
ESC_STATES = {"01","21","28","47"}

# ---- outcomes (script 47) ----
oc = pd.read_csv(D/"capex_debt_county_outcomes.csv", dtype={"county_fips":str})
oc["county_fips"] = fz(oc["county_fips"])
OUTCOMES = {
    "capex_share_chg":   "Capex intensity change (capital outlay / total expenditure)",
    "ds_burden_chg":     "Debt-service burden change ((principal+interest) / total revenue)",
    "newdebt_share_chg": "New-borrowing intensity change (proceeds from capital debt / total exp)",
    "capex_level_cagr":  "Capex level CAGR (secondary, lumpy)",
}
VAL = {o: dict(zip(oc["county_fips"], oc[o])) for o in OUTCOMES}
def val(o, f):
    v = VAL[o].get(f);  return None if v is None or (isinstance(v,float) and np.isnan(v)) else float(v)

# ---- matched pairs (script 45) ----
P = pd.read_csv(D/"division_matched_pairs.csv")
P["treated_fips"] = fz(P["treated_fips"].astype(int).astype(str))
P["control_fips"] = fz(P["control_fips"].astype(int).astype(str))
P["treated_state"] = P["treated_fips"].str[:2]


def matched_effects(pairs, o):
    rows = []
    for t, grp in pairs.groupby("treated_fips"):
        vt = val(o, t)
        if vt is None: continue
        ctrls = [val(o, c) for c in grp["control_fips"].unique()]
        ctrls = [x for x in ctrls if x is not None]
        if not ctrls: continue
        rows.append({"treated_fips": t, "state": t[:2], "effect": vt - float(np.mean(ctrls)),
                     "v_treated": vt})
    return pd.DataFrame(rows)

def effect_block(eff_df, title, pct):
    out = [f"### {title}", ""]
    if len(eff_df) < 3:
        return out + [f"- too few usable treated ({len(eff_df)})", ""]
    eff = eff_df["effect"].to_numpy()
    sc = 100 if pct else 1; unit = "pp" if pct else ""
    tp = stats.ttest_1samp(eff, 0).pvalue
    wp = stats.wilcoxon(eff).pvalue if np.any(eff != 0) else np.nan
    npos = int((eff > 0).sum()); sp = stats.binomtest(npos, len(eff), 0.5).pvalue
    boot = [rng.choice(eff, len(eff), replace=True).mean() for _ in range(10000)]
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return out + [
        f"- N treated (matched): **{len(eff)}**",
        f"- Matched effect mean **{eff.mean()*sc:+.3f}{unit}** (t p={tp:.4f}); median {np.median(eff)*sc:+.3f}{unit}",
        f"- Wilcoxon p={wp:.4f}; sign {npos}/{len(eff)} positive (p={sp:.4f})",
        f"- Bootstrap 95% CI [{lo*sc:+.3f}, {hi*sc:+.3f}]{unit}", ""]

def stacked_ols(pairs, o):
    recs = []
    for _, r in pairs.iterrows():
        for f, tr in ((r["treated_fips"],1),(r["control_fips"],0)):
            v = val(o, f)
            if v is not None: recs.append({"county_fips":f,"y":v,"is_treated":tr,"state_fips":f[:2]})
    df = pd.DataFrame(recs)
    if df.empty or df["is_treated"].nunique()<2: return None
    fit = smf.ols("y ~ is_treated + C(state_fips)", data=df).fit(
        cov_type="cluster", cov_kwds={"groups": df["county_fips"]})
    return fit, int(fit.nobs), df["county_fips"].nunique()

def unique_ols(pairs, o):
    t_set=set(pairs["treated_fips"]); c_set=set(pairs["control_fips"])-t_set
    recs=[]
    for f in t_set:
        v=val(o,f);  recs.append({"county_fips":f,"y":v,"is_treated":1,"state_fips":f[:2]}) if v is not None else None
    for f in c_set:
        v=val(o,f);  recs.append({"county_fips":f,"y":v,"is_treated":0,"state_fips":f[:2]}) if v is not None else None
    df=pd.DataFrame(recs)
    if df.empty or df["is_treated"].nunique()<2: return None
    fit=smf.ols("y ~ is_treated + C(state_fips)", data=df).fit(cov_type="HC1")
    return fit, int(fit.nobs)

def ols_line(label, res, pct):
    if res is None: return f"- {label}: insufficient variation"
    fit, n, *rest = res; sc = 100 if pct else 1; unit = "pp" if pct else ""
    b=fit.params["is_treated"]*sc; se=fit.bse["is_treated"]*sc; p=fit.pvalues["is_treated"]
    tail=f", clusters={rest[0]}" if rest else ""
    return f"- {label}: treated coef **{b:+.3f}{unit}** (SE {se:.3f}, p={p:.4f}), N={n}{tail}"


L = ["# Capex & Debt-Service Matched DiD (V2 all-funds)\n",
     "**Date:** 2026-06-10. Same 101-treated / 1:3 division-matched sample as the property-tax "
     "DiD (script 46); outcomes = change in capex/debt INTENSITY from v2 all-funds (script 47). "
     "Intensities are unit-free (cancel v2's x1000 errors) and window-averaged (smooth capex "
     "lumpiness). Debt = flows only (v2 carries no long-term debt stock).\n",
     "Positive capex / new-borrowing effect = DC counties invest & finance more; positive "
     "debt-service-burden effect = they carry more debt service (could be GOOD — funding the "
     "build-out — or a strain; read alongside capex).\n"]

P_state = P[P["match_tier"]=="state"]
P_noesc = P[~P["treated_state"].isin(ESC_STATES)]

for o, lab in OUTCOMES.items():
    pct = (o != "capex_level_cagr")   # ratios reported in pp; CAGR already a rate -> also pp-style
    pct = True
    L += [f"\n## {lab}", ""]
    L += ["**(1) Matched-pair effect**", ""]
    L += effect_block(matched_effects(P, o),        "FULL (state + division)", pct)
    L += effect_block(matched_effects(P_state, o),  "STATE-ONLY", pct)
    L += effect_block(matched_effects(P_noesc, o),  "ESC-DROPPED", pct)
    L += ["**(2) Pair-stacked OLS, clustered on county**", ""]
    L += [ols_line("FULL", stacked_ols(P, o), pct),
          ols_line("STATE-ONLY", stacked_ols(P_state, o), pct),
          ols_line("ESC-DROPPED", stacked_ols(P_noesc, o), pct), ""]
    L += ["**(3) Unique-county OLS, state FE, HC1**", ""]
    L += [ols_line("FULL", unique_ols(P, o), pct), ""]

L += ["## Reading guide",
      "- Capex/debt intensities are shares, so effects are in **percentage points of the share** "
      "(e.g. +1.0pp capex_share = capital outlay rises by 1% of total expenditure relative to controls).",
      "- The matched-pair effect (1) is the headline; the county-clustered OLS (2) is the preferred "
      "inferential spec (controls reused up to ~8x). STATE-ONLY and ESC-DROPPED are the same two "
      "robustness probes as the property-tax DiD.",
      "- Coverage is far better than property tax (capex ~1,041, debt-service ~1,431 counties "
      "nationally) because these are clean GASB expenditure lines, not bundled tax lines.", ""]

(D/"capex_debt_did_results.md").write_text("\n".join(L))
print("\n".join(L))
print("Wrote data/derived/capex_debt_did_results.md")
