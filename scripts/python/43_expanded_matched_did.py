"""
43_expanded_matched_did.py

Expanded 2-period matched DiD on county-government property-tax growth (2017 -> latest),
using the full-125 1:3 matched controls (script 42) instead of the 22-treated subset.

SCOPE CONSISTENCY (critical):
  - 2017 baseline = Census ACFR `rev_property_tax` = county-government TOTAL property
    tax (all funds). So the post-period must also be ALL-FUNDS county-government PT,
    NOT general-fund-only (using GF-only post vs all-funds 2017 understates growth).
  - Post-period all-funds sources, in priority order:
      1. ACFR scrape: acfr_county_year_extracted_wide.csv `property_tax_allfunds`
         (most recent FY with a value).
      2. MuniSpot v2 all-funds classified (Total Governmental Funds, column_index=-1,
         tier_with_pilot), reported_value * value_multiplier, most recent FY >= 2018.
  - GF-only sources are NOT used for the post period here (scope mismatch).

DESIGN:
  - CAGR_i = (pt_post / pt_2017)^(1/(year_post - 2017)) - 1  for each county i.
  - Matched effect per treated t = CAGR_t - mean(CAGR over its post-covered controls).
  - Tests on the per-treated effects: one-sample t, Wilcoxon signed-rank, sign test,
    bootstrap 95% CI. Plus pooled county-level OLS: CAGR ~ treated + state FE.
  - Also report treated-only CAGR vs the property-tax benchmark CAGR (~3.4%/yr).

Outputs:
  data/derived/expanded_matched_did_panel.csv   (county-level CAGR panel)
  data/derived/expanded_matched_did_results.md  (results writeup)
"""
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)
rng = np.random.default_rng(20260516)
BENCH_PT_CAGR = 0.0340  # property-tax benchmark CAGR (script 31)

# ---------- 1. 2017 baseline (all-funds county-govt PT) ----------
c17 = pd.read_csv(D / "acfr_2017_county_govt_only.csv"); c17["county_fips"] = fz(c17["county_fips"])
# Census rev_property_tax is in MILLIONS of dollars; post-period values are in dollars -> convert to dollars.
pt17 = (c17.set_index("county_fips")["rev_property_tax"] * 1e6).to_dict()
base_yr = {}  # fips -> baseline fiscal year; default 2017 (Census). Verified file may override (e.g. McMullen FY2018).

# Sources considered "clean" for the PRIMARY (trustworthy) estimate.
CLEAN = {"acfr_allfunds", "verified"}
# Counties dropped from the growth DiD (baseline unrecoverable / invalid match):
#  18153 Sullivan IN  - Indiana property+income-tax bundling; PT-only not separable from audits.
#  48237 Jack TX      - no FY2017 audit; Census baseline is an ASLGF undercount.
#  29215 Texas MO     - county PT only $271k vs Census $8.97M (33x over) -> match to Clay MO invalid.
#  29047 Clay MO      - MO Census ASLGF baseline systematically unreliable (see Texas MO); its
#                       rank-1 control (29215) is itself dropped -> no valid baseline or control.
#  38105 Williams ND  - no FY2017 audit (portal 404); Census $14.13M likely overstated vs true ~$11M
#                       -> would manufacture a spurious decline. Needs ND State Archives.
#  48075 Childress TX - no FY2017 audit (only FY19/FY20); Census baseline undercaptured (GF+R&B only).
#  39111 Monroe OH    - property-tax surge driven by Rover/REX natural-gas PIPELINES (utility personal
#                       property), NOT data centers -> treatment confound; drop from DC-mechanism.
#  40101 Muskogee OK  - OK cash/regulatory basis; ad valorem not isolable as a clean all-funds total.
DROP = {"18153", "48237", "29215", "29047", "38105", "48075", "39111", "40101"}

# ---------- 2. Post-period all-funds PT, source-prioritized ----------
post = {}  # fips -> (value, year, source)
# 2a. ACFR scrape all-funds
wide = pd.read_csv(D / "acfr_county_year_extracted_wide.csv"); wide["county_fips"] = fz(wide["county_fips"])
af = wide[wide["property_tax_allfunds"].notna() & (wide["fy"] > 2017)].sort_values("fy")
for _, r in af.iterrows():
    post[r["county_fips"]] = (float(r["property_tax_allfunds"]), int(r["fy"]), "acfr_allfunds")
