"""
35_classify_munispot_property_tax.py

Build a reported_stat-based property-tax classifier for MuniSpot v2.

Why: Raj's normalized class_1='PROPERTY TAX REVENUES' bucket only covers 917
distinct counties out of the 2,485 covered in v2 (~37%). The rest of the
property-tax lines fall under broader buckets like 'TAX REVENUES' (mixed),
'PAYMENTS IN LIEU OF TAXES' (PILOT substitutes), or are mis-bucketed. Per Raj's
own README note ("Use reported_stat to build a property-tax classification to
your paper's definition"), we mine the raw line-item labels ourselves.

Three classification tiers (each row gets all three flags):

  tier_strict       PT lines you can defend to a referee with one sentence:
                    class_1 == 'PROPERTY TAX REVENUES' minus explicit negations
                    ("Non-property tax items", "Nonproperty tax items") plus
                    high-confidence reported_stat matches from other buckets.
  tier_extended     tier_strict + broader reported_stat patterns: "real estate
                    tax", "ad valorem", "real property", "personal property",
                    "general property", "tangible property".
  tier_with_pilot   tier_extended + Payments In Lieu Of Taxes (PILOT) rows.
                    DC tax-incentive structures sometimes substitute PILOT for
                    property tax — include but flag separately so users decide.

Negative exclusions applied BEFORE positive matching, so they always win:
  - Bucket-level: class_1 in {USE OF MONEY AND PROPERTY, INTEREST AND DIVIDEND
    REVENUE, MISCELLANEOUS, REVENUES, LOCAL REVENUE} — "property" in these
    bucket/label names refers to gov-owned property, not property tax.
  - reported_stat negation patterns: "non-property", "nonproperty",
    "less property", "excluding property".

Sales / income / franchise / motor-vehicle / utility taxes are explicitly NOT
property tax. Motor vehicle is borderline in VA (personal-property tax on
cars), but our DC-paper focus is on DC-servers personal-property tax, captured
under "personal property" / "tangible property" reported_stat, not MV.

Output:
  data/derived/muni_property_tax_v2_classified_gf_only_FY2016_2026.{csv,parquet}
  data/derived/muni_property_tax_v2_classified_allfunds_FY2016_2026.{csv,parquet}

Each output row carries: original 33 columns + tier_strict + tier_extended +
tier_with_pilot + match_reason (text). Filter on the tier you want.

Run:
  ~/.pyenv/versions/3.12.0/bin/python scripts/python/35_classify_munispot_property_tax.py
"""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PQ   = ROOT / "data" / "munispot" / "parquet_v2"
OUT  = ROOT / "data" / "derived"
OUT.mkdir(parents=True, exist_ok=True)

# ===== Classification rules ==================================================

# Bucket-level exclusions: class_1 values that are never property tax. Applied
# first, so reported_stat patterns inside these buckets don't accidentally match.
#
# NOTE: MISCELLANEOUS and LOCAL REVENUE deliberately NOT excluded — Raj's
# extractor dumps LA-parish "Ad valorem taxes" into MISCELLANEOUS (1,150 hits)
# and some counties report "Local property taxes" in LOCAL REVENUE. Bucket
# exclusion would silently drop these. Instead, we rely on the reported_stat
# patterns being strict enough to only match unambiguous PT phrases.
BUCKETS_NEVER_PT = {
    "USE OF MONEY AND PROPERTY",       # rental/investment income from gov-owned property
    "INTEREST AND DIVIDEND REVENUE",
    "INTEREST INCOME",
    "REVENUES",                         # too generic — has "Revenue from use of money and property"
    "FEDERAL REVENUE",
    "INTERGOVERNMENTAL REVENUE",
    "FRANCHISE TAX REVENUES",
    "INCOME TAX REVENUES",
    "MOTOR VEHICLE TAX REVENUES",       # not property tax in our paper's definition
    "UTILITY TAX REVENUES",
    "OTHER OPERATING REVENUES",
    "CHARGES FOR SERVICES",
    "LICENSES AND PERMITS",
}

# Buckets where PT lines plausibly live (used for tier_extended scanning)
BUCKETS_PT_CANDIDATES = {
    "PROPERTY TAX REVENUES",
    "TAX REVENUES",                     # generic — needs strong reported_stat evidence
    "PAYMENTS IN LIEU OF TAXES",        # only counted in tier_with_pilot
    "MISCELLANEOUS",                    # LA parishes' ad-valorem hide here (Raj's misbucket)
    "LOCAL REVENUE",                    # some counties' "Local property taxes" here
}

# Negation patterns in reported_stat — always exclude even if other patterns match
NEG_PATTERNS = [
    r"\bnon[- ]?property\b",
    r"\bnonproperty\b",
    r"\bexcluding\s+property\b",
    r"\bless\s+property\b",
    r"\bnet\s+of\s+property\b",
]
NEG_RE = re.compile("|".join(NEG_PATTERNS), flags=re.IGNORECASE)

