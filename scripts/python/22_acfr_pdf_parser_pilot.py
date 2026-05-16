"""
22_acfr_pdf_parser_pilot.py

Pilot ACFR PDF parser for the top-25 high-DC-share counties.

This is **scaffolding** for the broader hand-collection effort. It does three things:

  1. Maintains the target list (top-25 counties with DC share ≥ 1%).
  2. Catalogues known ACFR source URLs per county (manually populated, validates
     via WebFetch in a separate pass).
  3. Provides a pdfplumber-based extractor that pulls property tax revenue, total
     general revenue, capital outlay, and long-term debt outstanding from a given
     ACFR PDF. Works on the "Statistical Section" tables that are GASB-standard
     across counties.

The extractor is intentionally conservative — it surfaces the matches and lets
the human verify. ACFR formatting varies; brittle regex would mis-parse.

Inputs:
  data/external/acfr_pdfs/{county_slug}/raw_pdfs/*.pdf
  data/intermediate/top25_acfr_targets.csv

Outputs:
  data/derived/acfr_pilot_extraction.csv      (parsed per-PDF row)
  data/derived/acfr_pilot_coverage.md         (status report)

Run: python3 scripts/python/22_acfr_pdf_parser_pilot.py
"""

import re
from pathlib import Path
import pandas as pd
import pdfplumber

ROOT = Path(__file__).resolve().parents[2]
PDF_DIR = ROOT / 'data/external/acfr_pdfs'
OUT_CSV = ROOT / 'data/derived/acfr_pilot_extraction.csv'
OUT_MD  = ROOT / 'data/derived/acfr_pilot_coverage.md'

