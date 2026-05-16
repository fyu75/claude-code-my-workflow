"""
09_spread_and_panel_v3.py

Build a richer county-year panel with:
  * Treasury benchmark (DGS5, DGS10, DGS20 from FRED, yearly avg)
  * Deal-level par-weighted maturity (from tranche file)
  * Deal-level matched-maturity Treasury yield
  * Deal-level spread = par_wtd_coupon - matched Treasury yield
  * County-year par-weighted spread

Outputs:
  data/derived/fred_treasury_yearly.csv
  data/derived/sdc_deal_spread.csv
  data/derived/county_year_panel_v3.csv

Run: python3 scripts/python/09_spread_and_panel_v3.py
"""

import pandas as pd, numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATURITY = ROOT / 'data/sdc_muni/sdc_municipals/maturity.sas7bdat'
DEALS    = ROOT / 'data/sdc_muni/sdc_municipals/deals_data.sas7bdat'
ISS_MAP  = ROOT / 'data/derived/sdc_issuer_county_full_v3.csv'
PNL_V2   = ROOT / 'data/derived/county_year_panel_v2.csv'

FRED_DIR = ROOT / 'data/external/fred'
OUT_TR   = ROOT / 'data/derived/fred_treasury_yearly.csv'
OUT_DEAL = ROOT / 'data/derived/sdc_deal_spread.csv'
OUT_PNL  = ROOT / 'data/derived/county_year_panel_v3.csv'

TIER_A = {'District','City, Town Vlg','Local Authority','County/Parish'}

