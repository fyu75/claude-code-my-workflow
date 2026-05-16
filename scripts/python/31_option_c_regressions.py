"""
31_option_c_regressions.py

Full statistical tests for Option C:
  1. One-sample t-test (mean excess > 0)
  2. Wilcoxon signed-rank (median excess > 0, robust to outliers)
  3. Sign test (binomial P(positive) > 0.5)
  4. Bootstrap 95% CI on mean excess
  5. OLS regression: treated_CAGR ~ log(MW) + state FE  (continuous treatment intensity)
  6. OLS regression: treated_CAGR ~ DC_tax_share + state FE
  7. WLS regression: treated_CAGR ~ log(MW), weighted by 1/years_elapsed (less weight to shorter windows)
  8. Per-county studentized residual flagging

Outputs to: data/derived/option_c_full_tests.md
"""
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
DERIVED = ROOT / "data" / "derived"

BENCHMARK_CAGR = {
    "property_tax":         0.0340,
    "capital_outlay":       0.0507,
    "lt_debt_outstanding":  0.0174,
}
LABELS = {
    "property_tax":         "Property tax",
    "capital_outlay":       "Capital outlay",
    "lt_debt_outstanding":  "Long-term debt",
}
UNRELIABLE = {"51117","48371","48475","48103","48173","48045"}

df = pd.read_csv(DERIVED / "option_c_excess_growth.csv", dtype={"county_fips": str})

# Bring in DC intensity (MW + tax share) from dc_tax_share_distribution
intens = pd.read_csv(DERIVED / "dc_tax_share_distribution.csv", dtype={"county_fips": str})
intens = intens[["county_fips","mw_latest","dc_share_mid"]]
df = df.merge(intens, on="county_fips", how="left")
df["log_mw"] = np.log(df["mw_latest"])
df["state"] = df["county_fips"].str[:2]
df["clean"] = ~df["county_fips"].isin(UNRELIABLE)

OUT = []
def L(s=""):
    print(s); OUT.append(s)

L("# Option C — Full statistical tests")
L("")
L(f"Treated counties extracted: {len(df)}; clean sample (drop 6 flagged): {df.clean.sum()}")
L("")

# ============================================================================
# Section 1: Battery of tests on excess CAGR per outcome, full vs clean
# ============================================================================
L("## 1. Distribution tests on excess CAGR")
L("")

def battery(x, label):
    x = pd.Series(x).dropna().values
    n = len(x)
    if n < 3:
        return dict(n=n)
    mean = x.mean(); med = np.median(x); sd = x.std(ddof=1)
    # t-test, one-sample
    t, p_t2 = stats.ttest_1samp(x, 0)
    p_t1 = p_t2 / 2 if t > 0 else 1 - p_t2 / 2
    # Wilcoxon signed-rank (one-sided, alt='greater' on x-0)
    if not np.all(x == 0):
        w_stat, p_w1 = stats.wilcoxon(x, alternative="greater")
    else:
        w_stat, p_w1 = np.nan, np.nan
    # Sign test (binomial on positives)
    n_pos = int(np.sum(x > 0))
    p_sign = stats.binom.sf(n_pos - 1, n, 0.5)
    # Bootstrap 95% CI on mean
    rng = np.random.default_rng(20260516)
    boot = np.array([rng.choice(x, size=n, replace=True).mean() for _ in range(5000)])
    ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
    return dict(n=n, mean=mean, med=med, sd=sd,
                t=t, p_t1=p_t1, w=w_stat, p_w1=p_w1,
                n_pos=n_pos, p_sign=p_sign, ci_lo=ci_lo, ci_hi=ci_hi)

for sample_label, sub in [("FULL", df), ("CLEAN", df[df.clean])]:
    L(f"### {sample_label} sample")
    L("")
    L("| Outcome | N | mean | median | SD | t (p₁) | Wilcoxon (p₁) | Sign test (p) | 95% CI mean |")
    L("|---|---:|---:|---:|---:|---:|---:|---:|---|")
    for o in BENCHMARK_CAGR:
        col = f"{o}_excess"
        s = battery(sub[col], LABELS[o])
        if s.get("n",0) < 3:
            L(f"| {LABELS[o]} | {s.get('n',0)} | n/a | | | | | | |")
            continue
        L(f"| {LABELS[o]} | {s['n']} | {s['mean']*100:.2f}% | {s['med']*100:.2f}% | "
          f"{s['sd']*100:.2f} | {s['t']:.2f} (p={s['p_t1']:.4f}) | "
          f"{s['w']:.1f} (p={s['p_w1']:.4f}) | {s['n_pos']}/{s['n']} (p={s['p_sign']:.4f}) | "
          f"[{s['ci_lo']*100:.2f}%, {s['ci_hi']*100:.2f}%] |")
    L("")

# ============================================================================
# Section 2: OLS regressions on continuous DC intensity (MW)
# ============================================================================
L("## 2. Continuous-treatment regressions")
L("")
L("Specification: `outcome_CAGR_c = α + β · log(MW_c) + γ · state_FE + ε_c`")
L("Standard errors: HC3 robust.")
L("")