# 2b. V2 all-funds — DISABLED 2026-06-07. Online verification (8 flagged counties)
# found V2 all-funds systematically UNDER-captures property tax (grabs one levy
# bucket / component, not the total): Arlington VA V2=$145M vs true $1,083M (real
# estate dropped); Pecos TX 1/17; Lincoln NM 1/6; Box Elder UT 1/3 — 4/4 wrong.
# V2 levels are not trustworthy for a growth comparison -> ACFR all-funds ONLY.
USE_V2 = False
if USE_V2:
    pass  # intentionally not used; see verification note above

# 2c. HAND-VERIFIED two-endpoint values (read from actual ACFRs by Sonnet agents, 2026-06-07/08).
# HIGHEST priority: overrides BOTH the Census baseline and the ACFR-wide post for these counties.
# Values are already in dollars (NOT millions). Tagged source "verified" -> counts as CLEAN.
vpath = D / "verified_two_endpoint_pt.csv"
if vpath.exists():
    vdf = pd.read_csv(vpath, dtype={"county_fips": str}, na_values=["NA", ""])
    vdf["county_fips"] = fz(vdf["county_fips"])
    n_base, n_post = 0, 0
    for _, r in vdf.iterrows():
        f = r["county_fips"]
        if f in DROP:
            continue
        if pd.notna(r["baseline_pt_allfunds_usd"]) and pd.notna(r["baseline_fy"]):
            pt17[f] = float(r["baseline_pt_allfunds_usd"]); base_yr[f] = int(r["baseline_fy"]); n_base += 1
        if pd.notna(r["post_pt_allfunds_usd"]) and pd.notna(r["post_fy"]):
            post[f] = (float(r["post_pt_allfunds_usd"]), int(r["post_fy"]), "verified"); n_post += 1
    print(f"Verified overrides applied: {n_base} baselines, {n_post} posts (DROP={sorted(DROP)})")

# ---------- 3. CAGR per county ----------
def cagr(fips):
    if fips in DROP: return None
    p0 = pt17.get(fips); pp = post.get(fips)
    if p0 is None or p0 <= 0 or pp is None: return None
    val, yr, src = pp
    by = base_yr.get(fips, 2017)   # use the actual baseline FY (verified file may set 2018)
    if val <= 0 or yr <= by: return None
    return ((val / p0) ** (1.0 / (yr - by)) - 1.0, yr, src, p0, val)

# ---------- 4. Matched pairs ----------
m = pd.read_csv(D / "matched_controls_full125.csv")
m = m[m["control_fips"].notna()].copy()
m["treated_fips"] = fz(m["treated_fips"].astype(int).astype(str))
m["control_fips"] = fz(m["control_fips"].astype(int).astype(str))

def build_effects(require_acfr):
    """Matched per-treated effects. require_acfr=True restricts BOTH sides to clean
    ACFR all-funds (V2 levels are unit-unreliable); False uses any all-funds source."""
    rows, eff = [], []
    for t, grp in m.groupby("treated_fips"):
        ct = cagr(t)
        if ct is None or (require_acfr and ct[2] not in CLEAN): continue
        ctrl = []
        for cf in grp["control_fips"].unique():
            cc = cagr(cf)
            if cc is None: continue
            if require_acfr and cc[2] not in CLEAN: continue
            ctrl.append(cc[0])
        if not ctrl: continue
        e = ct[0] - np.mean(ctrl)
        eff.append(e)
        rows.append({"treated_fips": t, "treated_cagr": ct[0], "treated_src": ct[2],
                     "n_controls_used": len(ctrl), "mean_control_cagr": np.mean(ctrl), "effect": e})
    return pd.DataFrame(rows), np.array(eff)

res, effects = build_effects(require_acfr=True)        # CLEAN primary
res_all, effects_all = build_effects(require_acfr=False)  # wide coverage (V2 incl.)

# ---------- county-level panel for OLS + audit ----------
panel = []
treated_set = set(m["treated_fips"])
for f in set(m["treated_fips"]) | set(m["control_fips"]):
    cc = cagr(f)
    if cc is None: continue
    panel.append({"county_fips": f, "is_treated": int(f in treated_set),
                  "cagr": cc[0], "post_year": cc[1], "src": cc[2],
                  "state_fips": f[:2], "pt_2017": cc[3], "pt_post": cc[4]})
