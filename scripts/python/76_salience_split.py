"""
76_salience_split.py

Pre-specified heterogeneity test: does the bond market's non-response reflect LIMITED
ATTENTION rather than rational non-pricing?

If attention drives the null, effects should appear where attention is HIGHEST:
  (a) MEGA counties — first major DC announcement was very large (top-decile announced MW;
      also >=300 MW alternative cut)
  (b) POST-2022 ERA — after ChatGPT made data centers a salient national asset-class
  (c) COMBINED — mega counties x post-2022 period (attention maximized)

DESIGN: Mirrors script 68 EXACTLY.
  - Treated = treated_universe_labeled.csv minus phantoms {47121, 54047, 21127}
  - Anchor = A_firstmaj (ann_firstmaj from announcement_anchor_county; fallback = announce_year)
  - Controls = clean never-DC counties (n_dc_cumulative == 0 in panel_v4)
  - Spec: spread_bps ~ announced + logamt + logmat | county_fips + year, cluster county
  - Deals 2008-2025 from sdc_deal_spread + sdc_deal_rating
  - Cuts: ALL / clean_dc (dc_class filters on treated side)

MW CONSTRUCTION:
  Use cum_ann_mw from dc_dose_announced_mw_panel at the county's anchor year A_firstmaj.
  This captures announced capacity at the moment of the county's first major announcement.
  For counties without dose-panel coverage (65/125 have it), fall back to mw_latest
  from treated_universe_labeled (total operational capacity — noisier but 100% coverage).
  Top decile is computed within treated counties using this combined MW measure.

REGRESSIONS:
  1. MEGA split: mega vs rest, announced dummy, each vs controls separately
  2. ERA split: announced x 1[year<=2022] + announced x 1[year>=2023] in one model (no
     base announced term), same county+year FE — coefficients are period-specific ATTs
  3. COMBINED: mega counties only, announced x 1[year>=2023]
  4. SANITY: pooled announced (should reproduce script 68 ~-0.5 ns)

Output: data/derived/salience_split.md
"""
from pathlib import Path
import numpy as np, pandas as pd
import pyfixest as pf
import warnings; warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "data" / "derived"

def fz(s): return s.astype(str).str.zfill(5)

Y0, Y1 = 2008, 2025
PHANTOMS = {"47121", "54047", "21127"}

# ── 1. Build treatment map (mirror script 68) ─────────────────────────────────
T = pd.read_csv(D / "treated_universe_labeled.csv", dtype={"county_fips": str})
T["county_fips"] = fz(T["county_fips"])
T = T[~T.county_fips.isin(PHANTOMS)].copy()
treated = set(T.county_fips)

anc = pd.read_csv(D / "announcement_anchor_county.csv", dtype={"county_fips": str})
anc["county_fips"] = fz(anc["county_fips"])
cty = pd.read_csv(D / "dc_announcement_years.csv", dtype={"county_fips": str})
cty["county_fips"] = fz(cty["county_fips"])

A = (
    T[["county_fips", "dc_class", "name", "mw_latest"]]
    .merge(anc[["county_fips", "ann_firstmaj"]], on="county_fips", how="left")
    .merge(cty[["county_fips", "announce_year"]], on="county_fips", how="left")
)
A["A_firstmaj"] = A["ann_firstmaj"].fillna(A["announce_year"])

amap = dict(zip(A.county_fips, A.A_firstmaj))
cls  = dict(zip(A.county_fips, A.dc_class))
nmap = dict(zip(A.county_fips, A.name))

# ── 2. MW at anchor year (from dose panel; fallback mw_latest) ────────────────
dose = pd.read_csv(D / "dc_dose_announced_mw_panel.csv", dtype={"county_fips": str})
dose["county_fips"] = fz(dose["county_fips"])
dose = dose.sort_values(["county_fips", "year"])
dose["delta_mw"] = dose.groupby("county_fips")["cum_ann_mw"].diff().fillna(dose["cum_ann_mw"])

# pull cum_ann_mw at anchor year for each treated county
dose_anchor_rows = []
for fips, grp in dose.groupby("county_fips"):
    if fips not in treated:
        continue
    anchor = amap.get(fips)
    if pd.isna(anchor):
        continue
    row = grp[grp.year == int(anchor)]
    if len(row) > 0:
        dose_anchor_rows.append({"county_fips": fips, "mw_anchor": row["cum_ann_mw"].values[0]})