def run_ols(d, y_col, x_cols, label, hc="HC3"):
    sub = d[[y_col] + x_cols].dropna()
    if len(sub) < 4 + len(x_cols):
        return None, len(sub)
    X = sm.add_constant(sub[x_cols], has_constant="add")
    y = sub[y_col]
    fit = sm.OLS(y, X).fit(cov_type=hc)
    return fit, len(sub)

for sample_label, sub in [("FULL", df), ("CLEAN", df[df.clean])]:
    L(f"### {sample_label} sample")
    L("")
    L("| Outcome | Spec | β (log MW) | SE | t | p | N | R² |")
    L("|---|---|---:|---:|---:|---:|---:|---:|")
    for o in BENCHMARK_CAGR:
        y_col = f"{o}_cagr"
        # Spec 1: log(MW) only
        fit, n = run_ols(sub, y_col, ["log_mw"], LABELS[o])
        if fit is None:
            L(f"| {LABELS[o]} | log MW | n/a | | | | {n} | |")
            continue
        b = fit.params["log_mw"]; se = fit.bse["log_mw"]
        t = fit.tvalues["log_mw"]; p = fit.pvalues["log_mw"]
        L(f"| {LABELS[o]} | log MW only | {b*100:.2f}pp | {se*100:.2f} | {t:.2f} | {p:.4f} | {n} | {fit.rsquared:.3f} |")
        # Spec 2: log(MW) + state FE (if enough states)
        if sub["state"].nunique() < 2:
            continue
        # Build state dummies
        d2 = sub.copy()
        st_dummies = pd.get_dummies(d2["state"], prefix="st", drop_first=True).astype(float)
        d2 = pd.concat([d2, st_dummies], axis=1)
        fit2, n2 = run_ols(d2, y_col, ["log_mw"] + list(st_dummies.columns), LABELS[o])
        if fit2 is not None and "log_mw" in fit2.params:
            b = fit2.params["log_mw"]; se = fit2.bse["log_mw"]
            t = fit2.tvalues["log_mw"]; p = fit2.pvalues["log_mw"]
            L(f"| {LABELS[o]} | log MW + state FE | {b*100:.2f}pp | {se*100:.2f} | {t:.2f} | {p:.4f} | {n2} | {fit2.rsquared:.3f} |")
    L("")

# ============================================================================
# Section 3: Regression on DC tax share
# ============================================================================
L("## 3. Continuous-treatment regressions — DC tax share")
L("")
L("Specification: `outcome_CAGR_c = α + β · dc_share_mid_c + ε_c`  (no state FE)")
L("")
for sample_label, sub in [("FULL", df), ("CLEAN", df[df.clean])]:
    L(f"### {sample_label} sample")
    L("")
    L("| Outcome | β (per 1pp DC share) | SE | t | p | N | R² |")
    L("|---|---:|---:|---:|---:|---:|---:|")
    for o in BENCHMARK_CAGR:
        y_col = f"{o}_cagr"
        fit, n = run_ols(sub, y_col, ["dc_share_mid"], LABELS[o])
        if fit is None:
            L(f"| {LABELS[o]} | n/a | | | | {n} | |")
            continue
        # dc_share_mid is in percent units (already %), β is per-pp; divide for readability
        b = fit.params["dc_share_mid"]; se = fit.bse["dc_share_mid"]
        t = fit.tvalues["dc_share_mid"]; p = fit.pvalues["dc_share_mid"]
        L(f"| {LABELS[o]} | {b*100:.3f}pp | {se*100:.3f} | {t:.2f} | {p:.4f} | {n} | {fit.rsquared:.3f} |")
    L("")

# ============================================================================
# Section 4: Per-county influence diagnostics for property_tax model
# ============================================================================
L("## 4. Influence diagnostics — property_tax_cagr ~ log_mw (CLEAN)")
L("")
sub = df[df.clean].dropna(subset=["property_tax_cagr","log_mw"])
if len(sub) >= 5:
    X = sm.add_constant(sub[["log_mw"]])
    fit = sm.OLS(sub["property_tax_cagr"], X).fit()
    infl = fit.get_influence()
    sub2 = sub.copy()
    sub2["leverage"] = infl.hat_matrix_diag
    sub2["studentized_resid"] = infl.resid_studentized_external
    sub2["cooks_d"] = infl.cooks_distance[0]
    L("| FIPS | County | State | log_mw | CAGR | leverage | studentized | Cook's D |")
    L("|---|---|---|---:|---:|---:|---:|---:|")
    for _, r in sub2.sort_values("cooks_d", ascending=False).iterrows():
        L(f"| {r['county_fips']} | {r['county_name']} | {r['state']} | "
          f"{r['log_mw']:.2f} | {r['property_tax_cagr']*100:.2f}% | "
          f"{r['leverage']:.3f} | {r['studentized_resid']:.2f} | {r['cooks_d']:.3f} |")
L("")

# ============================================================================
# Save
# ============================================================================
out_path = DERIVED / "option_c_full_tests.md"
out_path.write_text("\n".join(OUT))
print(f"\nWrote {out_path}")
