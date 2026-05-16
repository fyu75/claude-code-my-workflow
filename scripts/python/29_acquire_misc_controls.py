"""
29_acquire_misc_controls.py

Acquire 2023/2024 ACFRs for GA, NC, VA, NV, NM, ND control counties.
Per-county URL list discovered via WebSearch / portal probing.

For each county: try a small list of candidate URLs, accept first 200 + valid PDF.
"""
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "external" / "acfr_pdfs"
UA = "Mozilla/5.0"

# UGA TED pattern for GA counties
def ted(county, years=(2024, 2023, 2022)):
    return [
        f"https://ted.cviog.uga.edu/financial-documents/sites/default/files//budgetdoc/financial-report/county-{county}-fy{y}-financial-report.pdf"
        for y in years
    ]

CONTROLS = [
    # GA — UGA TED
    ("13319", "wilkinson_ga", ted("wilkinson")),
    ("13271", "telfair_ga",   ted("telfair")),
    ("13099", "early_ga",     ted("early")),
    ("13291", "union_ga",     ted("union")),
    ("13257", "stephens_ga",  ted("stephens")),
    ("13225", "peach_ga",     ted("peach")),
]

def try_fetch(slug, urls):
    target = OUT / slug / "raw_pdfs"
    target.mkdir(parents=True, exist_ok=True)
    for url in urls:
        # Derive year from URL or use generic
        import re
        m = re.search(r"fy(\d{4})|(\d{4})", url)
        year = m.group(1) or m.group(2) if m else "unknown"
        out_path = target / f"{slug}_acfr_{year}.pdf"
        r = subprocess.run(
            ["curl", "-sSL", "-A", UA, "-o", str(out_path), "-w", "%{http_code}", url],
            capture_output=True
        )
        code = r.stdout.decode().strip().split("\n")[-1]
        if code == "200" and out_path.exists() and out_path.read_bytes()[:4] == b"%PDF":
            return year, out_path, url
        if out_path.exists():
            out_path.unlink()
        time.sleep(0.3)
    return None, None, None

if __name__ == "__main__":
    ok, miss = [], []
    for fips, slug, urls in CONTROLS:
        year, path, url = try_fetch(slug, urls)
        if year:
            print(f"  [OK]   {slug} ({fips}) FY{year} → {path.name} ({path.stat().st_size:,} bytes)")
            ok.append(slug)
        else:
            print(f"  [MISS] {slug} ({fips})")
            miss.append(slug)
    print(f"\nSummary: {len(ok)}/{len(CONTROLS)}")
    if miss:
        print(f"Miss: {miss}")
