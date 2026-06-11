"""
33_recover_county_equivalents.py

DEPRECATED 2026-06-07: superseded by `36_recover_county_equivalents_v2.py`,
which runs against MuniSpot v2 (Raj's 2026-06 interim delivery). This v1
script is retained because the 2026-05-19 and 2026-05-28 memos to Raj cite
its output (`munispot_county_equiv_coverage_v1.csv`, renamed). Do NOT use for
new analysis — v1 is missing 5 fiscal years of newer data and uses an entity
identifier (`munispot_id`) that v2 replaced with `auditee_ein`.

Re-examine MuniSpot county coverage after the vendor noted that states name
county-equivalents differently (Louisiana = parishes, Alaska = boroughs,
Virginia = independent cities, plus consolidated city-counties). Question:
did our earlier strict filter `municipality_type == 'County-General Purpose
Government'` under-count true county-equivalents that carry a different label?

Findings (see printed summary):
  - LA parishes ARE already labeled County-General Purpose Government (no loss).
  - VA independent cities, AK boroughs, and consolidated city-counties (Denver,
    Philadelphia, Honolulu, Indianapolis, Baltimore city, ...) are labeled
    Municipality-General Purpose Government -> recoverable as county-equivalents.
  - Recovery adds +71 county-equivalents nationally (1,879 -> 1,950), +14
    DC-host counties, but +0 of our >=1% treated counties.
  - The 38 missing treated counties are GENUINELY absent (county government not
    in MuniSpot), not a labeling artifact -> only the ACFR-PDF route can fill them.

A county is NOT counted as covered merely because a city inside it filed
(that is the South Dakota / Jefferson-County-AL pattern). A Municipality-GP
entity counts as a county-equivalent ONLY when it IS the county-equivalent
government: an independent city, a consolidated city-county, or an Alaska borough.

Output:
  data/derived/munispot_county_equiv_coverage.csv
    one row per covered county-equivalent GEOID, with coverage flags.

Run:
  ~/.pyenv/versions/3.12.0/bin/python scripts/python/33_recover_county_equivalents.py
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PARQUET = ROOT / "data" / "muni" / "parquet"
DERIVED = ROOT / "data" / "derived"

# Consolidated city-counties + independent cities that are labeled as a
# municipality but ARE the county-equivalent government (no separate county).
# VA independent cities (state 51, county code >= 510) and all Alaska
# county-equivalents (state 02) are handled by rule below, not enumerated here.
INDEP_CONSOL = {
    "24510",  # Baltimore city, MD
    "29510",  # St. Louis city, MO
    "32510",  # Carson City, NV
    "08031",  # Denver, CO
    "15003",  # Honolulu, HI
    "18097",  # Indianapolis-Marion, IN
    "21111",  # Louisville-Jefferson, KY
    "42101",  # Philadelphia, PA
    "11001",  # District of Columbia
    "13245", "13215", "13059", "13021",  # GA consolidated: Augusta, Columbus, Athens, Macon
}

COLS = ["munispot_id", "fiscal_year", "municipality_name", "state",
        "county_name", "municipality_type", "state_fips", "fips_county", "fips_place"]


def load_gp():
    m = pd.read_parquet(PARQUET,
                        filters=[("statement_type", "==", "income_statement")],
                        columns=COLS)
    m = m[m.state_fips.notna() & m.fips_county.notna()].copy()
    m["geoid"] = m.state_fips + m.fips_county
    gp = m[m.municipality_type.str.contains("General Purpose", na=False)].copy()
    gp["cc"] = pd.to_numeric(gp.fips_county, errors="coerce").fillna(-1)
    return m, gp


def classify(gp):
    is_cgp = gp.municipality_type == "County-General Purpose Government"
    recov = (~is_cgp) & (
        (gp.state_fips == "02") |                              # Alaska boroughs
        ((gp.state_fips == "51") & (gp.cc >= 510)) |           # VA independent cities
        (gp.geoid.isin(INDEP_CONSOL))                          # named consolidated/indep cities
    )
    return is_cgp, recov


def geos_2period(sub):
    """GEOIDs that have BOTH FY2017 and FY2024 records (2-period DiD window)."""
    y = sub.groupby("geoid").fiscal_year.agg(lambda s: {2017, 2024}.issubset(set(s)))
    return set(y[y].index)


def main():
    allent, gp = load_gp()
    any_entity_geo = set(allent.geoid)            # any entity at all (city/school/district)
    is_cgp, recov = classify(gp)

    cgp_geo   = set(gp.loc[is_cgp, "geoid"])
    recov_geo = set(gp.loc[recov, "geoid"]) - cgp_geo
    exp_geo   = cgp_geo | recov_geo

    cgp_2p   = geos_2period(gp[is_cgp])
    recov_2p = geos_2period(gp[recov]) - cgp_2p
    exp_2p   = cgp_2p | recov_2p

    # --- our DC universe ---
    dc = pd.read_csv(DERIVED / "dc_property_county_fips.csv", dtype={"county_fips": str})
    dc_counties = set(dc.county_fips.dropna())
    share = pd.read_csv(DERIVED / "dc_tax_share_distribution.csv", dtype={"county_fips": str})
    share["s"] = pd.to_numeric(share.dc_share_mid, errors="coerce")
    treated = set(share.loc[share.s >= 1.0, "county_fips"])

    def report(label, u):
        u = set(u)
        n = len(u)
        print(f"\n{label}: N={n}")
        print(f"  STRICT  County-GP : any-yr {len(u&cgp_geo):4d} ({len(u&cgp_geo)/n*100:4.1f}%)"
              f" | 2-period {len(u&cgp_2p):4d} ({len(u&cgp_2p)/n*100:4.1f}%)")
        print(f"  EXPANDED +county-eq munis: any-yr {len(u&exp_geo):4d} ({len(u&exp_geo)/n*100:4.1f}%)"
              f" | 2-period {len(u&exp_2p):4d} ({len(u&exp_2p)/n*100:4.1f}%)")
        print(f"  RECOVERED : any-yr +{len(u&exp_geo)-len(u&cgp_geo)} | 2-period +{len(u&exp_2p)-len(u&cgp_2p)}")

    print("=" * 78)
    print(f"NATIONAL: strict County-GP = {len(cgp_geo)} county-equivalents; "
          f"recoverable (indep cities / AK boroughs / consolidated) = +{len(recov_geo)}; "
          f"expanded = {len(exp_geo)}")
    report("DC-host counties", dc_counties)
    report("Treated (dc_share_mid >= 1%)", treated)

    # Missing treated: split absent vs city-only
    miss = treated - exp_geo
    absent = miss - any_entity_geo
    city_only = miss & any_entity_geo
    print(f"\nMissing treated: {len(miss)} | completely absent {len(absent)} | "
          f"city/other-only (county-gov missing) {len(city_only)}")

    # --- year-completeness measured on the COUNTY-EQUIVALENT entity only ---
    # (not on cities sharing the GEOID -- that would overcount full panels)
    ce = gp[is_cgp | recov]
    ce_years = ce.groupby("geoid").fiscal_year.apply(lambda s: set(s))

    # --- persist coverage crosswalk ---
    rows = []
    cnames = gp.drop_duplicates("geoid").set_index("geoid")[["state", "county_name"]]
    for g in sorted(exp_geo):
        yrs = ce_years.get(g, set())
        rows.append({
            "geoid": g,
            "state": cnames.state.get(g, ""),
            "county_name": cnames.county_name.get(g, ""),
            "recovery_type": "county_gp" if g in cgp_geo else "county_equiv_municipality",
            "covered_any_year": True,
            "covered_2period": {2017, 2024}.issubset(yrs),
            "covered_n_years": len(yrs),
            "covered_balanced9": len(yrs) >= 9,
        })
    out = pd.DataFrame(rows)
    dest = DERIVED / "munispot_county_equiv_coverage.csv"
    out.to_csv(dest, index=False)
    print(f"\nWrote {len(out):,} covered county-equivalents -> {dest.relative_to(ROOT)}")
    print(out.recovery_type.value_counts().to_string())

    national(out, any_entity_geo)


def national(cov, any_entity_geo):
    """Overall coverage and missing breakdown vs the full Census county universe."""
    nc = pd.read_csv(ROOT / "data" / "external" / "national_county.txt", header=None,
                     dtype=str, names=["state", "sfips", "cfips", "name", "classfp"])
    nc = nc[~nc.state.isin(["PR", "UM", "VI", "GU", "AS", "MP"])].copy()  # 50 states + DC
    nc["geoid"] = nc.sfips + nc.cfips
    universe = set(nc.geoid)
    N = len(universe)

    covered_any = set(cov.geoid) & universe
    covered_2p  = set(cov.loc[cov.covered_2period, "geoid"]) & universe
    covered_bal = set(cov.loc[cov.covered_balanced9, "geoid"]) & universe
    missing     = universe - covered_any
    absent      = missing - any_entity_geo      # no record of any kind in the delivery
    other_only  = missing & any_entity_geo      # a local entity present, county gov't absent

    print("\n" + "=" * 78)
    print(f"OVERALL coverage of US county-equivalents (50 states + DC, N={N}):")
    print(f"  covered, any year      : {len(covered_any):4d} ({len(covered_any)/N*100:4.1f}%)")
    print(f"  covered, FY2017 & FY2024: {len(covered_2p):4d} ({len(covered_2p)/N*100:4.1f}%)")
    print(f"  covered, all 9 years    : {len(covered_bal):4d} ({len(covered_bal)/N*100:4.1f}%)")
    print(f"  MISSING                 : {len(missing):4d} ({len(missing)/N*100:4.1f}%)")
    print(f"    - county gov't absent, but a local entity present: {len(other_only):4d}")
    print(f"    - entirely absent (no record of any kind)        : {len(absent):4d}")

    nc["covered"] = nc.geoid.isin(covered_any)
    st = (nc.groupby("state")
            .agg(total=("geoid", "size"), covered=("covered", "sum")).reset_index())
    st["missing"] = st.total - st.covered
    st["pct"] = (st.covered / st.total * 100).round(0).astype(int)
    print("\nStates with the largest missing county-government counts:")
    print(st.sort_values("missing", ascending=False).head(12).to_string(index=False))
    print("\nStates with zero county-government coverage:")
    print(st[st.covered == 0].sort_values("total", ascending=False).to_string(index=False))


def threshold_test():
    """Test the 'minimum filing threshold' explanation for year-gaps.

    If a county is missing some years because its figures fall below a small
    filing threshold ($10K-$100K), then counties with year-gaps should be small.
    We measure how large the gap counties actually are, using TOTAL REVENUES
    from the years they DID file (the vendor's own reported values).
    """
    cols = ["municipality_type", "state_fips", "fips_county", "fiscal_year",
            "class_1", "reported_value"]
    m = pd.read_parquet(PARQUET, columns=cols,
                        filters=[("statement_type", "==", "income_statement"),
                                 ("class_1", "==", "TOTAL REVENUES")])
    m = m[m.state_fips.notna() & m.fips_county.notna()].copy()
    m["fiscal_year"] = m.fiscal_year.astype(int)   # partition key reads back categorical
    m["geoid"] = m.state_fips + m.fips_county
    m["cc"] = pd.to_numeric(m.fips_county, errors="coerce").fillna(-1)
    is_cgp = m.municipality_type == "County-General Purpose Government"
    recov = (~is_cgp) & ((m.state_fips == "02") |
                         ((m.state_fips == "51") & (m.cc >= 510)) |
                         (m.geoid.isin(INDEP_CONSOL)))
    ce = m[is_cgp | recov]
    g = ce.groupby(["geoid", "fiscal_year"], observed=True).reported_value.max().reset_index()
    prof = pd.DataFrame({"n_years": g.groupby("geoid").fiscal_year.nunique(),
                         "rev": g.groupby("geoid").reported_value.median()})
    gaps = prof[(prof.n_years >= 1) & (prof.n_years < 9)]

    print("\n" + "=" * 78)
    print("MINIMUM-FILING-THRESHOLD TEST (year-gaps)")
    print(f"  county governments with TOTAL REVENUES in >=1 year: {len(prof)}")
    print(f"  of which missing >=1 year (year-gap)              : {len(gaps)} "
          f"({len(gaps)/len(prof)*100:.0f}%)")
    print(f"  typical annual TOTAL REVENUES among gap counties:")
    for thr, lab in [(1e5, "$100K"), (1e6, "$1M"), (1e7, "$10M"), (5e7, "$50M")]:
        print(f"    above {lab:>5}: {(gaps.rev>thr).sum():4d} ({(gaps.rev>thr).mean()*100:5.1f}%)")
    print(f"    median ${gaps.rev.median()/1e6:,.1f}M | "
          f"10th pct ${gaps.rev.quantile(.1)/1e6:,.1f}M | "
          f"90th pct ${gaps.rev.quantile(.9)/1e6:,.0f}M")


if __name__ == "__main__":
    main()
    threshold_test()
