"""
01_sdc_issuer_to_county.py

Pilot run: parse SDC ISSUER strings to county FIPS for a 200-issuer sample.

Sample frame:
  * deals_data, DELDATE year >= 2000
  * AMT >= 1 ($M)
  * CORPORATE_BACKED == 'No'
  * ISSTYPE_TRANS in Tier A: District, City/Town/Village, Local Authority, County/Parish

Output:
  data/intermediate/sdc_issuer_county_pilot200.csv

Steps:
  1. Load Tier A filtered subset, get unique (ISSUER, STATECODE).
  2. Random-sample 200 unique issuers (stratified by ISSTYPE_TRANS).
  3. Apply regex parser to extract candidate county-name OR place-name.
  4. Join to Census county FIPS table (state + county_name -> 5-digit FIPS).
  5. Report coverage by method and by ISSTYPE_TRANS.

Not committed. Run with: cd repo root && python3 scripts/python/01_sdc_issuer_to_county.py
"""

import os
import re
import sys
import random
import pandas as pd
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEALS_PATH = ROOT / 'data/sdc_muni/sdc_municipals/deals_data.sas7bdat'
CENSUS_PATH = ROOT / 'data/external/census_national_county.txt'
OUT_PATH = ROOT / 'data/intermediate/sdc_issuer_county_pilot200.csv'
LOG_PATH = ROOT / 'logs/01_sdc_issuer_to_county.log'

TIER_A = {'District', 'City, Town Vlg', 'Local Authority', 'County/Parish'}
PILOT_N = 200
SEED = 20260516
random.seed(SEED)

# Census table -> dict[(state_abbr, normalized_county_name)] -> (state_fips, county_fips, county_full_name)
def load_census(path):
    df = pd.read_csv(path, sep='|', dtype=str)
    out = {}
    for _, r in df.iterrows():
        state = r['STATE']
        # Normalize: lowercase, drop punctuation, drop trailing "county/parish/borough/city/municipality/census area"
        name = r['COUNTYNAME'].lower()
        name = re.sub(r'\b(county|parish|borough|municipality|census area|city and borough|municipio)\b', '', name)
        name = re.sub(r'[^a-z0-9 ]', '', name).strip()
        name = re.sub(r'\s+', ' ', name)
        out[(state, name)] = (r['STATEFP'], r['COUNTYFP'], r['COUNTYNAME'])
    return out

# === Regex parser (Pass 2 from earlier exploration) ===
COUNTY_RX = re.compile(r'^([A-Z][A-Za-z\.\' \-]+?)\s+(?:Co|County|Parish|Boro|Borough)(?:\b|-|\s|,|\()', re.I)
CITY_RX = re.compile(r'^([A-Z][A-Za-z\.\' \-]+?)\s+(?:City|Town|Village|Township|Twp|Vlg|Twnshp)(?:\b|-|\s|,)', re.I)
LEADING_OF_RX = re.compile(
    r'^(?:City|Town|Village|Borough|Township)\s+of\s+([A-Z][A-Za-z\.\' \-]+?)(?:[-,]|$|\s\(|\s+(?:in|of)\s)', re.I)
STATE_NAMES = ['New Jersey','California','New York','Pennsylvania','Connecticut','Massachusetts','Vermont','Maine',
               'New Hampshire','Rhode Island','Maryland','Virginia','Texas','Florida','Illinois','Ohio','Michigan',
               'Wisconsin','Minnesota','Iowa','Missouri','Kansas','Nebraska','Indiana','Kentucky','Tennessee',
               'North Carolina','South Carolina','Georgia','Alabama','Mississippi','Louisiana','Arkansas','Oklahoma',
               'Colorado','New Mexico','Arizona','Nevada','Utah','Idaho','Montana','Wyoming','Washington','Oregon',
               'Alaska','Hawaii','Delaware','West Virginia','North Dakota','South Dakota']
PLACE_DASH_STATE_RX = re.compile(
    r'^([A-Z][A-Za-z\.\' \-]+?)-(' + '|'.join(re.escape(s) for s in STATE_NAMES) + r')$')

def normalize_name(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9 ]', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def parse_issuer(issuer):
    """Return (parse_method, extracted_name) or (parse_method, None) if unresolved."""
    if not isinstance(issuer, str): return ('unknown', None)
    s = issuer.strip()
    m = COUNTY_RX.match(s)
    if m: return ('county_explicit', m.group(1).strip())
    m = CITY_RX.match(s)
    if m: return ('city_suffix', m.group(1).strip())
    m = LEADING_OF_RX.match(s)
    if m: return ('city_prefix', m.group(1).strip())
    m = PLACE_DASH_STATE_RX.match(s)
    if m: return ('place_dash', m.group(1).strip())
    return ('unresolved', None)

