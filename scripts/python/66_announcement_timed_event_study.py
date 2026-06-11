"""
66_announcement_timed_event_study.py

Compile the DC ANNOUNCEMENT years collected by the 6-agent wave (2026-06-10), quantify the
announcement->operational lead, and RE-TIME the bond-spread event study to the announcement year
(tests Frank's anticipation hypothesis: does the market reprice when the DC is ANNOUNCED, years
before it is operational?).

Confidence: H/M/L. Drop L for the event study (small crypto miners w/o press releases -> unreliable
announcement timing). Spread panel = county-year (script 63 build); event time = year - announce_yr,
binned, ref -1, county + year FE, cluster county.

Output: data/derived/dc_announcement_years.csv, data/derived/announcement_timed_event_study.md
"""
from pathlib import Path
import numpy as np, pandas as pd
import pyfixest as pf
ROOT=Path(__file__).resolve().parents[2]; D=ROOT/"data"/"derived"
def fz(s): return s.astype(str).str.zfill(5)

# (announce_year, confidence) per county_fips, from the 6 agent batches
A={
"01071":(2015,"H"),"01075":(None,"L"),"01089":(2018,"H"),"04013":(2000,"L"),"08085":(2021,"M"),
"13075":(2019,"H"),"13097":(2007,"M"),"13121":(2000,"M"),"13145":(2021,"H"),"13157":(2021,"M"),
"13217":(2018,"H"),"13285":(2021,"H"),"13303":(2020,"H"),"13313":(2018,"H"),"13317":(2022,"H"),
"16001":(2000,"M"),"17037":(2020,"H"),"18127":(2023,"H"),"18141":(2003,"M"),"18153":(2022,"H"),
"19049":(2017,"H"),"19075":(2019,"M"),"19083":(2022,"H"),"19153":(2008,"H"),"19155":(2007,"H"),
"19181":(2016,"H"),"21035":(2020,"L"),"21109":(2021,"L"),"21127":(2022,"H"),"21145":(2021,"H"),
"21157":(2019,"H"),"21195":(2022,"H"),"21225":(2022,"M"),"26027":(2020,"H"),"28089":(2024,"H"),
"29047":(2022,"H"),"30003":(2020,"H"),"31019":(2019,"H"),"31081":(2010,"M"),"31153":(2017,"H"),
"32003":(2000,"M"),"32031":(2012,"H"),"35061":(2016,"H"),"36063":(2019,"M"),"36089":(2018,"H"),
"37027":(2007,"H"),"37035":(2009,"H"),"37069":(2017,"M"),"37161":(2010,"H"),"38021":(2022,"H"),
"38035":(2021,"H"),"38093":(2021,"H"),"38105":(2022,"H"),"39045":(2024,"M"),"39049":(2015,"M"),
"39063":(2024,"M"),"39089":(2017,"H"),"39111":(2021,"M"),"39159":(2021,"M"),"40097":(2007,"H"),
"40101":(2024,"H"),"41013":(2009,"H"),"41049":(2010,"M"),"41059":(2011,"M"),"41065":(2005,"H"),
"41067":(2000,"M"),"42007":(2022,"H"),"42079":(2021,"H"),"42121":(2021,"M"),"45015":(2007,"H"),
"45083":(2022,"H"),"45087":(2022,"H"),"45091":(2023,"H"),"47013":(2022,"M"),"47025":(2021,"L"),
"47035":(2022,"L"),"47105":(2021,"M"),"47107":(2023,"L"),"47113":(2024,"H"),"47121":(2020,"L"),
"47125":(2015,"H"),"47151":(2020,"M"),"47165":(2020,"H"),"47173":(2021,"M"),"48003":(2021,"M"),
"48045":(2021,"H"),"48067":(2021,"L"),"48075":(2022,"H"),"48103":(2022,"L"),"48109":(2023,"H"),
"48125":(2021,"H"),"48135":(2021,"H"),"48139":(2017,"H"),"48173":(2022,"H"),"48221":(2022,"H"),
"48275":(2023,"L"),"48277":(2023,"L"),"48325":(2021,"M"),"48331":(2018,"H"),"48349":(2022,"H"),
"48355":(2025,"M"),"48371":(2021,"H"),"48389":(2021,"M"),"48441":(2021,"H"),"48461":(2021,"H"),
"48475":(2021,"M"),"49035":(2009,"M"),"49049":(2018,"H"),"51047":(2007,"H"),"51061":(2016,"H"),
"51087":(2010,"H"),"51107":(1998,"H"),"51153":(2003,"M"),"51193":(2019,"L"),"53017":(2006,"H"),
"53025":(2005,"H"),"53051":(2021,"H"),"55101":(2023,"H"),"56021":(2012,"H"),
}
ann=pd.DataFrame([(k,v[0],v[1]) for k,v in A.items()],columns=["county_fips","announce_year","conf"])
T=pd.read_csv(D/"treated_universe_labeled.csv",dtype={"county_fips":str}); T["county_fips"]=fz(T["county_fips"])
ann=ann.merge(T[["county_fips","name","state","dc_class","first_op_year"]],on="county_fips",how="left")
ann["lead"]=ann["first_op_year"]-ann["announce_year"]
ann.to_csv(D/"dc_announcement_years.csv",index=False)

