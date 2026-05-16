"""
14_dc_intensity_heterogeneity.py

Cross-sectional DC intensity analysis using 2017 ACFR.

Hypothesis (Frank's intuition):
  DC fiscal effect should concentrate in counties where DC investment is large
  relative to the existing county property tax base. Use 2017 ACFR property tax
  revenue as the fiscal denominator.

For each DC-host county:
  DC_count_2017          = cumulative DC count through 2017 (from S&P 451)
  property_tax_2017_M    = 2017 ACFR property tax revenue ($M)
  dc_intensity           = DC_count_2017 / property_tax_2017_M    (DCs per $M tax)

Split DC-host counties into 4 quartiles by intensity.

Outcomes for the heterogeneity test (post 2013 means, when most DCs operational):
  mean_par_post     — mean annual par issued, 2014–2017
  mean_deals_post   — mean annual deals, 2014–2017
  mean_spread_post  — mean annual par-weighted spread, 2014–2017
  Compared to pre period 2000–2010 for the same county.

Outputs:
  data/derived/dc_intensity_panel.csv
  data/derived/intensity_quartile_summary.md
  data/derived/figures/fig08_intensity_quartile.png

Run: python3 scripts/python/14_dc_intensity_heterogeneity.py
"""

import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from linearmodels.panel import PanelOLS

ROOT = Path(__file__).resolve().parents[2]
PNL  = ROOT / 'data/derived/county_year_panel_v3.csv'
ACFR = ROOT / 'data/derived/acfr_county_year_wide.csv'
DC_FIPS = ROOT / 'data/derived/dc_property_county_fips.csv'
OUT_FIG = ROOT / 'data/derived/figures'
OUT_PANEL = ROOT / 'data/derived/dc_intensity_panel.csv'
OUT_MD = ROOT / 'data/derived/intensity_quartile_summary.md'

