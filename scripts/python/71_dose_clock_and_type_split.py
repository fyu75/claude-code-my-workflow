"""
71_dose_clock_and_type_split.py

Two refinements of Test 3 (Frank, 2026-06-10):

1. CLOCK: announcement ("investors know") vs OPERATIONAL ("county begins to collect
   revenue from the DC"). Same dose construction, cumulated on each clock. If the
   market prices cash flows when they ARRIVE rather than when they are announced,
   the operational clock could reveal what the announcement clock missed.

2. TYPE-SPLIT dose: split each county's >=50MW capacity into CRYPTO-MW vs
   HYPERSCALE/COLO-MW using the per-DC S&P PROVIDERTYPE flag ('Cryptocurrency
   Mining'/'Cryptocurrency Hosting' ever attached to the property). Sharper than the
   county-level dc_class cuts in script 70: mixed counties (Laramie, Niagara, Pecos...)
   host BOTH types; two dose regressors in ONE regression identify which capacity
   type drives any bond response.

dose construction identical to script 70: cum MW (>=50MW DCs only) on the given clock /
baseline-2017 property tax ($M). log(1+dose) primary (verified robust); linear winsorized
at 50 MW/$M (Glasscock 641 leverage, see 70's appendix). County+year FE, cluster county;
clean never pool (2,639); phantoms excluded.

Output: data/derived/dose_clock_and_type_split.md
"""
from pathlib import Path
import numpy as np, pandas as pd
import pyfixest as pf
import warnings; warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
RAW = Path("/Users/fangyu/claude/datacenter/raw")
D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)
Y0, Y1 = 2008, 2025
PHANTOM = {"47121", "54047", "21127"}

# ---------- per-DC MW + clocks + crypto flag ----------
per = pd.read_sas(RAW / "dcpropertiesperiodic_latest.sas7bdat", encoding="latin-1")
per["pid"] = per["PROPERTYUNIQUEID"].astype(str).str.replace(r"\.0$", "", regex=True)
mw = per.groupby("pid")["TOTALITPOWER"].max().div(1000).rename("mw_peak").reset_index()
nm = per.dropna(subset=["DATACENTERNAME"]).groupby("pid")["DATACENTERNAME"].first().rename("dcname").reset_index()
pv = pd.read_sas(RAW / "dcprovider_latest.sas7bdat", encoding="latin-1")
pv["pid"] = pv["PROPERTYUNIQUEID"].astype(str).str.replace(r"\.0$", "", regex=True)
crypto_pids = set(pv.loc[pv.PROVIDERTYPE.str.contains("Cryptocurrency", na=False), "pid"])
# finer category: crypto > hyperscale > colo (Retail/Wholesale/Telco/Hosting/Reseller) > other
ptypes = pv.groupby("pid")["PROVIDERTYPE"].apply(lambda x: set(x.dropna()))
def _cat(ts):
    if any("Cryptocurrency" in t for t in ts): return "cry"
    if "Hyperscale" in ts: return "hyp"
    if ts & {"Retail", "Wholesale", "Telco", "Hosting", "Reseller"}: return "colo"
    return "oth"
pid_cat = ptypes.apply(_cat)

prop = pd.read_csv(D / "dc_property_county_fips.csv")
prop["pid"] = prop["PROPERTYUNIQUEID"].astype("Int64").astype(str)
prop["county_fips"] = fz(prop["county_fips"].astype(str))
prop["oy"] = pd.to_numeric(prop["YEARFACILITYBECAMEOPERATIONAL"], errors="coerce")
m = prop.merge(mw, on="pid").merge(nm, on="pid", how="left")
m["is_crypto_dc"] = m.pid.isin(crypto_pids)
m["cat"] = m.pid.map(pid_cat).fillna("oth")

T = pd.read_csv(D / "treated_universe_labeled.csv", dtype={"county_fips": str}); T["county_fips"] = fz(T["county_fips"])
T = T[~T.county_fips.isin(PHANTOM)].copy()
treated = set(T.county_fips); cls = dict(zip(T.county_fips, T.dc_class))

big = m[(m.mw_peak >= 50) & m.county_fips.isin(treated)].copy()
a = pd.read_csv(D / "dc_dc_level_announcements.csv", dtype={"county_fips": str}); a["county_fips"] = fz(a["county_fips"])
a = a[a.announce_year.notna()][["county_fips", "dcname", "announce_year"]]
big = big.merge(a, on=["county_fips", "dcname"], how="left")
cty = pd.read_csv(D / "dc_announcement_years.csv", dtype={"county_fips": str}); cty["county_fips"] = fz(cty["county_fips"])
cmap = dict(zip(cty.county_fips, cty.announce_year))
big["ann"] = big["announce_year"].fillna(big.county_fips.map(cmap)).fillna(big["oy"] - 1)
print(f"big DCs: {len(big)} | crypto-flagged: {int(big.is_crypto_dc.sum())} | "
      f"counties with BOTH types: {big.groupby('county_fips')['is_crypto_dc'].nunique().eq(2).sum()}")