dose_at_anchor = pd.DataFrame(dose_anchor_rows)

# Merge with treated; fallback to mw_latest
mw_df = A[["county_fips", "name", "dc_class", "mw_latest", "A_firstmaj"]].merge(
    dose_at_anchor, on="county_fips", how="left"
)
# Combined MW: prefer dose-derived anchor MW; fallback mw_latest
mw_df["mw_combined"] = mw_df["mw_anchor"].fillna(mw_df["mw_latest"])
# Drop counties without anchor (same filter as script 68: treated w/o anchor dropped)
mw_df = mw_df[mw_df.A_firstmaj.notna()].copy()

# ── 3. Define MEGA counties (top decile + >=300 MW alternative) ───────────────
p90 = mw_df["mw_combined"].quantile(0.90)
mega_decile = set(mw_df[mw_df.mw_combined >= p90].county_fips)
mega_300    = set(mw_df[mw_df.mw_combined >= 300].county_fips)

# Record mega county names for the report
mega_dec_names = sorted(
    [(fips, nmap[fips], mw_df.loc[mw_df.county_fips==fips,"mw_combined"].values[0],
      mw_df.loc[mw_df.county_fips==fips,"dc_class"].values[0])
     for fips in mega_decile if fips in nmap],
    key=lambda x: -x[2]
)
mega_300_names = sorted(
    [(fips, nmap[fips], mw_df.loc[mw_df.county_fips==fips,"mw_combined"].values[0],
      mw_df.loc[mw_df.county_fips==fips,"dc_class"].values[0])
     for fips in mega_300 if fips in nmap],
    key=lambda x: -x[2]
)

# ── 4. Build deal-level panel (mirror script 68) ──────────────────────────────
pan = pd.read_csv(D / "county_year_panel_v4.csv", dtype={"county_fips": str})
pan["county_fips"] = fz(pan["county_fips"])
never = (
    pan.groupby("county_fips")["n_dc_cumulative"].max()
    .pipe(lambda s: set(s[s == 0].index))
) - treated

d = pd.read_csv(D / "sdc_deal_spread.csv")
d["county_fips"] = fz(d["county_fips"].astype(int).astype(str))
r = pd.read_csv(D / "sdc_deal_rating.csv")
for x in (d, r):
    x["MASTER_DEAL_NO"] = pd.to_numeric(x["MASTER_DEAL_NO"], errors="coerce").astype("Int64")
d = d.merge(r, on="MASTER_DEAL_NO", how="left")
d = d[(d.AMT > 0) & d.year.between(Y0, Y1)].copy()
d["logamt"] = np.log(d.AMT)
d["logmat"] = np.log(d.par_wtd_yrs2mat.clip(lower=0.25))


def add_treat(df):
    """Exact mirror of script 68 add_treat."""
    df = df[df.county_fips.isin(treated | never)].copy()
    df["A"] = df.county_fips.map(amap)
    df = df[~(df.county_fips.isin(treated) & df.A.isna())].copy()
    df["announced"] = ((df.county_fips.isin(treated)) & (df.year >= df.A)).astype(int)
    df["dc_class"] = df.county_fips.map(cls)
    return df


d = add_treat(d)

# era indicators
d["post2022"]  = (d.year >= 2023).astype(int)
d["pre2023"]   = (d.year <= 2022).astype(int)
d["ann_post"]  = d["announced"] * d["post2022"]
d["ann_pre"]   = d["announced"] * d["pre2023"]

# mega flag on deals
d["is_mega_dec"] = d.county_fips.isin(mega_decile).astype(int)
d["is_mega_300"] = d.county_fips.isin(mega_300).astype(int)


# ── 5. Regression helpers ─────────────────────────────────────────────────────
CTRL = "logamt + logmat"
FE   = "county_fips + year"


def run_one(df, y, rhs, fe=FE):
    """Run a single feols, return (beta_dict, se_dict, pval_dict, N)."""
    s = df.dropna(subset=[y] + [c.strip() for c in CTRL.split("+") if c.strip()])
    f = f"{y} ~ {rhs} | {fe}"
    m = pf.feols(f, data=s, vcov={"CRV1": "county_fips"})
    return m.coef(), m.se(), m.pvalue(), int(m._N)


def star(p):
    return "***" if p < .01 else "**" if p < .05 else "*" if p < .10 else ""


