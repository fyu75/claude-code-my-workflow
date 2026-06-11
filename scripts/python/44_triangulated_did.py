"""
44_triangulated_did.py  (v2: adds CENSUS_TRUST tier + high-risk gate + ACFR-wide post)

Three-tier sample for the 2-period matched property-tax growth DiD:

  PRIMARY      - both endpoints hand-read from ACFR (verified_two_endpoint_pt.csv, status VERIFIED).
  EXPANDED     - + baseline triangulation-CONFIRMED (Census-2017 ~= v2-2017 within +-10%); post
                 from hand-ACFR / ACFR-wide / gated v2.
  CENSUS_TRUST - + SINGLE-source Census baseline accepted for LOW-RISK counties (Census is reliable
                 there: ~76% within 10%, validated), post from ACFR-wide / v2.

HIGH-RISK gate (Census NOT trusted; routed to hand-verification, NOT included):
  - KY / TN  (property tax bundled with local sales/income tax -> Census scope wrong)
  - TX with Census-2017 < $6M (small oil/mineral counties -> Census wildly mis-samples)
  - any county with Census-2017 < $3M (tiny -> thin Census sampling)

Baseline priority: hand-VERIFIED > CONFIRMED(Census=v2) > SINGLE_census(low-risk) / SINGLE_v2.
Post priority:     hand-VERIFIED > ACFR-wide(extracted) > gated v2 (only if baseline trustworthy).
CAGR sanity gate:  keep implied CAGR in [-15%, +45%]/yr.

Outputs:
  data/derived/triangulated_baseline_status.csv
  data/derived/triangulated_did_results.md
"""
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[2]; D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)
rng = np.random.default_rng(20260516)
BENCH = 0.0340
AGREE = 0.10
CAGR_LO, CAGR_HI = -0.15, 0.45
DROP = {"18153","48237","29215","29047","38105","48075","39111","40101"}
HIRISK_STATES = {"21","47"}  # KY, TN (bundling)

# ---- Census 2017 ----
c17 = pd.read_csv(D/"acfr_2017_county_govt_only.csv"); c17["county_fips"]=fz(c17["county_fips"])
census = {k: v*1e6 for k,v in zip(c17["county_fips"], c17["rev_property_tax"])}

# ---- v2 all-funds (col=-1) ----
v2 = pd.read_parquet(D/"muni_property_tax_v2_classified_allfunds_FY2016_2026.parquet",
        columns=["county_fips","fiscal_year","tier_with_pilot","column_index","reported_value","value_multiplier"])
v2["county_fips"]=fz(v2["county_fips"])
pt = v2[(v2["tier_with_pilot"]==True)&(v2["column_index"]==-1)].copy()
pt["val"]=pt["reported_value"]*pt["value_multiplier"]
v2w = pt.groupby(["county_fips","fiscal_year"])["val"].sum().unstack("fiscal_year")
def v2_at(f,y): return float(v2w.loc[f,y]) if (f in v2w.index and y in v2w.columns and pd.notna(v2w.loc[f,y])) else None
def v2_post(f):
    if f not in v2w.index: return (None,None)
    s = v2w.loc[f].dropna(); s = s[[y for y in s.index if y>=2019]]
    if len(s)==0: return (None,None)
    y=max(s.index); return (float(s[y]), int(y))

# ---- ACFR-wide extracted post (hand-scraped earlier pipeline) ----
wide = pd.read_csv(D/"acfr_county_year_extracted_wide.csv", dtype={"county_fips":str}); wide["county_fips"]=fz(wide["county_fips"])
waf = wide[wide["property_tax_allfunds"].notna() & (wide["fy"]>2017)].sort_values("fy")
WPOST = {r["county_fips"]:(float(r["property_tax_allfunds"]),int(r["fy"])) for _,r in waf.iterrows()}
def wide_post(f): return WPOST.get(f)

# ---- hand-verified ----
ver = pd.read_csv(D/"verified_two_endpoint_pt.csv", dtype={"county_fips":str}, na_values=["NA",""])
ver["county_fips"]=fz(ver["county_fips"]); HV={r["county_fips"]:r for _,r in ver.iterrows()}
def hv_base(f):
    if f not in HV: return None
    r=HV[f]
    if pd.notna(r["baseline_pt_allfunds_usd"]) and pd.notna(r["baseline_fy"]):
        return (float(r["baseline_pt_allfunds_usd"]), int(r["baseline_fy"]))
    return None