L=["# Announcement-Timed Event Study (anticipation test)\n",
   "**Date:** 2026-06-10. `scripts/python/66`. DC announcement years (6-agent wave) -> announcement→"
   "operational lead, and bond-spread event study RE-TIMED to announcement.\n",
   f"## Coverage: {len(ann)} counties | confidence H={sum(ann.conf=='H')} M={sum(ann.conf=='M')} "
   f"L={sum(ann.conf=='L')}",
   f"## Announcement → Operational LEAD (the anticipation window)"]
hl=ann[ann.conf.isin(["H","M"])&ann.lead.notna()]
L+=[f"- Mean lead **{hl.lead.mean():.1f} yrs**, median **{hl.lead.median():.0f} yrs** (H+M, n={len(hl)})",
    f"- lead distribution: "+", ".join(f"{int(k)}y:{v}" for k,v in hl.lead.clip(-1,8).value_counts().sort_index().items()),
    f"- clean_dc mean lead {hl[hl.dc_class=='clean_dc'].lead.mean():.1f}y vs crypto {hl[hl.dc_class=='crypto'].lead.mean():.1f}y "
    "(hyperscale plans further ahead than crypto)",""]

# ---- announcement-timed spread event study ----
share_keep=set(ann[ann.conf.isin(["H","M"])]["county_fips"])
annyr=dict(zip(ann.county_fips,ann.announce_year))
d=pd.read_csv(D/"sdc_deal_spread.csv"); d["county_fips"]=fz(d["county_fips"].astype(int).astype(str))
pan=pd.read_csv(D/"county_year_panel_v4.csv",dtype={"county_fips":str}); pan["county_fips"]=fz(pan["county_fips"])
never=pan.groupby("county_fips")["n_dc_cumulative"].max().pipe(lambda s:set(s[s==0].index))-set(T.county_fips)
d=d[d.county_fips.isin(share_keep|never)&(d.AMT>0)&d.year.between(2008,2025)].copy()
def pw(g,c):
    w=g.loc[g[c].notna(),"AMT"]; return (g.loc[g[c].notna(),c]*w).sum()/w.sum() if w.sum()>0 else np.nan
cyr=d.groupby(["county_fips","year"]).apply(lambda g: pd.Series({"spr":pw(g,"spread_bps")})).reset_index().dropna(subset=["spr"])
cyr["treated_ever"]=cyr.county_fips.isin(share_keep).astype(int); cyr["ay"]=cyr.county_fips.map(annyr)
cyr["et"]=np.where(cyr.treated_ever==1, cyr.year-cyr.ay, np.nan)
for k in [-4,-3,-2,0,1,2,3,4]:
    cyr[f"e{k:+d}".replace('+','p').replace('-','m')]=((cyr.treated_ever==1)&(np.clip(cyr.et,-4,4)==k)).astype(int)
ec=[c for c in cyr.columns if c.startswith("ep") or c.startswith("em")]
m=pf.feols("spr ~ "+" + ".join(ec)+" | county_fips + year",data=cyr,vcov={"CRV1":"county_fips"})
co,pv=m.coef(),m.pvalue()
L+=["## Spread event study RE-TIMED to ANNOUNCEMENT (county+year FE, bps; ref −1)",
    "| event time vs ANNOUNCE | coef (bps) | p | |","|---|---:|---:|---|"]
for k in [-4,-3,-2,0,1,2,3,4]:
    c=f"e{k:+d}".replace('+','p').replace('-','m'); b=co.get(c,np.nan); p=pv.get(c,np.nan)
    st="***" if p<.01 else "**" if p<.05 else "*" if p<.10 else ""
    tag="pre-announcement (placebo)" if k<0 else ("**announced**" if k==0 else "post-announcement")
    L.append(f"| {k:+d} | {b:+.2f}{st} | {p:.3f} | {tag} |")
L+=["| −1 | 0 (ref) | — | reference |","",
    "## Reading",
    "- If spreads are FLAT pre-announcement and FALL after announcement (0,+1,+2 negative) -> ANTICIPATION "
    "confirmed: the market reprices at announcement, which the operational-dated specs mistimed as a 'pre-trend'.",
    "- If pre-announcement is also negative/noisy -> still a level/selection difference, not anticipation.",
    f"- Mean lead {hl.lead.median():.0f}yrs means the operational-dated event study's 'year −{int(hl.lead.median())}' "
    "≈ this study's 'year 0' (announcement).",
    "- LOW-confidence counties dropped; small crypto miners w/o press releases have unreliable announce timing.",""]
(D/"announcement_timed_event_study.md").write_text("\n".join(L)); print("\n".join(L))
print("\nWrote dc_announcement_years.csv + announcement_timed_event_study.md")
