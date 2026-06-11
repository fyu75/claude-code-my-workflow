"""
41_integrate_d2_controls.py

Integrate D2 control-county property-tax extractions (2026-06-07 Sonnet+firecrawl
agent wave) into the master wide CSV. Covers the 19 controls that had no MuniSpot
v2 match and no disk PDF (firecrawl-acquired) PLUS the 3 GA + 1 OR controls whose
PDFs were on disk but un-extracted.

Provenance tags (state_pt_structure):
  'acfr_pdf_d2'        - fund-level property tax read from the ACFR (clean line)
  'acfr_govwide_d2'    - GA counties: property tax only on the government-wide
                         Statement of Activities (fund level bundles "Taxes");
                         value placed in property_tax_allfunds, GF left null.

Notes captured in code comments:
  - WA/ND/NV: GF-only understates (much county property tax sits in Road/special
    funds); the all-funds property-tax figure is the better measure -> populated.
  - NV Humboldt all-funds PT includes net-proceeds-of-minerals (flagged).
  - ND Mountrail property tax is genuinely tiny vs oil-driven intergovernmental rev.
  - TX Kenedy/Kimble/Stonewall: NOT_FOUND (no audited ACFR published) -> not added.
"""
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WIDE = ROOT / "data/derived/acfr_county_year_extracted_wide.csv"

# (fips, name, state, fy, pt_gf, tr_gf, pt_allfunds, tr_allfunds, tag)
NA = np.nan
ROWS = [
    # --- firecrawl-acquired (19-without-PDF set) ---
    ("13319","Wilkinson County","GA",2022, NA,        9700716,  4799935,  12035986, "acfr_govwide_d2"),  # GA: govwide PT; fund "Taxes" bundled
    ("38009","Bottineau County","ND",2023, 2662297,   5593251,  4197528,  16573828, "acfr_pdf_d2"),
    ("38061","Mountrail County","ND",2023, 31621,     52582155, 1635689,  72812683, "acfr_pdf_d2"),       # Bakken: PT tiny vs oil intergov rev
    ("38067","Pembina County","ND",  2023, 2383155,   4522403,  3318201,  11999599, "acfr_pdf_d2"),
    ("32011","Eureka County","NV",   2020, 4765613,   18502359, NA,       26439620, "acfr_pdf_d2"),       # ad valorem only; mines excluded
    ("32013","Humboldt County","NV", 2023, NA,        22690058, 10938070, 38591519, "acfr_govwide_d2"),   # allfunds PT incl net-proceeds-of-minerals
    ("53003","Asotin County","WA",   2022, 3497541,   10007783, 5663963,  28689029, "acfr_pdf_d2"),
    ("53015","Cowlitz County","WA",  2023, 20879507,  61056806, 33735374, 111438555,"acfr_pdf_d2"),
    ("53041","Lewis County","WA",    2022, 14731259,  41842222, 28518589, 104738292,"acfr_pdf_d2"),
    ("53043","Lincoln County","WA",  2021, 2362173,   8230264,  4704109,  28741920, "acfr_pdf_d2"),
    ("53059","Skamania County","WA", 2023, 2588108,   14899365, 4695869,  30954547, "acfr_pdf_d2"),
    ("48011","Armstrong County","TX",2021, 1056787,   1790921,  1502967,  2352264,  "acfr_pdf_d2"),
    ("48037","Bowie County","TX",    2024, 25068631,  46519183, 27324751, 73571637, "acfr_pdf_d2"),       # GF PT from Stmt of Activities
    ("48237","Jack County","TX",     2021, 4802180,   5683584,  6649313,  8500058,  "acfr_pdf_d2"),
    ("48311","McMullen County","TX", 2022, 14721368,  16555458, 14721368, 17083419, "acfr_pdf_d2"),       # oil county, large PT base
    ("48435","Sutton County","TX",   2022, 3763986,   5807436,  4593611,  7769402,  "acfr_pdf_d2"),
    # --- disk-PDF GA/OR set (3 GA govwide-only + Josephine OR fund-level) ---
    ("13099","Early County","GA",    2024, NA,        11175640, 6204070,  18814861, "acfr_govwide_d2"),
    ("13225","Peach County","GA",    2024, NA,        24965692, 13773859, 42237215, "acfr_govwide_d2"),
    ("13291","Union County","GA",    2023, NA,        26782739, 14072399, 47823440, "acfr_govwide_d2"),
    ("41033","Josephine County","OR",2024, 5387245,   21016900, 15003041, 78952067, "acfr_pdf_d2"),       # "Taxes"=property (marijuana tax separate)
]

df = pd.read_csv(WIDE)
df['county_fips'] = df['county_fips'].astype(str).str.zfill(5)
print(f"Wide CSV before: {len(df)} rows, {df['county_fips'].nunique()} counties")

existing = set(zip(df['county_fips'], df['fy']))
new_rows, skipped = [], []
for fips, name, st, fy, pt_gf, tr_gf, pt_af, tr_af, tag in ROWS:
    if (fips, fy) in existing:
        skipped.append((fips, name, fy))
        continue
    row = {c: np.nan for c in df.columns}
    row.update({
        'county_fips': fips, 'county_name': name, 'state': st, 'fy': fy,
        'property_tax_gf': pt_gf, 'total_revenue_gf': tr_gf,
        'property_tax_allfunds': pt_af, 'total_revenue_allfunds': tr_af,
        'state_pt_structure': tag,
    })
    new_rows.append(row)

if skipped:
    print(f"Skipped (already present): {skipped}")
df = pd.concat([df, pd.DataFrame(new_rows)[df.columns]], ignore_index=True)
df = df.sort_values(['county_fips', 'fy']).reset_index(drop=True)
df.to_csv(WIDE, index=False)

print(f"Added {len(new_rows)} D2 control rows.")
print(f"Wide CSV after: {len(df)} rows, {df['county_fips'].nunique()} counties")
has_pt = df['property_tax_gf'].notna() | df['property_tax_allfunds'].notna()
print(f"Counties with any property tax: {df[has_pt]['county_fips'].nunique()}")
print(f"\nNOT added (no published ACFR): 48261 Kenedy, 48267 Kimble, 48433 Stonewall (TX)")
