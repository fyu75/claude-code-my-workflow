"""
Add pt_structure_state column to dc_tax_share_distribution.csv.
Based on state-mechanism findings from the ACFR sprint
(documented in memos/2026-06-07_dc_share_formula_refinement.md).
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIST_CSV = ROOT / "data/derived/dc_tax_share_distribution.csv"

df = pd.read_csv(DIST_CSV)
df['county_fips'] = df['county_fips'].astype(str).str.zfill(5)
print(f"Loaded {len(df)} counties from dc_tax_share_distribution.csv")

# ── State-mechanism multipliers from ACFR sprint ─────────────────────
# Ordered most-specific to most-general; last match wins.
def assign_pt_structure(row):
    fips = row['county_fips']
    state = str(row.get('state', '')).strip().upper()

    # State-level catch-alls first
    if state == 'SC':
        return 'SC-FILOT'
    if state == 'GA':
        return 'GA-IDA-leasehold'
    if state == 'OH':
        return 'OH-categorical-no-TPP'
    if state == 'TX':
        return 'TX-Chapter-312-abatement'
    if state == 'KY':
        return 'KY-consolidated-with-PILOT'
    if state == 'VA':
        return 'VA-consolidated'

    # County-specific overrides (evidence from specific ACFR extractions)
    COUNTY_OVERRIDES = {
        '01089': 'AL-abatement-heavy',   # Madison AL — 90% abatement
        '01071': 'AL-abatement-heavy',   # Jackson AL — 100% DC abatement
        '32029': 'NV-Switch-deals',      # Storey NV (Tesla/Switch)
        '32003': 'NV-Switch-deals',      # Clark NV (Switch etc.)
    }
    if fips in COUNTY_OVERRIDES:
        return COUNTY_OVERRIDES[fips]

    return 'standard'

df['pt_structure_state'] = df.apply(assign_pt_structure, axis=1)

# Summary
print("\npt_structure_state distribution:")
print(df['pt_structure_state'].value_counts().to_string())

# For the treated set (dc_share_mid >= 1%), show breakdown
# NOTE: dc_share_mid is stored as PERCENT (ratio x 100), so the 1% cut is >= 1.0, NOT >= 0.01.
treated = df[df['dc_share_mid'] >= 1.0]
print(f"\nTreated set (dc_share_mid >= 1%, n={len(treated)}) breakdown:")
print(treated['pt_structure_state'].value_counts().to_string())

df.to_csv(DIST_CSV, index=False)
print(f"\nSaved → {DIST_CSV}")

# ── Also compute adjusted DC share with state multipliers ────────────
# Mid-point multipliers from the memo discussion
MULTIPLIERS_MID = {
    'SC-FILOT':              0.50,  # FILOT reduces assessment from 10.5% to 4-6%
    'GA-IDA-leasehold':      0.20,  # IDA holds title; effective DC PT ~20% of formula
    'AL-abatement-heavy':    0.15,  # 90-100% abatement, net ~10-15% of gross
    'OH-categorical-no-TPP': 0.20,  # No TPP; only building shell; ~20% of formula
    'TX-Chapter-312-abatement': 0.25,  # 85% abatement on improvement + 100% personal prop
    'KY-consolidated-with-PILOT': 0.90,  # Mostly standard; PILOT adds ~5-10%
    'VA-consolidated':       1.00,  # No structural abatement; standard
    'NV-Switch-deals':       0.50,  # Abatements typical but not universal
    'standard':              1.00,
}

for col_suffix in ['low', 'mid', 'high']:
    naive_col = f'dc_tax_M_{col_suffix}'
    adj_col   = f'dc_tax_M_{col_suffix}_adjusted'
    share_adj = f'dc_share_{col_suffix}_adjusted'
    if naive_col in df.columns:
        df[adj_col] = df.apply(
            lambda r: r[naive_col] * MULTIPLIERS_MID.get(r['pt_structure_state'], 1.0),
            axis=1
        )
        if 'prop_tax_2017_M' in df.columns:
            # x100 so the adjusted share is PERCENT-scaled, matching the naive dc_share_* columns.
            df[share_adj] = 100 * df[adj_col] / df['prop_tax_2017_M']

df.to_csv(DIST_CSV, index=False)

# Comparison: naive vs adjusted for treated
print("\nTreated set: naive vs adjusted mid DC share distribution (at 1% cut):")
t = df[df['dc_share_mid'] >= 1.0].copy()
print(f"  naive:    {t['dc_share_mid'].describe()[['mean','50%','max']].to_string()}")
if 'dc_share_mid_adjusted' in df.columns:
    print(f"  adjusted: {t['dc_share_mid_adjusted'].describe()[['mean','50%','max']].to_string()}")

# How many treated counties would fall below 1% with adjustment?
if 'dc_share_mid_adjusted' in df.columns:
    drops_out = t[t['dc_share_mid_adjusted'] < 1.0]
    print(f"\nCounties that fall below 1% threshold after adjustment: {len(drops_out)}")
    if len(drops_out) > 0:
        print(drops_out[['county_fips','name','state','dc_share_mid','dc_share_mid_adjusted','pt_structure_state']].to_string())
