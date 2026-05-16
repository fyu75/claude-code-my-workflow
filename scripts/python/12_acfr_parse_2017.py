"""
12_acfr_parse_2017.py

Parse 2017 Census of Governments / State and Local Government Finance Individual Unit File.
Prototype to verify structure and produce a county-level fiscal panel for FY2017.

File format (FinEstDAT, 32 chars per record):
  1-2   FIPS state code
  3     Type code (0=state, 1=county, 2=city, 3=township, 4=special district, 5=school)
  4-6   FIPS county code
  7-12  Unit identifier
  13-15 Item code (e.g., T01, F12, 49U, E32)
  16-27 Amount in $thousands (12 chars right-aligned)
  28-31 Year
  32    Imputation flag

Key item codes (from technical doc):
  T01: General Property Tax (revenue)            ← STAR variable
  T09: General Sales Tax
  T40: Local Income Tax (selective; CA has none)
  B01-B94: Federal intergovernmental revenue (by function)
  C21-C94: State intergovernmental revenue (by function)
  D21-D94: Local intergovernmental revenue
  E01-E89: Current operations expenditure (by function)
  F01-F92: Capital outlay (construction + equipment), by function
  G01-G92: Capital outlay - construction only
  I89: Interest on general debt
  J19, J67, J68: Insurance trust expenditure
  19T: Beginning LT debt outstanding (public purpose)
  19U: Beginning LT debt outstanding (other / NEC)
  24T: LT debt issued (public purpose)
  29U: LT debt issued (NEC)
  34T: LT debt retired (public purpose)
  39U: LT debt retired (NEC)
  44T: LT debt O/S - Industrial Revenue
  49U: LT debt O/S - Other (end of FY)
  W01: Total revenue (sometimes; varies by year)
  W31: Total general revenue (sometimes; varies by year)

Run: python3 scripts/python/12_acfr_parse_2017.py
"""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DAT = ROOT / 'data/external/acfr/2017/2017FinEstDAT_06122023modp_pu.txt'
PID = ROOT / 'data/external/acfr/2017/Fin_PID_2017.txt'
OUT_LONG = ROOT / 'data/derived/acfr_2017_long.csv'
OUT_WIDE = ROOT / 'data/derived/acfr_2017_county_wide.csv'

# Variables of interest (project mechanism map)
KEEP_ITEMS = {
    # Revenue
    'T01': 'rev_property_tax',
    'T09': 'rev_general_sales_tax',
    'T19': 'rev_other_sales_tax',
    'T22': 'rev_motor_fuels_tax',
    'T28': 'rev_alcohol_tax',
    'T40': 'rev_indiv_income_tax',
    'T41': 'rev_corp_income_tax',
    # Federal IGA aggregated codes:
    'B89': 'rev_fed_other',
    # Total revenue, total expenditure (some years W codes; use F00/E00/G00 carefully)
    # Current operations (current expenditure)
    'E12': 'exp_curr_elem_sec_educ',
    'E18': 'exp_curr_higher_educ',
    'E32': 'exp_curr_health',
    'E36': 'exp_curr_hospitals',
    'E44': 'exp_curr_highways',
    'E61': 'exp_curr_parks_rec',
    'E62': 'exp_curr_police',
    'E80': 'exp_curr_sewer',
    'E81': 'exp_curr_solid_waste',
    'E89': 'exp_curr_general_nec',
    # Capital outlay (the canonical capex measure)
    'F12': 'capex_elem_sec_educ',
    'F18': 'capex_higher_educ',
    'F25': 'capex_judicial',
    'F32': 'capex_health',
    'F36': 'capex_hospitals',
    'F44': 'capex_highways',
    'F61': 'capex_parks_rec',
    'F62': 'capex_police',
    'F80': 'capex_sewer',
    'F89': 'capex_general_nec',
    # Debt
    '19T': 'lt_debt_outstanding_beg_pub',
    '19U': 'lt_debt_outstanding_beg_other',
    '24T': 'lt_debt_issued_pub',
    '29U': 'lt_debt_issued_other',
    '34T': 'lt_debt_retired_pub',
    '39U': 'lt_debt_retired_other',
    '44T': 'lt_debt_outstanding_indrev',
    '49U': 'lt_debt_outstanding_end',
    '61V': 'st_debt_outstanding_beg',
    '64V': 'st_debt_outstanding_end',
    'I89': 'interest_on_debt',
}