# Strict-tier positive patterns (high precision — no ambiguity)
STRICT_PATTERNS = [
    r"\bproperty\s+tax(es)?\b",
    r"\breal\s+estate\s+tax(es)?\b",
    r"\bgeneral\s+property\s+tax(es)?\b",
    r"\btaxes\s*[-,]\s*real\s+estate\b",
    r"\btaxes\s*[-,]\s*property\b",
    r"\btaxes,\s*primarily\s+property\b",
]
STRICT_RE = re.compile("|".join(STRICT_PATTERNS), flags=re.IGNORECASE)

# Extended-tier additional patterns (still high precision, broader vocabulary)
EXTENDED_PATTERNS = [
    r"\bad\s+valorem\b",
    r"\breal\s+property\b",
    r"\bpersonal\s+property\s+tax(es)?\b",     # DC-server personal-property tax!
    r"\btangible\s+(personal\s+)?property\s+tax(es)?\b",
    r"\bproperty\s+and\s+other\s+(county\s+)?tax\b",   # mixed, but property-anchored
    r"\bland\s+tax(es)?\b",
    r"\bmilage\b",                              # mill levy alternative spelling
    r"\bmillage\b",                             # mill levy
]
EXTENDED_RE = re.compile("|".join(EXTENDED_PATTERNS), flags=re.IGNORECASE)

# PILOT patterns (Payments In Lieu Of Taxes) — tier_with_pilot only
PILOT_PATTERNS = [
    r"\bpayments?\s+in\s+lieu\s+of\s+tax(es)?\b",
    r"\brevenues?\s+in\s+lieu\s+of\s+tax(es)?\b",
    r"\bvoluntary\s+payments?\s+in\s+lieu\b",
]
PILOT_RE = re.compile("|".join(PILOT_PATTERNS), flags=re.IGNORECASE)


def classify(df: pd.DataFrame) -> pd.DataFrame:
    """Add tier_strict, tier_extended, tier_with_pilot, match_reason columns."""
    df = df.copy()

    stat = df["reported_stat"].fillna("").astype(str)
    cls1 = df["class_1"].fillna("").astype(str)

    # Negation (always wins)
    is_negation = stat.str.contains(NEG_RE)

    # PT candidate eligibility (bucket-level filter)
    bucket_blocked = cls1.isin(BUCKETS_NEVER_PT)

    # Strict matches:
    #   (a) class_1 == 'PROPERTY TAX REVENUES' AND not a negation row
    #   (b) class_1 == 'TAX REVENUES' AND reported_stat matches STRICT pattern
    is_strict_bucket_a = (cls1 == "PROPERTY TAX REVENUES") & ~is_negation
    is_strict_bucket_b = (cls1 == "TAX REVENUES") & stat.str.contains(STRICT_RE) & ~is_negation
    tier_strict = (is_strict_bucket_a | is_strict_bucket_b) & ~bucket_blocked

    # Extended adds broader reported_stat patterns inside PT-candidate buckets
    is_extended_match = stat.str.contains(EXTENDED_RE) | stat.str.contains(STRICT_RE)
    is_in_candidate_bucket = cls1.isin(BUCKETS_PT_CANDIDATES)
    tier_extended = tier_strict | (is_in_candidate_bucket & is_extended_match & ~is_negation & ~bucket_blocked)

    # PILOT — explicit PILOT bucket OR reported_stat matches PILOT pattern in PT-candidate bucket
    is_pilot_bucket = (cls1 == "PAYMENTS IN LIEU OF TAXES")
    is_pilot_pattern = stat.str.contains(PILOT_RE)
    tier_pilot_only = (is_pilot_bucket | (is_in_candidate_bucket & is_pilot_pattern)) & ~bucket_blocked

    tier_with_pilot = tier_extended | tier_pilot_only

    # match_reason — for auditing
    reason = pd.Series([""] * len(df), index=df.index, dtype="object")
    reason.loc[is_strict_bucket_a] = "PROPERTY_TAX_REVENUES_bucket"
    reason.loc[is_strict_bucket_b] = "TAX_REVENUES_bucket+strict_stat"
    reason.loc[~tier_strict & tier_extended] = "extended_stat_pattern"
    reason.loc[~tier_extended & tier_with_pilot & is_pilot_bucket] = "PILOT_bucket"
    reason.loc[~tier_extended & tier_with_pilot & ~is_pilot_bucket] = "PILOT_pattern"

    df["tier_strict"]      = tier_strict
    df["tier_extended"]    = tier_extended
    df["tier_with_pilot"]  = tier_with_pilot
    df["match_reason"]     = reason
    return df