def fmt_coef(b, se, p):
    return f"{b:+.2f} ({se:.2f}) p={p:.3f}{star(p)}"


def n_treated_counties(df):
    return df[df.county_fips.isin(treated)]["county_fips"].nunique()


def n_treated_post_deals(df):
    return int(((df.county_fips.isin(treated)) & (df.announced == 1)).sum())


# ── 6. Filter helper ──────────────────────────────────────────────────────────
def sub_cut(df, dc_classes):
    """Filter to controls + treated in given dc_class set."""
    return df[(df.county_fips.isin(never)) | (df.dc_class.isin(dc_classes))]


# ── Build results ─────────────────────────────────────────────────────────────
rows = []

def r_row(label, df, y, rhs, tag):
    try:
        coef, se, pv, N = run_one(df, y, rhs)
        for term in coef.index:
            rows.append({
                "label": label, "term": term, "tag": tag,
                "beta": coef[term], "se": se[term], "p": pv[term], "N": N,
                "n_tr_cty": n_treated_counties(df),
                "n_tr_post": n_treated_post_deals(df),
            })
    except Exception as e:
        rows.append({"label": label, "term": "ERR", "tag": tag,
                     "beta": np.nan, "se": np.nan, "p": np.nan,
                     "N": 0, "n_tr_cty": 0, "n_tr_post": 0, "err": str(e)})


# ── SANITY: pooled (should match script 68 ALL ~ -0.5 ns) ────────────────────
for nm, ks in [("ALL", ["clean_dc","crypto","mixed"]),
               ("clean_dc", ["clean_dc"]),
               ("crypto", ["crypto"])]:
    sub = sub_cut(d, ks)
    r_row(f"SANITY_spread_{nm}",  sub, "spread_bps",     "announced + " + CTRL, "sanity")
    r_row(f"SANITY_rating_{nm}", sub, "any_rated_share", "announced + " + CTRL, "sanity")

# ── MEGA split: top-decile vs rest ────────────────────────────────────────────
for nm, ks in [("ALL", ["clean_dc","crypto","mixed"]),
               ("clean_dc", ["clean_dc"])]:
    sub = sub_cut(d, ks)

    # MEGA group: controls + mega-treated
    mega_sub = sub[sub.county_fips.isin(never | mega_decile)].copy()
    r_row(f"MEGA_dec_spread_{nm}", mega_sub, "spread_bps",    "announced + " + CTRL, "mega_dec")
    r_row(f"MEGA_dec_rating_{nm}", mega_sub, "any_rated_share","announced + " + CTRL, "mega_dec")

    # REST group: controls + non-mega-treated
    rest_sub = sub[sub.county_fips.isin(never | (treated - mega_decile))].copy()
    r_row(f"REST_dec_spread_{nm}", rest_sub, "spread_bps",    "announced + " + CTRL, "rest_dec")
    r_row(f"REST_dec_rating_{nm}", rest_sub, "any_rated_share","announced + " + CTRL, "rest_dec")

    # MEGA >=300 MW alternative
    mega_300_sub = sub[sub.county_fips.isin(never | mega_300)].copy()
    r_row(f"MEGA_300_spread_{nm}", mega_300_sub, "spread_bps",    "announced + " + CTRL, "mega_300")
    r_row(f"MEGA_300_rating_{nm}", mega_300_sub, "any_rated_share","announced + " + CTRL, "mega_300")

# ── ERA split: announced x pre/post in one model ─────────────────────────────
# No base `announced` term — coefficients are period-specific ATTs
for nm, ks in [("ALL", ["clean_dc","crypto","mixed"]),
               ("clean_dc", ["clean_dc"])]:
    sub = sub_cut(d, ks)
    # Drop base "announced" — replace with ann_pre + ann_post (no collinearity issue since
    # they partition the post-announcement period)
    # Note: ann_pre and ann_post together = announced (with zero overlap since pre2023 + post2022 = 1 for all rows)
    r_row(f"ERA_spread_{nm}", sub, "spread_bps",    "ann_pre + ann_post + " + CTRL, "era")
    r_row(f"ERA_rating_{nm}", sub, "any_rated_share","ann_pre + ann_post + " + CTRL, "era")