def resolve_fips(state_abbr, candidate, method, census):
    """Try to resolve a candidate name to a county FIPS via Census table.
    For 'county_explicit', do direct lookup.
    For 'city_*' or 'place_dash', this WON'T find a county directly (place != county) — flag for Census Place crosswalk (future step).
    """
    if method == 'county_explicit' and candidate:
        key = (state_abbr, normalize_name(candidate))
        hit = census.get(key)
        if hit: return ('county_fips_direct', hit[0]+hit[1], hit[2])
        # Try removing trailing words like "city" if any slipped in
        alt = normalize_name(re.sub(r'\b(city|state)\b','',candidate, flags=re.I))
        hit = census.get((state_abbr, alt))
        if hit: return ('county_fips_direct_alt', hit[0]+hit[1], hit[2])
        return ('county_name_unmatched', None, None)
    if method in {'city_suffix','city_prefix','place_dash'}:
        return ('needs_place_crosswalk', None, None)  # next-pass work
    return ('unresolved', None, None)

def main():
    print(f'Loading Census county table from {CENSUS_PATH}...')
    census = load_census(CENSUS_PATH)
    print(f'  {len(census):,} (state, county_name) keys loaded')

    print(f'\nStreaming deals_data, filtering to Tier A 2000+ $1M+ non-conduit...')
    pairs = {}  # (ISSUER, STATECODE) -> dict(deals=N, isstype=..., par=sum)
    for ch in pd.read_sas(DEALS_PATH, encoding='latin-1', chunksize=200000):
        d = pd.to_datetime(ch['DELDATE'], errors='coerce')
        keep = ch[
            (d.dt.year >= 2000)
            & (ch['AMT'] >= 1)
            & (ch['CORPORATE_BACKED'] == 'No')
            & (ch['ISSTYPE_TRANS'].isin(TIER_A))
            & ch['ISSUER'].notna()
            & ch['STATECODE'].notna()
        ]
        for _, r in keep[['ISSUER','STATECODE','ISSTYPE_TRANS','AMT']].iterrows():
            k = (r['ISSUER'].strip(), r['STATECODE'].strip())
            v = pairs.setdefault(k, {'deals':0, 'isstype':r['ISSTYPE_TRANS'], 'par':0.0})
            v['deals'] += 1
            v['par']   += r['AMT']
    print(f'  Tier A unique (issuer, state) pairs: {len(pairs):,}')

    # Stratified random sample of 200 by ISSTYPE_TRANS
    by_type = {}
    for k, v in pairs.items():
        by_type.setdefault(v['isstype'], []).append(k)
    n_each = {t: max(1, round(PILOT_N * len(items)/len(pairs))) for t, items in by_type.items()}
    sample = []
    for t, items in by_type.items():
        random.shuffle(items)
        sample.extend(items[:n_each[t]])
    sample = sample[:PILOT_N]
    print(f'\nSampled {len(sample)} issuers, stratified by ISSTYPE_TRANS:')
    for t, n in Counter(pairs[k]['isstype'] for k in sample).items():
        print(f'  {t}: {n}')

    rows = []
    for (issuer, state) in sample:
        info = pairs[(issuer, state)]
        method, cand = parse_issuer(issuer)
        resolve, fips, full = resolve_fips(state, cand, method, census)
        rows.append({
            'ISSUER': issuer, 'STATECODE': state, 'ISSTYPE_TRANS': info['isstype'],
            'n_deals': info['deals'], 'par_total_M': round(info['par'],2),
            'parse_method': method, 'extracted_name': cand,
            'resolve_status': resolve, 'county_fips': fips, 'county_full_name': full,
        })
    out = pd.DataFrame(rows)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_PATH, index=False)
    print(f'\nWrote {OUT_PATH}')

    print('\n=== Parser-method breakdown ===')
    print(out['parse_method'].value_counts().to_string())
    print('\n=== Resolve-status breakdown ===')
    print(out['resolve_status'].value_counts().to_string())
    print('\n=== Coverage by ISSTYPE_TRANS ===')
    cross = pd.crosstab(out['ISSTYPE_TRANS'], out['resolve_status'])
    print(cross.to_string())

    direct = (out['resolve_status'].isin(['county_fips_direct','county_fips_direct_alt'])).sum()
    needs_place = (out['resolve_status']=='needs_place_crosswalk').sum()
    name_unmatched = (out['resolve_status']=='county_name_unmatched').sum()
    unresolved = (out['resolve_status']=='unresolved').sum()
    print(f'\n=== Summary on {len(out)} sampled issuers ===')
    print(f'  Direct county FIPS hit              : {direct} ({100*direct/len(out):.1f}%)')
    print(f'  Needs Census place->county crosswalk: {needs_place} ({100*needs_place/len(out):.1f}%)')
    print(f'  County name extracted but no FIPS match (spelling / edge case): {name_unmatched} ({100*name_unmatched/len(out):.1f}%)')
    print(f'  Unresolved (regex did not extract anything): {unresolved} ({100*unresolved/len(out):.1f}%)')

    print('\n=== 15 unresolved samples for eyeball ===')
    sub = out[out['resolve_status']=='unresolved'].head(15)
    for _, r in sub.iterrows():
        print(f'  [{r.STATECODE}] {r.ISSUER}  ({r.ISSTYPE_TRANS}, {r.n_deals} deals)')
    print('\n=== 15 county-name-unmatched samples ===')
    sub = out[out['resolve_status']=='county_name_unmatched'].head(15)
    for _, r in sub.iterrows():
        print(f'  [{r.STATECODE}] {r.ISSUER}  -> extracted: "{r.extracted_name}"')

if __name__ == '__main__':
    main()
