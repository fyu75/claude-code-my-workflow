"""
27_acquire_or_controls.py

Acquire 2025/2024 ACFRs for the 8 OR control counties via OR SOS portal.

Uses curl subprocess because urllib trips a bot-detection JS challenge.
"""
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "external" / "acfr_pdfs"

OR_CONTROLS = [
    ("41031", "Jefferson County", "16", "jefferson_or"),
    ("41019", "Douglas County",   "10", "douglas_or"),
    ("41011", "Coos County",      "06", "coos_or"),
    ("41033", "Josephine County", "17", "josephine_or"),
    ("41045", "Malheur County",   "23", "malheur_or"),
    ("41057", "Tillamook County", "29", "tillamook_or"),
    ("41053", "Polk County",      "27", "polk_or"),
    ("41035", "Klamath County",   "18", "klamath_or"),
]

FORM_URL   = "https://secure.sos.state.or.us/muni/public.do"
SEARCH_URL = "https://secure.sos.state.or.us/muni/search.do"
REPORT_URL = "https://secure.sos.state.or.us/muni/report.do"
UA = "Mozilla/5.0"

def curl(cj, args):
    cmd = ["curl", "-sS", "-A", UA, "-b", cj, "-c", cj] + args
    return subprocess.run(cmd, capture_output=True, check=False)

def warmup(cj):
    curl(cj, [FORM_URL, "-o", "/dev/null"])

def search(cj, year, county_code):
    r = curl(cj, ["-X", "POST", SEARCH_URL,
                  "-d", f"fiscalYear={year}&county={county_code}&type=02&name=&nameCriteriaGroup=contains&search=Search"])
    html = r.stdout.decode("utf-8", errors="ignore")
    m = re.search(r"doc_rsn\.value='(\d+)'", html)
    return m.group(1) if m else None

def fetch_pdf(cj, doc_rsn, out_path):
    r = curl(cj, ["-X", "POST", REPORT_URL, "-d", f"doc_rsn={doc_rsn}", "-o", str(out_path)])
    return r.returncode == 0 and out_path.exists() and out_path.read_bytes()[:4] == b"%PDF"

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {"ok": [], "miss": [], "err": []}
    for fips, name, code, slug in OR_CONTROLS:
        target = OUT / slug / "raw_pdfs"
        target.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix="_cj.txt") as f:
            cj = f.name
        warmup(cj)
        found = None
        for year in (2025, 2024, 2023):
            rsn = search(cj, year, code)
            if rsn:
                found = (year, rsn)
                break
            time.sleep(0.5)
        if not found:
            print(f"  [MISS]  {slug} ({fips}) — no FY25/24/23 audit on file")
            summary["miss"].append(slug)
            continue
        year, rsn = found
        out_path = target / f"{slug}_acfr_{year}.pdf"
        if fetch_pdf(cj, rsn, out_path):
            print(f"  [OK]    {slug} ({fips}) FY{year} → {out_path.name} ({out_path.stat().st_size:,} bytes)")
            summary["ok"].append((slug, year))
        else:
            print(f"  [ERR]   {slug} ({fips}) FY{year} — fetch failed")
            summary["err"].append(slug)
        time.sleep(0.7)
    print("\nSummary:")
    print(f"  OK:   {len(summary['ok'])} / {len(OR_CONTROLS)} — {summary['ok']}")
    print(f"  MISS: {len(summary['miss'])} — {summary['miss']}")
    print(f"  ERR:  {len(summary['err'])} — {summary['err']}")

if __name__ == "__main__":
    main()
