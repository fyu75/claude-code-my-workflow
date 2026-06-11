"""
36_recover_county_equivalents_v2.py

v2 equivalent of 33_recover_county_equivalents.py — adapted for MuniSpot v2
(which is already filtered to `municipality_type=='County-General Purpose
Government'` upstream by Raj).

Differences from the v1 version:

  v1 contained Independent Local Education Agencies, Municipality-GP entities,
  Townships, etc. all tagged with county_fips. The v1 script had to *exclude*
  non-county entities, then *recover* VA independent cities / AK boroughs /
  named consolidated city-counties that were labeled Municipality-GP.

  v2 is restricted to County-GP only. So the recovery step is moot — those
  entities either pass the filter naturally (AK boroughs, Denver, Honolulu,
  which Raj labels County-GP) or are systematically EXCLUDED (Indianapolis,
  Louisville, Philadelphia, DC, Baltimore, St. Louis, Carson City, all 38 VA
  independent cities — labeled Municipality-GP). We document both groups.

Key empirical findings from running on v2:
  - v2 county-equivalent coverage (any year):     2,055  (vs v1 GP-only: 1,879)
  - v2 county-equivalents in BOTH FY17 and FY24:  ~1,449  (vs v1: 949)
  - Of the 3,143 Census county-equivalents:
      * covered any-year:                   ~65%
      * systematically excluded due to entity-type filter:  ~50 (see EXCLUDED_BY_FILTER)
      * absent for other reasons:           the residual gap
  - VA independent cities (n=38) are entirely absent from v2.

Output:
  data/derived/munispot_county_equiv_coverage_v2.csv
    One row per county-equivalent geoid in v2, with coverage flags.
  data/derived/munispot_filter_exclusions_v2.csv
    Named county-equivalents excluded by Raj's `municipality_type` filter.

Run:
  ~/.pyenv/versions/3.12.0/bin/python scripts/python/36_recover_county_equivalents_v2.py
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PARQUET = ROOT / "data" / "munispot" / "parquet_v2"
DERIVED = ROOT / "data" / "derived"

# County-equivalents that Census recognizes but Raj's `municipality_type='County-GP'`
# filter excludes from v2. These exist in v1 (as Municipality-GP) but were dropped.
# This list is documented evidence; the script counts how many are absent from v2
# and reports them as filter exclusions.
EXCLUDED_BY_FILTER = {
    "11001":  "District of Columbia",
    "18097":  "Marion County / Indianapolis (consolidated)",
    "21111":  "Jefferson County / Louisville (consolidated)",
    "24510":  "Baltimore city (independent)",
    "29510":  "St. Louis city (independent)",
    "32510":  "Carson City (consolidated)",
    "42101":  "Philadelphia County (consolidated)",
    # All 38 VA independent cities (county code >= 510 in state 51)
    # — listed dynamically below
}

COLS = ["auditee_ein", "fiscal_year", "municipality_name", "state",
        "county_name", "municipality_type", "state_fips", "fips_county", "fips_place",
        "column_index"]


def load_v2():
    m = pd.read_parquet(PARQUET,
                        filters=[("statement_type", "==", "income_statement")],
                        columns=COLS)
    m = m[m.state_fips.notna() & m.fips_county.notna()].copy()
    m["geoid"] = m.state_fips + m.fips_county
    m["fiscal_year"] = m.fiscal_year.astype(int)   # partition key reads back categorical
    return m


def geos_2period(sub, y_a=2017, y_b=2024):
    """GEOIDs that have BOTH y_a and y_b records (2-period DiD window)."""
    y = sub.groupby("geoid", observed=True).fiscal_year.agg(
        lambda s: {y_a, y_b}.issubset(set(s))
    )
    return set(y[y].index)


def main():
    v2 = load_v2()
    # v2 should be 100% County-General Purpose Government (Raj's filter)
    mt_breakdown = v2.municipality_type.value_counts(dropna=False)
    print("v2 entity types (sanity check — expect 100% County-GP):")
    print(mt_breakdown.to_string())
    print()

    # county-equivalent coverage measures
    all_geo  = set(v2.geoid)
    geo_2p   = geos_2period(v2)
    geo_3p   = geos_2period(v2, 2017, 2024)        # alias of 2p above for label clarity
    geo_full = set(v2.groupby("geoid", observed=True).fiscal_year.nunique()[lambda s: s >= 9].index)

    print(f"v2 distinct county_fips (any year, any column_index):  {len(all_geo):,}")
    print(f"v2 with BOTH FY2017 and FY2024:                         {len(geo_2p):,}")
    print(f"v2 with >= 9 fiscal years (balanced FY16-24):           {len(geo_full):,}")
    print()

    # GF-only equivalent (column_index = 1)
    gf = v2[v2.column_index == 1]
    gf_all = set(gf.geoid)
    gf_2p  = geos_2period(gf)
    print(f"v2 GF-only (column_index=1) distinct county_fips:       {len(gf_all):,}")
    print(f"v2 GF-only with BOTH FY2017 and FY2024:                 {len(gf_2p):,}")
    print()

    # ---- DC overlap ----
    dc = pd.read_csv(DERIVED / "dc_property_county_fips.csv", dtype={"county_fips": str})
    dc_counties = set(dc.county_fips.dropna().astype(str).str.zfill(5))
    share = pd.read_csv(DERIVED / "dc_tax_share_distribution.csv", dtype={"county_fips": str})
    share["s"] = pd.to_numeric(share.dc_share_mid, errors="coerce")
    treated = set(share.loc[share.s >= 1.0, "county_fips"].astype(str).str.zfill(5))

    def report(label, u):
        u = set(u)
        n = len(u)
        any_pct = len(u & all_geo) / n * 100
        gf_pct  = len(u & gf_all) / n * 100
        twoper  = len(u & geo_2p)
        print(f"\n{label}: N={n}")
        print(f"  in v2 any-year:        {len(u & all_geo):4d} ({any_pct:4.1f}%)")
        print(f"  in v2 GF-only any-yr:  {len(u & gf_all):4d} ({gf_pct:4.1f}%)")
        print(f"  in v2 with FY17+FY24:  {twoper:4d} ({twoper/n*100:4.1f}%)")

    report("DC-host counties (any DC ever)", dc_counties)
    report("Treated (dc_share_mid >= 1%)", treated)

    # ---- Persist coverage map ----
    cnames = (v2.drop_duplicates("geoid").set_index("geoid")
              [["state", "county_name", "municipality_name"]])
    ce_years = v2.groupby("geoid", observed=True).fiscal_year.apply(lambda s: set(s))
    gf_years = gf.groupby("geoid", observed=True).fiscal_year.apply(lambda s: set(s))

    rows = []
    for g in sorted(all_geo):
        yrs    = ce_years.get(g, set())
        gf_yrs = gf_years.get(g, set())
        rows.append({
            "geoid": g,
            "state": cnames.state.get(g, ""),
            "county_name": cnames.county_name.get(g, ""),
            "municipality_name": cnames.municipality_name.get(g, ""),
            "covered_any_year": True,
            "covered_2period_FY17_FY24": {2017, 2024}.issubset(yrs),
            "covered_n_years": len(yrs),
            "covered_balanced9": len(yrs) >= 9,
            "covered_gf_any_year": g in gf_all,
            "covered_gf_2period_FY17_FY24": {2017, 2024}.issubset(gf_yrs),
            "covered_gf_n_years": len(gf_yrs),
            "fiscal_year_max": max(yrs) if yrs else None,
        })
    out = pd.DataFrame(rows)
    dest = DERIVED / "munispot_county_equiv_coverage_v2.csv"
    out.to_csv(dest, index=False)
    print(f"\nWrote {len(out):,} county-equivalents → {dest.relative_to(ROOT)}")

    national(out, all_geo, gf_all, geo_2p, gf_2p)


def national(cov, all_geo, gf_all, geo_2p, gf_2p):
    """Coverage vs the full Census county universe + filter-exclusion accounting."""
    nc = pd.read_csv(ROOT / "data" / "external" / "national_county.txt", header=None,
                     dtype=str, names=["state", "sfips", "cfips", "name", "classfp"])
    nc = nc[~nc.state.isin(["PR", "UM", "VI", "GU", "AS", "MP"])].copy()  # 50 states + DC
    nc["geoid"] = nc.sfips + nc.cfips
    universe = set(nc.geoid)
    N = len(universe)

    covered_any   = set(cov.geoid) & universe
    covered_2p    = set(cov.loc[cov.covered_2period_FY17_FY24, "geoid"]) & universe
    covered_gf    = gf_all & universe
    covered_gf2p  = gf_2p & universe
    covered_full  = set(cov.loc[cov.covered_balanced9, "geoid"]) & universe
    missing       = universe - covered_any

    print("\n" + "=" * 78)
    print(f"OVERALL coverage of US county-equivalents (50 states + DC, N={N}):")
    print(f"  any-year (any column_index):  {len(covered_any):4d} ({len(covered_any)/N*100:4.1f}%)")
    print(f"  any-year (GF only):           {len(covered_gf):4d} ({len(covered_gf)/N*100:4.1f}%)")
    print(f"  FY2017 + FY2024 (any fund):   {len(covered_2p):4d} ({len(covered_2p)/N*100:4.1f}%)")
    print(f"  FY2017 + FY2024 (GF only):    {len(covered_gf2p):4d} ({len(covered_gf2p)/N*100:4.1f}%)")
    print(f"  balanced 9 years (FY16-24):   {len(covered_full):4d} ({len(covered_full)/N*100:4.1f}%)")
    print(f"  MISSING                       {len(missing):4d} ({len(missing)/N*100:4.1f}%)")

    # --- Filter-exclusion accounting: county-equivalents that Raj's pipeline
    # systematically drops because of municipality_type ---
    named_excluded = set(EXCLUDED_BY_FILTER) & universe
    # All 38 VA independent cities (state 51, county code >= 510)
    va_indep = nc[(nc.state == "VA") & nc.cfips.astype(int).between(510, 840)]
    va_indep_geo = set(va_indep.geoid) & universe
    excluded = named_excluded | va_indep_geo
    excluded_missing = excluded & missing
    excluded_present = excluded - missing   # any sneaked through despite the filter

    print(f"\nFilter-exclusion accounting (Raj's municipality_type filter):")
    print(f"  Named consolidated city-counties / DC / VA indep cities expected to be dropped: {len(excluded):4d}")
    print(f"    - of those, indeed missing from v2: {len(excluded_missing):4d}")
    print(f"    - of those, present in v2 anyway:   {len(excluded_present):4d}  "
          f"({sorted(excluded_present)[:10]}{'...' if len(excluded_present)>10 else ''})")
    print(f"  Of the {len(missing)} missing total, {len(excluded_missing)} ({len(excluded_missing)/len(missing)*100:.0f}%) "
          f"are filter-driven; the rest ({len(missing)-len(excluded_missing)}) are absent for other reasons.")

    # Persist the exclusion list
    excl_rows = []
    for g in sorted(excluded):
        meta = nc[nc.geoid == g].iloc[0]
        excl_rows.append({
            "geoid": g, "state": meta.state, "county_name": meta["name"],
            "reason": EXCLUDED_BY_FILTER.get(g, "VA independent city"),
            "in_v2": g in all_geo,
        })
    excl_df = pd.DataFrame(excl_rows)
    excl_dest = DERIVED / "munispot_filter_exclusions_v2.csv"
    excl_df.to_csv(excl_dest, index=False)
    print(f"\nWrote {len(excl_df)} systematic exclusions → {excl_dest.relative_to(ROOT)}")

    # By-state coverage table
    nc["covered_any"] = nc.geoid.isin(covered_any)
    nc["covered_gf"]  = nc.geoid.isin(covered_gf)
    st = (nc.groupby("state")
            .agg(total=("geoid", "size"),
                 cov_any=("covered_any", "sum"),
                 cov_gf=("covered_gf", "sum")).reset_index())
    st["missing"] = st.total - st.cov_any
    st["pct_any"] = (st.cov_any / st.total * 100).round(0).astype(int)
    st["pct_gf"]  = (st.cov_gf  / st.total * 100).round(0).astype(int)
    print("\nStates with the largest missing county-equivalent counts:")
    print(st.sort_values("missing", ascending=False).head(12).to_string(index=False))


if __name__ == "__main__":
    main()
