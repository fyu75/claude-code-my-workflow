"""
46_division_matched_did.py

Run the 2-period property-tax growth DiD on the division-matched sample built by
script 45 (`division_matched_pairs.csv`). Frank signed off on the 101-treated /
1:3 sample construction on 2026-06-10; this is the first DiD wired to it.

Design recap:
  - Outcome  = within-county annualized property-tax CAGR (FY2017 baseline -> post),
               taken from the triangulated verified spine (script 44 output).
  - Treated  = DC county (DC tax share >= 1%), USABLE tier (PRIMARY/EXPANDED/CENSUS_TRUST).
  - Controls = never-DC counties, 1:3 matched on log baseline PT, same state preferred,
               same Census division as fallback (match_tier in {state, division}).

Estimators:
  (1) MATCHED-PAIR EFFECT (headline) - per treated county,
        effect_t = CAGR_treated - mean(CAGR of its matched controls);
        one-sample t / Wilcoxon / sign / bootstrap CI on the effect distribution,
        plus treated CAGR vs the national benchmark (+3.40%/yr).
  (2) PAIR-STACKED OLS - cagr ~ is_treated + state FE on the stacked pair sample,
        SEs CLUSTERED ON COUNTY so a reused control counts as one cluster.
  (3) UNIQUE-COUNTY OLS - cagr ~ is_treated + state FE, HC1, on the unique counties
        (comparable to script 44's pooled spec; no reuse weighting).

Robustness columns (requested at sign-off):
  - STATE-ONLY   : drop division-fallback pairs (match_tier == 'state' only).
  - ESC-DROPPED  : drop East-South-Central treated (the 8x control-reuse bottleneck).

This script runs tests only; it does NOT rebuild the sample (that's script 45).
Outputs:
  data/derived/division_matched_did_results.md
  data/derived/division_matched_did_pairs_resolved.csv   (per-treated effects, for audit)
"""
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[2]; D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)
rng = np.random.default_rng(20260516)
BENCH = 0.0340                       # national county-govt PT CAGR benchmark (same as script 44)
ESC_STATES = {"01","21","28","47"}   # East South Central: AL, KY, MS, TN

# ---- CAGRs + tiers from the triangulation (script 44 output) ----
prov = pd.read_csv(D/"triangulated_baseline_status.csv", dtype={"county_fips":str})
prov["county_fips"] = fz(prov["county_fips"])
usable = prov[prov["status"]=="USABLE"].copy()
CAGR = dict(zip(usable["county_fips"], usable["cagr"].astype(float)))
TIER = dict(zip(usable["county_fips"], usable["tier"]))

# ---- matched pairs (script 45 output) ----
P = pd.read_csv(D/"division_matched_pairs.csv")
P["treated_fips"] = fz(P["treated_fips"].astype(int).astype(str))
P["control_fips"] = fz(P["control_fips"].astype(int).astype(str))
# keep only pairs where BOTH endpoints resolve to a usable CAGR (should be all, by construction)
P = P[P["treated_fips"].isin(CAGR) & P["control_fips"].isin(CAGR)].copy()
P["treated_state"] = P["treated_fips"].str[:2]


# ============================ estimators ============================
def matched_effects(pairs):
    """Per-treated matched effect = CAGR_treated - mean(CAGR controls). Returns df."""
    rows = []
    for t, grp in pairs.groupby("treated_fips"):
        ct = CAGR[t]
        ctrls = [CAGR[c] for c in grp["control_fips"].unique()]
        if not ctrls: continue
        rows.append({"treated_fips": t, "state": t[:2], "division": grp["division"].iloc[0],
                     "tier": TIER.get(t,"?"), "n_ctrl": len(ctrls),
                     "cagr_treated": ct, "cagr_ctrl_mean": float(np.mean(ctrls)),
                     "effect": ct - float(np.mean(ctrls))})
    return pd.DataFrame(rows)


def effect_block(eff_df, title):
    out = [f"### {title}", ""]
    eff = eff_df["effect"].to_numpy(); tc = eff_df["cagr_treated"].to_numpy()
    if len(eff) < 3:
        return out + [f"- too few usable treated ({len(eff)})", ""]
    tp = stats.ttest_1samp(eff, 0).pvalue
    wp = stats.wilcoxon(eff).pvalue
    npos = int((eff > 0).sum()); sp = stats.binomtest(npos, len(eff), 0.5).pvalue
    boot = [rng.choice(eff, len(eff), replace=True).mean() for _ in range(10000)]
    lo, hi = np.percentile(boot, [2.5, 97.5])
    exc = tc - BENCH; ep = stats.ttest_1samp(exc, 0).pvalue
    return out + [
        f"- N treated (matched): **{len(eff)}**",
        f"- Matched effect mean **{eff.mean()*100:+.2f}%/yr** (t p={tp:.4f}); median {np.median(eff)*100:+.2f}%",
        f"- Wilcoxon p={wp:.4f}; sign {npos}/{len(eff)} positive (p={sp:.4f})",
        f"- Bootstrap 95% CI [{lo*100:+.2f}, {hi*100:+.2f}]%/yr",
        f"- Treated CAGR mean **{tc.mean()*100:+.2f}%/yr** vs {BENCH*100:.2f}% benchmark "
        f"-> excess **{exc.mean()*100:+.2f}%/yr** (p={ep:.4f})", ""]


