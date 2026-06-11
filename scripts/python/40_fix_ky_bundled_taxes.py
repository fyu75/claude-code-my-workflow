"""
40_fix_ky_bundled_taxes.py

Decision 3 resolution. KY county audits use the Department for Local Government
REGULATORY (cash) basis, which reports ALL taxes (ad valorem property +
occupational license + net profits + ...) under a single bundled "Taxes" line.
A Sonnet agent wave (2026-06-07) read every KY ACFR PDF on disk and confirmed:
12 of 13 counties CANNOT separate property tax from the bundle. Two exceptions:
  - Marshall (21157): occupational tax flows through a separate Occupational Tax
    Administrator Fund, so the GF "Taxes" line is effectively ad-valorem-only
    (agent-inferred). Keep, flag as inferred.
  - Jackson KY (21109): quarterly statement DOES itemize by revenue code -> real
    property-only = $313,743. New data point; audit had a disclaimer of opinion.

Action:
  - Preserve the bundled value in a new column `bundled_taxes_gf`.
  - Null property_tax_gf / property_tax_allfunds for the bundled counties.
  - Flag state_pt_structure accordingly.
  - Keep Marshall as property-only (inferred); add Jackson KY itemized row.
"""
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WIDE = ROOT / "data/derived/acfr_county_year_extracted_wide.csv"

df = pd.read_csv(WIDE)
df['county_fips'] = df['county_fips'].astype(str).str.zfill(5)
if 'bundled_taxes_gf' not in df.columns:
    df['bundled_taxes_gf'] = np.nan

# FIPS confirmed bundled (property tax NOT separable) -> null PT, preserve bundle, flag
BUNDLED = {'21019','21127','21145','21195','21225'}  # Boyd, Lawrence, McCracken, Pike, Union
for fips in BUNDLED:
    mask = df['county_fips'] == fips
    if not mask.any():
        continue
    # stash whatever PT we had as the bundled figure (it WAS the bundled Taxes line)
    df.loc[mask & df['property_tax_gf'].notna(), 'bundled_taxes_gf'] = \
        df.loc[mask & df['property_tax_gf'].notna(), 'property_tax_gf']
    df.loc[mask, 'property_tax_gf'] = np.nan
    df.loc[mask, 'property_tax_allfunds'] = np.nan
    df.loc[mask, 'state_pt_structure'] = 'KY-bundled-taxes-not-separable'

# Marshall (21157): GF Taxes = ad-valorem only (occupational in separate fund), agent-inferred
m = df['county_fips'] == '21157'
if m.any():
    df.loc[m, 'property_tax_gf'] = 3038437
    df.loc[m, 'property_tax_allfunds'] = 3256190
    df.loc[m, 'state_pt_structure'] = 'KY-property-only-occ-in-separate-fund(inferred)'

# Jackson KY (21109): itemized quarterly statement -> real property-only $313,743 (FY2022)
# (real 59045 + personal 167849 + motor vehicle 7762 + delinquent 16707 + other advalorem 62381)
if not (df['county_fips'] == '21109').any():
    new = {c: np.nan for c in df.columns}
    new.update({
        'county_fips': '21109', 'county_name': 'Jackson County', 'state': 'KY', 'fy': 2022,
        'property_tax_gf': 313743, 'total_revenue_gf': 3281657,
        'state_pt_structure': 'KY-itemized-property-only(audit-disclaimer)',
    })
    df = pd.concat([df, pd.DataFrame([new])[df.columns]], ignore_index=True)

df = df.sort_values(['county_fips', 'fy']).reset_index(drop=True)
df.to_csv(WIDE, index=False)

# Report
ky = df[df['state'] == 'KY']
print(f"KY rows after fix: {len(ky)}")
cols = ['county_fips','county_name','fy','property_tax_gf','bundled_taxes_gf','total_revenue_gf','state_pt_structure']
print(ky[cols].to_string(index=False))
print(f"\nKY counties with usable property-only PT: "
      f"{ky.loc[ky['property_tax_gf'].notna(),'county_fips'].nunique()} "
      f"(Marshall inferred + Jackson itemized)")
print(f"KY counties nulled as bundled: {len(BUNDLED)}")
print(f"\nWrote -> {WIDE}")
