"""
74_go_vs_revenue_split.py

PRE-SPECIFIED HETEROGENEITY TEST: GO vs Revenue bond split + maturity gradient.

HYPOTHESIS: A property-tax windfall from data centers should be priced in
GENERAL OBLIGATION bonds (backed by taxing power) more than revenue bonds
(backed by project revenues). Also: effect should increase with maturity
(long bonds embed long-run tax-base expectations).

SPEC: Mirrors 68_announcement_did_bonds.py exactly.
  announced_{c,t} = 1[ c is treated AND t >= A_firstmaj ]
  spread_bps ~ announced + logamt + logmat | county_fips + year,
               vcov = CRV1(county_fips)
  Robustness: county_fips + STATECODE^year FE
  Deals 2008-2025, AMT > 0.

CUTS: ALL / clean_dc / crypto (same as script 68).

REGRESSIONS:
  1. Spread, GO deals only
  2. Spread, RV deals only
  3. Spread, GO & tax-exempt only (TAXABLE=='E')
  4. Rating extensive (any_rated_share), GO only and RV only
  5. Maturity gradient: full sample, spread ~ announced + announced:logmat + logamt + logmat
  6. SANITY CHECK: pooled GO+RV spread (should match script 68 ALL ~+4.9/-0.5 ns, clean ~-2 ns)

Output: data/derived/go_vs_revenue_split.md
"""
from pathlib import Path
import numpy as np
import pandas as pd
import pyfixest as pf
import warnings
warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "data" / "derived"
Y0, Y1 = 2008, 2025

PHANTOMS = {"47121", "54047", "21127"}


def fz(s):
    return s.astype(str).str.zfill(5)


# ---------- Load announcement anchors (mirror script 68) ----------
T = pd.read_csv(D / "treated_universe_labeled.csv", dtype={"county_fips": str})
T["county_fips"] = fz(T["county_fips"])
treated = set(T.county_fips) - PHANTOMS

anc = pd.read_csv(D / "announcement_anchor_county.csv", dtype={"county_fips": str})
anc["county_fips"] = fz(anc["county_fips"])
cty = pd.read_csv(D / "dc_announcement_years.csv", dtype={"county_fips": str})
cty["county_fips"] = fz(cty["county_fips"])

A = (
    T[["county_fips", "dc_class"]]
    .merge(anc[["county_fips", "ann_firstmaj"]], on="county_fips", how="left")
    .merge(cty[["county_fips", "announce_year"]], on="county_fips", how="left")
)
A = A[~A.county_fips.isin(PHANTOMS)]
A["A_firstmaj"] = A["ann_firstmaj"].fillna(A["announce_year"])

amap = dict(zip(A.county_fips, A.A_firstmaj))
cls  = dict(zip(A.county_fips, A.dc_class))

# ---------- Controls: clean never-DC counties ----------
ctrl_df = pd.read_csv(D / "clean_never_dc_controls.csv", dtype={"county_fips": str})
ctrl_df["county_fips"] = fz(ctrl_df["county_fips"])
never = set(ctrl_df.county_fips) - PHANTOMS


# ---------- Load SAS deals: SECURITY + TAXABLE only ----------
print("Reading deals_data.sas7bdat ...")
sas_chunks = []
for chunk in pd.read_sas(
    ROOT / "data/sdc_muni/sdc_municipals/deals_data.sas7bdat",
    encoding="latin-1",
    chunksize=200_000,
):
    sub = chunk[["MASTER_DEAL_NO", "SECURITY", "TAXABLE"]].copy()
    sub["MASTER_DEAL_NO"] = pd.to_numeric(sub["MASTER_DEAL_NO"], errors="coerce").astype("Int64")
    sas_chunks.append(sub)

sas = pd.concat(sas_chunks, ignore_index=True)
# SECURITY/TAXABLE are constant within MASTER_DEAL_NO (verified: 0 conflicts)
sas = sas.drop_duplicates(subset="MASTER_DEAL_NO", keep="first")
print(f"SAS unique deals: {len(sas):,}")


# ---------- Load deal-level spread data ----------
d = pd.read_csv(D / "sdc_deal_spread.csv")
d["county_fips"] = fz(d["county_fips"].astype(int).astype(str))
d["MASTER_DEAL_NO"] = pd.to_numeric(d["MASTER_DEAL_NO"], errors="coerce").astype("Int64")

