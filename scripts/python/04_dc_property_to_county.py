"""
04_dc_property_to_county.py

Assign every US data-center property to a county FIPS via spatial join.

Inputs:
  data/datacenter/dcproperties_latest.sas7bdat   (S&P 451 properties)
  data/external/cb_2023_us_county_500k/*.shp     (Census county polygons)

Output:
  data/derived/dc_property_county_fips.csv
    one row per US property with lat/lon, joined to county FIPS

Run: python3 scripts/python/04_dc_property_to_county.py
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROP_PATH = ROOT / 'data/datacenter/dcproperties_latest.sas7bdat'
SHP_PATH = ROOT / 'data/external/cb_2023_us_county_500k/cb_2023_us_county_500k.shp'
OUT_PATH = ROOT / 'data/derived/dc_property_county_fips.csv'

def main():
    print('Loading DC properties...')
    df = pd.read_sas(PROP_PATH, encoding='latin-1')
    print(f'  {len(df):,} total properties (global)')

    us = df[df['COUNTRYID']=='US'].copy()
    has_coords = us[us['LATITUDE'].notna() & us['LONGITUDE'].notna()].copy()
    print(f'  {len(us):,} US properties; {len(has_coords):,} have coords ({100*len(has_coords)/len(us):.1f}%)')

    keep_cols = ['PROPERTYUNIQUEID','DATACENTERNAME','LATITUDE','LONGITUDE',
                 'STATE','STATEFIPS','CITY','ZIP','STREETADDRESS1',
                 'YEARFACILITYBECAMEOPERATIONAL','BUILTYEAR','DECOMMISSIONEDYEAR',
                 'NCREIFREGIONNAME','GEOGRAPHICREGION']
    has_coords = has_coords[[c for c in keep_cols if c in has_coords.columns]].copy()

    print('\nLoading county shapefile...')
    counties = gpd.read_file(SHP_PATH)
    counties = counties[['STATEFP','COUNTYFP','NAME','geometry']].copy()
    counties['county_fips'] = counties['STATEFP'].astype(str) + counties['COUNTYFP'].astype(str)
    counties = counties.rename(columns={'NAME':'county_name'})
    print(f'  {len(counties):,} counties (50 states + DC + PR + territories)')

    print('\nSpatial join (point-in-polygon, EPSG matched)...')
    gp = gpd.GeoDataFrame(
        has_coords,
        geometry=gpd.points_from_xy(has_coords['LONGITUDE'], has_coords['LATITUDE']),
        crs='EPSG:4326'
    ).to_crs(counties.crs)
    joined = gpd.sjoin(gp, counties[['county_fips','county_name','STATEFP','geometry']],
                       how='left', predicate='within')

    matched = joined[joined['county_fips'].notna()]
    print(f'  matched: {len(matched):,} / {len(joined):,} = {100*len(matched)/len(joined):.1f}%')

    # Diagnose unmatched (should be ~0 — points just outside coastline)
    unmatched = joined[joined['county_fips'].isna()]
    if len(unmatched):
        print(f'  unmatched: {len(unmatched)}')
        print(unmatched[['PROPERTYUNIQUEID','LATITUDE','LONGITUDE','STATE','CITY']].head(10).to_string(index=False))

    # Drop geometry and save
    out = joined.drop(columns=['geometry','index_right','STATEFP'], errors='ignore').copy()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_PATH, index=False)
    print(f'\nWrote {OUT_PATH}  ({len(out):,} rows)')

    # ===== Summary =====
    print('\n=== State-level distribution (top 15) ===')
    s = matched.groupby('STATE').size().sort_values(ascending=False).head(15)
    for st, n in s.items(): print(f'  {st}: {n}')

    print('\n=== County-level distribution (top 20) ===')
    by = matched.groupby(['county_fips','county_name','STATE']).size().sort_values(ascending=False).head(20)
    for (fips, name, st), n in by.items():
        print(f'  {fips} {name}, {st}: {n}')

    # By opening year decade
    print('\n=== US openings by decade (cumulative) ===')
    matched_yr = matched.copy()
    matched_yr['open_yr'] = pd.to_numeric(matched_yr['YEARFACILITYBECAMEOPERATIONAL'], errors='coerce')
    with_yr = matched_yr[matched_yr['open_yr'].between(2000, 2030)]
    hist = with_yr.groupby((with_yr['open_yr']//5)*5).size()
    cum = 0
    for y, n in hist.items():
        cum += n
        print(f'  {int(y)}-{int(y)+4}: {int(n):>4d}    (cumulative: {cum:,})')
    print(f'  Properties WITHOUT open year: {(matched["YEARFACILITYBECAMEOPERATIONAL"].isna()).sum()}')

    # Number of unique DC counties
    n_unique_counties = matched['county_fips'].nunique()
    print(f'\n=== Unique DC-host counties: {n_unique_counties} / 3,143 US counties ({100*n_unique_counties/3143:.1f}%) ===')

if __name__ == '__main__':
    main()
