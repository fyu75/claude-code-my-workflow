"""
02_sdc_issuer_to_county_pass3.py

Pass-3 parser: same 200-issuer pilot as 01_*, but with:
  (a) State-aware borough rule (NJ/PA Boro = town, AK Borough = county)
  (b) Directional-prefix strip (No/N./North/East/West/South/etc.)
  (c) Suffix-stripping for special-district / school / authority issuers
  (d) Place->county FIPS lookup via spatial-join crosswalk
       (data/external/place_to_county_fips.csv built in helper script)

Output:
  data/intermediate/sdc_issuer_county_pilot200_pass3.csv

Run: python3 scripts/python/02_sdc_issuer_to_county_pass3.py
"""

import os, re, random
import pandas as pd
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEALS_PATH = ROOT / 'data/sdc_muni/sdc_municipals/deals_data.sas7bdat'
COUNTY_PATH = ROOT / 'data/external/census_national_county.txt'
PLACE_PATH = ROOT / 'data/external/place_to_county_fips.csv'
COUSUB_PATH = ROOT / 'data/external/cousub_to_county_fips.csv'
OUT_PATH = ROOT / 'data/intermediate/sdc_issuer_county_pilot200_pass4.csv'

TIER_A = {'District', 'City, Town Vlg', 'Local Authority', 'County/Parish'}
PILOT_N = 200
SEED = 20260516

# ----- helpers -----
def norm(s):
    if not isinstance(s, str): return ''
    s = re.sub(r'[^a-z0-9 ]', '', s.lower())
    return re.sub(r'\s+', ' ', s).strip()

def load_county_table(path):
    df = pd.read_csv(path, sep='|', dtype=str)
    out = {}
    for _, r in df.iterrows():
        name = re.sub(r'\b(county|parish|borough|municipality|census area|city and borough|municipio)\b','',
                      r['COUNTYNAME'].lower())
        name = norm(name)
        out[(r['STATE'], name)] = (r['STATEFP'], r['COUNTYFP'], r['COUNTYNAME'])
    return out

def load_place_table(path):
    df = pd.read_csv(path, dtype={'state':str, 'name_norm':str, 'FIPS':str})
    out = {}
    for _, r in df.iterrows():
        out.setdefault((r['state'], r['name_norm']), r['FIPS'])
    return out

def load_cousub_table(path):
    df = pd.read_csv(path, dtype={'state':str, 'name_norm':str, 'county_fips':str})
    out = {}
    for _, r in df.iterrows():
        out.setdefault((r['state'], r['name_norm']), r['county_fips'])
    return out

# ----- regex layers -----
COUNTY_RX = re.compile(r'^([A-Z][A-Za-z\.\' \-]+?)\s+(?:Co|County|Parish)(?:\b|-|\s|,|\()', re.I)
# AK boroughs ARE counties; NJ/PA "Boro" is a TOWN — handle separately
AK_BOROUGH_RX = re.compile(r'^([A-Z][A-Za-z\.\' \-]+?)\s+Borough(?:\b|-|\s|,|\()', re.I)
NJ_PA_BORO_RX = re.compile(r'^([A-Z][A-Za-z\.\' \-]+?)\s+(?:Boro|Borough)(?:\b|-|\s|,|\()', re.I)

CITY_SUFFIX_RX = re.compile(r'^([A-Z][A-Za-z\.\' \-]+?)\s+(?:City|Town|Village|Township|Twp|Vlg|Twnshp)(?:\b|-|\s|,)', re.I)
LEADING_OF_RX = re.compile(r'^(?:City|Town|Village|Borough|Township)\s+of\s+([A-Z][A-Za-z\.\' \-]+?)(?:[-,]|$|\s\(|\s+(?:in|of)\s)', re.I)
STATE_NAMES = ['New Jersey','California','New York','Pennsylvania','Connecticut','Massachusetts','Vermont','Maine',
               'New Hampshire','Rhode Island','Maryland','Virginia','Texas','Florida','Illinois','Ohio','Michigan',
               'Wisconsin','Minnesota','Iowa','Missouri','Kansas','Nebraska','Indiana','Kentucky','Tennessee',
               'North Carolina','South Carolina','Georgia','Alabama','Mississippi','Louisiana','Arkansas','Oklahoma',
               'Colorado','New Mexico','Arizona','Nevada','Utah','Idaho','Montana','Wyoming','Washington','Oregon',
               'Alaska','Hawaii','Delaware','West Virginia','North Dakota','South Dakota']
PLACE_DASH_STATE_RX = re.compile(r'^([A-Z][A-Za-z\.\' \-]+?)-(' + '|'.join(re.escape(s) for s in STATE_NAMES) + r')$')

# Pass-3: county after a leading place name, "XX-Yy Co" pattern
PLACE_DASH_COUNTY_RX = re.compile(r'^[A-Z][A-Za-z\.\']+\-([A-Z][A-Za-z\.\' ]+?)\s+Co\b', re.I)