# ── COMBINED: mega x post-2023 ────────────────────────────────────────────────
for nm, ks in [("ALL", ["clean_dc","crypto","mixed"]),
               ("clean_dc", ["clean_dc"])]:
    sub = sub_cut(d, ks)
    mega_sub = sub[sub.county_fips.isin(never | mega_decile)].copy()
    r_row(f"COMBINED_spread_{nm}", mega_sub, "spread_bps",    "ann_pre + ann_post + " + CTRL, "combined")
    r_row(f"COMBINED_rating_{nm}", mega_sub, "any_rated_share","ann_pre + ann_post + " + CTRL, "combined")

# ── Assemble DataFrame ────────────────────────────────────────────────────────
res = pd.DataFrame(rows)


# ── Format results into markdown sections ─────────────────────────────────────
L = []

L.append("# Salience-split heterogeneity test — bond spread & rating")
L.append("**Script:** `scripts/python/76_salience_split.py`  ")
L.append("**Date:** 2026-06-11  ")
L.append("**Hypothesis:** if bond-market non-response reflects limited attention, effects "
         "should appear in (a) mega-announcement counties and (b) post-2022 era.")
L.append("")

# ── Treatment / Control definition block ─────────────────────────────────────
L.append("## A. Sample construction")
L.append("")
L.append(f"**Treated universe:** {len(T)} counties (treated_universe_labeled.csv minus "
         f"phantoms 47121, 54047, 21127)")
L.append(f"**Controls:** {len(never):,} clean never-DC counties "
         f"(n_dc_cumulative == 0 in county_year_panel_v4; excludes all DC hosts)")
L.append(f"**Anchor (A_firstmaj):** DC-level ann_firstmaj (announcement_anchor_county.csv, "
         f"{len(anc)} counties); county-level fallback (dc_announcement_years.csv)")
L.append(f"**Sample years:** {Y0}–{Y1} (deal-level from sdc_deal_spread + sdc_deal_rating)")
L.append("")

L.append("**MW construction for MEGA split:**")
L.append(f"  - Primary: cum_ann_mw from dc_dose_announced_mw_panel at county anchor year "
         f"({dose_at_anchor.county_fips.nunique()} of {len(T)} treated counties covered)")
L.append(f"  - Fallback: mw_latest from treated_universe_labeled "
         f"(remaining {len(T) - dose_at_anchor.county_fips.nunique()} counties)")
L.append(f"  - Top-decile threshold (p90): **{p90:.0f} MW**")
L.append(f"  - Alternative cut: **>=300 MW**")
L.append("")

# Mega county list
n_dec = len(mega_decile)
n_300 = len(mega_300)
L.append(f"**Mega counties — top-decile (≥{p90:.0f} MW), n={n_dec}:**")
L.append("| FIPS | County name | mw_combined | dc_class |")
L.append("|---|---|---:|---|")
for fips, name, mw, dcl in mega_dec_names:
    L.append(f"| {fips} | {name} | {mw:.0f} | {dcl} |")
L.append("")

L.append(f"**Mega counties — ≥300 MW alternative, n={n_300}:**")
L.append("| FIPS | County name | mw_combined | dc_class |")
L.append("|---|---|---:|---|")
for fips, name, mw, dcl in mega_300_names:
    L.append(f"| {fips} | {name} | {mw:.0f} | {dcl} |")
L.append("")

# ── Helper to pull a result row ───────────────────────────────────────────────
def get_r(label, term, tag):
    hit = res[(res.label == label) & (res.term == term) & (res.tag == tag)]
    if len(hit) == 0:
        return None
    return hit.iloc[0]


def fmt_row(rw):
    if rw is None or pd.isna(rw["beta"]):
        err = rw.get("err", "missing") if rw is not None else "missing"
        return f"ERR ({str(err)[:30]})", "—", "—", "—"
    return (fmt_coef(rw["beta"], rw["se"], rw["p"]),
            f"{int(rw['N']):,}", f"{int(rw['n_tr_cty'])}", f"{int(rw['n_tr_post']):,}")


# ── SANITY block ─────────────────────────────────────────────────────────────
L.append("## B. Sanity check — pooled (reproduce script 68)")
L.append("")
L.append("| Cut | Outcome | announced beta (SE) p | N deals | N treated cty | N treated post deals |")
L.append("|---|---|---|---:|---:|---:|")

