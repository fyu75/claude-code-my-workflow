"""
45_division_matched_sample.py

Build the matched-control sample for the 2-period property-tax growth DiD using
ALL usable treated counties (triangulated tier = PRIMARY/EXPANDED/CENSUS_TRUST),
each matched 1:3 on the 2017 baseline property-tax LEVEL, with a Census-DIVISION
fallback when the treated county's own state has fewer than 3 usable controls.

Matching ladder (per treated county):
  1. SAME STATE   usable controls, nearest 3 by |log(base_ctrl) - log(base_treat)|
  2. SAME DIVISION usable controls (other states in the same Census division),
     used only to FILL the remaining slots up to 3, again nearest by log-distance.
Each pair is tagged match_tier = "state" or "division" so the strict (state-only)
and relaxed (state+division) samples can both be reported.

Control pool = USABLE controls only (clean baseline AND clean post), so every
matched control actually enters the DiD. Matching is WITH replacement (a strong
control can anchor several treated); control reuse is reported.

This script ONLY builds and reviews the sample. It does NOT run the DiD tests.
Output: data/derived/division_matched_pairs.csv
"""
from pathlib import Path
import numpy as np, pandas as pd
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]; D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)

# ---- Census Bureau 9 divisions, keyed by state FIPS ----
DIVISION = {
 "New England":      ["09","23","25","33","44","50"],
 "Middle Atlantic":  ["34","36","42"],
 "East North Central":["17","18","26","39","55"],
 "West North Central":["19","20","27","29","31","38","46"],
 "South Atlantic":   ["10","11","12","13","24","37","45","51","54"],
 "East South Central":["01","21","28","47"],
 "West South Central":["05","22","40","48"],
 "Mountain":         ["04","08","16","30","32","35","49","56"],
 "Pacific":          ["02","06","15","41","53"],
}
ST2DIV = {st:div for div,sts in DIVISION.items() for st in sts}
def div_of(fips): return ST2DIV.get(fips[:2], "NA")

# ---- Usable universe from the triangulation (script 44 output) ----
prov = pd.read_csv(D/"triangulated_baseline_status.csv", dtype={"county_fips":str})
prov["county_fips"] = fz(prov["county_fips"])
usable = prov[prov["status"]=="USABLE"].copy()
usable["state"] = usable["county_fips"].str[:2]
usable["division"] = usable["county_fips"].map(div_of)
usable["logpt"] = np.log(usable["baseline"].astype(float))

treated = usable[usable["role"]=="treated"].copy()
controls = usable[usable["role"]=="control"].copy()
print(f"Usable treated: {len(treated)} | Usable controls: {len(controls)}")

N = 3
pairs = []
fill_log = []          # per-treated diagnostics
for _, t in treated.iterrows():
    tf, tst, tdiv, tlog = t["county_fips"], t["state"], t["division"], t["logpt"]
    same_state = controls[controls["state"]==tst].copy()
    same_div   = controls[(controls["division"]==tdiv) & (controls["state"]!=tst)].copy()
    chosen = []
    # 1) same-state nearest
    if len(same_state):
        same_state["d"] = (same_state["logpt"]-tlog).abs()
        for _, c in same_state.nsmallest(N, "d").iterrows():
            chosen.append((c["county_fips"], c["baseline"], "state"))
    # 2) division fallback to fill remaining slots
    need = N - len(chosen)
    if need > 0 and len(same_div):
        same_div["d"] = (same_div["logpt"]-tlog).abs()
        for _, c in same_div.nsmallest(need, "d").iterrows():
            chosen.append((c["county_fips"], c["baseline"], "division"))
    for cf, cb, mt in chosen:
        pairs.append({"treated_fips":tf,"treated_state":tst,"division":tdiv,
                      "pt_2017_treated":float(t["baseline"]),
                      "control_fips":cf,"pt_2017_control":float(cb),
                      "ratio":float(cb)/float(t["baseline"]),"match_tier":mt})
    n_state = sum(1 for x in chosen if x[2]=="state")
    n_div   = sum(1 for x in chosen if x[2]=="division")
    fill_log.append({"treated_fips":tf,"division":tdiv,"n_state":n_state,
                     "n_div":n_div,"n_total":len(chosen)})

P = pd.DataFrame(pairs); F = pd.DataFrame(fill_log)
P.to_csv(D/"division_matched_pairs.csv", index=False)

# ===================== SAMPLE REVIEW (no tests) =====================
print("\n" + "="*64)
print("SAMPLE REVIEW — division-matched 1:3 (state preferred, division fallback)")
print("="*64)

n_treated_in = F[F["n_total"]>0]["treated_fips"].nunique()
print(f"\nTreated entering the matched sample: {n_treated_in} / {len(treated)}")
print(f"  filled to full 1:3            : {(F['n_total']==3).sum()}")
print(f"  partial (<3 even w/ division) : {(F['n_total']<3).sum()}  "
      f"{sorted(F.loc[F['n_total']<3,'treated_fips'].tolist())}")
print(f"  state-only (no division used) : {(F['n_div']==0).sum()}")
print(f"  needed >=1 division control   : {(F['n_div']>0).sum()}")

print(f"\nPairs total: {len(P)}  ({(P['match_tier']=='state').sum()} state, "
      f"{(P['match_tier']=='division').sum()} division)")

print(f"\nUnique controls used: {P['control_fips'].nunique()} / {len(controls)} usable")
reuse = Counter(P["control_fips"]); rc = Counter(reuse.values())
print("Control reuse (times used -> #controls): " +
      ", ".join(f"{k}x:{v}" for k,v in sorted(rc.items())))
top = reuse.most_common(5)
print("Most-reused controls: " + ", ".join(f"{c}({n})" for c,n in top))

print("\nBy division — usable treated / usable controls / treated needing fallback:")
rows=[]
for div in DIVISION:
    tt = treated[treated["division"]==div]
    cc = controls[controls["division"]==div]
    ff = F[F["division"]==div]
    rows.append((div, len(tt), len(cc), int((ff["n_div"]>0).sum()), int((ff["n_total"]<3).sum())))
rev = pd.DataFrame(rows, columns=["division","treated","controls","need_fallback","still_partial"])
print(rev.to_string(index=False))

# tier composition of the treated that entered
tier = prov.set_index("county_fips")["tier"]
P_tiers = treated.set_index("county_fips").loc[F[F["n_total"]>0]["treated_fips"]]["tier"].value_counts()
print(f"\nTreated-in by quality tier: {dict(P_tiers)}")

# ratio-band quality of the matches
inband = ((P["ratio"]>=0.5)&(P["ratio"]<=2.0)).mean()
print(f"\nMatch quality: {inband*100:.0f}% of pairs within 0.5x-2.0x baseline PT band; "
      f"median |log ratio| = {np.log(P['ratio']).abs().median():.2f}")
print("\nWrote data/derived/division_matched_pairs.csv")
