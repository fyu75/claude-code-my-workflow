"""
15_dc_tax_share_distribution.py

Estimate the share of county property tax revenue that comes from DCs, using:
  DC contribution = total MW × $/MW per year   (industry rule-of-thumb)
  DC share        = DC contribution / county total property tax (2017 ACFR)

Three $/MW scenarios:
  Low:    $30,000/MW/yr   (personal-property tax only, in incentive-heavy states)
  Mid:    $50,000/MW/yr   (Prince William County FY22 stylized fact: ~$36k/MW PP tax + some real-property tax)
  High:   $100,000/MW/yr  (full real + personal property tax, Loudoun-like counties)

Then plots the distribution across counties to help pick a meaningful threshold.

Run: python3 scripts/python/15_dc_tax_share_distribution.py
"""

import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PNL  = ROOT / 'data/derived/county_year_panel_v3.csv'
ACFR = ROOT / 'data/derived/acfr_county_year_wide.csv'
MW   = ROOT / 'data/derived/dc_county_year_mw.csv'
OUT_FIG = ROOT / 'data/derived/figures'
OUT_TBL = ROOT / 'data/derived/dc_tax_share_distribution.csv'

# $/MW/year tax revenue scenarios
TAX_PER_MW = {'low':30_000, 'mid':50_000, 'high':100_000}

