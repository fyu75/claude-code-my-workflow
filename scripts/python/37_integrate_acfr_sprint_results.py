"""
Integrate Tier 3-5 ACFR sprint results into the master wide CSV.
- Adds new county-year rows
- Updates existing rows with allfunds data where missing
- Flags suspicious zero/tiny values for review
"""
import re
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WIDE_CSV = ROOT / "data/derived/acfr_county_year_extracted_wide.csv"
RAW_CSV  = ROOT / "data/derived/acfr_agent_extracted_raw.csv"

# ── Load existing wide CSV ──────────────────────────────────────────────
existing = pd.read_csv(WIDE_CSV)
existing['county_fips'] = existing['county_fips'].astype(str).str.zfill(5)
print(f"Existing wide CSV: {len(existing)} rows, {existing['county_fips'].nunique()} counties")

# ── Load extracted data ─────────────────────────────────────────────────
raw = pd.read_csv(RAW_CSV)
raw['county_fips'] = raw['county_fips'].astype(str).str.zfill(5)

# Parse county_name and state from county_raw
def split_county_name(s):
    """'Madison County AL' → ('Madison County', 'AL') or ('Madison County, AL', 'AL')"""
    s = s.strip()
    # Remove everything after ' — ' (Butte-Silver Bow annotation)
    s = re.split(r'\s+—\s+', s)[0].strip()
    # Last 2 uppercase chars are state abbreviation if preceded by space
    m = re.search(r'\s+([A-Z]{2})$', s)
    if m:
        state = m.group(1)
        name = s[:m.start()].strip()
        return name, state
    return s, None

raw[['county_name_parsed', 'state_parsed']] = pd.DataFrame(
    raw['county_raw'].apply(split_county_name).tolist(),
    index=raw.index
)

# Columns to integrate (match wide CSV schema)
VALUE_COLS = ['property_tax_gf', 'total_revenue_gf', 'capital_outlay_gf',
              'property_tax_allfunds', 'total_revenue_allfunds', 'capital_outlay_allfunds']

# Flag suspicious values (< $50k for a county is almost certainly wrong)
SUSPICIOUS_THRESHOLD = 50_000
for col in VALUE_COLS:
    suspicious = (raw[col].notna()) & (raw[col] < SUSPICIOUS_THRESHOLD) & (raw[col] > 0)
    if suspicious.any():
        print(f"\nWARNING — suspicious small values in {col}:")
        print(raw[suspicious][['county_fips', 'county_raw', 'fy', col]])

# ── Match raw to existing ───────────────────────────────────────────────
existing_keys = set(zip(existing['county_fips'], existing['fy']))
raw_keys = set(zip(raw['county_fips'], raw['fy']))

new_keys = raw_keys - existing_keys
update_keys = raw_keys & existing_keys
print(f"\nNew county-years to add: {len(new_keys)}")
print(f"Existing county-years to update: {len(update_keys)}")

# ── Build new rows ──────────────────────────────────────────────────────
new_rows = []
for fips, fy in sorted(new_keys):
    r = raw[(raw['county_fips'] == fips) & (raw['fy'] == fy)].iloc[0]
    row = {
        'county_fips': fips,
        'county_name': r['county_name_parsed'] or r['county_raw'],
        'state': r['state_parsed'] or '',
        'fy': fy,
    }
    for col in VALUE_COLS:
        row[col] = r[col]
    row['state_pt_structure'] = r.get('state_pt_structure')
    # Remaining columns from existing schema
    for col in existing.columns:
        if col not in row:
            row[col] = np.nan
    new_rows.append(row)

if new_rows:
    new_df = pd.DataFrame(new_rows)[existing.columns]
    print(f"\nNew rows preview:")
    print(new_df[['county_fips','county_name','state','fy'] + VALUE_COLS[:4]].to_string())

# ── Update existing rows ────────────────────────────────────────────────
updated_count = 0
existing = existing.copy()
for fips, fy in sorted(update_keys):
    r = raw[(raw['county_fips'] == fips) & (raw['fy'] == fy)].iloc[0]
    mask = (existing['county_fips'] == fips) & (existing['fy'] == fy)
    for col in VALUE_COLS:
        # Only update if new value exists AND existing is null
        new_val = r[col]
        if pd.notna(new_val) and existing.loc[mask, col].isna().all():
            existing.loc[mask, col] = new_val
            updated_count += 1
    # Update state_pt_structure if missing
    if pd.notna(r.get('state_pt_structure')) and existing.loc[mask, 'state_pt_structure'].isna().all():
        existing.loc[mask, 'state_pt_structure'] = r['state_pt_structure']

print(f"\nUpdated {updated_count} field-values in existing rows")

# ── Combine and save ────────────────────────────────────────────────────
if new_rows:
    combined = pd.concat([existing, new_df], ignore_index=True)
else:
    combined = existing

combined = combined.sort_values(['county_fips', 'fy']).reset_index(drop=True)
combined.to_csv(WIDE_CSV, index=False)
print(f"\nWrote {len(combined)} rows ({combined['county_fips'].nunique()} counties) → {WIDE_CSV}")

# ── Coverage summary ────────────────────────────────────────────────────
has_pt = combined['property_tax_gf'].notna() | combined['property_tax_allfunds'].notna()
has_tr = combined['total_revenue_gf'].notna() | combined['total_revenue_allfunds'].notna()
print(f"\nCoverage summary:")
print(f"  Counties with any PT data: {combined[has_pt]['county_fips'].nunique()}")
print(f"  Counties with any revenue data: {combined[has_tr]['county_fips'].nunique()}")
print(f"  Counties with dual-scope PT: {combined[combined['property_tax_gf'].notna() & combined['property_tax_allfunds'].notna()]['county_fips'].nunique()}")