def hv_post(f):
    if f not in HV: return None
    r=HV[f]
    if pd.notna(r["post_pt_allfunds_usd"]) and pd.notna(r["post_fy"]):
        return (float(r["post_pt_allfunds_usd"]), int(r["post_fy"]))
    return None
def hv_primary(f):
    if f not in HV: return False
    r=HV[f]
    return (str(r["status"])=="VERIFIED" and pd.notna(r["baseline_pt_allfunds_usd"]) and pd.notna(r["post_pt_allfunds_usd"]))

def is_hirisk(f, cen):
    st=f[:2]
    if st in HIRISK_STATES: return True
    if st=="48" and cen is not None and cen < 6e6: return True
    if cen is not None and cen < 3e6: return True
    return False

def resolve(f):
    if f in DROP: return {"fips":f,"status":"DROP"}
    cen=census.get(f); v17=v2_at(f,2017); hb=hv_base(f)
    # ---- baseline ----
    if hb is not None: bval,byr,bstat = hb[0],hb[1],"VERIFIED"
    elif cen is not None and v17 is not None:
        if abs(v17/cen-1)<=AGREE: bval,byr,bstat = cen,2017,"CONFIRMED"
        else: return {"fips":f,"status":"CONFLICT","baseline":cen,"v2_2017":v17}
    elif cen is not None: bval,byr,bstat = cen,2017,"SINGLE_census"
    elif v17 is not None: bval,byr,bstat = v17,2017,"SINGLE_v2"
    else: return {"fips":f,"status":"NO_BASELINE"}
    hir = is_hirisk(f,cen)
    # ---- post ----
    hp=hv_post(f); wp=wide_post(f); pv2,py2=v2_post(f)
    base_trust = bstat in ("VERIFIED","CONFIRMED") or (bstat=="SINGLE_census" and not hir) or bstat=="SINGLE_v2"
    if hp is not None: pval,pyr,psrc = hp[0],hp[1],"verified"
    elif wp is not None: pval,pyr,psrc = wp[0],wp[1],"acfr_wide"
    elif pv2 is not None and base_trust: pval,pyr,psrc = pv2,py2,"v2"
    else:
        tag = bstat + ("_hirisk" if (bstat=="SINGLE_census" and hir) else "") + "_nopost"
        return {"fips":f,"status":tag,"baseline":bval}
    if pval<=0 or pyr<=byr: return {"fips":f,"status":"BADPOST"}
    cagr=(pval/bval)**(1/(pyr-byr))-1
    if not (CAGR_LO<=cagr<=CAGR_HI): return {"fips":f,"status":"CAGR_OUT","cagr":cagr}
    # ---- tier ----
    if hv_primary(f): tier="PRIMARY"
    elif bstat in ("VERIFIED","CONFIRMED","SINGLE_v2"): tier="EXPANDED"
    elif bstat=="SINGLE_census" and not hir: tier="CENSUS_TRUST"
    else: return {"fips":f,"status":"SINGLE_census_HIRISK","cagr":cagr}
    return {"fips":f,"status":"USABLE","tier":tier,"baseline":bval,"baseline_fy":byr,"base_src":bstat,
            "post":pval,"post_fy":pyr,"post_src":psrc,"cagr":cagr,"hirisk":hir}

# ---- matched design ----
m = pd.read_csv(D/"matched_controls_full125.csv"); m=m[m["control_fips"].notna()].copy()
m["treated_fips"]=fz(m["treated_fips"].astype(int).astype(str)); m["control_fips"]=fz(m["control_fips"].astype(int).astype(str))
treated=sorted(set(m["treated_fips"])); controls=sorted(set(m["control_fips"]))
allc=sorted(set(treated)|set(controls)); R={f:resolve(f) for f in allc}
prov=pd.DataFrame([{"county_fips":f,"role":"treated" if f in set(treated) else "control",
                    **{k:v for k,v in (R[f] or {"status":"NA"}).items() if k!="fips"}} for f in allc])
prov.to_csv(D/"triangulated_baseline_status.csv", index=False)

TIERS={"PRIMARY":{"PRIMARY"},"EXPANDED":{"PRIMARY","EXPANDED"},"FULL":{"PRIMARY","EXPANDED","CENSUS_TRUST"}}
def cagr_of(f,tset):
    r=R.get(f)
    if not r or r.get("status")!="USABLE" or r["tier"] not in tset: return None
    return r["cagr"]