# Pass-4: school district with parenthetical sub-name — "Schoharie (Gilboa-Conesville) CSD",
#         "Yavapai (Cottonwood-Oak Creek) ESD #6". The county name is the leading token before "(".
SCHOOL_PAREN_RX = re.compile(
    r'^([A-Z][A-Za-z\.\' \-]+?)\s*\([^)]+\)\s*'
    r'(?:CSD|ISD|UFSD|UHSD|ESD|CUSD|UESD|PSD|SD)\b', re.I)

# Pass-3: special-district / school / authority suffixes — strip and treat residual as a place name
SUFFIX_STRIP = re.compile(
    r'\s+(?:'
    r'MUD(?:\s+#?\d+)?|'
    r'CFD(?:\s+#?[\d\-]+)?|'
    r'Metropolitan\s+(?:Dt|District)(?:\s+#?\d+)?|'
    r'Metro\s+Dt(?:\s+#?\d+)?|'
    r'Comm\s+Dev\s+Dt|Community\s+Develop(?:ment)?\s+Dt|Community\s+Development\s+District|'
    r'Park(?:\s+&\s+Rec)?\s+(?:Dt|Dist|District)|'
    r'Library\s+(?:Dt|District)|'
    r'Dt\s+Library|'
    r'Fire\s+(?:Dt|Dist|District)|'
    r'Water\s+(?:Dt|Dist|Supply\s+Dt(?:\s+#?\d+)?|Conservation\s+Dt|District)|'
    r'Wtr\s+(?:Dt|Dist)(?:\s+#?\d+)?|'
    r'Hospital\s+(?:Dt|Dist|District)|'
    r'Util(?:ity)?\s+(?:Dt|Dist)|'
    r'Sanitary\s+(?:Dt|Dist|District)|'
    r'Drain(?:age)?\s+(?:Dt|Dist|District)|'
    r'Public\s+Schools?(?:\s+BOE)?|'
    r'School\s+(?:Bldg|Building)\s+Corp|'
    r'ISD\s+Finance\s+Corp|SD\s+Fin\s+Corp|SD\s+Finance\s+Corp|'
    r'Comm\s+Coll\s+Dt|Community\s+College\s+(?:Dt|District)|'
    r'Public\s+Building\s+Comm(?:ission)?|'
    r'Board\s+of\s+Education|'
    r'BOE'
    r')\b.*$', re.I)

# Pass-3: directional prefix strip
DIR_PREFIX = re.compile(r'^(?:No|N|N\.|North|Nthn|Northern|E|E\.|East|Eastrn|Eastern|S|S\.|South|Sthn|Southern|W|W\.|West|Wstn|Western|Northeast|Northwest|Southeast|Southwest|NE|NW|SE|SW)\s+', re.I)

NJ_PA = {'NJ','PA'}

def parse_issuer(issuer, state):
    """Return list of (parse_method, candidate_name, candidate_type) tuples to try in order."""
    if not isinstance(issuer, str): return []
    s = issuer.strip()
    cands = []

    # 1) Explicit county / parish (US-wide rule)
    m = COUNTY_RX.match(s)
    if m:
        n = m.group(1).strip()
        # Strip directional prefix if present
        n = DIR_PREFIX.sub('', n).strip()
        cands.append(('county_explicit', n, 'county'))

    # 2) AK borough = county; NJ/PA boro = town
    if state == 'AK':
        m = AK_BOROUGH_RX.match(s)
        if m: cands.append(('ak_borough', m.group(1).strip(), 'county'))
    if state in NJ_PA:
        m = NJ_PA_BORO_RX.match(s)
        if m: cands.append(('njpa_boro', m.group(1).strip(), 'place'))

    # 3) "Place-County Co" pattern (e.g., "Newport-Vermillion Co Pub Library")
    m = PLACE_DASH_COUNTY_RX.match(s)
    if m: cands.append(('place_dash_county', DIR_PREFIX.sub('', m.group(1).strip()), 'county'))

    # 3b) School district with parenthetical: "Schoharie (Gilboa-Conesville) CSD" → Schoharie Co
    m = SCHOOL_PAREN_RX.match(s)
    if m:
        n = DIR_PREFIX.sub('', m.group(1).strip())
        cands.append(('school_paren_county', n, 'county'))
        cands.append(('school_paren_place',  n, 'place'))   # fallback if not a county name

    # 4) City suffix
    m = CITY_SUFFIX_RX.match(s)
    if m: cands.append(('city_suffix', m.group(1).strip(), 'place'))

    # 5) "City of XX" / "Town of XX"
    m = LEADING_OF_RX.match(s)
    if m: cands.append(('city_prefix', m.group(1).strip(), 'place'))

    # 6) Place-dash-state ("Cranbury-New Jersey")
    m = PLACE_DASH_STATE_RX.match(s)
    if m: cands.append(('place_dash_state', m.group(1).strip(), 'place'))

    # 7) Strip special-district / authority suffix; residual is candidate place name
    stripped = SUFFIX_STRIP.sub('', s).strip()
    if stripped and stripped != s and len(stripped) > 1:
        cands.append(('suffix_strip', stripped, 'place'))

    return cands or [('unresolved', None, None)]

