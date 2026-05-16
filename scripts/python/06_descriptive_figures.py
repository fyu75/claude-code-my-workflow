"""
06_descriptive_figures.py

First-look descriptive figures on the county-year panel.

Outputs to data/derived/figures/:
  fig01_dc_growth_us.png            US-wide DC count and new openings, 2000-2025
  fig02_dc_county_concentration.png Top-20 DC-host counties (cumulative count)
  fig03_top10_dc_county_issuance.png Par-volume by year, top 10 DC counties, with first-DC-year line
  fig04_treated_vs_control_par.png  Average par/county/year, DC-host vs non-host

Run: python3 scripts/python/06_descriptive_figures.py
"""

import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PNL  = ROOT / 'data/derived/county_year_panel.csv'
OUT  = ROOT / 'data/derived/figures'
OUT.mkdir(parents=True, exist_ok=True)

def main():
    pnl = pd.read_csv(PNL, dtype={'county_fips':str,'state_fips':str})

    # === Fig 1: US DC growth ===
    yr = pnl.groupby('year').agg(
        n_new=('n_dc_new','sum'),
        n_cum=('n_dc_cumulative','sum'),
    ).reset_index()
    fig, ax1 = plt.subplots(figsize=(9,5))
    ax1.bar(yr['year'], yr['n_new'], alpha=0.6, color='steelblue', label='New DCs opened (year)')
    ax1.set_xlabel('Year'); ax1.set_ylabel('New DC openings', color='steelblue')
    ax2 = ax1.twinx()
    ax2.plot(yr['year'], yr['n_cum'], color='darkred', lw=2, marker='o', label='Cumulative operational DCs')
    ax2.set_ylabel('Cumulative operational DCs', color='darkred')
    ax1.set_title('US data-center growth, 2000–2025 (S&P 451)')
    ax1.set_xticks(range(2000, 2026, 2))
    fig.tight_layout(); fig.savefig(OUT/'fig01_dc_growth_us.png', dpi=140)
    plt.close()
    print(f'  Wrote fig01_dc_growth_us.png')

    # === Fig 2: county concentration ===
    top = pnl[pnl['is_dc_host']==1].groupby(['county_fips','state_abbr','county_name']).agg(
        n_dc=('n_dc_cumulative','max'),
    ).reset_index().sort_values('n_dc', ascending=False).head(20)
    top['label'] = top['county_name'] + ', ' + top['state_abbr']
    fig, ax = plt.subplots(figsize=(8,7))
    ax.barh(top['label'][::-1], top['n_dc'][::-1], color='steelblue')
    ax.set_xlabel('Cumulative operational DCs (2025)')
    ax.set_title('Top-20 US data-center–host counties')
    ax.grid(axis='x', alpha=0.3)
    fig.tight_layout(); fig.savefig(OUT/'fig02_dc_county_concentration.png', dpi=140)
    plt.close()
    print(f'  Wrote fig02_dc_county_concentration.png')

    # === Fig 3: top-10 DC counties — par-volume time series with first-DC marker ===
    top10 = pnl[pnl['is_dc_host']==1].groupby('county_fips').agg(
        n_dc=('n_dc_cumulative','max'),
        first_dc=('first_dc_year','first'),
        name=('county_name','first'), st=('state_abbr','first'),
    ).reset_index().sort_values('n_dc', ascending=False).head(10)

    fig, axes = plt.subplots(5, 2, figsize=(13, 14), sharex=True)
    for i, (_, c) in enumerate(top10.iterrows()):
        ax = axes[i//2][i%2]
        sub = pnl[pnl['county_fips']==c['county_fips']].sort_values('year')
        ax.bar(sub['year'], sub['par_total_M'], color='steelblue', alpha=0.7)
        ax.axvline(c['first_dc'], color='darkred', linestyle='--', lw=2,
                   label=f'first DC: {int(c["first_dc"])}')
        ax.set_title(f'{c["name"]}, {c["st"]} ({int(c["n_dc"])} DCs)')
        ax.set_ylabel('Par issued ($M)')
        ax.legend(fontsize=8, loc='upper left')
        ax.grid(axis='y', alpha=0.3)
    axes[-1][0].set_xlabel('Year'); axes[-1][1].set_xlabel('Year')
    plt.suptitle('Bond issuance par by year — top 10 DC-host counties (vertical line = first DC opening)', y=1.00, fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT/'fig03_top10_dc_county_issuance.png', dpi=140)
    plt.close()
    print(f'  Wrote fig03_top10_dc_county_issuance.png')

    # === Fig 4: treated vs control mean issuance ===
    by = pnl.groupby(['year','is_dc_host']).agg(
        mean_par=('par_total_M','mean'),
        mean_deals=('n_deals','mean'),
        n_counties=('county_fips','nunique'),
    ).reset_index()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13,5))
    for h, lbl, col in [(1,'DC-host counties','darkred'), (0,'Non-host counties','grey')]:
        s = by[by['is_dc_host']==h]
        ax1.plot(s['year'], s['mean_par'], label=lbl, color=col, lw=2, marker='o', markersize=3)
        ax2.plot(s['year'], s['mean_deals'], label=lbl, color=col, lw=2, marker='o', markersize=3)
    ax1.set_title('Mean par-issued per county-year ($M)'); ax1.set_xlabel('Year'); ax1.legend(); ax1.grid(alpha=0.3)
    ax2.set_title('Mean #deals per county-year'); ax2.set_xlabel('Year'); ax2.legend(); ax2.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(OUT/'fig04_treated_vs_control_par.png', dpi=140)
    plt.close()
    print(f'  Wrote fig04_treated_vs_control_par.png')

    # === Quick numeric summary ===
    print('\n=== Mean issuance by host status ===')
    print('Overall means across all county-years (2000-2025):')
    summary = pnl.groupby('is_dc_host').agg(
        n_cy=('county_fips','size'),
        mean_par=('par_total_M','mean'),
        mean_deals=('n_deals','mean'),
        share_with_deals=('n_deals', lambda x: (x>0).mean()),
    ).round(2)
    summary.index = ['Non-host','DC-host']
    print(summary.to_string())

    # Event-study-style rough: avg par by years-since-first-DC
    print('\n=== Pre/post DC opening — avg par/county (DC-host only, ±5 yr window) ===')
    es = pnl[pnl['is_dc_host']==1].copy()
    es['t'] = es['years_since_first_dc']
    es = es[es['t'].between(-5, 10)]
    by_t = es.groupby('t').agg(n=('county_fips','size'), mean_par=('par_total_M','mean'),
                                mean_deals=('n_deals','mean')).round(2)
    print(by_t.to_string())

if __name__ == '__main__':
    main()
