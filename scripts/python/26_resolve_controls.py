"""
26_resolve_controls.py

Attach county names + state codes to the matched-control list and group
by state portal for acquisition.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DERIVED = ROOT / "data" / "derived"

m = pd.read_csv(DERIVED / "matched_controls.csv", dtype={
    "treated_fips": str, "control_fips": str, "treated_state": str
})
m["treated_fips"] = m["treated_fips"].str.zfill(5)
m["control_fips"] = m["control_fips"].str.zfill(5)

# Pull names from S&P 451 county crosswalk (the most reliable name source we have on disk)
import csv
xwalk = {}
with open(DERIVED / "dc_property_county_fips.csv") as f:
    r = csv.DictReader(f)
    for row in r:
        fips = (row.get("county_fips") or "").zfill(5)
        if len(fips) == 5 and fips.isdigit():
            xwalk[fips] = (row.get("county_name") or "", row.get("STATE") or "")

# That only covers DC-counties. For the rest, use Census FIPS→name mapping.
# Simplest: read the standard Census county list if present, else fall back to
# pulling state codes via FIPS-state crosswalk.
STATE_FIPS_TO_ABBR = {
    "01":"AL","02":"AK","04":"AZ","05":"AR","06":"CA","08":"CO","09":"CT","10":"DE","11":"DC",
    "12":"FL","13":"GA","15":"HI","16":"ID","17":"IL","18":"IN","19":"IA","20":"KS","21":"KY",
    "22":"LA","23":"ME","24":"MD","25":"MA","26":"MI","27":"MN","28":"MS","29":"MO","30":"MT",
    "31":"NE","32":"NV","33":"NH","34":"NJ","35":"NM","36":"NY","37":"NC","38":"ND","39":"OH",
    "40":"OK","41":"OR","42":"PA","44":"RI","45":"SC","46":"TN","47":"TN","48":"TX","49":"UT",
    "50":"VT","51":"VA","53":"WA","54":"WV","55":"WI","56":"WY",
}
# Fix: 47 = TN not duplicate. (47=TN)
STATE_FIPS_TO_ABBR["47"] = "TN"

# Use Census ANSI county file if available; else just label state.
def name_state(fips):
    if fips in xwalk:
        n, s = xwalk[fips]
        return n, s
    return ("", STATE_FIPS_TO_ABBR.get(fips[:2], ""))

# Need names for control counties — let's pull from gov.com or the Census ANSI list.
# Quickest: fetch BLS/Census state-county list (likely not on disk). Use a fallback —
# the 2017 ACFR re-aggregated file has fips only. Use US Census 'national_county.txt'.
# Try local cache first
import os
NATIONAL_COUNTY = ROOT / "data" / "external" / "national_county.txt"
if NATIONAL_COUNTY.exists():
    print(f"Using cached {NATIONAL_COUNTY}")
    nc = pd.read_csv(NATIONAL_COUNTY, header=None,
                     names=["state_abbr","state_fips","county_fips_3","county_name","class"],
                     dtype=str)
    nc["county_fips"] = nc["state_fips"] + nc["county_fips_3"]
    fips_to_name = dict(zip(nc["county_fips"], nc["county_name"]))
else:
    print(f"NOTE: {NATIONAL_COUNTY} not present — will use S&P xwalk only.")
    fips_to_name = {}

def resolve(fips):
    nm = fips_to_name.get(fips) or xwalk.get(fips, ("", ""))[0]
    state = STATE_FIPS_TO_ABBR.get(fips[:2], "")
    return nm, state

t_names = []
c_names = []
for _, row in m.iterrows():
    tn, ts = resolve(row["treated_fips"])
    cn, cs = resolve(row["control_fips"])
    t_names.append(tn); c_names.append(cn)
m["treated_name"] = t_names
m["control_name"] = c_names
m["state_abbr"] = m["treated_state"].apply(lambda x: STATE_FIPS_TO_ABBR.get(str(x).zfill(2), ""))

out = DERIVED / "matched_controls_named.csv"
m.to_csv(out, index=False)
print(f"\nWrote {out}")
print(f"\nUnique controls to acquire: {m['control_fips'].nunique()}")
print(f"\nBy state portal:")
print(m.groupby("state_abbr")["control_fips"].nunique().rename("n_controls"))

print(f"\nFirst rows:")
print(m[["state_abbr","treated_fips","treated_name","control_fips","control_name","ratio"]].head(15).to_string(index=False))