# ============================================================
# Target catalogue: top-25 high-DC-share counties.
# `acfr_source_url` is the SEARCH/INDEX page; `direct_pdf_template` is the
# pattern when a PDF directly downloads (filled in as we discover each).
# `state_portal` flags whether the state centralizes county financials.
# ============================================================
TARGETS = {
    # === 5 pilot counties (selected for high DC scale + likely good ACFR availability) ===
    'crook_or': dict(
        fips='41013', state='OR', name='Crook County',
        dc_share=81.2, mw=404, n_dc=14,
        source_url='https://co.crook.or.us/treasurer-finance/page/financial-statements',
        direct_pdf='https://www.crookcountyor.gov/DocumentCenter/View/12239/Crook-County-Financial-Statements-2025',
        state_portal=None,
        notes='Crook County (Prineville) — Apple, Meta, Google DC cluster. ACFR direct on county website.',
    ),
    'mecklenburg_va': dict(
        fips='51117', state='VA', name='Mecklenburg County',
        dc_share=48.7, mw=316, n_dc=22,
        source_url='https://www.apa.virginia.gov/local-government/reports/Financial-Reports/18641',
        direct_pdf='https://dlasprodpublic.blob.core.windows.net/apa/576E4581-90D5-4D6F-8352-2555D9882110.pdf',
        state_portal='VA APA — apa.virginia.gov. Centralizes all VA county reports.',
        notes='Boydton DC cluster (Microsoft). VA APA has all VA counties — promising bulk source.',
    ),
    'grant_wa': dict(
        fips='53025', state='WA', name='Grant County',
        dc_share=36.1, mw=748, n_dc=31,
        source_url='https://www.grantcountywa.gov/1103/Annual-Reports-Strategic-Plans',
        direct_pdf='https://www.grantcountywa.gov/DocumentCenter/View/13356/2023-Financial-Statements-and-Federal-Single-Audit-Report-PDF',
        state_portal='WA SAO — sao.wa.gov/reports-data/audit-reports/. Centralizes all WA county audits.',
        notes='Quincy/Moses Lake DC cluster — Microsoft, Yahoo, Sabey. WA SAO has all WA counties.',
    ),
    'morrow_or': dict(
        fips='41049', state='OR', name='Morrow County',
        dc_share=185.6, mw=1004, n_dc=23,
        source_url='https://www.co.morrow.or.us/finance/page/financial-statements',
        direct_pdf=None,  # need to inspect page first
        state_portal=None,
        notes='Boardman (AWS, Google) — #1 by MW, #2 by DC share. Direct PDF link not yet identified.',
    ),
    'umatilla_or': dict(
        fips='41059', state='OR', name='Umatilla County',
        dc_share=45.3, mw=795, n_dc=20,
        source_url='https://www.co.umatilla.or.us/departments/finance',
        direct_pdf=None,
        state_portal=None,
        notes='Hermiston (AWS) cluster. Finance page found; PDF locations to be probed.',
    ),

    # === Remaining 20 of top-25 (not pilot, but catalogued for scale-up) ===
    'lawrence_ky':   dict(fips='21127', state='KY', name='Lawrence County',  dc_share=191.0, mw=250,  n_dc=1,
                          source_url=None, direct_pdf=None,
                          state_portal='Kentucky Auditor: auditor.ky.gov',
                          notes='Very small county (~16k pop) — ACFR may be sparse.'),
    'dickens_tx':    dict(fips='48125', state='TX', name='Dickens County',   dc_share=181.1, mw=180,  n_dc=1,
                          source_url=None, direct_pdf=None,
                          state_portal='Texas: state comptroller filings',
                          notes='Very small TX county. ACFR availability uncertain.'),
    'storey_nv':     dict(fips='32029', state='NV', name='Storey County',    dc_share=176.0, mw=603,  n_dc=6,
                          source_url='https://www.storeycounty.org/government/finance',
                          direct_pdf=None,
                          state_portal=None,
                          notes='Tahoe-Reno Industrial Center (Google, Switch, Tesla).'),
    'milam_tx':      dict(fips='48331', state='TX', name='Milam County',     dc_share=156.8, mw=1192, n_dc=2,
                          source_url=None, direct_pdf=None,
                          state_portal='Texas: state comptroller filings',
                          notes='Rockdale (Microsoft, Meta).'),
    'dickey_nd':     dict(fips='38021', state='ND', name='Dickey County',    dc_share=145.3, mw=440,  n_dc=3,
                          source_url=None, direct_pdf=None,
                          state_portal='ND State Auditor portal',
                          notes='Small ND county.'),
    'franklin_nc':   dict(fips='37069', state='NC', name='Franklin County',  dc_share=131.2, mw=500,  n_dc=1,
                          source_url=None, direct_pdf=None,
                          state_portal='NC Treasurer — LGC reports',
                          notes='Rural NC county; NC LGC has standardized county reports.'),
    'cook_ga':       dict(fips='13075', state='GA', name='Cook County',      dc_share=122.5, mw=270,  n_dc=1,
                          source_url=None, direct_pdf=None,
                          state_portal='GA Department of Audits and Accounts',
                          notes='Small GA county.'),
    'knox_tx':       dict(fips='48275', state='TX', name='Knox County',      dc_share=114.8, mw=166,  n_dc=1,
                          source_url=None, direct_pdf=None,
                          state_portal='Texas comptroller',
                          notes='Tiny TX county (~3.6k pop) — ACFR may not exist publicly.'),
    'crane_tx':      dict(fips='48103', state='TX', name='Crane County',     dc_share=73.8,  mw=280,  n_dc=1,
                          source_url=None, direct_pdf=None,
                          state_portal='Texas comptroller',
                          notes='Small TX oil-county.'),
    'mayes_ok':      dict(fips='40097', state='OK', name='Mayes County',     dc_share=55.5,  mw=330,  n_dc=12,
                          source_url=None, direct_pdf=None,
                          state_portal='OK State Auditor',
                          notes='Pryor (Google) — established DC cluster.'),
    'pendoreille_wa':dict(fips='53051', state='WA', name='Pend Oreille County', dc_share=52.8, mw=100, n_dc=1,
                          source_url=None, direct_pdf=None,
                          state_portal='WA SAO',
                          notes='WA SAO covers it.'),
    'washington_ga': dict(fips='13303', state='GA', name='Washington County',dc_share=52.3,  mw=222,  n_dc=1,
                          source_url=None, direct_pdf=None,
                          state_portal='GA Audits',
                          notes='Small GA county.'),
    'ward_tx':       dict(fips='48475', state='TX', name='Ward County',      dc_share=51.3,  mw=423,  n_dc=3,
                          source_url=None, direct_pdf=None,
                          state_portal='Texas comptroller',
                          notes='Texas oil-county; some DC.'),
    'valencia_nm':   dict(fips='35061', state='NM', name='Valencia County',  dc_share=48.9,  mw=414,  n_dc=7,
                          source_url=None, direct_pdf=None,
                          state_portal='NM State Auditor',
                          notes='Belen area.'),
    'pecos_tx':      dict(fips='48371', state='TX', name='Pecos County',     dc_share=47.2,  mw=497,  n_dc=4,
                          source_url=None, direct_pdf=None,
                          state_portal='Texas comptroller',
                          notes='Texas oil + DC overlap.'),
    'marshall_ky':   dict(fips='21157', state='KY', name='Marshall County',  dc_share=43.1,  mw=195,  n_dc=2,
                          source_url=None, direct_pdf=None,
                          state_portal='KY Auditor',
                          notes='KY auditor portal.'),
    'glasscock_tx':  dict(fips='48173', state='TX', name='Glasscock County', dc_share=37.6,  mw=200,  n_dc=1,
                          source_url=None, direct_pdf=None,
                          state_portal='Texas comptroller',
                          notes='Very small TX county (~1.4k pop).'),
    'wilkes_ga':     dict(fips='13317', state='GA', name='Wilkes County',    dc_share=37.0,  mw=82,   n_dc=1,
                          source_url=None, direct_pdf=None,
                          state_portal='GA Audits',
                          notes='Small GA county.'),
    'briscoe_tx':    dict(fips='48045', state='TX', name='Briscoe County',   dc_share=36.7,  mw=50,   n_dc=1,
                          source_url=None, direct_pdf=None,
                          state_portal='Texas comptroller',
                          notes='Tiny TX county (~1.4k pop) — ACFR availability uncertain.'),
    'cherokee_nc':   dict(fips='37039', state='NC', name='Cherokee County',  dc_share=34.5,  mw=134,  n_dc=3,
                          source_url=None, direct_pdf=None,
                          state_portal='NC LGC',
                          notes='NC LGC has standardized county financial reports.'),
}

