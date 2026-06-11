"""
70_continuous_dose_announcement.py

Test 3 of the chain (Frank, 2026-06-10): CONTINUOUS measure of DC impact on county
finances, on the announcement clock, with the knowledge dummy absorbing (1 in every
year >= announcement — "investors know there is a DC in this county").

Primary continuous measure (new, assumption-free, in the information set):

   dose_{c,t} = ( cumulative ANNOUNCED major-DC capacity, MW ) / ( baseline 2017 county
                 property tax, $M )

 - numerator: sum of mw_peak over the county's >=50MW DCs whose ANNOUNCEMENT year <= t
   (per-DC announce dates from the 172/172 wave; county-level fallback; op-1 last resort).
   Absorbing: once announced, capacity stays in the investor information set.
 - denominator: scope-consistent 2017 property tax (Phase-1 final where available, else
   Census) — the county's fiscal size when the boom started.
 - interpretation: MW of known data-center capacity per $M of baseline property tax.
   Under the working $50k/MW assumption, 1 MW/$M ~ 5% of the baseline tax base, so
   beta per MW/$M ~ beta per 5pp of expected fiscal share. No $/MW assumption enters
   the regressor itself.

Specs (county + year FE, cluster county; clean never-DC pool 2,639; cuts ALL/clean/crypto):
   (i)   dose (linear, MW/$M)
   (ii)  log(1 + dose)        [dose spans 0.3 -> 87, log compresses the skew]
   (iii) announced x dc_share_mid (static fiscal-share ratio — Frank's original; robustness)

Outcomes: deal-level spread (hedonic), cy par-wtd spread, issuance extensive/intensive,
rating extensive. If the bond market prices the DC fiscal channel, beta should be
significant and monotone; flat dose-response + dummy nulls = the channel is not priced.

Output: data/derived/continuous_dose_announcement.md (+ dose panel csv)
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

# ---------- per-DC MW x announcement (built in pre-step, regenerate here) ----------
per = pd.read_sas(RAW / "dcpropertiesperiodic_latest.sas7bdat", encoding="latin-1")
per["pid"] = per["PROPERTYUNIQUEID"].astype(str).str.replace(r"\.0$", "", regex=True)
mw = per.groupby("pid")["TOTALITPOWER"].max().div(1000).rename("mw_peak").reset_index()
nm = per.dropna(subset=["DATACENTERNAME"]).groupby("pid")["DATACENTERNAME"].first().rename("dcname").reset_index()
prop = pd.read_csv(D / "dc_property_county_fips.csv")
prop["pid"] = prop["PROPERTYUNIQUEID"].astype("Int64").astype(str)
prop["county_fips"] = fz(prop["county_fips"].astype(str))
prop["oy"] = pd.to_numeric(prop["YEARFACILITYBECAMEOPERATIONAL"], errors="coerce")
m = prop.merge(mw, on="pid").merge(nm, on="pid", how="left")

T = pd.read_csv(D / "treated_universe_labeled.csv", dtype={"county_fips": str}); T["county_fips"] = fz(T["county_fips"])
T = T[~T.county_fips.isin(PHANTOM)].copy()
treated = set(T.county_fips); cls = dict(zip(T.county_fips, T.dc_class))
share = dict(zip(T.county_fips, T.dc_share_mid))

big = m[(m.mw_peak >= 50) & m.county_fips.isin(treated)].copy()
a = pd.read_csv(D / "dc_dc_level_announcements.csv", dtype={"county_fips": str}); a["county_fips"] = fz(a["county_fips"])
a = a[a.announce_year.notna()][["county_fips", "dcname", "announce_year"]]
big = big.merge(a, on=["county_fips", "dcname"], how="left")
cty = pd.read_csv(D / "dc_announcement_years.csv", dtype={"county_fips": str}); cty["county_fips"] = fz(cty["county_fips"])
cmap = dict(zip(cty.county_fips, cty.announce_year))
big["ann"] = big["announce_year"].fillna(big.county_fips.map(cmap)).fillna(big["oy"] - 1)

# baseline PT denominator: Phase-1 final preferred, Census fallback
tp = pd.read_csv(D / "treated_pt_final.csv", dtype={"county_fips": str}); tp["county_fips"] = fz(tp["county_fips"])
g = pd.read_csv(D / "census_2017_2022_growth.csv", dtype={"county_fips": str}); g["county_fips"] = fz(g["county_fips"])
pt17 = {**dict(zip(g.county_fips, g.rev_property_tax_17)), **dict(zip(tp.county_fips, tp.pt_2017_final))}

# county x year dose panel
years = range(Y0, Y1 + 1)
rows = []
for f in sorted(set(big.county_fips)):
    sub = big[big.county_fips == f]; p = pt17.get(f, np.nan)
    for y in years:
        cmw = sub.loc[sub.ann <= y, "mw_peak"].sum()
        rows.append({"county_fips": f, "year": y, "cum_ann_mw": cmw,
                     "dose": cmw / p if (p and p > 0) else np.nan})
dose = pd.DataFrame(rows)
dose["log_dose"] = np.log1p(dose["dose"])
# winsorize the LINEAR spec at 50 MW/$M: Glasscock 48173 (documented artifact/oil county)
# reaches dose=641 and single-handedly flips the linear crypto-spread coefficient
# (-0.169*** raw -> +0.21 ns winsorized; verified 2026-06-10). Raw dose kept in the csv.
dose["dose_w"] = dose["dose"].clip(upper=50)
dose.to_csv(D / "dc_dose_announced_mw_panel.csv", index=False)
dmap = dose.set_index(["county_fips", "year"])

# announcement (county) anchor for the static ratio spec
anc = pd.read_csv(D / "announcement_anchor_county.csv", dtype={"county_fips": str}); anc["county_fips"] = fz(anc["county_fips"])
A = (T[["county_fips"]].merge(anc[["county_fips", "ann_firstmaj"]], on="county_fips", how="left")
       .merge(cty[["county_fips", "announce_year"]], on="county_fips", how="left"))
A["A_firstmaj"] = A["ann_firstmaj"].fillna(A["announce_year"])
amap = dict(zip(A.county_fips, A.A_firstmaj))

never = set(pd.read_csv(D / "clean_never_dc_controls.csv", dtype=str)["county_fips"].pipe(fz))

# ---------- outcome panels ----------
d = pd.read_csv(D / "sdc_deal_spread.csv"); d["county_fips"] = fz(d["county_fips"].astype(int).astype(str))
r_ = pd.read_csv(D / "sdc_deal_rating.csv")
for x in (d, r_): x["MASTER_DEAL_NO"] = pd.to_numeric(x["MASTER_DEAL_NO"], errors="coerce").astype("Int64")
d = d.merge(r_, on="MASTER_DEAL_NO", how="left")
d = d[(d.AMT > 0) & d.year.between(Y0, Y1)].copy()
d["logamt"] = np.log(d.AMT); d["logmat"] = np.log(d.par_wtd_yrs2mat.clip(lower=0.25))
pan = pd.read_csv(D / "county_year_panel_v4.csv", dtype={"county_fips": str}); pan["county_fips"] = fz(pan["county_fips"])
cy = pan.copy(); cy["any_issue"] = (cy.n_deals.fillna(0) > 0).astype(int)
cy["log_par"] = np.log1p(cy.par_total_M.fillna(0))

def prep(df):
    s = df[df.county_fips.isin(treated | never)].copy()
    idx = pd.MultiIndex.from_arrays([s.county_fips, s.year])
    s["dose_w"] = dmap["dose_w"].reindex(idx).values
    s["log_dose"] = dmap["log_dose"].reindex(idx).values
    for c in ("dose_w", "log_dose"): s[c] = s[c].fillna(0.0)      # controls + pre-announcement = 0
    s["AY"] = s.county_fips.map(amap)
    s["announced"] = ((s.county_fips.isin(treated)) & (s.year >= s.AY)).astype(int)
    s["ann_x_share"] = s["announced"] * s.county_fips.map(share).fillna(0)
    s["dc_class"] = s.county_fips.map(cls)
    return s

dd, cc = prep(d), prep(cy)

def beta(df, y, x, ctrl=""):
    s = df.dropna(subset=[y] + ([c.strip() for c in ctrl.split("+") if c.strip()] if ctrl else []))
    m_ = pf.feols(f"{y} ~ {x}" + (f" + {ctrl}" if ctrl else "") + " | county_fips + year",
                  data=s, vcov={"CRV1": "county_fips"})
    b, se, p = m_.coef()[x], m_.se()[x], m_.pvalue()[x]
    st = "***" if p < .01 else "**" if p < .05 else "*" if p < .10 else ""
    return f"{b:+.3f}{st} ({se:.3f}) p={p:.3f}"

L = ["# Continuous DC dose on the announcement clock — Test 3 (dose-response)\n",
     "**Date:** 2026-06-10. `scripts/python/70`. dose = cumulative ANNOUNCED >=50MW capacity (MW) / "
     "baseline 2017 property tax ($M) — absorbing, assumption-free, in the investor information set. "
     "1 MW/$M ~ 5pp of expected fiscal share under the $50k/MW working assumption. County+year FE, "
     "cluster county; clean never pool (2,639); phantoms excluded.\n",
     f"Dose panel: 74 counties; p50/p90/max dose at 2025 = "
     f"{dose[dose.year == 2025].dose.median():.1f} / {dose[dose.year == 2025].dose.quantile(.9):.1f} / "
     f"{dose[dose.year == 2025].dose.max():.0f} MW/$M.\n",
     "| Outcome | Cut | (i) dose MW/$M (wins. 50) | (ii) log(1+dose) | (iii) announced x share |",
     "|---|---|---|---|---|"]

OUTC = [("Spread (bps, deal hedonic)", dd, "spread_bps", "logamt + logmat"),
        ("Rating ext (any-rated, deal)", dd, "any_rated_share", ""),
        ("Issuance P(any deal) (cy)", cc, "any_issue", ""),
        ("Issuance log(1+par) (cy)", cc, "log_par", ""),
        ("Spread par-wtd (cy)", cc[cc.n_deals.fillna(0) > 0], "par_wtd_spread_bps", "")]
for label, df, y, ctl in OUTC:
    for nm_, ks in [("ALL", ["clean_dc", "crypto", "mixed"]), ("clean_dc", ["clean_dc"]), ("crypto", ["crypto"])]:
        sub = df[(df.county_fips.isin(never)) | (df.dc_class.isin(ks))]
        try:
            L.append(f"| {label} | {nm_} | {beta(sub, y, 'dose_w', ctl)} | "
                     f"{beta(sub, y, 'log_dose', ctl)} | {beta(sub, y, 'ann_x_share', ctl)} |")
        except Exception as e:
            L.append(f"| {label} | {nm_} | ERR {str(e)[:25]} | | |")

L += ["", "## Verification appendix (run 2026-06-10, before trusting any cell)",
      "- LINEAR dose is winsorized at 50 MW/$M: raw-dose crypto-spread -0.169*** was 100% Glasscock "
      "48173 leverage (dose=641, documented artifact/oil county); winsorized -> +0.21 ns.",
      "- cy par-wtd spread shows log-dose +12.7** for clean even after dropping dose>50 counties, but the "
      "PREFERRED deal-level hedonic spec is null (-2.0 ns, also null without hedonics; no dose-related "
      "shift in maturity/amount mix). Discrepancy = aggregation weighting: cy gives tiny, rarely-issuing "
      "high-dose counties (Morrow/Storey/Briscoe) equal county-year weight; deal-level weights by actual "
      "market activity. READ: no robust spread dose-response in either direction.",
      "", "## Reading",
      "- A priced fiscal channel requires beta significant AND monotone in dose. Flat dose-response on top "
      "of the dummy nulls (script 68/69) = the bond market does not price the DC fiscal windfall, at any dose.",
      "- Crypto: if the spread-widening scales with dose, the risk interpretation sharpens (more mining capacity "
      "per $ of tax base -> wider spreads).",
      "- Caveat: continuous-treatment DiD requires stronger parallel-trends (de Chaisemartin-D'Haultfoeuille); "
      "we read sign/magnitude, not structural ATTs.",
      "- The dose regressor contains NO $/MW assumption; the $50k/MW translation is interpretation only.", ""]
(D / "continuous_dose_announcement.md").write_text("\n".join(L))
print("\n".join(L)); print("\nWrote continuous_dose_announcement.md + dc_dose_announced_mw_panel.csv")
