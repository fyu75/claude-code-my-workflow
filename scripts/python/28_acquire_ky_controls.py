"""
28_acquire_ky_controls.py

Acquire latest available ACFRs for the 6 KY control counties via auditor.ky.gov.

URL pattern: https://www.auditor.ky.gov/Auditreports/{County}/{YYYY}{County}FC-audit.pdf
Try most recent year first.
"""
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "external" / "acfr_pdfs"

KY_CONTROLS = [
    ("21137", "Lincoln",  "lincoln_ky"),
    ("21069", "Fleming",  "fleming_ky"),
    ("21097", "Harrison", "harrison_ky"),
    ("21089", "Greenup",  "greenup_ky"),
    ("21107", "Hopkins",  "hopkins_ky"),
    ("21019", "Boyd",     "boyd_ky"),
]
UA = "Mozilla/5.0"
YEARS = [2025, 2024, 2023, 2022]

def fetch(fips, county, slug):
    target = OUT / slug / "raw_pdfs"
    target.mkdir(parents=True, exist_ok=True)
    for year in YEARS:
        url = f"https://www.auditor.ky.gov/Auditreports/{county}/{year}{county}FC-audit.pdf"
        out_path = target / f"{slug}_acfr_{year}.pdf"
        r = subprocess.run(
            ["curl", "-sS", "-A", UA, "-o", str(out_path), "-w", "%{http_code}", url],
            capture_output=True
        )
        code = r.stdout.decode().strip().split("\n")[-1]
        if code == "200" and out_path.exists() and out_path.read_bytes()[:4] == b"%PDF":
            return year, out_path
        if out_path.exists():
            out_path.unlink()
        time.sleep(0.3)
    return None, None

if __name__ == "__main__":
    summary = {"ok": [], "miss": []}
    for fips, county, slug in KY_CONTROLS:
        year, path = fetch(fips, county, slug)
        if year:
            print(f"  [OK]   {slug} ({fips}) FY{year} → {path.name} ({path.stat().st_size:,} bytes)")
            summary["ok"].append((slug, year))
        else:
            print(f"  [MISS] {slug} ({fips})")
            summary["miss"].append(slug)
    print(f"\nSummary: {len(summary['ok'])}/{len(KY_CONTROLS)} acquired")
