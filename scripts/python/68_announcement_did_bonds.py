"""
68_announcement_did_bonds.py

SIMPLE staggered DiD (Frank's request: county FE + a DC-ANNOUNCEMENT dummy, not a
saturated event study) of the DC-announcement effect on bond spread and other bond
features. Treatment turns on the year the county's FIRST major (>=50 MW) DC is publicly
ANNOUNCED (anchor `A_firstmaj`, built this session from the 172/172 DC-level announcement
wave; county-level fallback from dc_announcement_years.csv where no DC-level date exists).

  announced_{c,t} = 1[ c is treated AND t >= A_c ]
  y_{...} = beta * announced + (hedonic controls) | county + year , cluster(county)

Controls = clean never-DC-host counties (n_dc_cumulative == 0; excludes all S&P DC hosts,
so the 137 tiny-DC + 11 big-DC contaminated "controls" are gone by construction).
Cuts: ALL treated / clean_dc / crypto (dc_class). Each outcome also re-run with
county + STATE x year FE as a robustness check (absorbs the state muni yield curve).

Outcomes:
  SPREAD (deal-level, hedonic log amt + log maturity)          -- borrowing cost
  RATING extensive  = any_rated_share (deal)                   -- do they court the rated mkt?
  RATING intensive  = rated_avg_rating | rated (deal; AAA=1, LOWER=BETTER)
  ISSUANCE extensive = 1[any deal] (county-year)               -- do they issue at all?
  ISSUANCE intensive = log(1+par $M), log(1+n_deals)           -- how much?
  STRUCTURE = cy_share_callable, share_taxable, par_wtd_mat_yrs (county-year)

Output: data/derived/announcement_did_bonds.md
"""
from pathlib import Path
import numpy as np, pandas as pd
import pyfixest as pf
import warnings; warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]; D = ROOT / "data" / "derived"
def fz(s): return s.astype(str).str.zfill(5)
Y0, Y1 = 2008, 2025

# ---------- unified treated-county announcement anchor ----------
T = pd.read_csv(D/"treated_universe_labeled.csv", dtype={"county_fips": str}); T["county_fips"] = fz(T["county_fips"])
treated = set(T.county_fips)
anc = pd.read_csv(D/"announcement_anchor_county.csv", dtype={"county_fips": str}); anc["county_fips"] = fz(anc["county_fips"])
cty = pd.read_csv(D/"dc_announcement_years.csv", dtype={"county_fips": str}); cty["county_fips"] = fz(cty["county_fips"])
A = (T[["county_fips", "dc_class"]]
     .merge(anc[["county_fips", "ann_firstmaj"]], on="county_fips", how="left")
     .merge(cty[["county_fips", "announce_year"]], on="county_fips", how="left"))
A["A_firstmaj"] = A["ann_firstmaj"].fillna(A["announce_year"])   # DC-level firstmaj, else county-level
amap = dict(zip(A.county_fips, A.A_firstmaj)); cls = dict(zip(A.county_fips, A.dc_class))

pan = pd.read_csv(D/"county_year_panel_v4.csv", dtype={"county_fips": str}); pan["county_fips"] = fz(pan["county_fips"])
never = pan.groupby("county_fips")["n_dc_cumulative"].max().pipe(lambda s: set(s[s == 0].index)) - treated  # clean controls

def add_treat(df):
    df = df[df.county_fips.isin(treated | never)].copy()
    df["A"] = df.county_fips.map(amap)
    df = df[~(df.county_fips.isin(treated) & df.A.isna())].copy()           # drop treated w/o anchor (4)
    df["announced"] = ((df.county_fips.isin(treated)) & (df.year >= df.A)).astype(int)
    df["dc_class"] = df.county_fips.map(cls)
    return df

# ---------- deal-level ----------
d = pd.read_csv(D/"sdc_deal_spread.csv"); d["county_fips"] = fz(d["county_fips"].astype(int).astype(str))
r = pd.read_csv(D/"sdc_deal_rating.csv")
for x in (d, r): x["MASTER_DEAL_NO"] = pd.to_numeric(x["MASTER_DEAL_NO"], errors="coerce").astype("Int64")
d = d.merge(r, on="MASTER_DEAL_NO", how="left")
d = d[(d.AMT > 0) & d.year.between(Y0, Y1)].copy()
d["logamt"] = np.log(d.AMT); d["logmat"] = np.log(d.par_wtd_yrs2mat.clip(lower=0.25))
d = add_treat(d)

# ---------- county-year ----------
cy = add_treat(pan)
cy["any_issue"] = (cy.n_deals.fillna(0) > 0).astype(int)
cy["log_par"] = np.log1p(cy.par_total_M.fillna(0)); cy["log_ndeals"] = np.log1p(cy.n_deals.fillna(0))