def effects(tset):
    eff=[];tc=[]
    for t,grp in m.groupby("treated_fips"):
        ct=cagr_of(t,tset)
        if ct is None: continue
        ctrl=[cagr_of(c,tset) for c in grp["control_fips"].unique()]; ctrl=[x for x in ctrl if x is not None]
        if not ctrl: continue
        eff.append(ct-np.mean(ctrl)); tc.append(ct)
    return np.array(eff),np.array(tc)
def block(eff,tc,title):
    out=[title]
    if len(eff)<3: return out+[f"- too few usable treated ({len(eff)})",""]
    tp=stats.ttest_1samp(eff,0).pvalue; wp=stats.wilcoxon(eff).pvalue
    npos=int((eff>0).sum()); sp=stats.binomtest(npos,len(eff),0.5).pvalue
    boot=[rng.choice(eff,len(eff),replace=True).mean() for _ in range(10000)]; lo,hi=np.percentile(boot,[2.5,97.5])
    exc=tc-BENCH; ep=stats.ttest_1samp(exc,0).pvalue
    return out+[f"- N treated (matched): **{len(eff)}**",
        f"- Matched effect mean **{eff.mean()*100:+.2f}%/yr** (t p={tp:.4f}); median {np.median(eff)*100:+.2f}%",
        f"- Wilcoxon p={wp:.4f}; sign {npos}/{len(eff)} (p={sp:.4f}); bootstrap CI [{lo*100:+.2f},{hi*100:+.2f}]%",
        f"- Treated CAGR mean **{tc.mean()*100:+.2f}%/yr** vs {BENCH*100:.2f}% bench -> excess **{exc.mean()*100:+.2f}%/yr** (p={ep:.4f})",""]

L=["# Triangulated Matched DiD v2 (Census x v2, + CENSUS_TRUST tier)\n","**Date:** 2026-06-08.\n"]
def brk(units,label):
    s=prov[prov["county_fips"].isin(units)]["status"].value_counts()
    return f"**{label}** (n={len(units)}): "+", ".join(f"{k}={v}" for k,v in s.items())
L+=["## Sample build", brk(treated,"Treated"), "", brk(controls,"Controls"), ""]
for f in treated:  # tier tally
    pass
ut={tier:sum(1 for f in treated if (R[f] or {}).get("status")=="USABLE" and R[f]["tier"]==tier) for tier in ["PRIMARY","EXPANDED","CENSUS_TRUST"]}
uc={tier:sum(1 for f in controls if (R[f] or {}).get("status")=="USABLE" and R[f]["tier"]==tier) for tier in ["PRIMARY","EXPANDED","CENSUS_TRUST"]}
L+=[f"- Usable treated by tier: {ut}  (total {sum(ut.values())})",
    f"- Usable controls by tier: {uc}  (total {sum(uc.values())})",""]
for name in ["PRIMARY","EXPANDED","FULL"]:
    e,t=effects(TIERS[name]); L+=block(e,t,f"## {name}")
# FULL pooled OLS
pan=[{"county_fips":f,"is_treated":int(f in set(treated)),"cagr":R[f]["cagr"],"state_fips":f[:2]}
     for f in allc if (R[f] or {}).get("status")=="USABLE" and R[f]["tier"] in TIERS["FULL"]]
pan=pd.DataFrame(pan)
if pan["is_treated"].nunique()==2 and len(pan)>=20:
    o=smf.ols("cagr ~ is_treated + C(state_fips)",data=pan).fit(cov_type="HC1")
    L+=["## FULL pooled OLS: CAGR ~ treated + state FE",
        f"- Treated coef **{o.params['is_treated']*100:+.2f}%/yr** (SE {o.bse['is_treated']*100:.2f}, p={o.pvalues['is_treated']:.4f}), N={int(o.nobs)}",""]
(D/"triangulated_did_results.md").write_text("\n".join(L)); print("\n".join(L))
# what still needs hand-verify
need=prov[prov["status"].isin(["CONFLICT","NO_BASELINE","SINGLE_census_HIRISK"]) |
          prov["status"].str.contains("nopost",na=False)]
print(f"\nNeeds hand-verify/post (CONFLICT/NO_BASELINE/HIRISK/nopost): treated={((need['role']=='treated')).sum()}, control={((need['role']=='control')).sum()}")
