"""
49_matched_spread_did.py

Re-run the BOND-SPREAD outcome on the SAME 1:3 division-matched sample as the
property-tax DiD (script 46), so the pricing result and the property-tax result
share one identification strategy (matched-pair difference, not CS-vs-never-treated).

Design (parallel to script 46, event-aligned for staggered DC timing):
  - For each treated county t with first-DC year g_t, define
        pre-spread  = mean par_wtd_spread_bps over years < g_t
        post-spread = mean par_wtd_spread_bps over years >= g_t
        d_spread_t  = post - pre                       (NEGATIVE = spread TIGHTENED)
  - Each matched control uses ITS MATCHED TREATED's g_t for the same pre/post split,
    so treated and control are differenced over the identical calendar window.
  - Matched-pair effect = d_spread_treated - mean(d_spread of its matched controls).
    NEGATIVE effect = DC counties' spreads tightened relative to matched controls.

Estimators + robustness identical to script 46:
  (1) matched-pair effect (t / Wilcoxon / sign / bootstrap)
  (2) pair-stacked OLS, SEs clustered on county
  (3) unique-county OLS, state FE, HC1
  robustness: STATE-ONLY pairs, ESC-DROPPED treated.

Sparsity note: a county contributes a pre/post mean only in years it came to market with
a Treasury-benchmarked deal; counties lacking either a pre or a post spread drop out.

Output: data/derived/matched_spread_did_results.md
        data/derived/matched_spread_did_pairs_resolved.csv
"""
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[2]; D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)
rng = np.random.default_rng(20260516)
ESC_STATES = {"01","21","28","47"}

# ---- panel with annual par-weighted spread + DC timing ----
pan = pd.read_csv(D/"county_year_panel_v4.csv", dtype={"county_fips":str})
pan["county_fips"] = fz(pan["county_fips"])
sp = pan.dropna(subset=["par_wtd_spread_bps"])[["county_fips","year","par_wtd_spread_bps"]]
# first_dc_year per county (treated only); take min observed
g_map = (pan.dropna(subset=["first_dc_year"]).groupby("county_fips")["first_dc_year"].min().astype(int).to_dict())

def pre_post_change(fips, g):
    """mean post-spread minus mean pre-spread for `fips`, split at year g. None if either side empty."""
    s = sp[sp["county_fips"]==fips]
    pre = s[s["year"] <  g]["par_wtd_spread_bps"]
    post= s[s["year"] >= g]["par_wtd_spread_bps"]
    if len(pre)==0 or len(post)==0: return None
    return float(post.mean() - pre.mean())

# ---- matched pairs (script 45) ----
P = pd.read_csv(D/"division_matched_pairs.csv")
P["treated_fips"] = fz(P["treated_fips"].astype(int).astype(str))
P["control_fips"] = fz(P["control_fips"].astype(int).astype(str))
P["treated_state"] = P["treated_fips"].str[:2]
P = P[P["treated_fips"].isin(g_map)].copy()           # treated must have a DC year
P["g"] = P["treated_fips"].map(g_map)

# precompute treated change (per treated) and control change (per pair, at treated's g)
P["d_treated"] = [pre_post_change(t, g) for t, g in zip(P["treated_fips"], P["g"])]
P["d_control"] = [pre_post_change(c, g) for c, g in zip(P["control_fips"], P["g"])]


def matched_effects(pairs):
    rows = []
    for t, grp in pairs.groupby("treated_fips"):
        dt = grp["d_treated"].iloc[0]
        if dt is None or pd.isna(dt): continue
        dctrl = [x for x in grp["d_control"].tolist() if x is not None and pd.notna(x)]
        if not dctrl: continue
        rows.append({"treated_fips": t, "state": t[:2], "g": int(grp["g"].iloc[0]),
                     "d_treated": dt, "d_ctrl_mean": float(np.mean(dctrl)),
                     "n_ctrl": len(dctrl), "effect": dt - float(np.mean(dctrl))})
    return pd.DataFrame(rows)

def effect_block(eff_df, title):
    out = [f"### {title}", ""]
    if len(eff_df) < 3: return out + [f"- too few usable treated ({len(eff_df)})", ""]
    eff = eff_df["effect"].to_numpy()
    tp = stats.ttest_1samp(eff, 0).pvalue
    wp = stats.wilcoxon(eff).pvalue
    nneg = int((eff < 0).sum()); sp_ = stats.binomtest(nneg, len(eff), 0.5).pvalue
    boot = [rng.choice(eff, len(eff), replace=True).mean() for _ in range(10000)]
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return out + [
        f"- N treated (matched): **{len(eff)}**",
        f"- Matched effect mean **{eff.mean():+.2f} bps** (t p={tp:.4f}); median {np.median(eff):+.2f} bps",
        f"- Wilcoxon p={wp:.4f}; **{nneg}/{len(eff)} tightened (negative)** (p={sp_:.4f})",
        f"- Bootstrap 95% CI [{lo:+.2f}, {hi:+.2f}] bps", ""]

