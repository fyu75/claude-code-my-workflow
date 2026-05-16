"""
24_within_county_growth.py

2017 → 2025 within-county property-tax growth analysis for 23 high-DC-share
treated counties.

Methodology:
  - 2017 baseline: Census of Governments ACFR (county-government records only,
    `type=1` filter, primary-government scope only — comparable to PDF data).
  - 2025 (or latest) endpoint: county-government PDF-extracted property tax
    from the bulk-acquisition pipeline.
  - Growth: (latest - 2017) / 2017, expressed as % change and CAGR.
  - Benchmark: US CPI 2017→2024 = ~28% (nominal); typical county property tax
    revenue growth 2017→2024 by BLS data = ~25-30% (driven mostly by real-estate
    valuation growth and inflation).

What we expect to see if the DC fiscal-expansion story is correct:
  Treated-county growth >> benchmark (significantly above the typical county's
  inflation-driven growth).

Caveats:
  - Unit mismatch risk: PDF extractor sometimes picked up county-area totals
    (e.g., Marshall KY $67M may include school district) instead of primary
    government. Flagged in output.
  - 2017 Census ACFR may be conservative (excludes some special-district
    property tax that the PDF captures as "general property taxes").
  - Multiple growth rates per county where multiple PDF years exist.

Outputs:
  data/derived/within_county_growth_2017_to_latest.csv
  data/derived/within_county_growth_report.md
  data/derived/figures/fig_within_county_growth.png

Run: python3 scripts/python/24_within_county_growth.py
"""

import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CENSUS_2017 = ROOT / 'data/derived/acfr_2017_county_govt_only.csv'
PDF_EXTRACTED = ROOT / 'data/derived/acfr_county_year_extracted_wide.csv'
TAX_SHARE = ROOT / 'data/derived/dc_tax_share_distribution.csv'
OUT_CSV = ROOT / 'data/derived/within_county_growth_2017_to_latest.csv'
OUT_MD = ROOT / 'data/derived/within_county_growth_report.md'
OUT_FIG = ROOT / 'data/derived/figures'

# CPI 2017→2024: BLS data. Annual CPI-U:
# 2017: 245.120;  2024: 313.689 → 28.0% cumulative.
CPI_GROWTH_2017_2024 = 0.280
# County tax revenue per capita growth 2017→2024 from BLS/Census aggregates ~26%.
NATIONAL_COUNTY_TAX_GROWTH = 0.26