def main():
    # ============================================================
    # 1. Treasury yields — yearly average per maturity
    # ============================================================
    print('1. Building yearly Treasury yields (5y, 10y, 20y constant maturity)...')
    tr = {}
    for sid in ['DGS5','DGS10','DGS20']:
        s = pd.read_csv(FRED_DIR/f'{sid}.csv')
        s.columns = ['date','y']
        s['date'] = pd.to_datetime(s['date'])
        s['y']    = pd.to_numeric(s['y'], errors='coerce')
        s = s.dropna(subset=['y'])
        s['year'] = s['date'].dt.year
        tr[sid] = s.groupby('year')['y'].mean().reset_index().rename(columns={'y':sid.lower()})
    treas = tr['DGS5'].merge(tr['DGS10'], on='year', how='outer').merge(tr['DGS20'], on='year', how='outer')
    treas = treas[treas['year'].between(2000,2025)].copy()
    treas.to_csv(OUT_TR, index=False)
    print(f'   {len(treas)} years; 2010 10y avg = {treas.loc[treas.year==2010,"dgs10"].values[0]:.2f}%')

    # ============================================================
    # 2. Tranche maturities + coupons -> deal-level summary
    # ============================================================
    print('\n2. Tranche file -> deal-level (par_wtd_coupon, par_wtd_yrs_to_mat)...')
    t = pd.read_sas(MATURITY, encoding='latin-1')
    t['coupon'] = pd.to_numeric(t['ENDSERIALCOUPON'], errors='coerce')
    t['amt']    = pd.to_numeric(t['AMTMATY'], errors='coerce')
    t['MATURITY']= pd.to_datetime(t['MATURITY'], errors='coerce')
    t = t[(t['coupon']>0) & (t['coupon']<=15) & (t['amt']>0) & t['MATURITY'].notna()].copy()
    print(f'   usable tranches: {len(t):,}')

    # Bring in DELDATE from deals_data for the years-to-maturity calc
    print('   Joining DELDATE...')
    deldates = []
    for ch in pd.read_sas(DEALS, encoding='latin-1', chunksize=200000):
        d = pd.to_datetime(ch['DELDATE'], errors='coerce')
        deldates.append(pd.DataFrame({'MASTER_DEAL_NO': ch['MASTER_DEAL_NO'], 'DELDATE': d}))
    dd = pd.concat(deldates, ignore_index=True).drop_duplicates('MASTER_DEAL_NO')
    t = t.merge(dd, on='MASTER_DEAL_NO', how='left')
    t['yrs_to_mat'] = (t['MATURITY'] - t['DELDATE']).dt.days / 365.25
    t = t[(t['yrs_to_mat']>0) & (t['yrs_to_mat']<=50)]
    print(f'   tranches with valid maturity diff: {len(t):,}')

    # Par-weighted aggregates per deal
    t['cxa']  = t['coupon']    * t['amt']
    t['mxa']  = t['yrs_to_mat']* t['amt']
    deal = t.groupby('MASTER_DEAL_NO').agg(
        par_M_w=('amt','sum'), cxa_sum=('cxa','sum'), mxa_sum=('mxa','sum')
    ).reset_index()
    deal['par_wtd_coupon']  = deal['cxa_sum'] / deal['par_M_w']
    deal['par_wtd_yrs2mat'] = deal['mxa_sum'] / deal['par_M_w']
    deal = deal[['MASTER_DEAL_NO','par_wtd_coupon','par_wtd_yrs2mat']]
    print(f'   deals with coupon+maturity: {len(deal):,}   median maturity: {deal.par_wtd_yrs2mat.median():.1f} yrs')

    # ============================================================
    # 3. Spread = coupon - matched-maturity Treasury (year-level)
    # ============================================================
    print('\n3. Computing spreads...')
    # Re-load deals_data to get DELDATE-year + AMT + filters
    rows = []
    for ch in pd.read_sas(DEALS, encoding='latin-1', chunksize=200000):
        d = pd.to_datetime(ch['DELDATE'], errors='coerce')
        sub = ch[d.dt.year.between(2000,2025) & (ch['AMT']>=1) & (ch['CORPORATE_BACKED']=='No')
                 & ch['ISSTYPE_TRANS'].isin(TIER_A) & ch['ISSUER'].notna() & ch['STATECODE'].notna()
                ][['MASTER_DEAL_NO','DELDATE','ISSUER','STATECODE','AMT']].copy()
        sub['year']      = d[sub.index].dt.year.astype('Int64')
        sub['ISSUER']    = sub['ISSUER'].str.strip()
        sub['STATECODE'] = sub['STATECODE'].str.strip()
        rows.append(sub)
    deals = pd.concat(rows, ignore_index=True)
    deals = deals.merge(deal, on='MASTER_DEAL_NO', how='left')

    # Maturity-matched Treasury yield: interpolate among 5/10/20-year
    deals = deals.merge(treas, on='year', how='left')
    def matched_treas(row):
        m = row['par_wtd_yrs2mat']
        if pd.isna(m): return np.nan
        if m <= 5:  return row['dgs5']
        if m <= 10: # linear interp between 5y and 10y
            w = (m-5)/5
            return (1-w)*row['dgs5'] + w*row['dgs10']
        if m <= 20:
            w = (m-10)/10
            return (1-w)*row['dgs10'] + w*row['dgs20']
        return row['dgs20']
    deals['treas_match'] = deals.apply(matched_treas, axis=1)
    deals['spread_pct']  = deals['par_wtd_coupon'] - deals['treas_match']
    deals['spread_bps']  = deals['spread_pct'] * 100

    # Sanity
    print(f'   deals with spread: {deals.spread_bps.notna().sum():,}')
    print(f'   spread (bps): p25={deals.spread_bps.quantile(0.25):.0f}, '
          f'median={deals.spread_bps.median():.0f}, p75={deals.spread_bps.quantile(0.75):.0f}, '
          f'mean={deals.spread_bps.mean():.0f}')
    # Drop crazy outliers
    deals.loc[(deals.spread_bps < -300) | (deals.spread_bps > 700), 'spread_bps'] = np.nan
    print(f'   after outlier trim (-300/+700 bps): {deals.spread_bps.notna().sum():,}')

    # Apply issuer mapping
    iss = pd.read_csv(ISS_MAP, dtype={'county_fips':str})
    iss['county_fips'] = iss['county_fips'].astype(str).str.zfill(5).where(
        iss['county_fips'].notna() & (iss['county_fips']!='nan'), None)
    iss = iss[['ISSUER','STATECODE','county_fips','resolve_status']]
    resolved_set = {'county_fips_direct','place_fips_via_crosswalk','cousub_fips_via_crosswalk','county_fips_override'}
    deals = deals.merge(iss, on=['ISSUER','STATECODE'], how='left')
    res = deals[deals['resolve_status'].isin(resolved_set) & deals['county_fips'].notna()].copy()
    res['county_fips'] = res['county_fips'].astype(str).str.zfill(5)

    # Save deal-level
    res[['MASTER_DEAL_NO','county_fips','STATECODE','year','AMT','par_wtd_coupon',
         'par_wtd_yrs2mat','treas_match','spread_bps']].to_csv(OUT_DEAL, index=False)
    print(f'   wrote {OUT_DEAL}')

    # ============================================================
    # 4. Aggregate to county-year (par-weighted spread + maturity)
    # ============================================================
    print('\n4. County-year aggregation...')
    res['sxa'] = res['spread_bps'] * res['AMT']
    res['cxa'] = res['par_wtd_coupon'] * res['AMT']
    res['m_x'] = res['par_wtd_yrs2mat'] * res['AMT']
    cy = res.groupby(['county_fips','year']).agg(
        par_M=('AMT','sum'),
        sxa=('sxa','sum'),
        cxa=('cxa','sum'),
        m_x=('m_x','sum'),
        n_deals_w_spread=('spread_bps', lambda x: x.notna().sum()),
        par_w_spread=('AMT', lambda x: x[res.loc[x.index,'spread_bps'].notna()].sum()),
    ).reset_index()
    cy['par_wtd_spread_bps'] = cy['sxa'] / cy['par_w_spread'].replace(0, np.nan)
    cy['par_wtd_coupon_v3']  = cy['cxa'] / cy['par_M'].replace(0, np.nan)
    cy['par_wtd_mat_yrs']    = cy['m_x'] / cy['par_M'].replace(0, np.nan)
    cy['year'] = cy['year'].astype(int)
    cy = cy[['county_fips','year','par_wtd_spread_bps','par_wtd_coupon_v3','par_wtd_mat_yrs','n_deals_w_spread']]

    # ============================================================
    # 5. Merge into panel v2 -> v3
    # ============================================================
    print('\n5. Merging into panel v3...')
    pnl = pd.read_csv(PNL_V2, dtype={'county_fips':str,'state_fips':str})
    pnl['county_fips'] = pnl['county_fips'].str.zfill(5)
    pnl = pnl.merge(cy, on=['county_fips','year'], how='left')
    pnl.to_csv(OUT_PNL, index=False)
    print(f'   wrote {OUT_PNL}   ({len(pnl):,} rows × {len(pnl.columns)} cols)')

    have_spread = pnl[pnl['par_wtd_spread_bps'].notna()]
    print(f'\n=== Sanity ===')
    print(f'   cells with spread: {len(have_spread):,}')
    print(f'   spread (bps): median={have_spread["par_wtd_spread_bps"].median():.0f}, '
          f'p25={have_spread["par_wtd_spread_bps"].quantile(0.25):.0f}, '
          f'p75={have_spread["par_wtd_spread_bps"].quantile(0.75):.0f}')
    print(f'   DC-host counties with spread: '
          f'{(pnl[pnl["is_dc_host"]==1].groupby("county_fips")["par_wtd_spread_bps"].count()>0).sum()}/'
          f'{pnl["is_dc_host"].astype(bool).groupby(pnl["county_fips"]).any().sum()}')

if __name__ == '__main__':
    main()