for nm, ks in [("ALL", None), ("clean_dc", None), ("crypto", None)]:
    for y_label, term in [("spread_bps", "announced"), ("any_rated_share", "announced")]:
        rw = get_r(f"SANITY_{y_label.split('_')[0]}{'_share' if 'rated' in y_label else ''}_{nm}",
                   term, "sanity")
        # fix label lookup
        if "spread" in y_label:
            lbl = f"SANITY_spread_{nm}"
        else:
            lbl = f"SANITY_rating_{nm}"
        rw = get_r(lbl, term, "sanity")
        fmted, N, nc, np_ = fmt_row(rw)
        L.append(f"| {nm} | {y_label} | {fmted} | {N} | {nc} | {np_} |")

L.append("")

# ── MEGA split block ──────────────────────────────────────────────────────────
L.append("## C. Mega split (top-decile ≥{:.0f} MW vs rest) — `announced` dummy".format(p90))
L.append("")
L.append("| Group | Cut | Outcome | beta (SE) p | N deals | N treated cty | N treated post |")
L.append("|---|---|---|---|---:|---:|---:|")

for nm in ["ALL", "clean_dc"]:
    for grp_tag, grp_label in [("mega_dec", "MEGA"), ("rest_dec", "REST")]:
        for y_label in ["spread_bps", "any_rated_share"]:
            ykey = "spread" if "spread" in y_label else "rating"
            lbl = f"{grp_label}_dec_{ykey}_{nm}"
            rw = get_r(lbl, "announced", grp_tag)
            fmted, N, nc, np_ = fmt_row(rw)
            L.append(f"| {grp_label}(≥{p90:.0f}MW) | {nm} | {y_label} | {fmted} | {N} | {nc} | {np_} |")

L.append("")
L.append("### C2. Alternative ≥300 MW cut")
L.append("")
L.append("| Group | Cut | Outcome | beta (SE) p | N deals | N treated cty | N treated post |")
L.append("|---|---|---|---|---:|---:|---:|")
for nm in ["ALL", "clean_dc"]:
    for y_label in ["spread_bps", "any_rated_share"]:
        ykey = "spread" if "spread" in y_label else "rating"
        lbl = f"MEGA_300_{ykey}_{nm}"
        rw = get_r(lbl, "announced", "mega_300")
        fmted, N, nc, np_ = fmt_row(rw)
        L.append(f"| MEGA(≥300MW) | {nm} | {y_label} | {fmted} | {N} | {nc} | {np_} |")

L.append("")

# ── ERA split block ───────────────────────────────────────────────────────────
L.append("## D. Era split — `announced × pre-2023` and `announced × post-2022`")
L.append("")
L.append("One regression with ann_pre + ann_post (no base announced); county+year FE, "
         "cluster county. Coefficients = period-specific ATTs.")
L.append("")
L.append("| Cut | Outcome | Period | beta (SE) p | N deals | N treated cty | N treated post |")
L.append("|---|---|---|---|---:|---:|---:|")

for nm in ["ALL", "clean_dc"]:
    for y_label in ["spread_bps", "any_rated_share"]:
        ykey = "spread" if "spread" in y_label else "rating"
        lbl = f"ERA_{ykey}_{nm}"
        for period_term, period_label in [("ann_pre", "≤2022"), ("ann_post", "≥2023")]:
            rw = get_r(lbl, period_term, "era")
            fmted, N, nc, np_ = fmt_row(rw)
            L.append(f"| {nm} | {y_label} | {period_label} | {fmted} | {N} | {nc} | {np_} |")

L.append("")

# ── COMBINED block ────────────────────────────────────────────────────────────
L.append("## E. Combined: mega counties × post-2022 (attention maximized)")
L.append("")
L.append("Mega-county sub-sample (controls + mega-treated), ann_pre + ann_post spec.")
L.append("")
L.append("| Cut | Outcome | Period | beta (SE) p | N deals | N treated cty | N treated post | Power flag |")
L.append("|---|---|---|---|---:|---:|---:|---|")

POWER_CTY = 15
POWER_DEALS = 100

