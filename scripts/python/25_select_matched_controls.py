"""
25_select_matched_controls.py

Select matched-control counties for the 2-period DiD (2017 → 2025).

Strategy:
- For each of the 23 treated (high-DC-share) counties, find 3 controls that:
  1. Are in the SAME STATE
  2. Have NO data center as of 2025 (filter against S&P 451)
  3. Have 2017 property tax revenue within 0.5x-2x of treated
  4. Are closest in 2017 property tax (size proxy)

Output: data/derived/matched_controls.csv
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DERIVED = ROOT / "data" / "derived"

# 1) Treated counties (from extraction wide file — anyone we have a PDF for)
treated_df = pd.read_csv(DERIVED / "acfr_county_year_extracted_wide.csv")
treated_fips = sorted(treated_df["county_fips"].astype(str).str.zfill(5).unique())
print(f"Treated counties (have PDF): {len(treated_fips)}")

# 2) All DC counties (to exclude from controls — any county hosting any DC)
dc = pd.read_csv(DERIVED / "dc_property_county_fips.csv", low_memory=False)
dc["county_fips"] = dc["county_fips"].astype(str).str.zfill(5)
dc_counties = set(dc.loc[dc["county_fips"].str.match(r"^\d{5}$"), "county_fips"].unique())
print(f"Counties with any DC: {len(dc_counties)}")

# 3) 2017 ACFR baseline (county-government records only)
acfr = pd.read_csv(DERIVED / "acfr_2017_county_govt_only.csv")
acfr["county_fips"] = acfr["county_fips"].astype(str).str.zfill(5)
acfr["state_fips"] = acfr["county_fips"].str[:2]
print(f"ACFR 2017 county-govt records: {len(acfr)}")

# 4) Build treated profile (2017 property tax level + state)
treated_profile = acfr[acfr["county_fips"].isin(treated_fips)][
    ["county_fips", "state_fips", "rev_property_tax"]
].copy()
treated_profile = treated_profile.rename(columns={"rev_property_tax": "pt_2017_treated"})

missing = set(treated_fips) - set(treated_profile["county_fips"])
print(f"Treated missing 2017 ACFR baseline: {len(missing)} ({sorted(missing)[:5]})")

# 5) Candidate control universe: ALL counties except DC-counties and treated themselves
candidates = acfr[~acfr["county_fips"].isin(dc_counties)].copy()
candidates = candidates[candidates["rev_property_tax"].notna() & (candidates["rev_property_tax"] > 0)]
print(f"Never-DC control candidates: {len(candidates)}")

# 6) For each treated, find 3 best matches
N_CONTROLS = 3
MIN_RATIO, MAX_RATIO = 0.5, 2.0

matches = []
for _, row in treated_profile.iterrows():
    fips = row["county_fips"]
    state = row["state_fips"]
    pt_t = row["pt_2017_treated"]
    if pd.isna(pt_t) or pt_t <= 0:
        continue

    pool = candidates[candidates["state_fips"] == state].copy()
    if len(pool) == 0:
        continue

    pool["ratio"] = pool["rev_property_tax"] / pt_t
    in_band = pool[(pool["ratio"] >= MIN_RATIO) & (pool["ratio"] <= MAX_RATIO)].copy()

    if len(in_band) < N_CONTROLS:
        # Fall back: drop the band, just pick nearest by log-distance
        pool["log_dist"] = (np.log(pool["rev_property_tax"]) - np.log(pt_t)).abs()
        top = pool.nsmallest(N_CONTROLS, "log_dist")
        band_status = "FALLBACK"
    else:
        in_band["log_dist"] = (np.log(in_band["rev_property_tax"]) - np.log(pt_t)).abs()
        top = in_band.nsmallest(N_CONTROLS, "log_dist")
        band_status = "OK"

    for _, c in top.iterrows():
        matches.append({
            "treated_fips": fips,
            "treated_state": state,
            "pt_2017_treated": pt_t,
            "control_fips": c["county_fips"],
            "pt_2017_control": c["rev_property_tax"],
            "ratio": c["rev_property_tax"] / pt_t,
            "band_status": band_status,
        })

m = pd.DataFrame(matches)
out_path = DERIVED / "matched_controls.csv"
m.to_csv(out_path, index=False)
print(f"\nWrote {out_path}: {len(m)} pairs across {m['treated_fips'].nunique()} treated counties")
print(f"\nBy state:")
print(m.groupby("treated_state").size().rename("n_pairs"))
print(f"\nBand status:")
print(m["band_status"].value_counts())
print(f"\nFirst 10 pairs:")
print(m.head(10).to_string(index=False))
