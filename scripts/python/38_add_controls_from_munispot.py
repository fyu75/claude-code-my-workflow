"""
Add matched-control county PT data from MuniSpot v2 to the wide CSV.
Controls don't have DC-specific tax structures (FILOT/IDA leasehold),
so v2 data is reliable for them. Uses tier_with_pilot (widest coverage).
"""
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WIDE_CSV = ROOT / "data/derived/acfr_county_year_extracted_wide.csv"

wide = pd.read_csv(WIDE_CSV)
wide['county_fips'] = wide['county_fips'].astype(str).str.zfill(5)
print(f"Wide CSV before: {len(wide)} rows, {wide['county_fips'].nunique()} counties")

controls = pd.read_csv(ROOT / "data/derived/matched_controls_named.csv")
controls['control_fips'] = controls['control_fips'].astype(str).str.zfill(5)
control_fips = set(controls['control_fips'].unique())

# ── Load MuniSpot v2 classified PT ─────────────────────────────────────
ms = pd.read_parquet(
    ROOT / "data/derived/muni_property_tax_v2_classified_gf_only_FY2016_2026.parquet",
    columns=['county_fips', 'fiscal_year', 'reported_value', 'tier_with_pilot',
             'municipality_name', 'state']
)
ms['county_fips'] = ms['county_fips'].astype(str).str.zfill(5)

# Filter to control counties with PT
ms_ctrl = ms[ms['county_fips'].isin(control_fips) & ms['tier_with_pilot']].copy()

# For each control county × fiscal_year: sum all PT rows
pt_by_county_year = (
    ms_ctrl
    .groupby(['county_fips', 'fiscal_year', 'municipality_name', 'state'])['reported_value']
    .sum()
    .reset_index()
    .rename(columns={'reported_value': 'property_tax_gf', 'fiscal_year': 'fy'})
)

# Use the most recent year available for each county (2024 or 2025 preferred)
pt_by_county_year = pt_by_county_year.sort_values('fy', ascending=False)
latest = pt_by_county_year.groupby('county_fips').first().reset_index()

print(f"\nMuniSpot v2 PT available for {len(latest)} control counties")

# ── Load MuniSpot v2 total revenue for same counties ──────────────────
ms_rev = pd.read_parquet(
    ROOT / "data/derived/muni_total_revenue_v2_gf_only_FY2016_2026.parquet",
    columns=['county_fips', 'fiscal_year', 'reported_value']
)
ms_rev['county_fips'] = ms_rev['county_fips'].astype(str).str.zfill(5)
ms_rev_ctrl = ms_rev[ms_rev['county_fips'].isin(control_fips)].copy()
rev_by_cy = ms_rev_ctrl.groupby(['county_fips', 'fiscal_year'])['reported_value'].sum().reset_index()
rev_by_cy = rev_by_cy.sort_values('fiscal_year', ascending=False)
rev_latest = rev_by_cy.groupby('county_fips').first().reset_index()
rev_latest.rename(columns={'reported_value': 'total_revenue_gf', 'fiscal_year': 'fy_rev'}, inplace=True)

# ── Build new rows for controls not yet in wide CSV ─────────────────────
already_in = set(wide['county_fips'].unique())
new_rows = []

for _, row in latest.iterrows():
    fips = row['county_fips']
    fy = int(row['fy'])
    if fips in already_in:
        continue  # skip counties already in wide CSV (shouldn't happen for controls)

    ctrl_info = controls[controls['control_fips'] == fips].iloc[0]

    # Get revenue for same FY if available
    rev_row = rev_latest[rev_latest['county_fips'] == fips]
    rev_val = rev_row['total_revenue_gf'].iloc[0] if len(rev_row) > 0 else np.nan

    new_row = {
        'county_fips': fips,
        'county_name': ctrl_info['control_name'],
        'state': row['state'],
        'fy': fy,
        'property_tax_gf': row['property_tax_gf'],
        'total_revenue_gf': rev_val,
        'capital_outlay_gf': np.nan,
        'lt_debt_outstanding': np.nan,
        'interest_expense': np.nan,
        'property_tax_allfunds': np.nan,   # v2 GF-only; no allfunds in this file
        'total_revenue_allfunds': np.nan,
        'capital_outlay_allfunds': np.nan,
        'state_pt_structure': 'munispot_v2_gf',  # tag data source
    }
    # Pad any missing columns
    for col in wide.columns:
        if col not in new_row:
            new_row[col] = np.nan
    new_rows.append(new_row)

print(f"Adding {len(new_rows)} control county rows from MuniSpot v2")

if new_rows:
    new_df = pd.DataFrame(new_rows)[wide.columns]
    combined = pd.concat([wide, new_df], ignore_index=True)
else:
    combined = wide

combined = combined.sort_values(['county_fips', 'fy']).reset_index(drop=True)
combined.to_csv(WIDE_CSV, index=False)
print(f"\nWrote {len(combined)} rows ({combined['county_fips'].nunique()} counties) → {WIDE_CSV}")

# Summary
has_pt = combined['property_tax_gf'].notna() | combined['property_tax_allfunds'].notna()
print(f"Counties with any PT data: {combined[has_pt]['county_fips'].nunique()}")

still_missing = control_fips - set(combined['county_fips'].unique())
print(f"\nControl counties STILL missing (need PDF extraction or drop from DiD): {len(still_missing)}")
for fips in sorted(still_missing):
    row = controls[controls['control_fips'] == fips].iloc[0]
    print(f"  {fips}  {row['control_name']}  ({row['state_abbr']})")