def main():
    print('Loading inputs...')
    # 2017 baseline: county-government-only property tax
    cen = pd.read_csv(CENSUS_2017, dtype={'county_fips':str})
    cen['county_fips'] = cen['county_fips'].str.zfill(5)
    cen = cen.rename(columns={'rev_property_tax':'pt_2017_M_census',
                                'lt_debt_outstanding_end':'debt_2017_M_census'})

    # PDF-extracted latest year per county
    pdf = pd.read_csv(PDF_EXTRACTED, dtype={'county_fips':str})
    pdf['county_fips'] = pdf['county_fips'].str.zfill(5)
    # Keep only rows with non-null property_tax
    pdf_pt = pdf[pdf['property_tax'].notna()].copy()
    # For each county, take the latest available year
    latest = pdf_pt.sort_values('fy').groupby('county_fips').tail(1)
    latest = latest[['county_fips','county_name','state','fy','property_tax']].rename(
        columns={'fy':'fy_latest','property_tax':'pt_latest_dollars'})
    latest['pt_latest_M_pdf'] = latest['pt_latest_dollars'] / 1e6
    print(f'  {len(latest)} counties have PDF property-tax data')

    # DC intensity
    tax = pd.read_csv(TAX_SHARE, dtype={'county_fips':str})
    tax['county_fips'] = tax['county_fips'].str.zfill(5)
    tax = tax[['county_fips','dc_share_mid','n_dc_latest','mw_latest']]

    # Also load 2018 PDF for Morrow OR (to use as "earliest year extracted" for trajectory)
    pdf_2018 = pdf[pdf['fy']==2018][['county_fips','property_tax']].rename(columns={'property_tax':'pt_2018_dollars'})

    # Merge
    df = latest.merge(cen[['county_fips','pt_2017_M_census']], on='county_fips', how='left')
    df = df.merge(tax, on='county_fips', how='left')
    df = df.merge(pdf_2018, on='county_fips', how='left')

    # Compute growth: (latest_pdf - 2017_census) / 2017_census
    df['pt_growth_pct'] = (df['pt_latest_M_pdf'] - df['pt_2017_M_census']) / df['pt_2017_M_census'] * 100
    # CAGR over (fy_latest - 2017) years
    df['years_elapsed'] = df['fy_latest'] - 2017
    df['pt_cagr_pct'] = ((df['pt_latest_M_pdf']/df['pt_2017_M_census']) ** (1/df['years_elapsed']) - 1) * 100

    df['vs_cpi_pct'] = df['pt_growth_pct'] - CPI_GROWTH_2017_2024*100*(df['years_elapsed']/7)
    df['vs_national_county_tax_pct'] = df['pt_growth_pct'] - NATIONAL_COUNTY_TAX_GROWTH*100*(df['years_elapsed']/7)

    df = df.sort_values('pt_cagr_pct', ascending=False)
    df.to_csv(OUT_CSV, index=False)

    # ===== Report =====
    lines = []
    L = lambda s='': (print(s), lines.append(s))[1]
    L('# Within-county property-tax growth 2017→2025 (PDF-extracted, county-govt only)\n')
    L(f'*Run {pd.Timestamp.now().date()}. Sample: {len(df)} high-DC-share counties.*\n')

    L('## Reference benchmarks (national 2017→2024)\n')
    L(f'- **CPI growth**: +{CPI_GROWTH_2017_2024*100:.0f}% nominal (BLS CPI-U)')
    L(f'- **Typical county property-tax revenue growth**: +{NATIONAL_COUNTY_TAX_GROWTH*100:.0f}% (BLS/Census aggregates)')
    L(f'- A county whose property tax tracks the national rate would grow ~26% over 7 years (CAGR ~3.4%).\n')

    L('## Per-county growth table (sorted by CAGR)\n')
    L('| County | State | DC share | 2017 ($M, Census) | Latest ($M, PDF) | FY | Years | **Growth %** | **CAGR %** | vs national |')
    L('|---|---|---:|---:|---:|---:|---:|---:|---:|---:|')
    for _, r in df.iterrows():
        if pd.isna(r.pt_2017_M_census) or pd.isna(r.pt_latest_M_pdf): continue
        gr = r.pt_growth_pct
        cagr = r.pt_cagr_pct
        natbench = NATIONAL_COUNTY_TAX_GROWTH*100*(r.years_elapsed/7)
        diff = gr - natbench
        L(f'| {r.county_name} | {r.state} | {r.dc_share_mid:.0f}% | ${r.pt_2017_M_census:.1f} | ${r.pt_latest_M_pdf:.1f} | {int(r.fy_latest)} | {int(r.years_elapsed)} | {gr:+.0f}% | {cagr:+.1f}% | {diff:+.0f}pp |')

    L('\n*Growth = total change 2017→latest. CAGR = annualized. vs national = excess over what national-average county growth would predict over the same window.*\n')

    # Summary stats
    valid = df.dropna(subset=['pt_growth_pct','pt_cagr_pct'])
    L(f'## Summary statistics ({len(valid)} counties with both 2017 + PDF latest)\n')
    L(f'- **Median CAGR**: **{valid["pt_cagr_pct"].median():.1f}%** vs national ~3.4%')
    L(f'- **Mean CAGR**: {valid["pt_cagr_pct"].mean():.1f}%')
    L(f'- **# counties growing > 5% CAGR**: {(valid["pt_cagr_pct"]>5).sum()} of {len(valid)}')
    L(f'- **# counties growing > 10% CAGR**: {(valid["pt_cagr_pct"]>10).sum()} of {len(valid)}')
    L(f'- **# counties growing slower than national**: {(valid["vs_national_county_tax_pct"]<0).sum()} of {len(valid)}')
    L('')

    # Highlight tier 1 (≥10% high-share)
    tier1 = valid[valid['dc_share_mid']>=10]
    if len(tier1):
        L(f'### Subset: counties with DC tax share ≥ 10% ({len(tier1)} counties)\n')
        L(f'- **Median CAGR**: **{tier1["pt_cagr_pct"].median():.1f}%**')
        L(f'- **Mean excess over national**: {tier1["vs_national_county_tax_pct"].mean():.0f}pp')

    L('\n## Caveats\n')
    L('1. **Unit mismatch risk**: Census 2017 = county-government only (`type=1`). PDF extraction targets the same scope, but the extractor occasionally captures county-AREA totals (e.g., Marshall KY $67M likely includes school district revenue). This biases growth UPWARD for affected counties — flag and verify.')
    L('2. **Latest-year variation**: counties have different latest-PDF years (2022 for some KY/TX/NV, 2025 for OR). CAGR normalization compensates but the sample-of-availability isn\'t random.')
    L('3. **Selection on outcome**: these 23 counties were selected because they have high DC tax share IN 2025. Counties where DCs failed to grow the tax base aren\'t in this sample. Survivor bias is mechanical here; the right comparison is treated vs matched controls, which requires more 2025 ACFRs.')
    L('4. **National benchmark is rough**: 26% is the per-capita figure; treated counties may be growing population at different rates. A better benchmark would be matched-control counties\' own 2017→2025 growth.\n')

    # === Plot ===
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    # Left: scatter of 2017 vs latest with diagonal
    ax = axes[0]
    valid_plot = valid.copy()
    ax.scatter(valid_plot['pt_2017_M_census'], valid_plot['pt_latest_M_pdf'],
                s=valid_plot['dc_share_mid'].clip(upper=100)*2, alpha=0.5, color='darkred')
    xmax = max(valid_plot['pt_2017_M_census'].max(), valid_plot['pt_latest_M_pdf'].max())*1.1
    ax.plot([0,xmax],[0,xmax], 'k--', lw=0.5, label='1:1 (no growth)')
    ax.plot([0,xmax],[0,xmax*(1+NATIONAL_COUNTY_TAX_GROWTH)], 'gray', linestyle=':', lw=1, label='+26% (national avg)')
    for _, r in valid_plot.iterrows():
        if r['pt_latest_M_pdf']/r['pt_2017_M_census'] > 1.5 or r['pt_latest_M_pdf'] > 30:
            ax.annotate(r['county_name'].replace(' County',''), (r['pt_2017_M_census'], r['pt_latest_M_pdf']),
                         fontsize=7, alpha=0.7)
    ax.set_xlabel('2017 property tax ($M, Census county-govt)'); ax.set_ylabel('Latest property tax ($M, PDF)')
    ax.set_title('2017 vs latest: 23 high-DC-share counties (size = DC share)')
    ax.grid(alpha=0.3); ax.legend()

    # Right: CAGR histogram + national reference line
    ax = axes[1]
    ax.hist(valid['pt_cagr_pct'].clip(-10, 60), bins=20, color='steelblue', alpha=0.8, edgecolor='black')
    ax.axvline(NATIONAL_COUNTY_TAX_GROWTH*100/7, color='gray', linestyle='--', lw=2, label=f'National avg CAGR ~3.4%')
    ax.axvline(valid['pt_cagr_pct'].median(), color='darkred', linestyle='-', lw=2, label=f'Treated median {valid["pt_cagr_pct"].median():.1f}%')
    ax.set_xlabel('Property-tax CAGR 2017→latest (%)'); ax.set_ylabel('# counties')
    ax.set_title('Distribution of within-county property-tax CAGR')
    ax.grid(alpha=0.3); ax.legend()

    fig.tight_layout()
    fig.savefig(OUT_FIG/'fig_within_county_growth.png', dpi=140, bbox_inches='tight')
    plt.close()
    L(f'![Within-county growth](figures/fig_within_county_growth.png)')

    OUT_MD.write_text('\n'.join(lines))
    print(f'\nWrote {OUT_CSV}')
    print(f'Wrote {OUT_MD}')
    print(f'Wrote figure: {OUT_FIG/"fig_within_county_growth.png"}')

if __name__ == '__main__':
    main()