# ============================================================
# Extraction patterns for property tax revenue, debt, capex.
# These are GASB-standard terms appearing in any county ACFR.
# Match line-with-amount: "Property taxes ... 1,154,616,000" or "$1,154.6"
# ============================================================
NUMBER_RE = re.compile(r'[\$\s]*([\d,]+(?:\.\d+)?)\s*$')

# We collect candidate matches and let the human verify rather than picking one.
PATTERNS = {
    'property_tax': [
        r'(?i)\bproperty\s+tax(?:es)?\b',           # "Property tax" / "Property taxes"
        r'(?i)\bgeneral\s+property\s+tax',          # "General Property Tax"
        r'(?i)\bad\s+valorem\s+tax',                # "Ad Valorem Tax" (some southern states)
    ],
    'total_revenue': [
        r'(?i)\btotal\s+(general\s+)?revenue',
        r'(?i)\btotal\s+revenues?\b',
    ],
    'capital_outlay': [
        r'(?i)\bcapital\s+outlay',
        r'(?i)\bcapital\s+expenditures?\b',
    ],
    'lt_debt': [
        r'(?i)\blong[\-\s]term\s+debt\b',
        r'(?i)\btotal\s+long[\-\s]term\s+debt',
        r'(?i)\bbonds?\s+payable\b',
    ],
    'interest_expense': [
        r'(?i)\binterest\s+(on\s+)?(long[\-\s]term\s+)?debt',
        r'(?i)\binterest\s+expense\b',
    ],
}

def extract_candidates(pdf_path):
    """For each pattern, return list of (page, line_text) hits — let human pick."""
    hits = {k: [] for k in PATTERNS}
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for pn, page in enumerate(pdf.pages, 1):
                txt = page.extract_text() or ''
                for line in txt.split('\n'):
                    line = line.strip()
                    if not line or len(line) > 200: continue
                    for key, regexes in PATTERNS.items():
                        if any(re.search(rx, line) for rx in regexes):
                            # Check if line contains a number suggesting dollar amount
                            if re.search(r'\d', line):
                                hits[key].append((pn, line))
    except Exception as e:
        return {'error': str(e)}
    return hits