def main():
    print('Parsing 2017 FinEstDAT...')
    rows = []
    with open(DAT, 'r', errors='replace') as f:
        for line in f:
            if len(line) < 32: continue
            id_     = line[0:12]
            state   = line[0:2]
            type_   = line[2]
            county  = line[3:6]
            unit    = line[6:12]
            item    = line[12:15]
            amt     = line[15:27]
            yr      = line[27:31]
            flag    = line[31]
            if item not in KEEP_ITEMS: continue
            rows.append((id_, state, type_, county, unit, item, amt.strip(), yr.strip(), flag))
    df = pd.DataFrame(rows, columns=['id','state_fips','type','county_fips_part','unit','item','amount','year','flag'])
    print(f'  rows kept: {len(df):,}')

    # Numeric amount
    df['amount_k'] = pd.to_numeric(df['amount'], errors='coerce')
    df['amount_M'] = df['amount_k'] / 1000  # $thousands → $millions
    df['county_fips'] = df['state_fips'] + df['county_fips_part']
    df['var_name']    = df['item'].map(KEEP_ITEMS)

    print(f'\n  Distribution by type:')
    print(df['type'].value_counts().to_string())

    # Save long format
    long_out = df[['id','state_fips','type','county_fips','unit','item','var_name','amount_M','year']].rename(
        columns={'amount_M':'amount_millions'})
    OUT_LONG.parent.mkdir(parents=True, exist_ok=True)
    long_out.to_csv(OUT_LONG, index=False)
    print(f'\n  Wrote long format: {OUT_LONG}  ({len(long_out):,} rows)')

    # ============================================================
    # Build county-level wide table.
    # Aggregate to county_fips by summing across all sub-county units (city, township, special district, school).
    # This gives "all-local-government" fiscal aggregates per county area.
    # ============================================================
    print('\nBuilding county-area wide aggregates (all local govts in county)...')
    # type==0 is state-level; drop. types 1-5 are county+sub-county local govts
    sub = df[df['type'].isin(['1','2','3','4','5'])].copy()
    # For each (county_fips, var_name), sum amounts
    wide = sub.groupby(['county_fips','var_name'])['amount_M'].sum().unstack(fill_value=0).reset_index()
    print(f'  counties with at least one var: {len(wide):,}')
    print(f'  variables present: {len(wide.columns)-1}')

    # Also compute aggregates
    capex_cols = [c for c in wide.columns if c.startswith('capex_')]
    curr_cols  = [c for c in wide.columns if c.startswith('exp_curr_')]
    rev_cols   = [c for c in wide.columns if c.startswith('rev_')]
    wide['capex_total'] = wide[capex_cols].sum(axis=1) if capex_cols else 0
    wide['curr_total']  = wide[curr_cols].sum(axis=1)  if curr_cols  else 0
    wide['rev_total_known'] = wide[rev_cols].sum(axis=1) if rev_cols else 0
    wide.to_csv(OUT_WIDE, index=False)
    print(f'  Wrote wide format: {OUT_WIDE}')

    # ============================================================
    # Quick sanity check on Prince William VA, Loudoun VA, Maricopa AZ
    # ============================================================
    print('\n=== Sanity check on stylized-fact counties (FY 2017) ===')
    spot = wide[wide['county_fips'].isin(['51107','51153','06085','04013','17031','19153'])][
        ['county_fips','rev_property_tax','capex_total','lt_debt_outstanding_end','interest_on_debt']
    ].copy()
    spot['county_name'] = spot['county_fips'].map({
        '51107':'Loudoun VA','51153':'Prince William VA','06085':'Santa Clara CA',
        '04013':'Maricopa AZ','17031':'Cook IL','19153':'Polk IA'
    })
    print(spot.to_string(index=False))

    print('\n=== Variable-coverage check ===')
    for v in ['rev_property_tax','capex_total','lt_debt_outstanding_end','lt_debt_issued_pub','lt_debt_issued_other','interest_on_debt']:
        n = (wide[v]>0).sum() if v in wide.columns else 0
        med = wide.loc[wide[v]>0,v].median() if v in wide.columns and (wide[v]>0).any() else 0
        print(f'  {v}: {n:,} counties >0, median {med:,.1f} $M')

if __name__ == '__main__':
    main()
