"""
05_build_county_year_panel.py

Build the primary county-year analysis panel.

Inputs:
  data/derived/dc_property_county_fips.csv   (4,507 US DCs with county_fips)
  data/derived/sdc_issuer_county_full_v3.csv (33,165 issuers, with county_fips for resolved)
  data/sdc_muni/sdc_municipals/deals_data.sas7bdat
  data/external/census_national_county.txt   (3,235 US counties skeleton)

Output:
  data/derived/county_year_panel.csv         (balanced county × year, 2000-2025)
  data/derived/county_year_panel_summary.md  (coverage diagnostics)

Run: python3 scripts/python/05_build_county_year_panel.py
"""

import sys, re
from pathlib import Path
import pandas as pd, numpy as np

ROOT = Path(__file__).resolve().parents[2]
DC_FIPS = ROOT / 'data/derived/dc_property_county_fips.csv'
SDC_ISS = ROOT / 'data/derived/sdc_issuer_county_full_v3.csv'
DEALS   = ROOT / 'data/sdc_muni/sdc_municipals/deals_data.sas7bdat'
COUNTIES= ROOT / 'data/external/census_national_county.txt'
OUT_PNL = ROOT / 'data/derived/county_year_panel.csv'
OUT_SUM = ROOT / 'data/derived/county_year_panel_summary.md'

YEAR_MIN, YEAR_MAX = 2000, 2025
TIER_A = {'District','City, Town Vlg','Local Authority','County/Parish'}

