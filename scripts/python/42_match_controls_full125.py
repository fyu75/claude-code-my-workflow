"""
42_match_controls_full125.py

Expand the matched-control design from the 22-treated subset to ALL 125 treated
counties (dc_share_mid >= 1%), 1:3 matching on 2017 Census ACFR property tax.

Fix vs script 25: treated set is defined from dc_tax_share_distribution.csv
(dc_share_mid >= 1%), NOT from acfr_county_year_extracted_wide.csv (which now
contains D2 *control* counties and would mislabel them as treated).

Matching rule (same as script 25):
  1. control in SAME STATE as treated
  2. control has NO data center (never-treated; filter against S&P 451)
  3. 2017 property tax within 0.5x-2x of treated; else fallback to nearest by log-dist
  4. 3 closest by |log(pt_control) - log(pt_treated)|

Matching only needs the 2017 baseline (national Census coverage). The script then
reports POST-PERIOD coverage (V2 MuniSpot OR scraped ACFR) so we know how many
pairs are actually runnable in the 2-period DiD vs. still need control scraping.

Output: data/derived/matched_controls_full125.csv  (does NOT overwrite the
22-treated matched_controls.csv).
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DERIVED = ROOT / "data" / "derived"

def fz(s): return s.astype(str).str.zfill(5)

# ---- Treated = dc_share_mid >= 1% (the 125), the CORRECT source ----
dist = pd.read_csv(DERIVED / "dc_tax_share_distribution.csv"); dist["county_fips"] = fz(dist["county_fips"])
treated_fips = sorted(dist.loc[dist["dc_share_mid"] >= 1.0, "county_fips"].unique())
print(f"Treated counties (dc_share_mid >= 1%): {len(treated_fips)}")

# ---- 2017 Census ACFR baseline ----
acfr = pd.read_csv(DERIVED / "acfr_2017_county_govt_only.csv")
acfr["county_fips"] = fz(acfr["county_fips"]); acfr["state_fips"] = acfr["county_fips"].str[:2]

# ---- DC counties to exclude from controls ----
dc = pd.read_csv(DERIVED / "dc_property_county_fips.csv", low_memory=False)
dc["county_fips"] = fz(dc["county_fips"])
dc_counties = set(dc.loc[dc["county_fips"].str.match(r"^\d{5}$"), "county_fips"].unique())

treated_profile = acfr[acfr["county_fips"].isin(treated_fips)][["county_fips", "state_fips", "rev_property_tax"]] \
    .rename(columns={"rev_property_tax": "pt_2017_treated"})
no_baseline = sorted(set(treated_fips) - set(treated_profile["county_fips"]))
print(f"Treated WITH 2017 baseline: {treated_profile['county_fips'].nunique()}  |  WITHOUT: {len(no_baseline)} {no_baseline[:8]}")

candidates = acfr[~acfr["county_fips"].isin(dc_counties)].copy()
candidates = candidates[candidates["rev_property_tax"].notna() & (candidates["rev_property_tax"] > 0)]
print(f"Never-DC control candidates (2017 PT>0): {len(candidates)}")

N_CONTROLS, MIN_RATIO, MAX_RATIO = 3, 0.5, 2.0
matches = []
for _, row in treated_profile.iterrows():
    fips, state, pt_t = row["county_fips"], row["state_fips"], row["pt_2017_treated"]
    if pd.isna(pt_t) or pt_t <= 0:
        continue
    pool = candidates[candidates["state_fips"] == state].copy()
    if len(pool) == 0:
        matches.append({"treated_fips": fips, "treated_state": state, "pt_2017_treated": pt_t,
                        "control_fips": np.nan, "pt_2017_control": np.nan, "ratio": np.nan,
                        "band_status": "NO_SAME_STATE_CANDIDATE"})
        continue
    pool["ratio"] = pool["rev_property_tax"] / pt_t
    in_band = pool[(pool["ratio"] >= MIN_RATIO) & (pool["ratio"] <= MAX_RATIO)].copy()
    if len(in_band) < N_CONTROLS:
        pool["log_dist"] = (np.log(pool["rev_property_tax"]) - np.log(pt_t)).abs()
        top = pool.nsmallest(N_CONTROLS, "log_dist"); band = "FALLBACK"
    else:
        in_band["log_dist"] = (np.log(in_band["rev_property_tax"]) - np.log(pt_t)).abs()
        top = in_band.nsmallest(N_CONTROLS, "log_dist"); band = "OK"
    for _, c in top.iterrows():
        matches.append({"treated_fips": fips, "treated_state": state, "pt_2017_treated": pt_t,
                        "control_fips": c["county_fips"], "pt_2017_control": c["rev_property_tax"],
                        "ratio": c["rev_property_tax"] / pt_t, "band_status": band})

m = pd.DataFrame(matches)

# ---- POST-PERIOD coverage assessment ----
v2 = pd.read_parquet(DERIVED / "muni_property_tax_v2_classified_gf_only_FY2016_2026.parquet",
                     columns=["county_fips", "tier_with_pilot"])
v2["county_fips"] = fz(v2["county_fips"])
v2_pt = set(v2.loc[v2["tier_with_pilot"] == True, "county_fips"])
wide = pd.read_csv(DERIVED / "acfr_county_year_extracted_wide.csv"); wide["county_fips"] = fz(wide["county_fips"])
acfr_pt = set(wide.loc[wide["property_tax_gf"].notna() | wide["property_tax_allfunds"].notna(), "county_fips"])
post = v2_pt | acfr_pt

m["control_post_covered"] = m["control_fips"].isin(post)
m["treated_post_covered"] = m["treated_fips"].isin(post)
m.to_csv(DERIVED / "matched_controls_full125.csv", index=False)

# ---- Report ----
valid = m[m["control_fips"].notna()]
print(f"\nWrote matched_controls_full125.csv: {len(valid)} pairs, "
      f"{valid['treated_fips'].nunique()} treated, {valid['control_fips'].nunique()} unique controls")
print(f"Band status: {dict(m['band_status'].value_counts())}")
n_per = valid.groupby("treated_fips").size()
print(f"Treated with full 3 matches: {(n_per==3).sum()}  |  <3: {(n_per<3).sum()}")

print("\n--- POST-PERIOD usability (need PT for BOTH treated & control) ---")
print(f"Treated post-covered: {valid['treated_post_covered'].any() and valid.loc[valid['treated_post_covered'],'treated_fips'].nunique()} / {valid['treated_fips'].nunique()}")
usable = valid[valid["treated_post_covered"] & valid["control_post_covered"]]
print(f"Fully-usable pairs (both sides post-covered): {len(usable)}")
print(f"Treated with >=1 usable control: {usable['treated_fips'].nunique()} / {valid['treated_fips'].nunique()}")
print(f"Treated with all-3 usable: {(usable.groupby('treated_fips').size()==3).sum()}")
need_scrape = set(valid.loc[~valid['control_post_covered'],'control_fips']) - post
print(f"Unique matched controls still NEEDING post-period data (not in V2 or ACFR): {len(need_scrape)}")