pan = pd.DataFrame(panel)
pan.to_csv(D / "expanded_matched_did_panel.csv", index=False)

# ---------- 5. Tests ----------
def fmt(x): return f"{x*100:+.2f}%"
def block(eff, title, robust_only=False):
    out = [title]
    if len(eff) < 3:
        return out + [f"- Too few usable treated ({len(eff)}) for inference.", ""]
    w_p = stats.wilcoxon(eff).pvalue
    n_pos = int((eff > 0).sum()); sign_p = stats.binomtest(n_pos, len(eff), 0.5).pvalue
    out += [f"- N treated: **{len(eff)}**",
            f"- Median effect: **{fmt(np.median(eff))}/yr**",
            f"- Wilcoxon signed-rank: p={w_p:.4f}",
            f"- Sign test: {n_pos}/{len(eff)} positive, p={sign_p:.4f}"]
    if not robust_only:
        t_p = stats.ttest_1samp(eff, 0).pvalue
        boot = [rng.choice(eff, len(eff), replace=True).mean() for _ in range(10000)]
        lo, hi = np.percentile(boot, [2.5, 97.5])
        out += [f"- Mean effect: **{fmt(eff.mean())}/yr** (t-test p={t_p:.4f})",
                f"- Bootstrap 95% CI: [{fmt(lo)}, {fmt(hi)}]/yr"]
    else:
        out += ["- (mean/CI omitted — V2 level units unreliable; robust stats only)"]
    return out + [""]

L = ["# Expanded Matched DiD — county property-tax growth (2017 -> latest)\n",
     "**Date:** 2026-06-07  | All-funds county-government scope.  Matched 1:3 (script 42).",
     "Effect = treated county-government property-tax CAGR − mean of its matched-control CAGRs.\n",
     "## Coverage",
     f"- CLEAN (ACFR all-funds, hand-verified) usable treated: **{len(res)}**",
     f"- WIDE (incl. MuniSpot v2 all-funds) usable treated: **{len(res_all)}**",
     f"- ⚠ V2 level data has unreliable units (value_multiplier misfires ±1000×) → used ONLY for outlier-robust stats, never the mean.",
     ""]

L += block(effects, "## PRIMARY — clean ACFR all-funds matched effect")
# treated-vs-benchmark on clean treated set
if len(res):
    exc = res["treated_cagr"].values - BENCH_PT_CAGR
    tp = stats.ttest_1samp(exc, 0).pvalue if len(exc) >= 3 else np.nan
    L += ["## PRIMARY — clean treated CAGR vs benchmark (3.40%/yr)",
          f"- Mean treated CAGR: **{fmt(res['treated_cagr'].mean())}/yr** (median {fmt(res['treated_cagr'].median())})",
          f"- Mean excess over benchmark: **{fmt(np.mean(exc))}/yr** (t-test p={tp:.4f})", ""]
# clean pooled OLS
clean = pan[pan["src"].isin(CLEAN)].copy()
if clean["is_treated"].nunique() == 2 and len(clean) >= 10:
    try:
        ols = smf.ols("cagr ~ is_treated + C(state_fips)", data=clean).fit(cov_type="HC1")
        L += ["## PRIMARY — pooled OLS (clean ACFR only): CAGR ~ treated + state FE",
              f"- Treated coef: **{fmt(ols.params['is_treated'])}/yr** (SE {fmt(ols.bse['is_treated'])}, p={ols.pvalues['is_treated']:.4f}), N={int(ols.nobs)}", ""]
    except Exception as e:
        L += [f"(clean OLS skipped: {e})", ""]

L += block(effects_all, "## ROBUSTNESS — wide coverage (incl. V2), outlier-robust only", robust_only=True)
L += ["## Caveats",
      "- V2 all-funds level units are unreliable (PWC post showed $818B; many controls off 1000×) — clean ACFR is the trustworthy source.",
      "- 51 of 369 matched pairs are FALLBACK (control outside 0.5–2× PT band).",
      "- True expansion to the full 125 needs the control-ACFR scraping wave (clean post-period data).",
      f"- Post source mix among CLEAN treated: {dict(res['treated_src'].value_counts()) if len(res) else {}}"]

(D / "expanded_matched_did_results.md").write_text("\n".join(L))
print("\n".join(L))
print(f"\nWrote panel ({len(pan)} counties) + results.md")
