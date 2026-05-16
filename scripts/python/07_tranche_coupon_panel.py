"""
07_tranche_coupon_panel.py

Build deal-level par-weighted coupon from the tranche-level `maturity.sas7bdat`,
then aggregate to (county_fips, year). Adds a clean coupon column to the
county-year panel.

Outputs:
  data/derived/sdc_deal_coupon.csv       (deal-level par-weighted coupon)
  data/derived/county_year_panel_v2.csv  (panel + coupon)

Run: python3 scripts/python/07_tranche_coupon_panel.py
"""

import pandas as pd, numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATURITY = ROOT / 'data/sdc_muni/sdc_municipals/maturity.sas7bdat'
DEALS    = ROOT / 'data/sdc_muni/sdc_municipals/deals_data.sas7bdat'
ISS_MAP  = ROOT / 'data/derived/sdc_issuer_county_full_v3.csv'
PNL_IN   = ROOT / 'data/derived/county_year_panel.csv'
OUT_DEAL = ROOT / 'data/derived/sdc_deal_coupon.csv'
OUT_PNL  = ROOT / 'data/derived/county_year_panel_v2.csv'

TIER_A = {'District','City, Town Vlg','Local Authority','County/Parish'}

def main():
    # 1. Tranche-level: filter to reasonable coupons, compute par-weighted coupon per deal
    print('1. Loading tranche file...')
    tr = pd.read_sas(MATURITY, encoding='latin-1')
    tr['coupon'] = pd.to_numeric(tr['ENDSERIALCOUPON'], errors='coerce')
    tr['amt']    = pd.to_numeric(tr['AMTMATY'], errors='coerce')
    tr = tr[(tr['coupon']>0) & (tr['coupon']<=15) & (tr['amt']>0)].copy()
    print(f'   tranches with usable coupon: {len(tr):,}')

    # 2. Par-weighted coupon per deal
    print('\n2. Deal-level par-weighted coupon...')
    tr['cxa'] = tr['coupon'] * tr['amt']
    deal_coup = tr.groupby('MASTER_DEAL_NO').agg(
        coupon_par_M=('amt','sum'),
        cxa_sum=('cxa','sum'),
        n_tranches_with_coupon=('amt','size'),
        max_maturity=('amt', lambda x: x.size),   # placeholder
    ).reset_index()
    deal_coup['par_wtd_coupon'] = deal_coup['cxa_sum'] / deal_coup['coupon_par_M']
    deal_coup = deal_coup[['MASTER_DEAL_NO','par_wtd_coupon','coupon_par_M','n_tranches_with_coupon']]
    deal_coup.to_csv(OUT_DEAL, index=False)
    print(f'   deals with par-wtd coupon: {len(deal_coup):,}')
    print(f'   par-wtd coupon: median={deal_coup.par_wtd_coupon.median():.2f}%, '
          f'p25={deal_coup.par_wtd_coupon.quantile(0.25):.2f}%, '
          f'p75={deal_coup.par_wtd_coupon.quantile(0.75):.2f}%')

    # 3. Join coupon to deals_data, apply issuer mapping, aggregate to county-year
    print('\n3. Joining deals → issuer mapping → county_fips...')
    iss = pd.read_csv(ISS_MAP, dtype={'county_fips':str})
    iss['county_fips'] = iss['county_fips'].astype(str).str.zfill(5).where(
        iss['county_fips'].notna() & (iss['county_fips']!='nan'), None)
    iss = iss[['ISSUER','STATECODE','county_fips','resolve_status']]
    resolved_set = {'county_fips_direct','place_fips_via_crosswalk','cousub_fips_via_crosswalk','county_fips_override'}

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
    deals = deals.merge(iss, on=['ISSUER','STATECODE'], how='left')
    deals = deals.merge(deal_coup, on='MASTER_DEAL_NO', how='left')
    res = deals[deals['resolve_status'].isin(resolved_set) & deals['county_fips'].notna()].copy()
    res['county_fips'] = res['county_fips'].astype(str).str.zfill(5)
    print(f'   resolved deals: {len(res):,}   with coupon: {res.par_wtd_coupon.notna().sum():,} ({100*res.par_wtd_coupon.notna().mean():.1f}%)')

    # 4. Aggregate to county-year: par-weighted coupon (deal-par as weight)
    res['cxd'] = res['par_wtd_coupon'] * res['AMT']
    cy = res.dropna(subset=['par_wtd_coupon']).groupby(['county_fips','year']).agg(
        coupon_par_M=('AMT','sum'),
        cxd_sum=('cxd','sum'),
        n_deals_w_coupon=('AMT','size'),
    ).reset_index()
    cy['par_wtd_coupon_cy'] = cy['cxd_sum'] / cy['coupon_par_M']
    cy['year'] = cy['year'].astype(int)
    cy = cy[['county_fips','year','par_wtd_coupon_cy','n_deals_w_coupon']]
    print(f'   county-year cells with coupon: {len(cy):,}')

    # 5. Merge into existing panel
    print('\n4. Merging into county-year panel...')
    pnl = pd.read_csv(PNL_IN, dtype={'county_fips':str,'state_fips':str})
    pnl['county_fips'] = pnl['county_fips'].str.zfill(5)
    pnl = pnl.merge(cy, on=['county_fips','year'], how='left')
    pnl.to_csv(OUT_PNL, index=False)
    print(f'   wrote {OUT_PNL}  ({len(pnl):,} rows × {len(pnl.columns)} cols)')

    # 6. Quick sanity check
    have_coupon = pnl[pnl['par_wtd_coupon_cy'].notna()]
    print(f'\n=== Sanity check ===')
    print(f'  Cells with coupon: {len(have_coupon):,}')
    print(f'  Coupon median: {have_coupon["par_wtd_coupon_cy"].median():.2f}%')
    print(f'  Coupon p25/p75: {have_coupon["par_wtd_coupon_cy"].quantile(0.25):.2f}% / {have_coupon["par_wtd_coupon_cy"].quantile(0.75):.2f}%')
    print(f'\n  DC-host counties with coupon data: '
          f'{(pnl[pnl["is_dc_host"]==1].groupby("county_fips")["par_wtd_coupon_cy"].count()>0).sum()}/{pnl["is_dc_host"].astype(bool).groupby(pnl["county_fips"]).any().sum()}')

if __name__ == '__main__':
    main()