def main():
    print('Loading...')
    pnl = pd.read_csv(PNL, dtype={'county_fips':str,'state_fips':str})
    pnl['county_fips'] = pnl['county_fips'].str.zfill(5)

    acfr = pd.read_csv(ACFR, dtype={'county_fips':str})
    acfr['county_fips'] = acfr['county_fips'].str.zfill(5)
    a17 = acfr[acfr['year']==2017][['county_fips','rev_property_tax']].rename(
        columns={'rev_property_tax':'prop_tax_2017_M'})

    mw = pd.read_csv(MW, dtype={'county_fips':str})
    mw['county_fips'] = mw['county_fips'].str.zfill(5)
    # Latest MW per county across all years 2018-2025
    latest_mw = mw.sort_values('year').groupby('county_fips').tail(1)[['county_fips','year','mw_total','n_dc_active']].rename(
        columns={'mw_total':'mw_latest','year':'mw_year','n_dc_active':'n_dc_latest'})
    # Also peak MW
    peak_mw = mw.groupby('county_fips')['mw_total'].max().rename('mw_peak').reset_index()

    # Cross-section
    cs = a17.merge(latest_mw, on='county_fips', how='left').merge(peak_mw, on='county_fips', how='left')
    cs['mw_latest'] = cs['mw_latest'].fillna(0)
    cs['mw_peak']   = cs['mw_peak'].fillna(0)
    cs['n_dc_latest'] = cs['n_dc_latest'].fillna(0).astype(int)
    cs = cs[cs['prop_tax_2017_M']>0].copy()

    # Apply each $/MW scenario
    for label, dollar in TAX_PER_MW.items():
        cs[f'dc_tax_M_{label}'] = cs['mw_latest'] * dollar / 1e6   # $/MW × MW = $ → divide by 1e6 → $M
        cs[f'dc_share_{label}'] = 100 * cs[f'dc_tax_M_{label}'] / cs['prop_tax_2017_M']

    dch = cs[cs['mw_latest']>0].sort_values('dc_share_mid', ascending=False).copy()
    print(f'\nUS counties with non-zero DC MW: {len(dch)}')

    print('\n=== Distribution of DC share of property tax (mid scenario, $50k/MW) ===')
    for q in [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]:
        print(f'  p{int(q*100):2d}: {dch.dc_share_mid.quantile(q):8.3f}%')

    print('\n=== # counties above various thresholds ===')
    print(f'{"threshold":>10} | {"low ($30k/MW)":>15} | {"mid ($50k/MW)":>15} | {"high ($100k/MW)":>15}')
    for t in [0.1, 0.5, 1, 2, 5, 10, 20, 50]:
        n_low  = (dch['dc_share_low']>=t).sum()
        n_mid  = (dch['dc_share_mid']>=t).sum()
        n_high = (dch['dc_share_high']>=t).sum()
        print(f'  >={t:>4.1f}% | {n_low:>15d} | {n_mid:>15d} | {n_high:>15d}')

    print('\n=== Top 30 DC-host counties by estimated DC share (mid scenario) ===')
    pnl_names = pnl.groupby('county_fips').agg(state=('state_abbr','first'), name=('county_name','first')).reset_index()
    dch = dch.merge(pnl_names, on='county_fips', how='left')
    top = dch.head(30)[['county_fips','name','state','n_dc_latest','mw_latest','prop_tax_2017_M',
                         'dc_share_low','dc_share_mid','dc_share_high']].copy()
    top.columns = ['fips','county','st','#DC','MW','Prop Tax $M','low %','mid %','high %']
    print(top.round(2).to_string(index=False))

    # Save full table sorted
    dch.to_csv(OUT_TBL, index=False)
    print(f'\nWrote: {OUT_TBL}')

    # ====== Plots ======
    fig, axes = plt.subplots(2, 2, figsize=(14,10))

    # Distribution histogram (mid scenario)
    ax = axes[0][0]
    dch_pos = dch[dch['dc_share_mid']>0]
    ax.hist(dch_pos['dc_share_mid'].clip(upper=30), bins=50, color='steelblue', alpha=0.8)
    for t,c in [(1,'gray'),(5,'darkorange'),(10,'darkred')]:
        ax.axvline(t, color=c, linestyle='--', label=f'{t}% threshold ({(dch.dc_share_mid>=t).sum()} counties)')
    ax.set_xlabel('Estimated DC share of property tax (%, mid scenario, $50k/MW)')
    ax.set_ylabel('# of counties')
    ax.set_title('Distribution: DC share of county property tax')
    ax.legend()

    # Counties above threshold by scenario
    ax = axes[0][1]
    thresholds = [0.1, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30, 50]
    for label, color in [('low','lightgray'),('mid','steelblue'),('high','darkred')]:
        ns = [(dch[f'dc_share_{label}']>=t).sum() for t in thresholds]
        ax.plot(thresholds, ns, marker='o', label=f'{label} (${TAX_PER_MW[label]//1000}k/MW)', color=color)
    ax.set_xscale('log'); ax.set_xlabel('Threshold (%)'); ax.set_ylabel('# DC-host counties at or above threshold')
    ax.set_title('How many counties qualify, by threshold')
    ax.grid(alpha=0.3); ax.legend()

    # US DC growth (MW over time)
    ax = axes[1][0]
    us_mw = mw.groupby('year').agg(n=('county_fips','count'), mw=('mw_total','sum')).reset_index()
    us_mw['mw_GW'] = us_mw['mw']/1000
    ax.bar(us_mw['year'], us_mw['mw_GW'], color='darkred', alpha=0.7)
    ax.set_xlabel('Year'); ax.set_ylabel('Total US operational MW (GW)')
    ax.set_title('US data-center capacity, 2018–2025')
    ax.grid(axis='y', alpha=0.3)
    for _, r in us_mw.iterrows():
        ax.text(r['year'], r['mw_GW']+0.5, f'{r.mw_GW:.0f}', ha='center', fontsize=9)

    # Year-over-year MW growth %
    ax = axes[1][1]
    us_mw['yoy_pct'] = us_mw['mw'].pct_change()*100
    ax.bar(us_mw['year'], us_mw['yoy_pct'].fillna(0), color='steelblue', alpha=0.7)
    ax.axhline(0, color='black', lw=0.5)
    ax.set_xlabel('Year'); ax.set_ylabel('YoY MW growth (%)')
    ax.set_title('Year-over-year MW growth rate')
    ax.grid(axis='y', alpha=0.3)

    fig.suptitle('Where does DC investment matter fiscally? Distribution + DC growth timeline', y=1.00)
    fig.tight_layout()
    fig.savefig(OUT_FIG/'fig09_dc_tax_share_distribution.png', dpi=140, bbox_inches='tight')
    plt.close()
    print(f'Saved figure: {OUT_FIG/"fig09_dc_tax_share_distribution.png"}')

if __name__ == '__main__':
    main()
