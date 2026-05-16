"""
13_acfr_parse_all_years.py

Parse all available ACFR Individual Unit Files (2003-2017, 32-char modern format).
Skips 1992 (36-char with Census state codes — different format) and 1997, 2002 (older
formats that would need custom parsers; deferred).

Outputs:
  data/derived/acfr_county_year_long.csv   (all county-level records, long format)
  data/derived/acfr_county_year_wide.csv   (county × year × variable, wide)

Run: python3 scripts/python/13_acfr_parse_all_years.py
"""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACFR = ROOT / 'data/external/acfr'
OUT_LONG = ROOT / 'data/derived/acfr_county_year_long.csv'
OUT_WIDE = ROOT / 'data/derived/acfr_county_year_wide.csv'

# Map each year to its data file path (32-char modern format only)
# Census state code → FIPS state code crosswalk.
# Pre-2017 files use 2-digit Census codes (alphabetical, no gaps).
# 2017+ uses FIPS codes (with gaps for territories).
CENSUS_TO_FIPS = {
    '01':'01','02':'02','03':'04','04':'05','05':'06','06':'08','07':'09','08':'10',
    '09':'11','10':'12','11':'13','12':'15','13':'16','14':'17','15':'18','16':'19',
    '17':'20','18':'21','19':'22','20':'23','21':'24','22':'25','23':'26','24':'27',
    '25':'28','26':'29','27':'30','28':'31','29':'32','30':'33','31':'34','32':'35',
    '33':'36','34':'37','35':'38','36':'39','37':'40','38':'41','39':'42','40':'44',
    '41':'45','42':'46','43':'47','44':'48','45':'49','46':'50','47':'51','48':'53',
    '49':'54','50':'55','51':'56',
}

YEAR_FILES = {
    2003: ACFR / '2003/2003FinInddiv5_noimps030806.txt',
    2004: ACFR / '2004/2004FinInddiv7_noimps060308.txt',
    2005: ACFR / '2005/2005FinInddiv8_NoImps070809.txt',
    2006: ACFR / '2006/2006FinInddiv11_NoImps02012011.txt',
    2012: ACFR / '2012/2012FinEstDAT_10162019modp_pu.txt',
    2013: ACFR / '2013/2013FinEstDAT_07242018modp_pu.txt',
    2014: ACFR / '2014/2014FinEstDAT_10162019modp_pu.txt',
    2015: ACFR / '2015/2015FinEstDAT_10162019modp_pu.txt',
    2016: ACFR / '2016/2016FinEstDAT_10162019modp_pu.txt',
    2017: ACFR / '2017/2017FinEstDAT_06122023modp_pu.txt',
}

KEEP_ITEMS = {
    # Revenue
    'T01': 'rev_property_tax',
    'T09': 'rev_general_sales_tax',
    'T19': 'rev_other_sales_tax',
    'T22': 'rev_motor_fuels_tax',
    'T40': 'rev_indiv_income_tax',
    'T41': 'rev_corp_income_tax',
    'B89': 'rev_fed_other',
    # Current operations
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
    # Capital outlay
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

def parse_year(path, fy):
    """Parse ACFR Individual Unit File. Handles two formats:
       2003-2016: 14-char ID, item at [14:17], amount at [17:28/29]
       2017:      12-char ID, item at [12:15], amount at [15:27]
    Detection by record length.
    """
    rows = []
    item_slice, amt_slice = None, None
    with open(path, 'r', errors='replace') as f:
        for i, line in enumerate(f):
            line = line.rstrip('\n')
            L = len(line)
            if L < 25: continue
            if item_slice is None:
                # First record — auto-detect format by length
                if L >= 32 and L <= 33:
                    item_slice = slice(12,15); amt_slice = slice(15,27)
                else:
                    item_slice = slice(14,17); amt_slice = slice(17,29)
            state = line[0:2]
            type_ = line[2]
            county = line[3:6]
            item = line[item_slice]
            amt = line[amt_slice]
            if item not in KEEP_ITEMS: continue
            try:
                amt_k = float(amt.strip()) if amt.strip() else 0
            except ValueError:
                continue
            rows.append((state, type_, state+county, item, amt_k, fy))
    return pd.DataFrame(rows, columns=['state_fips','type','county_fips','item','amount_k','year'])

def main():
    print('Parsing all available years (2003-2017)...')
    parts = []
    for yr, path in sorted(YEAR_FILES.items()):
        if not path.exists():
            print(f'  {yr}: MISSING ({path})'); continue
        df = parse_year(path, yr)
        # Restrict to local government (type 1-5: county, city, township, special district, school)
        df = df[df['type'].isin(list('12345'))].copy()
        df['amount_M'] = df['amount_k'] / 1000
        # Pre-2017 files use Census state codes → translate to FIPS
        if yr < 2017:
            df['state_fips'] = df['state_fips'].map(CENSUS_TO_FIPS)
            # county_fips was built as state+county, need to rebuild after state translation
            df['county_fips'] = df['state_fips'] + df['county_fips'].str[2:]
        # Drop any rows with no state mapping
        df = df[df['state_fips'].notna()]
        print(f'  {yr}: {len(df):>8,} local-gov records  ({df.state_fips.nunique()} states)')
        parts.append(df)
    long = pd.concat(parts, ignore_index=True)
    long['var_name'] = long['item'].map(KEEP_ITEMS)
    OUT_LONG.parent.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_LONG, index=False)
    print(f'\nWrote long: {OUT_LONG}  ({len(long):,} rows)')

    # === Aggregate to county-year × variable (sum across sub-county govt units) ===
    print('\nAggregating to county-year × variable...')
    wide = long.groupby(['county_fips','year','var_name'])['amount_M'].sum().unstack(fill_value=0).reset_index()
    # Derived aggregates
    cap_cols = [c for c in wide.columns if c.startswith('capex_')]
    cur_cols = [c for c in wide.columns if c.startswith('exp_curr_')]
    rev_cols = [c for c in wide.columns if c.startswith('rev_')]
    wide['capex_total']      = wide[cap_cols].sum(axis=1) if cap_cols else 0
    wide['exp_curr_total']   = wide[cur_cols].sum(axis=1)
    wide['rev_total_known']  = wide[rev_cols].sum(axis=1)
    print(f'  panel: {len(wide):,} county-year cells across {wide.county_fips.nunique():,} counties × {wide.year.nunique()} years')
    wide.to_csv(OUT_WIDE, index=False)
    print(f'Wrote wide: {OUT_WIDE}')

    # === Sanity ===
    print('\n=== Spot check: Prince William VA (51153) property tax over years ===')
    pw = wide[wide['county_fips']=='51153'].sort_values('year')[['year','rev_property_tax','capex_total','lt_debt_outstanding_end']]
    print(pw.to_string(index=False))

    print('\n=== Spot check: Loudoun VA (51107) ===')
    lo = wide[wide['county_fips']=='51107'].sort_values('year')[['year','rev_property_tax','capex_total','lt_debt_outstanding_end']]
    print(lo.to_string(index=False))

    print('\n=== Coverage by year ===')
    cov = wide.groupby('year').agg(n_counties=('county_fips','nunique'),
                                    median_prop_tax=('rev_property_tax', lambda x: x[x>0].median()))
    print(cov.to_string())

if __name__ == '__main__':
    main()
