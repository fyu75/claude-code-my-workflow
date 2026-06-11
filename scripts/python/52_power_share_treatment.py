"""
52_power_share_treatment.py

ALTERNATIVE treatment-intensity definition: DC electricity as a share of county
total electricity consumption — a PHYSICAL importance measure, to sit alongside the
current FISCAL one (DC tax $ / county property tax, the dc_share_mid >=1% cut).

Why: the current `dc_share_mid` is a linear rescaling of S&P 451 MW capacity
(corr(mw_latest, dc_tax_M_mid)=1.000; numerator = MW x $50k/MW) divided by county
property-tax revenue. It is (a) constructed (assessment x rate assumptions, broken by
NCSL abatements) and (b) UNBOUNDED — it exceeds 100% for small counties (Lawrence KY
191%). A power share (DC MWh / county MWh) is bounded-in-spirit, physical, and robust
to tax-incentive heterogeneity. We keep fiscal share PRIMARY (it is on the paper's
causal path DC -> tax base -> muni finances); power share is a treatment VALIDATION
and a continuous dose for event studies.

Numerator  : DC total-facility electricity (MWh/yr) = mw_latest x 8760 x LOAD x PUE.
             S&P 451 mw_latest is (critical IT) capacity; LOAD = utilization (~0.6-0.8),
             PUE = total-facility/IT overhead (~1.4-1.6). The multiplier scales the share
             LEVEL but NOT the cross-county ranking, so the overlap question is robust.
Denominator: county total electricity (res+com+ind) MWh, NREL/OpenEI 2016 county energy
             profiles (data/derived/county_electricity_2016_nrel.csv; US total 3,529 TWh,
             matches EIA 2016 retail ~3,800 for a modeled set). 2016 = pre-boom baseline,
             so the share reads as DC size relative to the county's baseline load.

Outputs:
  data/derived/power_share_treatment.csv   one row per DC county: MW, DC MWh, county MWh,
                                           power_share (+ low/high sensitivity), fiscal share
  data/derived/power_vs_fiscal_treatment.md  overlap of the two treatment cuts, rank corr
"""
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]; D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)

# --- numerator assumptions (the one modeling choice) ---
LOAD, PUE = 0.70, 1.50           # effective ~9,198 MWh per MW-yr
HRS = 8760
def dc_mwh(mw, load, pue): return mw * HRS * load * pue

# --- DC MW + fiscal treatment ---
tax = pd.read_csv(D/"dc_tax_share_distribution.csv", dtype={"county_fips":str})
tax["county_fips"] = fz(tax["county_fips"])
tax = tax[tax["mw_latest"] > 0].copy()

# --- county electricity denominator (NREL 2016) ---
ce = pd.read_csv(D/"county_electricity_2016_nrel.csv", dtype={"county_fips":str})
ce["county_fips"] = fz(ce["county_fips"])

df = tax.merge(ce[["county_fips","elec_total_mwh","population"]], on="county_fips", how="left")

df["dc_mwh"]       = dc_mwh(df["mw_latest"], LOAD, PUE)
df["dc_mwh_low"]   = dc_mwh(df["mw_latest"], 0.55, 1.35)   # conservative
df["dc_mwh_high"]  = dc_mwh(df["mw_latest"], 0.85, 1.60)   # aggressive
df["power_share"]      = 100 * df["dc_mwh"]      / df["elec_total_mwh"]
df["power_share_low"]  = 100 * df["dc_mwh_low"]  / df["elec_total_mwh"]
df["power_share_high"] = 100 * df["dc_mwh_high"] / df["elec_total_mwh"]

keep = ["county_fips","name","state","mw_latest","mw_peak","elec_total_mwh","population",
        "dc_mwh","dc_mwh_low","dc_mwh_high","power_share","power_share_low","power_share_high",
        "prop_tax_2017_M","dc_share_mid"]
out = df[keep].sort_values("power_share", ascending=False)
out.to_csv(D/"power_share_treatment.csv", index=False)

n_nomatch = int(df["elec_total_mwh"].isna().sum())

# --- compare the two treatment definitions ---
c = df.dropna(subset=["elec_total_mwh","dc_share_mid","power_share"]).copy()
c["fiscal_treated"] = (c["dc_share_mid"] >= 1.0).astype(int)