tp = pd.read_csv(D / "treated_pt_final.csv", dtype={"county_fips": str}); tp["county_fips"] = fz(tp["county_fips"])
g = pd.read_csv(D / "census_2017_2022_growth.csv", dtype={"county_fips": str}); g["county_fips"] = fz(g["county_fips"])
pt17 = {**dict(zip(g.county_fips, g.rev_property_tax_17)), **dict(zip(tp.county_fips, tp.pt_2017_final))}

# ---------- dose panels: clock x type ----------
rows = []
for f in sorted(set(big.county_fips)):
    sub = big[big.county_fips == f]; p = pt17.get(f, np.nan)
    for y in range(Y0, Y1 + 1):
        r = {"county_fips": f, "year": y}
        for clock, col in [("ann", "ann"), ("op", "oy")]:
            known = sub[sub[col] <= y]
            r[f"mw_{clock}"] = known.mw_peak.sum()
            r[f"mw_{clock}_crypto"] = known.loc[known.is_crypto_dc, "mw_peak"].sum()
            r[f"mw_{clock}_clean"] = known.loc[~known.is_crypto_dc, "mw_peak"].sum()
            for cat in ("hyp", "colo", "cry", "oth"):
                r[f"mw_{clock}_{cat}"] = known.loc[known.cat == cat, "mw_peak"].sum()
        for k in list(r.keys()):
            if k.startswith("mw_"):
                dosev = r[k] / p if (p and p > 0) else np.nan
                r[k.replace("mw_", "ld_")] = np.log1p(dosev) if pd.notna(dosev) else np.nan
                r[k.replace("mw_", "dw_")] = min(dosev, 50) if pd.notna(dosev) else np.nan
        rows.append(r)
dose = pd.DataFrame(rows)
dmap = dose.set_index(["county_fips", "year"])
DOSEVARS = [c for c in dose.columns if c.startswith(("ld_", "dw_"))]

never = set(pd.read_csv(D / "clean_never_dc_controls.csv", dtype=str)["county_fips"].pipe(fz))

# ---------- outcome panels ----------
d = pd.read_csv(D / "sdc_deal_spread.csv"); d["county_fips"] = fz(d["county_fips"].astype(int).astype(str))
r_ = pd.read_csv(D / "sdc_deal_rating.csv")
for x in (d, r_): x["MASTER_DEAL_NO"] = pd.to_numeric(x["MASTER_DEAL_NO"], errors="coerce").astype("Int64")
d = d.merge(r_, on="MASTER_DEAL_NO", how="left")
d = d[(d.AMT > 0) & d.year.between(Y0, Y1)].copy()
d["logamt"] = np.log(d.AMT); d["logmat"] = np.log(d.par_wtd_yrs2mat.clip(lower=0.25))
pan = pd.read_csv(D / "county_year_panel_v4.csv", dtype={"county_fips": str}); pan["county_fips"] = fz(pan["county_fips"])
cy = pan.copy()

def prep(df):
    s = df[df.county_fips.isin(treated | never)].copy()
    idx = pd.MultiIndex.from_arrays([s.county_fips, s.year])
    for c in DOSEVARS: s[c] = dmap[c].reindex(idx).values
    s[DOSEVARS] = s[DOSEVARS].fillna(0.0)
    s["dc_class"] = s.county_fips.map(cls)
    return s

dd, cc = prep(d), prep(cy)

def run(df, y, xs, ctrl=""):
    s = df.dropna(subset=[y] + ([c.strip() for c in ctrl.split("+") if c.strip()] if ctrl else []))
    m_ = pf.feols(f"{y} ~ {' + '.join(xs)}" + (f" + {ctrl}" if ctrl else "") + " | county_fips + year",
                  data=s, vcov={"CRV1": "county_fips"})
    out = {}
    for x in xs:
        b, se, p = m_.coef()[x], m_.se()[x], m_.pvalue()[x]
        st = "***" if p < .01 else "**" if p < .05 else "*" if p < .10 else ""
        out[x] = f"{b:+.3f}{st} ({se:.3f}) p={p:.3f}"
    return out

OUTC = [("Spread (bps, deal hedonic)", dd, "spread_bps", "logamt + logmat"),
        ("Rating ext (any-rated, deal)", dd, "any_rated_share", ""),
        ("Spread par-wtd (cy)", cc[cc.n_deals.fillna(0) > 0], "par_wtd_spread_bps", "")]