def main():
    # ============================================================
    # 1. County skeleton — all 50 states + DC
    # ============================================================
    print('1. Building county skeleton...')
    cty = pd.read_csv(COUNTIES, sep='|', dtype=str)
    cty['county_fips'] = cty['STATEFP'] + cty['COUNTYFP']
    # Drop territories (only keep 50 states + DC)
    state_50_dc = {'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY',
                   'LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND',
                   'OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY','DC'}
    cty = cty[cty['STATE'].isin(state_50_dc)].copy()
    cty = cty[['county_fips','STATE','COUNTYNAME']].rename(columns={'STATE':'state_abbr','COUNTYNAME':'county_name'})
    print(f'   {len(cty):,} counties (50 states + DC)')

    years = pd.DataFrame({'year': range(YEAR_MIN, YEAR_MAX+1)})
    skel  = cty.merge(years, how='cross')
    print(f'   skeleton: {len(skel):,} county-year cells = {len(cty)} × {len(years)} years')

    # ============================================================
    # 2. DC side — count of DCs operational by county-year
    # ============================================================
    print('\n2. Building DC-side variables...')
    dc = pd.read_csv(DC_FIPS, dtype={'county_fips':str,'STATEFIPS':str})
    dc['county_fips'] = dc['county_fips'].str.zfill(5)
    dc['open_yr']  = pd.to_numeric(dc['YEARFACILITYBECAMEOPERATIONAL'], errors='coerce')
    dc['decom_yr'] = pd.to_numeric(dc['DECOMMISSIONEDYEAR'], errors='coerce')
    # Treat blank open year as not yet operational in panel window (conservative: don't count it as treated)
    valid = dc[dc['open_yr'].between(YEAR_MIN-50, YEAR_MAX)].copy()
    print(f'   DCs with valid open year (1950-{YEAR_MAX}): {len(valid)}/{len(dc)}')
    valid['decom_yr'] = valid['decom_yr'].where(valid['decom_yr'].notna(), YEAR_MAX+100)  # not yet decommissioned

    # For each (county_fips, year), count operational DCs (open_yr <= year AND decom_yr >= year)
    # Use a yearly cross-product approach (small)
    dc_events = []
    for _, r in valid.iterrows():
        s = int(max(YEAR_MIN, r['open_yr']))
        e = int(min(YEAR_MAX, r['decom_yr']))
        for y in range(s, e+1):
            dc_events.append((r['county_fips'], y, int(r['open_yr']) == y))
    dc_panel = pd.DataFrame(dc_events, columns=['county_fips','year','new_this_year'])
    dc_agg = dc_panel.groupby(['county_fips','year']).agg(
        n_dc_cumulative=('new_this_year','size'),
        n_dc_new=('new_this_year','sum')
    ).reset_index()
    print(f'   DC-operational cells: {len(dc_agg):,} (across {dc_agg.county_fips.nunique():,} counties)')

    # First DC year per county (time-invariant treatment marker)
    first_dc = valid.groupby('county_fips')['open_yr'].min().rename('first_dc_year').reset_index()
    first_dc['first_dc_year'] = first_dc['first_dc_year'].astype(int)
    print(f'   counties with at least one DC: {len(first_dc):,}')

    # ============================================================
    # 3. SDC side — deals aggregated to county-year
    # ============================================================
    print('\n3. Loading SDC deals + applying issuer mapping...')
    iss = pd.read_csv(SDC_ISS, dtype={'county_fips':str})
    iss['county_fips'] = iss['county_fips'].astype(str).str.zfill(5).where(iss['county_fips'].notna() & (iss['county_fips']!='nan'), None)
    iss = iss[['ISSUER','STATECODE','county_fips','resolve_status']].rename(columns={'STATECODE':'state_abbr'})
    resolved_set = {'county_fips_direct','place_fips_via_crosswalk','cousub_fips_via_crosswalk','county_fips_override'}

    deals_rows = []
    for ch in pd.read_sas(DEALS, encoding='latin-1', chunksize=200000):
        d = pd.to_datetime(ch['DELDATE'], errors='coerce')
        sub = ch[
            d.dt.year.between(YEAR_MIN, YEAR_MAX)
            & (ch['AMT']>=1)
            & (ch['CORPORATE_BACKED']=='No')
            & (ch['ISSTYPE_TRANS'].isin(TIER_A))
            & ch['ISSUER'].notna() & ch['STATECODE'].notna()
        ][['DELDATE','ISSUER','STATECODE','AMT','YTM','GENERAL_TRANS','TAXABLE','SECURITY']].copy()
        sub['year'] = d[sub.index].dt.year.astype('Int64')
        sub['ISSUER'] = sub['ISSUER'].str.strip()
        sub['STATECODE'] = sub['STATECODE'].str.strip()
        deals_rows.append(sub)
    deals = pd.concat(deals_rows, ignore_index=True)
    print(f'   filtered Tier-A deals: {len(deals):,}')
    deals = deals.merge(iss.rename(columns={'state_abbr':'STATECODE'}), on=['ISSUER','STATECODE'], how='left')
    print(f'   joined to issuer mapping: {deals["resolve_status"].notna().sum():,}')

    # Keep only resolved-to-FIPS deals (drop multi_county / state_conduit / metro_excluded / unresolved)
    res_deals = deals[deals['resolve_status'].isin(resolved_set) & deals['county_fips'].notna()].copy()
    res_deals['county_fips'] = res_deals['county_fips'].astype(str).str.zfill(5)
    print(f'   deals with county_fips: {len(res_deals):,} ({100*len(res_deals)/len(deals):.1f}%)')

    # Aggregate to county-year
    res_deals['ytm_x_par'] = pd.to_numeric(res_deals['YTM'], errors='coerce') * res_deals['AMT']
    res_deals['taxable_par'] = res_deals['AMT'] * (res_deals['TAXABLE']=='T').astype(float)
    sdc_agg = res_deals.groupby(['county_fips','year']).agg(
        n_deals=('AMT','size'),
        par_total_M=('AMT','sum'),
        ytm_par=('ytm_x_par', lambda x: x.sum(skipna=True)),
        par_with_ytm=('ytm_x_par', lambda x: pd.to_numeric(x, errors='coerce').notna().sum()),
        taxable_par=('taxable_par','sum'),
    ).reset_index()
    sdc_agg['par_wtd_ytm']    = sdc_agg['ytm_par'] / sdc_agg['par_total_M'].replace(0,np.nan)
    sdc_agg['share_taxable']  = sdc_agg['taxable_par'] / sdc_agg['par_total_M'].replace(0,np.nan)
    sdc_agg['year'] = sdc_agg['year'].astype(int)
    sdc_agg = sdc_agg.drop(columns=['ytm_par','par_with_ytm','taxable_par'])
    print(f'   county-year cells with SDC issuance: {len(sdc_agg):,}')

    # ============================================================
    # 4. Merge — skeleton ← DC ← SDC ← first_dc_year
    # ============================================================
    print('\n4. Merging skeleton + DC + SDC...')
    pnl = skel.merge(dc_agg, on=['county_fips','year'], how='left') \
              .merge(sdc_agg, on=['county_fips','year'], how='left') \
              .merge(first_dc, on='county_fips', how='left')
    pnl['n_dc_cumulative'] = pnl['n_dc_cumulative'].fillna(0).astype(int)
    pnl['n_dc_new']        = pnl['n_dc_new'].fillna(0).astype(int)
    pnl['n_deals']         = pnl['n_deals'].fillna(0).astype(int)
    pnl['par_total_M']     = pnl['par_total_M'].fillna(0)
    pnl['is_dc_host']      = pnl['first_dc_year'].notna().astype(int)
    pnl['treated_t']       = ((pnl['first_dc_year'].notna()) & (pnl['year']>=pnl['first_dc_year'])).astype(int)
    pnl['years_since_first_dc'] = pnl['year'] - pnl['first_dc_year']
    pnl['state_fips']      = pnl['county_fips'].str[:2]
    pnl = pnl.sort_values(['county_fips','year']).reset_index(drop=True)

    print(f'   panel shape: {pnl.shape}')
    OUT_PNL.parent.mkdir(parents=True, exist_ok=True)
    pnl.to_csv(OUT_PNL, index=False)
    print(f'   wrote {OUT_PNL}')

    # ============================================================
    # 5. Diagnostics
    # ============================================================
    print('\n5. Diagnostics...')
    lines = []
    def L(s=''): print(s); lines.append(s)

    L('# County-Year Panel — Coverage and Power Diagnostics')
    L(f'\n*Built {pd.Timestamp.now().date()}. Source: `scripts/python/05_build_county_year_panel.py`.*\n')

    L('## Panel dimensions')
    L(f'- **Counties**: {pnl["county_fips"].nunique():,} (50 states + DC, all US)')
    L(f'- **Years**: {YEAR_MIN}–{YEAR_MAX} ({YEAR_MAX-YEAR_MIN+1} years)')
    L(f'- **County-year cells**: {len(pnl):,}')
    L(f'- **DC-host counties** (≥1 DC opened {YEAR_MIN}–{YEAR_MAX} or earlier): {pnl["is_dc_host"].astype(bool).groupby(pnl["county_fips"]).any().sum():,}')

    L('\n## Treatment exposure')
    treated_cells = (pnl['treated_t']==1).sum()
    L(f'- Treated county-year cells (post-first-DC, inclusive): {treated_cells:,} ({100*treated_cells/len(pnl):.1f}%)')
    pre = pnl[pnl['is_dc_host']==1]
    pre_cells = (pre['treated_t']==0).sum()
    L(f'- Pre-treatment cells for DC-host counties: {pre_cells:,}')

    L('\n## SDC issuance coverage')
    cells_with_deals = (pnl['n_deals']>0).sum()
    L(f'- County-year cells with ≥1 SDC deal: {cells_with_deals:,} ({100*cells_with_deals/len(pnl):.1f}%)')
    n_counties_with_deals = (pnl.groupby('county_fips')['n_deals'].sum()>0).sum()
    L(f'- Counties with any SDC deal {YEAR_MIN}–{YEAR_MAX}: {n_counties_with_deals:,} / {pnl["county_fips"].nunique():,} ({100*n_counties_with_deals/pnl["county_fips"].nunique():.1f}%)')
    dc_w_deals = pnl[pnl['is_dc_host']==1].groupby('county_fips')['n_deals'].sum()
    dc_w_deals = (dc_w_deals>0).sum()
    n_dc = pnl['is_dc_host'].astype(bool).groupby(pnl['county_fips']).any().sum()
    L(f'- **DC-host counties with ≥1 SDC deal**: {dc_w_deals:,} / {n_dc:,} ({100*dc_w_deals/n_dc:.1f}%) ← critical')
    deal_cells = pnl[pnl['n_deals']>0]
    dc_deal_cells = deal_cells[deal_cells['is_dc_host']==1]
    L(f'- Total deals in panel (resolved to FIPS): {pnl["n_deals"].sum():,}')
    L(f'- Deals in DC-host counties: {dc_deal_cells["n_deals"].sum():,} ({100*dc_deal_cells["n_deals"].sum()/pnl["n_deals"].sum():.1f}%)')

    L('\n## DC-host coverage by entry cohort')
    cohort = pnl.dropna(subset=['first_dc_year']).groupby('first_dc_year').agg(
        n_counties=('county_fips','nunique'),
    ).reset_index()
    cohort['first_dc_year'] = cohort['first_dc_year'].astype(int)
    L('| First-DC year | # counties first treated |')
    L('|---|---:|')
    for _, r in cohort.iterrows():
        L(f'| {int(r.first_dc_year)} | {int(r.n_counties)} |')

    L('\n## Top 20 DC counties — issuance summary 2000-2025')
    summary = pnl[pnl['is_dc_host']==1].groupby(['county_fips','state_abbr','county_name']).agg(
        n_dc=('n_dc_cumulative','max'),
        first_dc=('first_dc_year','first'),
        n_deals=('n_deals','sum'),
        par_total_B=('par_total_M', lambda x: x.sum()/1000),
        mean_ytm=('par_wtd_ytm', lambda x: x.mean(skipna=True)),
    ).reset_index().sort_values('n_dc', ascending=False).head(20)
    L('| FIPS | County | State | #DC | 1st DC yr | # deals (2000-25) | par ($B) | mean par-wtd YTM |')
    L('|---|---|---|---:|---:|---:|---:|---:|')
    for _, r in summary.iterrows():
        L(f'| {r.county_fips} | {r.county_name} | {r.state_abbr} | {int(r.n_dc)} | {int(r.first_dc)} | {int(r.n_deals)} | ${r.par_total_B:,.1f} | {r.mean_ytm:.2f}% |')

    L('\n## Power calculation (rough)')
    L(f'- DC-host counties with issuance: {dc_w_deals:,}')
    L(f'- Mean deals/county-year among DC-host counties with any issuance: {dc_deal_cells["n_deals"].mean():.1f}')
    L(f'- Median par/deal: ${pnl[pnl["n_deals"]>0]["par_total_M"].median():.1f}M')

    L('\n## Files')
    L(f'- `{OUT_PNL.relative_to(ROOT)}` — balanced county-year panel ({len(pnl):,} rows × {len(pnl.columns)} cols)')
    L(f'- `{OUT_SUM.relative_to(ROOT)}` — this report')

    OUT_SUM.write_text('\n'.join(lines))
    print(f'\nWrote {OUT_SUM}')

if __name__ == '__main__':
    main()