def stacked_ols(pairs):
    recs = []
    for _, r in pairs.iterrows():
        if r["d_treated"] is not None and pd.notna(r["d_treated"]):
            recs.append({"county_fips": r["treated_fips"], "d": r["d_treated"], "is_treated":1, "state_fips": r["treated_fips"][:2]})
        if r["d_control"] is not None and pd.notna(r["d_control"]):
            recs.append({"county_fips": r["control_fips"], "d": r["d_control"], "is_treated":0, "state_fips": r["control_fips"][:2]})
    df = pd.DataFrame(recs)
    if df.empty or df["is_treated"].nunique()<2: return None
    fit = smf.ols("d ~ is_treated + C(state_fips)", data=df).fit(
        cov_type="cluster", cov_kwds={"groups": df["county_fips"]})
    return fit, int(fit.nobs), df["county_fips"].nunique()

def unique_ols(pairs):
    seen={}
    for _, r in pairs.iterrows():
        if r["d_treated"] is not None and pd.notna(r["d_treated"]): seen[r["treated_fips"]]=(r["d_treated"],1)
    for _, r in pairs.iterrows():
        if r["control_fips"] not in seen and r["d_control"] is not None and pd.notna(r["d_control"]):
            seen[r["control_fips"]]=(r["d_control"],0)
    df=pd.DataFrame([{"county_fips":k,"d":v[0],"is_treated":v[1],"state_fips":k[:2]} for k,v in seen.items()])
    if df.empty or df["is_treated"].nunique()<2: return None
    fit=smf.ols("d ~ is_treated + C(state_fips)", data=df).fit(cov_type="HC1")
    return fit, int(fit.nobs)

def ols_line(label, res):
    if res is None: return f"- {label}: insufficient variation"
    fit, n, *rest = res
    b=fit.params["is_treated"]; se=fit.bse["is_treated"]; p=fit.pvalues["is_treated"]
    tail=f", clusters={rest[0]}" if rest else ""
    return f"- {label}: treated coef **{b:+.2f} bps** (SE {se:.2f}, p={p:.4f}), N={n}{tail}"


P_state = P[P["match_tier"]=="state"]
P_noesc = P[~P["treated_state"].isin(ESC_STATES)]
eff_full = matched_effects(P)
eff_full.to_csv(D/"matched_spread_did_pairs_resolved.csv", index=False)

L = ["# Matched Bond-Spread DiD (same sample as the property-tax DiD)\n",
     "**Date:** 2026-06-10. Bond-spread outcome re-estimated on the 101-treated / 1:3 "
     "division-matched sample (script 45), event-aligned to each treated county's first-DC "
     "year, so pricing and property tax share ONE identification strategy. `scripts/python/49`.\n",
     "Outcome = within-county change in par-weighted spread (post-DC mean − pre-DC mean), bps. "
     "**NEGATIVE = spread tightened = cheaper borrowing.** Each matched control is split at its "
     "matched treated's DC year.\n",
     f"## Sample composition",
     f"- Pairs with treated DC-year: {len(P)} ({(P['match_tier']=='state').sum()} state, "
     f"{(P['match_tier']=='division').sum()} division)",
     f"- Treated usable (pre & post spread): **{len(eff_full)}**",
     f"- Unique controls contributing a change: {P['d_control'].notna().sum() and P.loc[P['d_control'].notna(),'control_fips'].nunique()}",
     ""]

L += ["## (1) Matched-pair effect (headline + robustness)", ""]
L += effect_block(eff_full, "FULL (state + division)")
L += effect_block(matched_effects(P_state), "STATE-ONLY (drop division-fallback pairs)")
L += effect_block(matched_effects(P_noesc), "ESC-DROPPED (drop East-South-Central treated)")

L += ["## (2) Pair-stacked OLS, SEs clustered on county", ""]
L += [ols_line("FULL", stacked_ols(P)),
      ols_line("STATE-ONLY", stacked_ols(P_state)),
      ols_line("ESC-DROPPED", stacked_ols(P_noesc)), ""]

L += ["## (3) Unique-county OLS, state FE, HC1", ""]
L += [ols_line("FULL", unique_ols(P)), ""]

L += ["## Notes",
      "- Sign: negative = spreads fell after DC arrival relative to matched controls.",
      "- Directly comparable to script 46 (property tax, +1.5pp/yr) and script 48 (capex/debt): "
      "same matched pairs, same three estimators, same two robustness columns.",
      "- Compare to the CS-vs-never-treated spec (script 16): ATT −23.4 bps (SE 12.3, p<0.10). "
      "This matched version swaps the control group from all never-DC-host counties to the "
      "size-and-region-matched controls.",
      "- Caveat: spread observed only in county-years with a Treasury-benchmarked issue; "
      "pre/post means rest on whatever years each county came to market.", ""]

(D/"matched_spread_did_results.md").write_text("\n".join(L))
print("\n".join(L))
print("Wrote data/derived/matched_spread_did_results.md")