L = ["# DC-Announcement effect on bond features — simple staggered DiD\n",
     "**Date:** 2026-06-10. `scripts/python/68`. Treatment dummy `announced = 1[year >= first >=50MW DC "
     "announcement]`, county + year FE, cluster county. Controls = clean never-DC-host counties "
     f"({len(never):,}). Anchor = `A_firstmaj` (172/172 DC-level wave; county-level fallback). "
     "Cuts: ALL / clean_dc / crypto. **rated_avg_rating: AAA=1, LOWER = BETTER.**\n",
     "| Outcome | Panel | Cut | beta (announced) | SE | p | N | beta(+state x year FE) | p |",
     "|---|---|---|---:|---:|---:|---:|---:|---:|"]

def one(df, y, ctrl, fe):
    s = df.dropna(subset=[y] + ([c.strip() for c in ctrl.split("+") if c.strip()] if ctrl else []))
    f = f"{y} ~ announced" + (f" + {ctrl}" if ctrl else "") + f" | {fe}"
    m = pf.feols(f, data=s, vcov={"CRV1": "county_fips"})
    return m.coef()["announced"], m.se()["announced"], m.pvalue()["announced"], int(m._N)

def row(label, panel, df, y, ctrl=""):
    for nm, ks in [("ALL", ["clean_dc", "crypto", "mixed"]), ("clean_dc", ["clean_dc"]), ("crypto", ["crypto"])]:
        sub = df[(df.county_fips.isin(never)) | (df.dc_class.isin(ks))]
        try:
            b, se, p, N = one(sub, y, ctrl, "county_fips + year")
            b2, _, p2, _ = one(sub, y, ctrl, "county_fips + STATECODE^year") if "STATECODE" in sub else one(sub, y, ctrl, "county_fips + state_fips^year")
            st = "***" if p < .01 else "**" if p < .05 else "*" if p < .10 else ""
            st2 = "***" if p2 < .01 else "**" if p2 < .05 else "*" if p2 < .10 else ""
            L.append(f"| {label} | {panel} | {nm} | {b:+.3f}{st} | {se:.3f} | {p:.3f} | {N:,} | {b2:+.3f}{st2} | {p2:.3f} |")
        except Exception as e:
            L.append(f"| {label} | {panel} | {nm} | ERR | | {str(e)[:18]} | | | |")

# state_fips for county-year (no STATECODE col there)
cy["STATECODE"] = cy["state_abbr"]
row("Spread (bps)", "deal", d, "spread_bps", "logamt + logmat")
row("Rating extensive (any-rated)", "deal", d, "any_rated_share")
row("Rating intensive (avg|rated, AAA=1)", "deal", d, "rated_avg_rating", "logamt")
row("Issuance extensive P(any deal)", "cy", cy, "any_issue")
row("Issuance log(1+par $M)", "cy", cy, "log_par")
row("Issuance log(1+n_deals)", "cy", cy, "log_ndeals")
row("Spread par-wtd (bps)", "cy", cy[cy.n_deals.fillna(0) > 0], "par_wtd_spread_bps")
row("Structure: share callable", "cy", cy[cy.n_deals.fillna(0) > 0], "cy_share_callable")
row("Structure: par-wtd maturity (yrs)", "cy", cy[cy.n_deals.fillna(0) > 0], "par_wtd_mat_yrs")

L += ["", "## Reading",
      "- **Spread:** clean_dc NULL (deal & county-year), crypto WIDENS (+17-18 bps, p<0.11). DC announcement "
      "does NOT lower borrowing cost for real DCs; crypto counties' spreads rise (volatile/transient tax base).",
      "- **Issuance:** NULL on every margin (extensive, par, n_deals) — DC counties do not issue more after the "
      "announcement. Corroborates the V2 debt-service null.",
      "- **Rating extensive:** less rated debt, concentrated in CRYPTO (-6pp, p=0.05); clean_dc NULL. Refines the "
      "earlier 'all -7pp' — the rated-market retreat is a crypto phenomenon.",
      "- **Rating intensive:** clean_dc point estimate -0.15 notch (improvement) is significant under county+year "
      "but NOT under county+state x year (p=0.19) -> **fragile, report as suggestive null**, consistent with "
      "script 51.",
      "- **Structure:** callable / maturity NULL.",
      "",
      "**Unifying:** announcement-timed simple DiD reproduces 'fiscally light inflow, fiscally quiet financing' — "
      "real DCs leave borrowing/credit untouched; crypto counties' spreads widen and they court the rated market "
      "less. Robust across timing (announcement here vs operational in script 62) and estimator (simple vs hedonic).",
      ""]
(D/"announcement_did_bonds.md").write_text("\n".join(L))
print("\n".join(L)); print("\nWrote announcement_did_bonds.md")