def main():
    print('=== ACFR PDF parser pilot ===\n')
    rows = []
    coverage = []

    for slug, info in TARGETS.items():
        pdf_dir = PDF_DIR / slug / 'raw_pdfs'
        pdfs = sorted(pdf_dir.glob('*.pdf')) if pdf_dir.exists() else []
        status = '✅ downloaded' if pdfs else ('🟡 source identified, not downloaded' if info.get('source_url') else '⚪ no source URL yet')
        print(f'{slug} [{info["state"]}] DC share {info["dc_share"]:.0f}% — {status}')
        coverage.append((slug, info, pdfs, status))

        for pdf in pdfs:
            print(f'  ↪ parsing {pdf.name}...')
            hits = extract_candidates(pdf)
            if 'error' in hits:
                print(f'     error: {hits["error"]}')
                rows.append({'slug':slug, 'fips':info['fips'], 'pdf':pdf.name, 'error':hits['error']})
                continue
            for key, items in hits.items():
                first = items[0] if items else ('','')
                print(f'     {key:<18s} : {len(items):>3d} hits, first @ p{first[0]}: {first[1][:80] if len(first)>1 else "(none)"}')
                # Save the first 3 hits per pattern
                for i, (pn, ln) in enumerate(items[:3]):
                    rows.append({
                        'slug':slug, 'fips':info['fips'], 'state':info['state'], 'name':info['name'],
                        'dc_share': info['dc_share'],
                        'pdf':pdf.name, 'pattern':key, 'rank':i+1, 'page':pn, 'line':ln,
                    })

    df = pd.DataFrame(rows)
    df.to_csv(OUT_CSV, index=False)
    print(f'\nWrote {OUT_CSV}')

    # Coverage markdown
    lines = ['# ACFR Pilot Collection — Status Report\n']
    lines.append(f'*Run {pd.Timestamp.now().date()}. Top-25 high-DC-share counties; 5-county pilot.*\n')
    lines.append('## Sample status\n')
    lines.append('| # | County | State | DC share | Source URL | Direct PDF | Status |')
    lines.append('|---:|---|---|---:|---|---|---|')
    for i, (slug, info, pdfs, status) in enumerate(coverage, 1):
        src = info.get('source_url','') or info.get('state_portal','')
        src_txt = src[:60]+'…' if len(src)>60 else src
        direct = '✓' if info.get('direct_pdf') else '—'
        lines.append(f'| {i} | {info["name"]} | {info["state"]} | {info["dc_share"]:.0f}% | {src_txt or "—"} | {direct} | {status} |')

    pilots = [s for s in TARGETS if s in ('crook_or','mecklenburg_va','grant_wa','morrow_or','umatilla_or')]
    downloaded = [s for s in pilots if (PDF_DIR/s/'raw_pdfs').exists() and list((PDF_DIR/s/'raw_pdfs').glob('*.pdf'))]
    lines.append(f'\n## Pilot status\n')
    lines.append(f'**Pilot counties**: 5 (Crook OR, Mecklenburg VA, Grant WA, Morrow OR, Umatilla OR)')
    lines.append(f'**ACFR PDFs downloaded**: {len(downloaded)} / 5  ({", ".join(downloaded)})')
    lines.append(f'\n**Outstanding**: Morrow OR (need direct PDF URL from finance page), Umatilla OR (same).')

    lines.append(f'\n## State-centralized portals worth leveraging\n')
    lines.append('Several states centralize county financial reports — these are bulk sources that cover many of our remaining 20 targets:')
    lines.append('- **VA Auditor of Public Accounts** — covers Mecklenburg + all VA counties')
    lines.append('- **WA State Auditor (SAO)** — covers Grant + Pend Oreille + all WA counties')
    lines.append('- **TX Comptroller** — bulk filing repository; covers Dickens, Milam, Knox, Crane, Ward, Pecos, Glasscock, Briscoe')
    lines.append('- **NC Treasurer / LGC** — covers Franklin + Cherokee + all NC counties (standardized)')
    lines.append('- **GA Department of Audits** — covers Cook, Washington, Wilkes')
    lines.append('- **KY Auditor** — covers Lawrence, Marshall')
    lines.append('- **OK State Auditor** — covers Mayes')
    lines.append('- **ND State Auditor** — covers Dickey')
    lines.append('- **NM State Auditor** — covers Valencia\n')
    lines.append('Direct county websites needed for: OR counties (Crook, Morrow, Umatilla), NV (Storey).')

    lines.append(f'\n## Parser scaffolding\n')
    lines.append('`scripts/python/22_acfr_pdf_parser_pilot.py` extracts candidate matches for five GASB-standard line items:')
    lines.append('- Property tax revenue')
    lines.append('- Total general revenue')
    lines.append('- Capital outlay')
    lines.append('- Long-term debt')
    lines.append('- Interest expense\n')
    lines.append('Match strategy: regex on line-level text from `pdfplumber`. Returns top-3 candidate hits per pattern per PDF; human verifies which is the load-bearing one.\n')

    if not df.empty and 'pattern' in df.columns:
        lines.append('## Extracted samples (first 3 hits per pattern per pilot PDF)\n')
        for slug in pilots:
            sub = df[df['slug']==slug]
            if sub.empty: continue
            lines.append(f'### {TARGETS[slug]["name"]} ({TARGETS[slug]["state"]})\n')
            for pattern in PATTERNS:
                sub2 = sub[sub['pattern']==pattern]
                if sub2.empty: continue
                lines.append(f'**{pattern}**:')
                for _, r in sub2.iterrows():
                    lines.append(f'  - p{r.page}: `{r.line[:120]}`')
                lines.append('')

    OUT_MD.write_text('\n'.join(lines))
    print(f'Wrote {OUT_MD}')

if __name__ == '__main__':
    main()
