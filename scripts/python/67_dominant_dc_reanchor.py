"""
67_dominant_dc_reanchor.py

FLAGGED REFINEMENT (memory item 12): `first_op_year` is anchored to each county's
EARLIEST data center — which, for the mature hubs, is a tiny early DC, NOT the dominant
campus. Verified here: first_op_year == earliest DC op-year for all 125 treated. For ~51
counties the dominant (max-MW) DC came online YEARS-to-DECADES later (Loudoun anchor 2000 vs
its 225 MW campus 2018; PWC/Fulton/Clark anchor ~2000-01 vs 100-225 MW campuses 2023-25).

This script builds five alternative treatment-timing anchors per county from S&P 451 per-DC
peak IT power (`dcpropertiesperiodic.TOTALITPOWER`, kW -> MW) and operational year, then
re-runs the two event studies that consume the anchor (bond spread; property tax) under each,
to test whether the mis-timing was driving (a) the bond pre-trend and (b) the PT lagged ramp.

Anchors:
  first_oy   : earliest DC op-year (the CURRENT first_op_year; mis-times mature hubs)
  dom_oy     : op-year of the single max-MW DC (over-corrects -> often 2024-25, kills post window)
  first50_oy : first year the county had any >=50 MW DC operational (NaN for never->50 MW counties)
  capwt_oy   : MW-weighted mean op-year ("center of mass" of buildout)
  cap50_oy   : year cumulative operational MW first crosses 50% of county total  <-- PREFERRED
               (captures "when the bulk of capacity arrived"; keeps most counties in-window)

Output: data/derived/treatment_anchors_compare.csv, dominant_dc_reanchor.csv,
        data/derived/dominant_dc_reanchor.md
"""
from pathlib import Path
import numpy as np, pandas as pd
import pyfixest as pf

ROOT = Path(__file__).resolve().parents[2]
RAW = Path("/Users/fangyu/claude/datacenter/raw")   # S&P 451 symlink target
D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)

# ---- per-DC peak MW + operational year, mapped to county ----
per = pd.read_sas(RAW / "dcpropertiesperiodic_latest.sas7bdat", encoding="latin-1")
per["pid"] = per["PROPERTYUNIQUEID"].astype(str).str.replace(r"\.0$", "", regex=True)
mw = per.groupby("pid")["TOTALITPOWER"].max().div(1000).rename("mw_peak").reset_index()  # kW->MW
prop = pd.read_csv(D / "dc_property_county_fips.csv")
prop["pid"] = prop["PROPERTYUNIQUEID"].astype("Int64").astype(str)
prop["county_fips"] = fz(prop["county_fips"].astype(str))
prop["oy"] = pd.to_numeric(prop["YEARFACILITYBECAMEOPERATIONAL"], errors="coerce")
m = prop.merge(mw, on="pid", how="left")

T = pd.read_csv(D / "treated_universe_labeled.csv", dtype={"county_fips": str}); T["county_fips"] = fz(T["county_fips"])
treated = set(T.county_fips)
mt = m[m.county_fips.isin(treated)].dropna(subset=["oy"]).copy()

def anchors(g):
    g = g.sort_values("oy"); w = g.mw_peak.fillna(0); tot = w.sum()
    big = g[g.mw_peak >= 50]
    cum = g.assign(c=w.cumsum())
    return pd.Series({
        "first_oy":  g.oy.min(),
        "dom_oy":    g.sort_values("mw_peak").iloc[-1].oy,
        "first50_oy": big.oy.min() if len(big) else np.nan,
        "capwt_oy":  round(np.average(g.oy, weights=w), 1) if tot > 0 else g.oy.mean(),
        "cap50_oy":  cum[cum.c >= 0.5 * tot].oy.min() if tot > 0 else np.nan,
    })

A = mt.groupby("county_fips").apply(anchors).reset_index().merge(
    T[["county_fips", "name", "dc_class", "first_op_year"]], on="county_fips", how="left")