r = pd.read_csv(D / "sdc_deal_rating.csv")
r["MASTER_DEAL_NO"] = pd.to_numeric(r["MASTER_DEAL_NO"], errors="coerce").astype("Int64")

d = d.merge(r, on="MASTER_DEAL_NO", how="left")
d = d.merge(sas[["MASTER_DEAL_NO", "SECURITY", "TAXABLE"]], on="MASTER_DEAL_NO", how="left")

# Sample restrictions (mirror script 68)
d = d[(d.AMT > 0) & d.year.between(Y0, Y1)].copy()
d["logamt"] = np.log(d.AMT)
d["logmat"] = np.log(d.par_wtd_yrs2mat.clip(lower=0.25))

# Sanity stats for SECURITY coverage (before geographic treatment filter)
total_deals_raw = len(d)
sec_nonmissing_raw = d["SECURITY"].notna().sum()
match_rate_raw = sec_nonmissing_raw / total_deals_raw
go_share_raw = (d["SECURITY"] == "GO").sum() / sec_nonmissing_raw

print(f"Total deals (AMT>0, 2008-2025, before geo filter): {total_deals_raw:,}")
print(f"Deals with SECURITY non-missing: {sec_nonmissing_raw:,} ({match_rate_raw:.1%})")
print(f"GO share among matched: {go_share_raw:.1%}")


# ---------- Add treatment indicator (mirror script 68) ----------
def add_treat(df):
    df = df[df.county_fips.isin(treated | never)].copy()
    df["A"] = df.county_fips.map(amap)
    df = df[~(df.county_fips.isin(treated) & df.A.isna())].copy()
    df["announced"] = ((df.county_fips.isin(treated)) & (df.year >= df.A)).astype(int)
    df["dc_class"] = df.county_fips.map(cls)
    return df


d = add_treat(d)

# Count treated counties (with valid anchor, not phantom) per class
treat_in_sample = d[d.county_fips.isin(treated)][["county_fips", "dc_class"]].drop_duplicates()
n_treated_all    = len(treat_in_sample)
n_clean_dc       = (treat_in_sample.dc_class == "clean_dc").sum()
n_crypto         = (treat_in_sample.dc_class == "crypto").sum()
n_mixed          = (treat_in_sample.dc_class == "mixed").sum()
n_never_in       = d[d.county_fips.isin(never)].county_fips.nunique()

print(f"\nTreatment summary:")
print(f"  Treated counties in sample: {n_treated_all} (clean_dc={n_clean_dc}, crypto={n_crypto}, mixed={n_mixed})")
print(f"  Control counties (never-DC): {n_never_in}")


# ---------- Regression helpers ----------
def one(df, y, ctrl, fe):
    sub = df.dropna(subset=[y] + ([c.strip() for c in ctrl.split("+") if c.strip()] if ctrl else []))
    if sub["county_fips"].nunique() < 5:
        raise ValueError("too few clusters")
    formula = f"{y} ~ {' + '.join(['announced'] + ([ctrl] if ctrl else []))}" + f" | {fe}"
    m = pf.feols(formula, data=sub, vcov={"CRV1": "county_fips"})
    b   = m.coef()["announced"]
    se  = m.se()["announced"]
    p   = m.pvalue()["announced"]
    N   = int(m._N)
    n_c = sub[sub.county_fips.isin(treated)].county_fips.nunique()
    return b, se, p, N, n_c


def one_interaction(df, y, ctrl, fe):
    """For maturity gradient: y ~ announced + announced:logmat + logamt + logmat | fe"""
    sub = df.dropna(subset=[y, ctrl] if ctrl else [y])
    sub = sub.dropna(subset=["logmat", "logamt"])
    if sub["county_fips"].nunique() < 5:
        raise ValueError("too few clusters")
    formula = f"{y} ~ announced + announced:logmat + logamt + logmat | {fe}"
    m = pf.feols(formula, data=sub, vcov={"CRV1": "county_fips"})
    b_ann   = m.coef().get("announced", np.nan)
    se_ann  = m.se().get("announced", np.nan)
    p_ann   = m.pvalue().get("announced", np.nan)
    # Interaction term key may vary
    int_key = [k for k in m.coef().index if "logmat" in k and "announced" in k]
    if int_key:
        b_int  = m.coef()[int_key[0]]
        se_int = m.se()[int_key[0]]
        p_int  = m.pvalue()[int_key[0]]
    else:
        b_int = se_int = p_int = np.nan
    N   = int(m._N)
    n_c = sub[sub.county_fips.isin(treated)].county_fips.nunique()
    return b_ann, se_ann, p_ann, b_int, se_int, p_int, N, n_c