for nm in ["ALL", "clean_dc"]:
    for y_label in ["spread_bps", "any_rated_share"]:
        ykey = "spread" if "spread" in y_label else "rating"
        lbl = f"COMBINED_{ykey}_{nm}"
        for period_term, period_label in [("ann_pre", "≤2022"), ("ann_post", "≥2023")]:
            rw = get_r(lbl, period_term, "combined")
            fmted, N, nc, np_ = fmt_row(rw)
            nc_int = int(nc) if nc != "—" else 0
            np_int = int(np_.replace(",","")) if np_ != "—" else 0
            pwr = ""
            if nc_int < POWER_CTY:
                pwr += f"⚠ <{POWER_CTY} treated cty "
            if np_int < POWER_DEALS:
                pwr += f"⚠ <{POWER_DEALS} post-deals"
            pwr = pwr.strip() or "OK"
            L.append(f"| {nm} | {y_label} | {period_label} | {fmted} | {N} | {nc} | {np_} | {pwr} |")

L.append("")

# ── 3-line summary ────────────────────────────────────────────────────────────
L.append("## F. Pre-specified prediction evaluation")
L.append("")

# Pull key cells for the summary
san_rw  = get_r("SANITY_spread_ALL", "announced", "sanity")
mega_rw = get_r("MEGA_dec_spread_ALL", "announced", "mega_dec")
rest_rw = get_r("REST_dec_spread_ALL", "announced", "rest_dec")
era_post_rw = get_r("ERA_spread_ALL", "ann_post", "era")
era_pre_rw  = get_r("ERA_spread_ALL", "ann_pre",  "era")
comb_post_rw = get_r("COMBINED_spread_ALL", "ann_post", "combined")

def brief(rw):
    if rw is None or pd.isna(rw["beta"]):
        return "ERR"
    return f"{rw['beta']:+.2f} (p={rw['p']:.3f})"

L.append(f"**Sanity:** pooled spread = {brief(san_rw)} — reproduces script 68 null as expected.")
L.append("")

mega_vs_rest = ""
if mega_rw is not None and rest_rw is not None and not pd.isna(mega_rw['beta']) and not pd.isna(rest_rw['beta']):
    if mega_rw['p'] < 0.10 and mega_rw['beta'] < 0 and rest_rw['p'] >= 0.10:
        mega_vs_rest = "CONSISTENT with attention hypothesis: mega negative and significant, rest null."
    elif mega_rw['p'] >= 0.10 and rest_rw['p'] >= 0.10:
        mega_vs_rest = "NOT consistent: both mega and rest null; announcement size does not shift the non-response."
    elif mega_rw['beta'] < rest_rw['beta']:
        mega_vs_rest = f"PARTIALLY consistent: mega ({brief(mega_rw)}) more negative than rest ({brief(rest_rw)}) but neither significant."
    else:
        mega_vs_rest = f"INCONSISTENT: mega ({brief(mega_rw)}) not more negative than rest ({brief(rest_rw)})."

L.append(f"**MEGA split:** {mega_vs_rest}")
L.append("")

era_summary = ""
if era_post_rw is not None and era_pre_rw is not None and not pd.isna(era_post_rw['beta']):
    if era_post_rw['p'] < 0.10 and era_post_rw['beta'] < 0 and era_pre_rw['p'] >= 0.10:
        era_summary = "CONSISTENT: post-2022 negative and significant, pre-2023 null; temporal salience shift detected."
    elif era_post_rw['p'] >= 0.10 and era_pre_rw['p'] >= 0.10:
        era_summary = "NOT consistent: both periods null; bond market non-response is uniform across eras."
    elif era_post_rw['beta'] < era_pre_rw['beta']:
        era_summary = (f"PARTIALLY consistent: post-2022 ({brief(era_post_rw)}) more negative than pre-2023 "
                       f"({brief(era_pre_rw)}) but post-2022 not significant at 10%.")
    else:
        era_summary = (f"INCONSISTENT: post-2022 ({brief(era_post_rw)}) not more negative than pre-2023 "
                       f"({brief(era_pre_rw)}).")

L.append(f"**ERA + COMBINED summary:** {era_summary} "
         f"Combined mega × post-2023 = {brief(comb_post_rw)}. "
         f"Overall verdict: the pre-specified attention hypothesis finds "
         + ("SUPPORT" if (era_post_rw is not None and not pd.isna(era_post_rw['beta'])
                          and era_post_rw['p'] < 0.10 and era_post_rw['beta'] < 0)
            else "NO SUPPORT") +
         " in this sample.")
L.append("")

out = D / "salience_split.md"
out.write_text("\n".join(L))
print("\n".join(L))
print(f"\nWrote {out}")