# choose a power-share threshold that matches the treated-set SIZE of the fiscal >=1% cut,
# so the two cuts are size-comparable; also report a round 1% power cut.
n_fiscal = int(c["fiscal_treated"].sum())
thr_sizematched = float(np.sort(c["power_share"])[::-1][n_fiscal-1])  # power cut giving same N
for thr, tag in [(thr_sizematched, f"size-matched ({thr_sizematched:.2f}%)"), (1.0, "round 1%")]:
    c[f"pt_{tag}"] = (c["power_share"] >= thr).astype(int)

def overlap(a, b):
    both = int(((c[a]==1)&(c[b]==1)).sum())
    only_a = int(((c[a]==1)&(c[b]==0)).sum())
    only_b = int(((c[a]==0)&(c[b]==1)).sum())
    jac = both / (both+only_a+only_b) if (both+only_a+only_b) else np.nan
    return both, only_a, only_b, jac

sm_tag = f"size-matched ({thr_sizematched:.2f}%)"
both, f_only, p_only, jac = overlap("fiscal_treated", f"pt_{sm_tag}")
rho = stats.spearmanr(c["dc_share_mid"], c["power_share"]).correlation
rho_mw = stats.spearmanr(c["mw_latest"], c["power_share"]).correlation

L = ["# Power-Share vs Fiscal-Share Treatment Definition\n",
     "**Date:** 2026-06-10. `scripts/python/52`. DC electricity / county electricity (physical "
     "intensity) vs the current DC-tax / county-property-tax >=1% cut (fiscal intensity).\n",
     f"**Numerator assumption:** DC MWh = MW x 8760 x {LOAD} (load) x {PUE} (PUE) "
     f"= {HRS*LOAD*PUE:,.0f} MWh/MW-yr. Sensitivity band: low (0.55x1.35) - high (0.85x1.60).\n",
     f"**Denominator:** NREL/OpenEI 2016 county total electricity (res+com+ind).\n",
     "## Coverage",
     f"- DC counties with MW>0: **{len(df)}**; matched to NREL electricity: **{len(c)}** "
     f"({n_nomatch} unmatched FIPS)",
     f"- Fiscal-treated (dc_share_mid>=1%): **{n_fiscal}**", "",
     "## How physical and fiscal intensity relate",
     f"- Spearman rank corr( fiscal dc_share_mid , power_share ) = **{rho:.3f}**",
     f"- Spearman rank corr( MW , power_share ) = {rho_mw:.3f}  (power share is NOT just MW — "
     "county size matters)", "",
     "## Do the two cuts select the same counties?",
     f"- Power cut set to match fiscal treated-set size (N={n_fiscal}) -> threshold "
     f"**power_share >= {thr_sizematched:.2f}%**",
     f"- **In BOTH: {both}** | fiscal-only: {f_only} | power-only: {p_only} | "
     f"Jaccard overlap **{jac:.2f}**", "",
     "## Top 20 counties by power share", "",
     "| FIPS | County | ST | MW | power % (low–high) | fiscal % | pop |",
     "|---|---|---|---:|---:|---:|---:|"]
for _, r in out.head(20).iterrows():
    pop = "" if pd.isna(r["population"]) else f"{int(r['population']):,}"
    ps = "n/a" if pd.isna(r["power_share"]) else \
         f"{r['power_share']:.1f} ({r['power_share_low']:.1f}–{r['power_share_high']:.1f})"
    L.append(f"| {r['county_fips']} | {r['name']} | {r['state']} | {r['mw_latest']:.0f} | "
             f"{ps} | {r['dc_share_mid']:.0f} | {pop} |")

L += ["", "## Reading guide",
      "- High rank corr + high Jaccard => the physical and fiscal cuts agree; power share buys "
      "OBJECTIVITY (no assessment/abatement assumptions) essentially for free, and gives a "
      "bounded continuous dose for intensity event-studies.",
      "- Divergent counties are themselves informative: fiscal-only = DC is a big share of a "
      "small tax base but not of county load (or vice-versa); inspect for abatement vs "
      "industrial-county cases.",
      "- Caveat: NREL county electricity is MODELED (2016 base year); DC MWh is derived from "
      "nameplate MW via load+PUE, not metered. Ranking is multiplier-invariant; the threshold "
      "is not.", ""]

(D/"power_vs_fiscal_treatment.md").write_text("\n".join(L))
print("\n".join(L))
print("\nWrote data/derived/power_share_treatment.csv and power_vs_fiscal_treatment.md")