def resolve(state, cand_name, cand_type, counties, places, cousubs):
    if cand_name is None: return ('unresolved', None, None)
    n = norm(cand_name)
    if cand_type == 'county':
        hit = counties.get((state, n))
        if hit: return ('county_fips_direct', hit[0]+hit[1], hit[2])
        return ('county_name_unmatched', None, None)
    if cand_type == 'place':
        hit = places.get((state, n))
        if hit: return ('place_fips_via_crosswalk', hit, None)
        # Try cousub (MCD) fallback — useful for Northeast townships not in Place file
        hit = cousubs.get((state, n))
        if hit: return ('cousub_fips_via_crosswalk', hit, None)
        return ('place_name_unmatched', None, None)
    return ('unresolved', None, None)

def main():
    print('Loading lookups...')
    counties = load_county_table(COUNTY_PATH); print(f'  county table: {len(counties):,}')
    places = load_place_table(PLACE_PATH); print(f'  place crosswalk: {len(places):,}')
    cousubs = load_cousub_table(COUSUB_PATH); print(f'  cousub crosswalk: {len(cousubs):,}')

    print('\nStreaming deals_data (2000+, AMT>=1, non-conduit, Tier A)...')
    pairs = {}
    for ch in pd.read_sas(DEALS_PATH, encoding='latin-1', chunksize=200000):
        d = pd.to_datetime(ch['DELDATE'], errors='coerce')
        keep = ch[
            (d.dt.year >= 2000)
            & (ch['AMT'] >= 1)
            & (ch['CORPORATE_BACKED'] == 'No')
            & (ch['ISSTYPE_TRANS'].isin(TIER_A))
            & ch['ISSUER'].notna() & ch['STATECODE'].notna()
        ]
        for _, r in keep[['ISSUER','STATECODE','ISSTYPE_TRANS','AMT']].iterrows():
            k = (r['ISSUER'].strip(), r['STATECODE'].strip())
            v = pairs.setdefault(k, {'deals':0,'isstype':r['ISSTYPE_TRANS'],'par':0.0})
            v['deals'] += 1; v['par'] += r['AMT']
    print(f'  Tier A unique issuers: {len(pairs):,}')

    # Same stratified sample as Pass-2 (seeded same)
    random.seed(SEED)
    by_type = {}
    for k,v in pairs.items():
        by_type.setdefault(v['isstype'], []).append(k)
    n_each = {t: max(1, round(PILOT_N * len(items)/len(pairs))) for t, items in by_type.items()}
    sample = []
    for t, items in by_type.items():
        random.shuffle(items)
        sample.extend(items[:n_each[t]])
    sample = sample[:PILOT_N]
    print(f'\nSampled {len(sample)} issuers')

    rows = []
    for (issuer, state) in sample:
        info = pairs[(issuer, state)]
        cands = parse_issuer(issuer, state)
        final_status, final_fips, final_full, used_method, used_name = 'unresolved', None, None, cands[0][0], cands[0][1]
        for method, name, ctype in cands:
            if method == 'unresolved': continue
            status, fips, full = resolve(state, name, ctype, counties, places, cousubs)
            if status in ('county_fips_direct','place_fips_via_crosswalk','cousub_fips_via_crosswalk'):
                final_status, final_fips, final_full = status, fips, full
                used_method, used_name = method, name
                break
            # otherwise keep walking through candidates; record the best non-resolved status
            if final_status == 'unresolved':
                final_status, used_method, used_name = status, method, name
        rows.append({
            'ISSUER': issuer, 'STATECODE': state, 'ISSTYPE_TRANS': info['isstype'],
            'n_deals': info['deals'], 'par_total_M': round(info['par'],2),
            'parse_method': used_method, 'extracted_name': used_name,
            'resolve_status': final_status, 'county_fips': final_fips, 'county_full_name': final_full,
        })
    out = pd.DataFrame(rows)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_PATH, index=False)

    print(f'\nWrote {OUT_PATH}')
    print('\n=== Resolve-status breakdown ===')
    print(out['resolve_status'].value_counts().to_string())
    print('\n=== Coverage by ISSTYPE_TRANS ===')
    print(pd.crosstab(out['ISSTYPE_TRANS'], out['resolve_status']).to_string())

    hit = out['resolve_status'].isin(['county_fips_direct','place_fips_via_crosswalk','cousub_fips_via_crosswalk']).sum()
    print(f'\n=== Summary ===')
    print(f'  Resolved to FIPS (county_direct OR place_crosswalk): {hit}/{len(out)} = {100*hit/len(out):.1f}%')
    print(f'  Unresolved: {len(out)-hit} = {100*(len(out)-hit)/len(out):.1f}%')

    print('\n=== 20 remaining unresolved (for eyeball) ===')
    for _, r in out[~out['resolve_status'].isin(['county_fips_direct','place_fips_via_crosswalk','cousub_fips_via_crosswalk'])].head(20).iterrows():
        print(f'  [{r.STATECODE}] {r.ISSUER}  (status={r.resolve_status}, extracted="{r.extracted_name}")')

if __name__ == '__main__':
    main()