def stars(p):
    if np.isnan(p): return ""
    return "***" if p < .01 else "**" if p < .05 else "*" if p < .10 else ""


CUT_DEFS = [
    ("ALL",      ["clean_dc", "crypto", "mixed"]),
    ("clean_dc", ["clean_dc"]),
    ("crypto",   ["crypto"]),
]


def run_cut(label, deal_filter_mask, df, y, ctrl="logamt + logmat", fe_base="county_fips + year"):
    """Run for all three cuts, both FE specs, on a pre-filtered deal subset."""
    rows = []
    for cut_nm, ks in CUT_DEFS:
        sub = df[(df.county_fips.isin(never)) | (df.dc_class.isin(ks))]
        if deal_filter_mask is not None:
            sub = sub[deal_filter_mask.reindex(sub.index, fill_value=False)]
        try:
            b, se, p, N, n_c = one(sub, y, ctrl, fe_base)
            b2, _, p2, _, n_c2 = one(sub, y, ctrl, "county_fips + STATECODE^year")
            row = (label, cut_nm, f"{b:+.2f}{stars(p)}", f"{se:.2f}", f"{p:.3f}",
                   f"{N:,}", f"{n_c}", f"{b2:+.2f}{stars(p2)}", f"{p2:.3f}")
        except Exception as e:
            row = (label, cut_nm, "ERR", "", str(e)[:30], "", "", "", "")
        rows.append(row)
    return rows


# ---------- Build output ----------
L = []
L.append("# GO vs Revenue Bond Split — Pre-Specified Heterogeneity Test")
L.append("")
L.append(f"**Date:** 2026-06-11. `scripts/python/74`. Mirrors script 68 spec exactly.")
L.append(f"**Treatment:** `announced = 1[year >= A_firstmaj]`, county + year FE, cluster county.")
L.append(f"**Period:** {Y0}–{Y1}. **Controls:** clean never-DC counties ({n_never_in:,}).")
L.append(f"**Phantoms excluded:** {{47121, 54047, 21127}}.")
L.append("")
L.append("## A. Sample Description")
L.append("")
L.append(f"| Item | Count |")
L.append(f"|---|---|")
L.append(f"| Treated counties (all classes, phantom-free) | {n_treated_all} |")
L.append(f"| — clean_dc | {n_clean_dc} |")
L.append(f"| — crypto | {n_crypto} |")
L.append(f"| — mixed | {n_mixed} |")
L.append(f"| Control counties (clean never-DC) | {n_never_in:,} |")
L.append(f"| Total deals in panel (AMT>0, 2008–2025, treated+control universe) | {len(d):,} |")
L.append(f"| Deals with SECURITY non-missing (treated+ctrl universe) | {d['SECURITY'].notna().sum():,} ({d['SECURITY'].notna().sum()/len(d):.1%}) |")
L.append(f"| GO share among SECURITY-matched deals | {(d['SECURITY']=='GO').sum() / d['SECURITY'].notna().sum():.1%} |")
L.append(f"| All SDC deals pre-geo-filter (AMT>0, 2008–2025) | {total_deals_raw:,} |")
L.append(f"| SECURITY match rate (full SDC universe) | {match_rate_raw:.1%} |")
L.append("")
L.append("## B. Spread Regressions: GO vs Revenue Splits")
L.append("")
L.append("**Spec:** `spread_bps ~ announced + logamt + logmat | county_fips + year`, CRV1(county_fips).")
L.append("Robustness column uses `county_fips + STATECODE^year` FE.")
L.append("")

hdr = ("| Subsample | Cut | beta_announced | SE | p | N_deals | N_treated | beta(+state×year FE) | p |")
sep = ("|---|---|---:|---:|---:|---:|---:|---:|---:|")

# --- REG 1: GO deals only ---
L.append("### 1. Spread — GO deals only (SECURITY == 'GO')")
L.append("")
L.append(hdr); L.append(sep)
go_mask = d["SECURITY"] == "GO"
for row in run_cut("GO only", go_mask, d, "spread_bps"):
    L.append("| " + " | ".join(row) + " |")
