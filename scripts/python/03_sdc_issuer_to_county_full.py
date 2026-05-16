"""
03_sdc_issuer_to_county_full.py

Full-population Pass-4 run on all unique (ISSUER, STATECODE) pairs in
the Tier-A 2000+, AMT>=1, non-conduit subset of SDC deals_data.

Reuses parsers and crosswalks from 02_*_pass3.py (Pass-4 layered on).

Output:
  data/derived/sdc_issuer_county_full.csv          (issuer-level, ~33k rows)
  data/derived/sdc_issuer_county_full_coverage.csv (summary by status)

Run: python3 scripts/python/03_sdc_issuer_to_county_full.py
"""

import sys, re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/python'))

# Reuse parser + lookup builders from Pass-4 module
import importlib.util
spec = importlib.util.spec_from_file_location("pass4", ROOT / "scripts/python/02_sdc_issuer_to_county_pass3.py")
pass4 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pass4)

DEALS_PATH = ROOT / 'data/sdc_muni/sdc_municipals/deals_data.sas7bdat'
OUT_ROWS = ROOT / 'data/derived/sdc_issuer_county_full.csv'
OUT_COV  = ROOT / 'data/derived/sdc_issuer_county_full_coverage.csv'
TIER_A = {'District', 'City, Town Vlg', 'Local Authority', 'County/Parish'}

def main():
    print('Loading lookups...')
    counties = pass4.load_county_table(pass4.COUNTY_PATH)
    places   = pass4.load_place_table(pass4.PLACE_PATH)
    cousubs  = pass4.load_cousub_table(pass4.COUSUB_PATH)
    print(f'  counties: {len(counties):,}   places: {len(places):,}   cousubs: {len(cousubs):,}')

    print('\nStreaming deals_data (2000+, AMT>=1, non-conduit, Tier A)...')
    pairs = {}
    n_kept = 0
    for ch in pd.read_sas(DEALS_PATH, encoding='latin-1', chunksize=200000):
        d = pd.to_datetime(ch['DELDATE'], errors='coerce')
        keep = ch[
            (d.dt.year >= 2000)
            & (ch['AMT'] >= 1)
            & (ch['CORPORATE_BACKED'] == 'No')
            & (ch['ISSTYPE_TRANS'].isin(TIER_A))
            & ch['ISSUER'].notna() & ch['STATECODE'].notna()
        ]
        n_kept += len(keep)
        for _, r in keep[['ISSUER','STATECODE','ISSTYPE_TRANS','AMT']].iterrows():
            k = (r['ISSUER'].strip(), r['STATECODE'].strip())
            v = pairs.setdefault(k, {'deals':0,'isstype':r['ISSTYPE_TRANS'],'par':0.0})
            v['deals'] += 1; v['par'] += r['AMT']
    print(f'  Tier A deals: {n_kept:,}   unique issuers: {len(pairs):,}')

    print('\nParsing all issuers...')
    rows = []
    for i, ((issuer, state), info) in enumerate(pairs.items()):
        if (i+1) % 5000 == 0: print(f'  {i+1:,} / {len(pairs):,}')
        cands = pass4.parse_issuer(issuer, state)
        final_status, final_fips, final_full = 'unresolved', None, None
        used_method, used_name = cands[0][0], cands[0][1]
        for method, name, ctype in cands:
            if method == 'unresolved': continue
            status, fips, full = pass4.resolve(state, name, ctype, counties, places, cousubs)
            if status in ('county_fips_direct','place_fips_via_crosswalk','cousub_fips_via_crosswalk'):
                final_status, final_fips, final_full = status, fips, full
                used_method, used_name = method, name
                break
            if final_status == 'unresolved':
                final_status, used_method, used_name = status, method, name
        rows.append({
            'ISSUER': issuer, 'STATECODE': state, 'ISSTYPE_TRANS': info['isstype'],
            'n_deals': info['deals'], 'par_total_M': round(info['par'],2),
            'parse_method': used_method, 'extracted_name': used_name,
            'resolve_status': final_status, 'county_fips': final_fips, 'county_full_name': final_full,
        })
    out = pd.DataFrame(rows)
    OUT_ROWS.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_ROWS, index=False)
    print(f'\nWrote {OUT_ROWS}')

    # ===== Coverage summary =====
    resolved_set = {'county_fips_direct','place_fips_via_crosswalk','cousub_fips_via_crosswalk'}
    out['resolved'] = out['resolve_status'].isin(resolved_set)

    print('\n=== Coverage — by unique issuer ===')
    print(out['resolve_status'].value_counts().to_string())
    n = len(out); hit = out['resolved'].sum()
    print(f'  RESOLVED: {hit:,}/{n:,} = {100*hit/n:.1f}%')

    print('\n=== Coverage — by deal count (each issuer weighted by its #deals) ===')
    dt = out.groupby('resolve_status')['n_deals'].sum().sort_values(ascending=False)
    print(dt.to_string())
    deals_total = out['n_deals'].sum()
    deals_hit = out.loc[out['resolved'],'n_deals'].sum()
    print(f'  RESOLVED: {deals_hit:,}/{deals_total:,} = {100*deals_hit/deals_total:.1f}%')

    print('\n=== Coverage — by par ($M) ===')
    pt = out.groupby('resolve_status')['par_total_M'].sum().sort_values(ascending=False)
    print(pt.to_string())
    par_total = out['par_total_M'].sum()
    par_hit   = out.loc[out['resolved'],'par_total_M'].sum()
    print(f'  RESOLVED: ${par_hit/1000:,.1f}B / ${par_total/1000:,.1f}B = {100*par_hit/par_total:.1f}%')

    print('\n=== By ISSTYPE_TRANS (issuer count, deal share, par share resolved) ===')
    grp = out.groupby('ISSTYPE_TRANS').agg(
        n_issuers=('ISSUER','size'),
        n_resolved=('resolved','sum'),
        deals_total=('n_deals','sum'),
        deals_resolved=('n_deals', lambda x: x[out.loc[x.index,'resolved']].sum()),
        par_total=('par_total_M','sum'),
        par_resolved=('par_total_M', lambda x: x[out.loc[x.index,'resolved']].sum()),
    )
    grp['issuer_pct']  = (100*grp['n_resolved']/grp['n_issuers']).round(1)
    grp['deals_pct']   = (100*grp['deals_resolved']/grp['deals_total']).round(1)
    grp['par_pct']     = (100*grp['par_resolved']/grp['par_total']).round(1)
    print(grp[['n_issuers','n_resolved','issuer_pct','deals_pct','par_pct']].to_string())

    # Save coverage report
    cov = pd.DataFrame({
        'level': ['unique_issuers','deals','par_USD_M'],
        'total': [n, deals_total, par_total],
        'resolved': [hit, deals_hit, par_hit],
        'pct': [round(100*hit/n,1), round(100*deals_hit/deals_total,1), round(100*par_hit/par_total,1)],
    })
    cov.to_csv(OUT_COV, index=False)
    print(f'\nWrote {OUT_COV}')

    print('\n=== Unresolved bucket — top 20 by deal count ===')
    sub = out[~out['resolved']].sort_values('n_deals', ascending=False).head(20)
    for _, r in sub.iterrows():
        print(f'  [{r.STATECODE}] {r.ISSUER}  (type={r.ISSTYPE_TRANS}, deals={r.n_deals}, par=${r.par_total_M:,.0f}M, status={r.resolve_status})')

if __name__ == '__main__':
    main()