def main():
    print('Loading...')
    pnl = pd.read_csv(PNL, dtype={'county_fips':str,'state_fips':str})
    pnl['county_fips'] = pnl['county_fips'].str.zfill(5)

    acfr = pd.read_csv(ACFR, dtype={'county_fips':str})
    acfr['county_fips'] = acfr['county_fips'].str.zfill(5)
    a17 = acfr[acfr['year']==2017][['county_fips','rev_property_tax','capex_total',
                                     'lt_debt_outstanding_end','exp_curr_total']].rename(
        columns={'rev_property_tax':'prop_tax_2017','capex_total':'capex_2017',
                 'lt_debt_outstanding_end':'lt_debt_2017','exp_curr_total':'exp_curr_2017'})
    print(f'  ACFR 2017 county records: {len(a17):,}')

    dc = pd.read_csv(DC_FIPS, dtype={'county_fips':str,'STATEFIPS':str})
    dc['county_fips'] = dc['county_fips'].str.zfill(5)
    dc['open_yr']  = pd.to_numeric(dc['YEARFACILITYBECAMEOPERATIONAL'], errors='coerce')
    # Cumulative DCs operational by 2017
    dc_2017 = dc[(dc['open_yr']<=2017) & dc['open_yr'].notna()].groupby('county_fips').size().rename('n_dc_2017').reset_index()
    # First-DC year per county
    first_dc = dc[dc['open_yr'].notna()].groupby('county_fips')['open_yr'].min().rename('first_dc_year').reset_index()

    # Cross-section table
    print('\nBuilding cross-section...')
    cs = a17.merge(dc_2017, on='county_fips', how='left').merge(first_dc, on='county_fips', how='left')
    cs['n_dc_2017'] = cs['n_dc_2017'].fillna(0).astype(int)
    cs['is_dc_host'] = (cs['n_dc_2017']>0).astype(int)
    cs['first_dc_year'] = pd.to_numeric(cs['first_dc_year'], errors='coerce')

    # DC intensity = DCs per $M of property tax revenue
    cs = cs[cs['prop_tax_2017']>0].copy()
    cs['dc_intensity'] = cs['n_dc_2017'] / cs['prop_tax_2017']      # DCs per $M prop tax
    cs['dc_per_capex'] = cs['n_dc_2017'] / cs['capex_2017'].replace(0,np.nan)
    cs['dc_per_debt']  = cs['n_dc_2017'] / cs['lt_debt_2017'].replace(0,np.nan)

    print(f'  US counties with ACFR 2017 + property tax > 0: {len(cs):,}')
    print(f'  DC-host counties: {cs["is_dc_host"].sum():,}')

    # Heterogeneity by intensity quartile (among DC-host counties only)
    dch = cs[cs['is_dc_host']==1].copy()
    dch['intensity_q'] = pd.qcut(dch['dc_intensity'], 4, labels=['Q1 low','Q2','Q3','Q4 high'])
    print(f'\nIntensity quartiles among DC-host counties (n={len(dch)}):')
    qsum = dch.groupby('intensity_q', observed=True).agg(
        n_counties=('county_fips','size'),
        median_n_dc=('n_dc_2017','median'),
        median_prop_tax_M=('prop_tax_2017','median'),
        median_intensity=('dc_intensity','median'),
        median_first_dc=('first_dc_year','median'),
    ).round(3)
    print(qsum.to_string())

    # Merge intensity onto county-year panel
    pnl = pnl.merge(dch[['county_fips','intensity_q','dc_intensity','prop_tax_2017','n_dc_2017']],
                    on='county_fips', how='left')

    # Pre/Post means by quartile
    print('\nPre (2000-2010) vs Post (2014-2017) means by intensity quartile...')
    pnl['period'] = pnl['year'].apply(lambda y: 'pre' if 2000<=y<=2010 else ('post' if 2014<=y<=2017 else 'mid'))
    sub = pnl[pnl['intensity_q'].notna()]
    summary = sub.groupby(['intensity_q','period'], observed=True).agg(
        n_cy=('county_fips','size'),
        mean_par=('par_total_M','mean'),
        mean_deals=('n_deals','mean'),
        mean_spread=('par_wtd_spread_bps','mean'),
    ).round(2)
    print(summary.to_string())

    # Per-county pre/post diffs
    print('\nPer-county pre→post change in spread, by quartile (DC-host only)...')
    pre = pnl[(pnl['period']=='pre') & pnl['intensity_q'].notna()].groupby('county_fips')[
        ['par_total_M','n_deals','par_wtd_spread_bps']].mean().rename(
        columns=lambda c: f'pre_{c}')
    post = pnl[(pnl['period']=='post') & pnl['intensity_q'].notna()].groupby('county_fips')[
        ['par_total_M','n_deals','par_wtd_spread_bps']].mean().rename(
        columns=lambda c: f'post_{c}')
    diff = pre.join(post, how='outer').reset_index()
    diff = diff.merge(dch[['county_fips','intensity_q']], on='county_fips')
    diff['d_spread'] = diff['post_par_wtd_spread_bps'] - diff['pre_par_wtd_spread_bps']
    diff['d_log_par'] = np.log1p(diff['post_par_total_M']) - np.log1p(diff['pre_par_total_M'])
    diff['d_log_deals'] = np.log1p(diff['post_n_deals']) - np.log1p(diff['pre_n_deals'])

    qstats = diff.groupby('intensity_q', observed=True).agg(
        n=('county_fips','size'),
        mean_d_log_par=('d_log_par', 'mean'),
        median_d_log_par=('d_log_par', 'median'),
        mean_d_log_deals=('d_log_deals', 'mean'),
        median_d_log_deals=('d_log_deals', 'median'),
        mean_d_spread=('d_spread','mean'),
        median_d_spread=('d_spread','median'),
        n_w_spread=('d_spread', lambda x: x.notna().sum()),
    ).round(3)
    print('\n=== Pre→Post diffs by intensity quartile ===')
    print(qstats.to_string())

    # Cross-sectional regression: outcome ~ intensity quartile dummies, control for state FE
    print('\n=== Cross-sectional regression: post-period spread ~ intensity quartile ===')
    print('     (within DC-host counties only, state FE)')
    cross = pnl[(pnl['period']=='post') & pnl['intensity_q'].notna() & pnl['par_wtd_spread_bps'].notna()].copy()
    cross['state_year'] = cross['state_fips'].astype(str).str.zfill(2) + '_' + cross['year'].astype(str)
    cross['log_par']    = np.log1p(cross['par_total_M'])
    cross['log_deals']  = np.log1p(cross['n_deals'])
    qdums = pd.get_dummies(cross['intensity_q'], prefix='q', drop_first=True, dtype=float)
    cross = pd.concat([cross, qdums], axis=1)
    x_cols = [c for c in cross.columns if c.startswith('q_')]

    def run(y):
        d = cross.dropna(subset=[y]+x_cols).copy()
        # need cluster on county - use PanelOLS framework
        d = d.set_index(['county_fips','year'])
        m = PanelOLS(d[y], d[x_cols], entity_effects=False, time_effects=False, drop_absorbed=True)
        return m.fit(cov_type='clustered', cluster_entity=True)

    for y, lab in [('par_wtd_spread_bps','Spread (bps)'),
                    ('log_par','log(par+1)'),
                    ('log_deals','log(n_deals+1)')]:
        try:
            r = run(y)
            print(f'\nOutcome: {lab}')
            tab = r.params.to_frame('coef')
            tab['se'] = r.std_errors
            tab['p'] = r.pvalues
            print(tab.round(4).to_string())
        except Exception as e:
            print(f'  failed: {e}')

    # Save and visualize
    cs.to_csv(OUT_PANEL, index=False)
    print(f'\nWrote cross-section to {OUT_PANEL}')

    # Figure: pre/post by quartile
    fig, axes = plt.subplots(1, 3, figsize=(15,5))
    means = pnl.groupby(['intensity_q','year'], observed=True).agg(
        par=('par_total_M','mean'),
        deals=('n_deals','mean'),
        spread=('par_wtd_spread_bps','mean')
    ).reset_index()
    colors = {'Q1 low':'lightgray','Q2':'lightblue','Q3':'steelblue','Q4 high':'darkred'}
    for ax, ycol, ylab in [(axes[0],'spread','Mean spread (bps)'),
                             (axes[1],'par','Mean par ($M)'),
                             (axes[2],'deals','Mean # deals')]:
        for q in ['Q1 low','Q2','Q3','Q4 high']:
            s = means[means['intensity_q']==q]
            ax.plot(s['year'], s[ycol], label=q, color=colors[q], marker='o', markersize=3)
        ax.set_xlabel('Year'); ax.set_ylabel(ylab)
        ax.legend(fontsize=8); ax.grid(alpha=0.3)
        ax.set_title(ylab)
    fig.suptitle('DC intensity quartiles — DC-host counties only', y=1.02)
    fig.tight_layout()
    fig.savefig(OUT_FIG/'fig08_intensity_quartile.png', dpi=140, bbox_inches='tight')
    plt.close()
    print(f'Saved figure to {OUT_FIG/"fig08_intensity_quartile.png"}')

    # === Show specific counties in Q4 high vs Q1 low ===
    print('\n=== Q4 highest-intensity DC-host counties (top 15) ===')
    q4 = dch[dch['intensity_q']=='Q4 high'].sort_values('dc_intensity', ascending=False).head(15)
    q4 = q4.merge(pnl.groupby('county_fips').agg(state=('state_abbr','first'), cname=('county_name','first')).reset_index(),
                   on='county_fips', how='left')
    print(q4[['county_fips','cname','state','n_dc_2017','prop_tax_2017','dc_intensity','first_dc_year']].to_string(index=False))

    print('\n=== Q1 lowest-intensity DC-host counties (top 10) ===')
    q1 = dch[dch['intensity_q']=='Q1 low'].sort_values('dc_intensity').head(10)
    q1 = q1.merge(pnl.groupby('county_fips').agg(state=('state_abbr','first'), cname=('county_name','first')).reset_index(),
                   on='county_fips', how='left')
    print(q1[['county_fips','cname','state','n_dc_2017','prop_tax_2017','dc_intensity','first_dc_year']].to_string(index=False))

if __name__ == '__main__':
    main()