L.append("")

# --- REG 2: RV deals only ---
L.append("### 2. Spread — Revenue deals only (SECURITY == 'RV')")
L.append("")
L.append(hdr); L.append(sep)
rv_mask = d["SECURITY"] == "RV"
for row in run_cut("RV only", rv_mask, d, "spread_bps"):
    L.append("| " + " | ".join(row) + " |")
L.append("")

# --- REG 3: GO & tax-exempt only ---
L.append("### 3. Spread — GO & Tax-Exempt only (SECURITY == 'GO' AND TAXABLE == 'E')")
L.append("")
L.append(hdr); L.append(sep)
go_te_mask = (d["SECURITY"] == "GO") & (d["TAXABLE"] == "E")
for row in run_cut("GO & tax-exempt", go_te_mask, d, "spread_bps"):
    L.append("| " + " | ".join(row) + " |")
L.append("")

# --- REG 4: Rating extensive (any_rated_share), GO and RV ---
L.append("### 4. Rating Extensive (any_rated_share) — GO and RV splits")
L.append("")
L.append(hdr.replace("beta_announced", "beta_announced (any_rated_share)").replace("N_deals", "N_obs"))
L.append(sep)
for subsamp, mask_fn in [("GO only", go_mask), ("RV only", rv_mask)]:
    for row in run_cut(subsamp, mask_fn, d, "any_rated_share", ctrl=""):
        L.append("| " + " | ".join(row) + " |")
L.append("")

# --- REG 5: Maturity gradient ---
L.append("### 5. Maturity Gradient — Full Sample")
L.append("**Spec:** `spread_bps ~ announced + announced:logmat + logamt + logmat | FE`")
L.append("")
L.append("| Cut | beta_announced | SE | p | beta(ann×logmat) | SE | p | N | N_treated | beta_ann(+state×yr) | p |")
L.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")

for cut_nm, ks in CUT_DEFS:
    sub = d[(d.county_fips.isin(never)) | (d.dc_class.isin(ks))]
    try:
        r1 = one_interaction(sub, "spread_bps", "", "county_fips + year")
        b_ann, se_ann, p_ann, b_int, se_int, p_int, N, n_c = r1
        r2 = one_interaction(sub, "spread_bps", "", "county_fips + STATECODE^year")
        b_ann2, _, p_ann2, _, _, _, _, _ = r2
        L.append(
            f"| {cut_nm} | {b_ann:+.2f}{stars(p_ann)} | {se_ann:.2f} | {p_ann:.3f} | "
            f"{b_int:+.2f}{stars(p_int)} | {se_int:.2f} | {p_int:.3f} | "
            f"{N:,} | {n_c} | {b_ann2:+.2f}{stars(p_ann2)} | {p_ann2:.3f} |"
        )
    except Exception as e:
        L.append(f"| {cut_nm} | ERR | | {str(e)[:40]} | | | | | | | |")

L.append("")

# --- REG 6: SANITY CHECK — pooled GO+RV spread (mirror script 68) ---
L.append("### 6. SANITY CHECK — Pooled GO+RV Spread (reference: script 68 ALL ~+4.9/-0.5 ns, clean ~-2 ns)")
L.append("")
L.append(hdr); L.append(sep)
for row in run_cut("Pooled (all SECURITY)", None, d, "spread_bps"):
    L.append("| " + " | ".join(row) + " |")
L.append("")
L.append("**Reference from script 68 (spread, deal panel):**")
L.append("- ALL: +4.9 bps (ns); clean_dc: ~-0.5 bps (ns)")
L.append("  *(script 68 Reading: 'clean_dc NULL')*")
L.append("")

# ---------- Summary / Evaluation ----------
L.append("## C. Pre-Specified Prediction Evaluation")
L.append("")
L.append("**Pre-specified prediction:** GO-only beta should be MORE NEGATIVE than RV-only beta")
L.append("if the DC tax windfall is priced in GO bonds.")
L.append("")
L.append("*(See data rows above; evaluation filled in from regression output.)*")
L.append("")
L.append("**Maturity gradient prediction:** announced:logmat interaction should be negative")
L.append("(longer maturity → larger spread compression if long-run tax base expectations matter).")
L.append("")

out_path = D / "go_vs_revenue_split.md"
(out_path).write_text("\n".join(L))
print(f"\nWrote {out_path}")
print("\n" + "\n".join(L))