L = ["# Test 3 refinements — clock (announcement vs operational) and type-split dose\n",
     "**Date:** 2026-06-10. `scripts/python/71`. dose = cum >=50MW MW / 2017 PT ($M); log(1+dose) primary; "
     "county+year FE; cluster county; clean never pool; phantoms excluded. Per-DC crypto flag from S&P "
     "PROVIDERTYPE.\n",
     "## 1. Clock comparison — log(1+dose), single dose term",
     "| Outcome | Cut | ANNOUNCEMENT clock | OPERATIONAL clock |", "|---|---|---|---|"]
for label, df, y, ctl in OUTC:
    for nm_, ks in [("ALL", ["clean_dc", "crypto", "mixed"]), ("clean_dc", ["clean_dc"]), ("crypto", ["crypto"])]:
        sub = df[(df.county_fips.isin(never)) | (df.dc_class.isin(ks))]
        try:
            ra = run(sub, y, ["ld_ann"], ctl)["ld_ann"]
            ro = run(sub, y, ["ld_op"], ctl)["ld_op"]
            L.append(f"| {label} | {nm_} | {ra} | {ro} |")
        except Exception as e:
            L.append(f"| {label} | {nm_} | ERR {str(e)[:20]} | |")

L += ["", "## 2. Type-split dose — crypto-MW and hyperscale-MW jointly, ALL counties",
      "| Outcome | Clock | beta crypto-dose | beta hyperscale-dose |", "|---|---|---|---|"]
for label, df, y, ctl in OUTC:
    for clock in ["ann", "op"]:
        try:
            r2 = run(df, y, [f"ld_{clock}_crypto", f"ld_{clock}_clean"], ctl)
            L.append(f"| {label} | {clock} | {r2[f'ld_{clock}_crypto']} | {r2[f'ld_{clock}_clean']} |")
        except Exception as e:
            L.append(f"| {label} | {clock} | ERR {str(e)[:20]} | |")

L += ["", "## 3. Three-way category split — hyperscale / colocation / crypto doses jointly, ALL counties",
      "93 hyperscale / 48 crypto / 27 colo / 3 other big DCs (MW share 37/50/11.5/1.6%). Colo sits in only "
      "8 counties -> noisy. 'other' included as an unreported control term.",
      "| Outcome | Clock | hyperscale-dose | colo-dose | crypto-dose |", "|---|---|---|---|---|"]
for label, df, y, ctl in OUTC:
    for clock in ["ann", "op"]:
        xs = [f"ld_{clock}_hyp", f"ld_{clock}_colo", f"ld_{clock}_cry", f"ld_{clock}_oth"]
        try:
            r3 = run(df, y, xs, ctl)
            L.append(f"| {label} | {clock} | {r3[xs[0]]} | {r3[xs[1]]} | {r3[xs[2]]} |")
        except Exception as e:
            L.append(f"| {label} | {clock} | ERR {str(e)[:20]} | | |")

# leave-one-out check on the colo-dose spread coefficient (Loudoun = 54% of colo MW)
loo_lines = ["", "### Colo-dose spread: leave-one-out (op clock, deal hedonic)"]
sX = dd.dropna(subset=["spread_bps", "logamt", "logmat"])
xs_loo = ["ld_op_hyp", "ld_op_colo", "ld_op_cry", "ld_op_oth"]
for lab, fr in [("full", sX), ("drop Loudoun 51107", sX[sX.county_fips != "51107"]),
                ("drop Loudoun+PWC", sX[~sX.county_fips.isin({"51107", "51153"})])]:
    m_ = pf.feols("spread_bps ~ " + " + ".join(xs_loo) + " + logamt + logmat | county_fips + year",
                  data=fr, vcov={"CRV1": "county_fips"})
    loo_lines.append(f"- {lab}: colo {m_.coef()['ld_op_colo']:+.1f} (p={m_.pvalue()['ld_op_colo']:.3f})")
loo_lines.append("-> survives LOO but rests on ~6-8 clusters, op clock only (ann clock ns): "
                 "SUGGESTIVE, not a headline.")
L += loo_lines

L += ["", "## Reading",
      "- Clock: announce->operational lead is short (median 1yr) so large differences are not expected; "
      "if the operational clock shows pricing the announcement clock missed, the market reacts to CASH "
      "FLOWS not news (and vice versa).",
      "- Type-split: identifies WHICH capacity type drives any response within one regression (mixed "
      "counties contribute to both terms). Prediction from the dummy results: crypto-dose carries any "
      "spread widening / rated-share retreat; hyperscale-dose flat.",
      "- cy spread cells inherit the aggregation-weighting caveat from script 70's appendix; deal-level "
      "hedonic is preferred.", ""]
(D / "dose_clock_and_type_split.md").write_text("\n".join(L))
print("\n".join(L)); print("\nWrote dose_clock_and_type_split.md")