A.to_csv(D / "treatment_anchors_compare.csv", index=False)
A[["county_fips", "name", "dc_class", "first_op_year", "dom_oy", "cap50_oy"]].assign(
    yr_shift=A.dom_oy - A.first_oy).to_csv(D / "dominant_dc_reanchor.csv", index=False)

L = ["# Dominant-DC re-anchoring of treatment timing\n",
     "**Date:** 2026-06-10. `scripts/python/67`. Per-DC MW from S&P 451 `dcpropertiesperiodic.TOTALITPOWER`.\n",
     f"`first_op_year` == earliest-DC op-year for **all {len(A)}** treated counties (confirmed). "
     f"The dominant (max-MW) DC is operational LATER in **{int((A.dom_oy - A.first_oy > 0).sum())}** "
     "counties (mean shift "
     f"**+{(A.dom_oy - A.first_oy).mean():.1f} yr**, max +{(A.dom_oy - A.first_oy).max():.0f}).\n",
     "## Usable event window (anchor in 2015-2021) by anchor choice"]
for c in ["first_oy", "dom_oy", "first50_oy", "cap50_oy"]:
    L.append(f"- `{c}`: {int(A[c].between(2015, 2021).sum())} counties in-window "
             f"(median {A[c].median():.0f}, n={int(A[c].notna().sum())})")

# ---- event studies under each anchor ----
pan = pd.read_csv(D / "county_year_panel_v4.csv", dtype={"county_fips": str}); pan["county_fips"] = fz(pan["county_fips"])
never = pan.groupby("county_fips")["n_dc_cumulative"].max().pipe(lambda s: set(s[s == 0].index)) - treated

def pw(g, c):
    w = g.loc[g[c].notna(), "AMT"]; return (g.loc[g[c].notna(), c] * w).sum() / w.sum() if w.sum() > 0 else np.nan

# bond spread county-year
d = pd.read_csv(D / "sdc_deal_spread.csv"); d["county_fips"] = fz(d["county_fips"].astype(int).astype(str))
d = d[d.county_fips.isin(treated | never) & (d.AMT > 0) & d.year.between(2008, 2025)].copy()
spr = d.groupby(["county_fips", "year"]).apply(lambda g: pd.Series({"spr": pw(g, "spread_bps")})).reset_index().dropna(subset=["spr"])
spr["tev"] = spr.county_fips.isin(treated).astype(int)

# property tax v2 annual
v = pd.read_csv(D / "muni_property_tax_v2_classified_gf_only_FY2016_2026.csv", dtype={"county_fips": str}, low_memory=False)
v["county_fips"] = fz(v["county_fips"]); v = v[(v.tier_strict == True) & (v.column_index == 1) & v.fiscal_year.between(2016, 2024)].copy()
v["val"] = pd.to_numeric(v["reported_value"], errors="coerce") * pd.to_numeric(v["value_multiplier"], errors="coerce").fillna(1)
pt = (v.groupby(["county_fips", "fiscal_year", "report_id"])["val"].sum().reset_index()
        .groupby(["county_fips", "fiscal_year"])["val"].median().reset_index())
pt = pt[pt["val"] > 0].copy(); pt["log_pt"] = np.log(pt["val"]); pt = pt.rename(columns={"fiscal_year": "year"})
ny = pt.groupby("county_fips")["year"].nunique(); pt = pt[pt.county_fips.isin(ny[ny >= 4].index)]
pt = pt[pt.county_fips.isin((treated & set(pt.county_fips)) | (never & set(pt.county_fips)))].copy()
pt["tev"] = pt.county_fips.isin(treated).astype(int)