def stacked_ols(pairs, cluster=True):
    """Pair-stacked OLS: cagr ~ is_treated + state FE; cluster on county (handles reuse)."""
    recs = []
    for _, r in pairs.iterrows():
        t, c = r["treated_fips"], r["control_fips"]
        recs.append({"county_fips": t, "cagr": CAGR[t], "is_treated": 1, "state_fips": t[:2]})
        recs.append({"county_fips": c, "cagr": CAGR[c], "is_treated": 0, "state_fips": c[:2]})
    df = pd.DataFrame(recs)
    if df["is_treated"].nunique() < 2 or df["state_fips"].nunique() < 1:
        return None
    if cluster:
        fit = smf.ols("cagr ~ is_treated + C(state_fips)", data=df).fit(
            cov_type="cluster", cov_kwds={"groups": df["county_fips"]})
        n_clust = df["county_fips"].nunique()
    else:
        fit = smf.ols("cagr ~ is_treated + C(state_fips)", data=df).fit(cov_type="HC1")
        n_clust = None
    return fit, int(fit.nobs), n_clust


def unique_county_ols(pairs):
    """Unique-county pooled OLS (comparable to script 44): cagr ~ treated + state FE, HC1."""
    t_set = set(pairs["treated_fips"]); c_set = set(pairs["control_fips"]) - t_set
    recs = ([{"county_fips": f, "cagr": CAGR[f], "is_treated": 1, "state_fips": f[:2]} for f in t_set]
          + [{"county_fips": f, "cagr": CAGR[f], "is_treated": 0, "state_fips": f[:2]} for f in c_set])
    df = pd.DataFrame(recs)
    if df["is_treated"].nunique() < 2: return None
    fit = smf.ols("cagr ~ is_treated + C(state_fips)", data=df).fit(cov_type="HC1")
    return fit, int(fit.nobs)


def ols_line(label, res):
    if res is None: return f"- {label}: insufficient variation"
    fit, n, *rest = res if isinstance(res, tuple) else (res,)
    b = fit.params["is_treated"]*100; se = fit.bse["is_treated"]*100; p = fit.pvalues["is_treated"]
    tail = f", clusters={rest[0]}" if rest and rest[0] else ""
    return f"- {label}: treated coef **{b:+.2f}%/yr** (SE {se:.2f}, p={p:.4f}), N={n}{tail}"


# ============================ run + write ============================
L = ["# Division-Matched 2-Period Property-Tax Growth DiD\n",
     "**Date:** 2026-06-10. First DiD on the 101-treated / 1:3 division-matched sample "
     "(script 45 `division_matched_pairs.csv`), run after Frank's sign-off on sample construction.\n",
     "Outcome = within-county annualized property-tax CAGR (FY2017 -> post) from the triangulated "
     "verified spine. Benchmark = national county-govt PT CAGR +3.40%/yr.\n"]

# sample composition
eff_full = matched_effects(P)
eff_full.to_csv(D/"division_matched_did_pairs_resolved.csv", index=False)
n_state_pairs = int((P["match_tier"]=="state").sum()); n_div_pairs = int((P["match_tier"]=="division").sum())
L += ["## Sample composition",
      f"- Pairs: **{len(P)}** ({n_state_pairs} same-state, {n_div_pairs} division-fallback)",
      f"- Treated with >=1 matched usable control: **{eff_full['treated_fips'].nunique()}**",
      f"- Unique controls used: **{P['control_fips'].nunique()}**",
      f"- Treated by tier: {dict(eff_full['tier'].value_counts())}", ""]

# (1) matched-pair effect — headline + robustness
L += ["## (1) Matched-pair effect (headline + robustness)", ""]
L += effect_block(eff_full, "FULL (state + division fallback)")
P_state = P[P["match_tier"]=="state"]
L += effect_block(matched_effects(P_state), "STATE-ONLY (drop division-fallback pairs)")
P_noesc = P[~P["treated_state"].isin(ESC_STATES)]
L += effect_block(matched_effects(P_noesc), "ESC-DROPPED (drop East-South-Central treated)")

# (2) pair-stacked OLS clustered on county
L += ["## (2) Pair-stacked OLS, SEs clustered on county (reused control = one cluster)", ""]
L += [ols_line("FULL  (state+division)", stacked_ols(P)),
      ols_line("STATE-ONLY", stacked_ols(P_state)),
      ols_line("ESC-DROPPED", stacked_ols(P_noesc)), ""]

# (3) unique-county pooled OLS (comparable to script 44)
L += ["## (3) Unique-county pooled OLS, state FE, HC1 (comparable to script 44)", ""]
L += [ols_line("FULL", unique_county_ols(P)),
      ols_line("STATE-ONLY", unique_county_ols(P_state)),
      ols_line("ESC-DROPPED", unique_county_ols(P_noesc)), ""]

L += ["## Notes",
      "- Headline = estimator (1) FULL. Estimators (2)/(3) are regression analogues; (2) is the "
      "preferred inferential spec because it clusters on county (controls are reused up to ~8x).",
      "- match_tier robustness isolates the strict same-state design; ESC-dropped probes the "
      "control-reuse bottleneck flagged in sample construction.",
      "- CAGRs and tiers inherited from script 44; DROP set and high-risk gating already applied there.",
      ""]

(D/"division_matched_did_results.md").write_text("\n".join(L))
print("\n".join(L))
print("Wrote data/derived/division_matched_did_results.md and ..._pairs_resolved.csv")
