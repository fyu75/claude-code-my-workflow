"""
Extract structured ACFR data from agent task output files.
Robust parser: handles $-prefixed values, ~approximations, NOT SEPARATELY STATED, null variants.
"""
import re
import json
import pandas as pd
from pathlib import Path

TASK_DIR = Path("/private/tmp/claude-501/-Users-fangyu-claude-datacenter2/b0d45ed4-b124-4985-9c2f-db97ed1112fe/tasks")

FIPS_RE = re.compile(r'\((\d{5})\)')
# COUNTY line
COUNTY_RE = re.compile(r'^COUNTY:\s*(.+)', re.MULTILINE)
# FY line — handles: "FY: 2023", "FY: FY2022", "FY: 2023 (year ended...)", "FY: FY2022 (Oct...)"
FY_RE = re.compile(r'^FY:\s*(?:FY)?(\d{4})', re.MULTILINE)
# Numeric field: grab first integer or decimal in the value (handles $, ~$, commas)
NUM_RE = re.compile(r'[\$~]*([0-9][0-9,]*(?:\.[0-9]+)?)')
# Fields we care about
FIELDS = {
    'GF_PROPERTY_TAX':       'property_tax_gf',
    'GF_TOTAL_REVENUE':      'total_revenue_gf',
    'GF_CAPITAL_OUTLAY':     'capital_outlay_gf',
    'ALLFUNDS_PROPERTY_TAX': 'property_tax_allfunds',
    'ALLFUNDS_TOTAL_REVENUE':'total_revenue_allfunds',
    'ALLFUNDS_CAPITAL_OUTLAY':'capital_outlay_allfunds',
    'STATE_PT_STRUCTURE':    'state_pt_structure',
    'STATUS':                'status',
}
# Build a pattern dict: field_key -> compiled regex for that line
FIELD_RE = {k: re.compile(rf'^{k}:\s*(.+)', re.MULTILINE) for k in FIELDS}

NULL_PREFIXES = ('null', 'n/a', 'none', 'not separately stated',
                 'not available', 'not reported', 'not extracted', 'not applicable',
                 'not found', 'unknown', 'n.a.', 'na')

def parse_num(s):
    """Return first number in string as float, or None."""
    if not s or not s.strip() or s.strip() == '-':
        return None
    low = s.strip().lower()
    for prefix in NULL_PREFIXES:
        if low.startswith(prefix):
            return None
    m = NUM_RE.search(s)
    if m:
        return float(m.group(1).replace(',', ''))
    return None

def extract_text_from_jsonl(path):
    """Extract all text content from JSONL task output file."""
    parts = []
    try:
        for line in path.read_text(errors='replace').split('\n'):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if not isinstance(obj, dict):
                    continue
                msg = obj.get('message', {})
                if not isinstance(msg, dict):
                    continue
                if msg.get('role') == 'assistant':  # skip user prompts with <int> templates
                    content = msg.get('content', '')
                    if isinstance(content, str):
                        parts.append(content)
                    elif isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get('type') == 'text':
                                parts.append(block.get('text', ''))
            except (json.JSONDecodeError, TypeError, AttributeError):
                # Plain text fallback
                parts.append(line)
    except Exception as e:
        pass
    return '\n'.join(parts)

def parse_block(block_text):
    """Parse one COUNTY block and return a record dict."""
    county_m = COUNTY_RE.search(block_text)
    fy_m = FY_RE.search(block_text)
    if not county_m or not fy_m:
        return None

    county_str = county_m.group(1).strip()
    fips_m = FIPS_RE.search(county_str)
    fips = fips_m.group(1) if fips_m else None
    county_clean = FIPS_RE.sub('', county_str).strip()

    try:
        fy = int(fy_m.group(1))
    except ValueError:
        return None

    rec = {
        'county_raw': county_clean,
        'county_fips': fips,
        'fy': fy,
    }

    for field_key, col_name in FIELDS.items():
        fm = FIELD_RE[field_key].search(block_text)
        if not fm:
            rec[col_name] = None
            continue
        raw_val = fm.group(1).strip()
        if col_name == 'state_pt_structure':
            # Take first word/phrase before any em-dash or space-dash
            rec[col_name] = re.split(r'\s*[-—]', raw_val)[0].strip().lower()
        elif col_name == 'status':
            rec[col_name] = raw_val
        else:
            rec[col_name] = parse_num(raw_val)

    return rec


def find_county_blocks(text):
    """
    Split text into segments starting at COUNTY: and ending before next COUNTY:.
    Return list of block strings.
    """
    # Find all positions of "COUNTY:" at line start
    positions = [m.start() for m in re.finditer(r'^COUNTY:', text, re.MULTILINE)]
    if not positions:
        return []
    blocks = []
    for i, pos in enumerate(positions):
        end = positions[i+1] if i+1 < len(positions) else len(text)
        blocks.append(text[pos:end])
    return blocks


records = []
no_acfr = []

output_files = sorted(TASK_DIR.glob("*.output"))
print(f"Scanning {len(output_files)} output files...")

for fpath in output_files:
    full_text = extract_text_from_jsonl(fpath)
    if not full_text:
        continue

    # Check for NO_ACFR_FOUND
    if 'NO_ACFR_FOUND' in full_text:
        county_m = COUNTY_RE.search(full_text)
        if county_m:
            no_acfr.append(county_m.group(1).strip())

    blocks = find_county_blocks(full_text)
    for block in blocks:
        rec = parse_block(block)
        if rec:
            rec['source_file'] = fpath.name
            records.append(rec)

if not records:
    print("No structured records extracted.")
    print("NO_ACFR counties:", set(no_acfr))
else:
    df = pd.DataFrame(records)

    # Drop duplicates — keep last (final answer usually comes last in JSONL)
    df = df.drop_duplicates(subset=['county_fips', 'fy'], keep='last')

    print(f"\nExtracted {len(df)} county-year records from {df['county_fips'].nunique()} distinct counties")
    print("\nCounties found:")
    for fips in sorted(df['county_fips'].dropna().unique()):
        rows = df[df['county_fips'] == fips]
        name = rows['county_raw'].iloc[0]
        fys = sorted(rows['fy'].tolist())
        has_pt = rows['property_tax_gf'].notna().any()
        has_af = rows['property_tax_allfunds'].notna().any()
        flag = ""
        if not has_pt:
            flag = " [GF PT=null]"
        if has_pt and not has_af:
            flag = " [allfunds=null]"
        print(f"  {fips}  {name:<35} FY {fys}{flag}")

    print(f"\nNO-ACFR counties ({len(set(no_acfr))}):")
    for c in sorted(set(no_acfr)):
        print(f"  {c}")

    # Save
    out_path = Path("/Users/fangyu/claude/datacenter2/data/derived/acfr_agent_extracted_raw.csv")
    df.to_csv(out_path, index=False)
    print(f"\nSaved raw extracted records → {out_path}")