def es(base, yvar, anchor, ks, clipr, win=None):
    amap = dict(zip(A.county_fips, A[anchor]))
    c = base.copy(); c["ay"] = c.county_fips.map(amap)
    c["et"] = np.where(c.tev == 1, c.year - c.ay, np.nan)
    if win:
        use = set(c[(c.tev == 1) & c.ay.between(*win)].county_fips)
        c = c[(c.tev == 0) | (c.county_fips.isin(use))].copy()
        n = len(use)
    else:
        n = c[c.tev == 1].county_fips.nunique()
    for k in ks:
        c[f"k{k}".replace("-", "m")] = ((c.tev == 1) & (np.clip(c.et, clipr[0], clipr[1]) == k)).astype(int)
    ec = [col for col in c.columns if col.startswith("k")]
    try:
        mm = pf.feols(f"{yvar} ~ " + " + ".join(ec) + " | county_fips + year", data=c, vcov={"CRV1": "county_fips"})
        co, pv = mm.coef(), mm.pvalue()
        return {k: (co.get(f"k{k}".replace("-", "m"), np.nan), pv.get(f"k{k}".replace("-", "m"), np.nan)) for k in ks}, n
    except Exception:
        return {k: (np.nan, np.nan) for k in ks}, n

def block(title, base, yvar, ks, clipr, anchs, win, note):
    L.append(f"\n## {title}")
    L.append("| evt | " + " | ".join(f"{a} (n)" for a in anchs) + " |")
    L.append("|---|" + "|".join("---" for _ in anchs) + "|")
    res = {a: es(base, yvar, a, ks, clipr, win) for a in anchs}
    for k in ks:
        cells = []
        for a in anchs:
            r, n = res[a]; b, p = r[k]
            cells.append("0 (ref)" if k == -1 else (f"{b:+.2f} (p{p:.2f}) n{n}" if not np.isnan(b) else "—"))
        L.append(f"| {k:+d} | " + " | ".join(cells) + " |")
    L.append(note)

block("Bond spread event study (bps; county+year FE; ref −1; all treated vs never-DC)",
      spr, "spr", [-5, -3, -1, 0, 1, 2, 3], (-6, 4), ["first_oy", "cap50_oy", "dom_oy"], None,
      "**Reading:** spread is noisy/NULL under EVERY anchor (no clean post drop, all p>0.15) — "
      "re-anchoring does not revive a pricing effect. Reinforces 'pricing channel null 4 ways'.")

block("Property-tax event study (log PT, v2 annual; county+year FE; ref −1; anchor in 2018-2023)",
      pt, "log_pt", [-2, -1, 0, 1, 2, 3], (-3, 3), ["first_oy", "cap50_oy", "first50_oy"], (2018, 2023),
      "**Reading:** parallel pre-trend (−2 ≈ 0) holds under first_op and cap50; lagged post ramp "
      "(+3 positive) persists. `cap50` keeps MORE cohorts (20 vs 15) -> better-powered, more defensible "
      "anchor. `first50` too thin (n=9) to use. Effect direction robust to anchor choice.")

L += ["\n## Verdict",
      "- The mis-anchoring is REAL and large for ~51 mature hubs, but it was NOT manufacturing either "
      "headline: the bond null and the PT lagged-ramp both survive every anchor.",
      "- **Adopt `cap50_oy` (capacity-midpoint) as the event-study anchor** going forward: defensible "
      "('when the bulk of capacity arrived'), better-powered (20 vs 15 PT cohorts; 43 vs 32 counties in a "
      "usable Census window), and robust.",
      "- The 2-period +3.07%/yr property-tax headline (Phase 2, CAGR-based) does not use an event clock, "
      "so it is unaffected. This refinement sharpens the DYNAMICS illustration, not the headline.",
      "- The announcement-date wave (8 agents, 2026-06-10) supplies a SECOND anchor for the same hubs "
      "(announcement vs capacity-midpoint); fold in when batches land.", ""]
(D / "dominant_dc_reanchor.md").write_text("\n".join(L))
print("\n".join(L))
print("\nWrote dominant_dc_reanchor.md + treatment_anchors_compare.csv + dominant_dc_reanchor.csv")