# ===== Load + classify =======================================================

print(f"Source: {PQ}")
print(f"Target: {OUT}\n")

# Load income statement only — property tax is a revenue line
print("Reading income_statement partitions...")
inc = pd.read_parquet(
    PQ,
    filters=[("statement_type", "==", "income_statement")],
)
print(f"  Rows: {len(inc):,}")
print(f"  Distinct counties (county_fips): {inc['county_fips'].nunique():,}")
print()

print("Classifying...")
cls = classify(inc)
matched = cls[cls["tier_with_pilot"]]
print(f"  Rows matching any tier: {len(matched):,}")
print(f"  By tier:")
print(f"    tier_strict      : {cls['tier_strict'].sum():>7,}")
print(f"    tier_extended    : {cls['tier_extended'].sum():>7,}")
print(f"    tier_with_pilot  : {cls['tier_with_pilot'].sum():>7,}")
print(f"  match_reason breakdown:")
print(matched["match_reason"].value_counts().to_string())
print()

# ===== Write outputs =========================================================

def write(df, stem):
    csv = OUT / f"{stem}.csv"
    pq  = OUT / f"{stem}.parquet"
    df.to_csv(csv, index=False)
    df.to_parquet(pq, compression="zstd", index=False)
    return csv, pq

print("Writing classified subsets:\n")

# GF-only (column_index=1)
gf = matched[matched["column_index"] == 1].copy()
af = matched[matched["column_index"] == -1].copy()   # "Total Governmental Funds"

csv_gf, pq_gf = write(gf, "muni_property_tax_v2_classified_gf_only_FY2016_2026")
csv_af, pq_af = write(af, "muni_property_tax_v2_classified_allfunds_FY2016_2026")

print(f"  GF-only  (col_index=1):   {len(gf):>6,} rows x {gf.shape[1]} cols  "
      f"({csv_gf.stat().st_size/1e6:.1f} MB csv, {pq_gf.stat().st_size/1e6:.1f} MB pq)")
print(f"  All-funds (col_index=-1): {len(af):>6,} rows x {af.shape[1]} cols  "
      f"({csv_af.stat().st_size/1e6:.1f} MB csv, {pq_af.stat().st_size/1e6:.1f} MB pq)")

# ===== Coverage report =======================================================

print("\n" + "=" * 78)
print("COVERAGE REPORT — distinct counties (county_fips) by tier and scope")
print("=" * 78)
print()

def cov(df, scope_name):
    print(f"--- {scope_name} ---")
    for tier in ("tier_strict", "tier_extended", "tier_with_pilot"):
        sub = df[df[tier]]
        n_county = sub["county_fips"].nunique()
        n_ein    = sub["auditee_ein"].nunique()
        n_cy     = sub.groupby(["county_fips","fiscal_year"]).ngroups
        print(f"  {tier:<18}  counties: {n_county:>5}   "
              f"EINs: {n_ein:>5}   county-years: {n_cy:>6}")
    print()

cov(cls[cls["column_index"] == 1],  "GF-only (column_index = 1)")
cov(cls[cls["column_index"] == -1], "All governmental funds (column_index = -1)")

# Headline comparison — strict bucket alone vs full classifier
strict_counties_gf = cls.loc[cls.tier_strict & (cls.column_index==1), "county_fips"].nunique()
pilot_counties_gf  = cls.loc[cls.tier_with_pilot & (cls.column_index==1), "county_fips"].nunique()
strict_counties_af = cls.loc[cls.tier_strict & (cls.column_index==-1), "county_fips"].nunique()
pilot_counties_af  = cls.loc[cls.tier_with_pilot & (cls.column_index==-1), "county_fips"].nunique()

total_covered = inc["county_fips"].nunique()
print(f"--- Headline (vs {total_covered:,} total covered counties in v2) ---")
print(f"  GF-only,   class_1='PROPERTY TAX REVENUES' only:    {strict_counties_gf:>5}  "
      f"({strict_counties_gf/total_covered*100:.1f}%)")
print(f"  GF-only,   tier_with_pilot (full classifier):       {pilot_counties_gf:>5}  "
      f"({pilot_counties_gf/total_covered*100:.1f}%)")
print(f"  Allfunds,  class_1='PROPERTY TAX REVENUES' only:    {strict_counties_af:>5}  "
      f"({strict_counties_af/total_covered*100:.1f}%)")
print(f"  Allfunds,  tier_with_pilot (full classifier):       {pilot_counties_af:>5}  "
      f"({pilot_counties_af/total_covered*100:.1f}%)")
print()

# Top states by PT row count (GF, tier_with_pilot)
print("Top 12 states by PT-classified row count (GF, tier_with_pilot):")
print(gf[gf["tier_with_pilot"]]["state"].value_counts().head(12).to_string())

print("\nDone.")
