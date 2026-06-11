"""
34_convert_munispot_v2_to_parquet.py

Convert MuniSpot's v2 interim county delivery (22 CSVs, FY2016-FY2026, ~4.04M
rows, ~1.5 GB total) to a single Parquet dataset partitioned by
(statement_type, fiscal_year). Parallels 32_convert_muni_csv_to_parquet.py
(which handled the v1 GF-only delivery), with these schema/scope differences:

  v1                              v2 (this script)
  ----------------------------    ------------------------------------
  munispot_id (entity key)        auditee_ein + report_id
  General Fund only               All governmental funds (filter on column_index=1
                                    to recover v1's GF-only scope exactly)
  18 files (FY2016-2024)          22 files (FY2016-2026)
  ~22 columns                     32 columns (adds fund_name, column_index,
                                    reported_stat, extraction_method, source_page,
                                    line_item_category, fiscal_year_type,
                                    created_at, updated_at)
  data/muni/data/gf_*.csv         data/munispot/data v2/county_allfunds_*.csv
  data/muni/parquet/              data/munispot/parquet_v2/

Why split parquet_v2 from parquet (v1) instead of overwriting:
- v1 derived files (muni_property_tax_FY2016_2024.csv) feed county_year_panel_v4.csv
  and the bond-spread analysis (script 30, 31). Keep v1 reproducible until we
  decide to migrate downstream code.
- v2 changes the entity key (munispot_id -> auditee_ein), which means we cannot
  do a strict UPSERT on top of v1. The two deliveries are distinct datasets.

Derived convenience files (under data/derived/, written with _v2_ suffix):
  - muni_property_tax_v2_gf_only_FY2016_2026.{csv,parquet}     ← column_index=1,
      directly comparable to v1's muni_property_tax_FY2016_2024
  - muni_property_tax_v2_allfunds_FY2016_2026.{csv,parquet}    ← column_index=-1
      (Total Governmental Funds), the new broader scope
  - muni_total_revenue_v2_{gf_only,allfunds}_FY2016_2026.{csv,parquet}
  - muni_total_expenditures_v2_{gf_only,allfunds}_FY2016_2026.{csv,parquet}

Run:
  ~/.pyenv/versions/3.12.0/bin/python scripts/python/34_convert_munispot_v2_to_parquet.py
"""
from pathlib import Path
import shutil
import time
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as pa_ds

ROOT = Path(__file__).resolve().parents[2]
SRC  = ROOT / "data" / "munispot" / "data v2"
OUT_PARQUET = ROOT / "data" / "munispot" / "parquet_v2"
OUT_DERIVED = ROOT / "data" / "derived"

OUT_PARQUET.mkdir(parents=True, exist_ok=True)
OUT_DERIVED.mkdir(parents=True, exist_ok=True)

# v2 README §"FIPS codes — load as strings": preserve leading zeros
FIPS_COLS = ["state_fips", "fips_county", "fips_place", "cbsa_code", "metrodiv_code"]
STR_COLS  = FIPS_COLS + [
    "auditee_ein", "report_id", "fiscal_year_type", "statement_type",
    "fund_name", "class_1", "class_2", "line_item_category", "statement_section",
    "reported_stat", "extraction_method", "basis_of_accounting",
    "municipality_name", "state", "county_name", "municipality_type",
    "csa_name",
]

def load_csv(path: Path) -> pd.DataFrame:
    """Read a MuniSpot v2 CSV with the dtype contract from the v2 README."""
    dtype = {c: "string" for c in STR_COLS}
    df = pd.read_csv(path, dtype=dtype, low_memory=False)

    # reported_value: numeric, already in dollars (value_multiplier pre-applied per README)
    df["reported_value"] = pd.to_numeric(df["reported_value"], errors="coerce")
    # fiscal_year: plain int64 so the partition key roundtrips through pyarrow cleanly
    df["fiscal_year"]    = pd.to_numeric(df["fiscal_year"], errors="coerce").astype("int64")
    # column_index: nullable int (some files may have nulls); use Int32 then to plain
    df["column_index"]   = pd.to_numeric(df["column_index"], errors="coerce").astype("Int32")
    # population: numeric (drop to float to allow NA)
    df["population"]     = pd.to_numeric(df["population"], errors="coerce")
    # value_multiplier: numeric (already applied to reported_value, kept for audit)
    df["value_multiplier"] = pd.to_numeric(df["value_multiplier"], errors="coerce")
    # latitude / longitude: numeric
    df["latitude"]       = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"]      = pd.to_numeric(df["longitude"], errors="coerce")
    # created_at / updated_at: parse as datetime (UTC tz-aware)
    for c in ("created_at", "updated_at"):
        df[c] = pd.to_datetime(df[c], errors="coerce", utc=True)
    # source_page: nullable int
    df["source_page"]    = pd.to_numeric(df["source_page"], errors="coerce").astype("Int32")

    # Derived 5-digit county GEOID — what our DC + SDC panels join on
    df["county_fips"] = (df["state_fips"].fillna("") + df["fips_county"].fillna("")).where(
        df["state_fips"].notna() & df["fips_county"].notna()
    )
    return df

# Pass 1: convert each CSV -> Parquet (per-partition), accumulate derived subsets
print(f"Source: {SRC}")
print(f"Target: {OUT_PARQUET}\n")
csvs = sorted(SRC.glob("county_allfunds_*.csv"))
print(f"Files to convert: {len(csvs)}\n")

# Clean any prior partial output so the partition layout is consistent
if OUT_PARQUET.exists():
    shutil.rmtree(OUT_PARQUET)
OUT_PARQUET.mkdir(parents=True, exist_ok=True)

total_rows = 0
derived_frames = {
    ("PROPERTY TAX REVENUES",  "gf"):     [],
    ("PROPERTY TAX REVENUES",  "all"):    [],
    ("TOTAL REVENUES",          "gf"):    [],
    ("TOTAL REVENUES",          "all"):   [],
    ("TOTAL EXPENDITURES",      "gf"):    [],
    ("TOTAL EXPENDITURES",      "all"):   [],
}

t0 = time.time()
for csv_path in csvs:
    # Filename: county_allfunds_income_statement_FY2017.csv
    #         | county_allfunds_balance_sheet_FY2017.csv
    parts = csv_path.stem.split("_")  # ['county','allfunds','income','statement','FY2017']
    assert parts[0] == "county" and parts[1] == "allfunds", f"unexpected file: {csv_path.name}"
    statement_type = "_".join(parts[2:-1])  # 'income_statement' or 'balance_sheet'
    fy             = int(parts[-1].replace("FY", ""))

    t1 = time.time()
    df = load_csv(csv_path)

    # Write Hive-partitioned. Partition keys live in the path only, not the file.
    table = pa.Table.from_pandas(df, preserve_index=False)
    part_schema = pa.schema([("statement_type", pa.string()),
                             ("fiscal_year",    pa.int64())])
    pa_ds.write_dataset(
        table,
        OUT_PARQUET,
        format="parquet",
        partitioning=pa_ds.partitioning(part_schema, flavor="hive"),
        existing_data_behavior="overwrite_or_ignore",
        file_options=pa_ds.ParquetFileFormat().make_write_options(compression="zstd"),
    )
    elapsed = time.time() - t1

    n = len(df)
    total_rows += n
    src_mb = csv_path.stat().st_size / 1e6
    part_dir = OUT_PARQUET / f"statement_type={statement_type}" / f"fiscal_year={fy}"
    dst_mb = sum(f.stat().st_size for f in part_dir.rglob("*.parquet")) / 1e6
    print(f"  {csv_path.name:<55} {n:>8,} rows  {src_mb:>6.1f} MB CSV -> {dst_mb:>5.1f} MB Parquet  ({elapsed:>4.1f}s)")

    # Stash derived subsets — both GF-only (col_index=1) and all-funds-total (col_index=-1)
    for c1 in ("PROPERTY TAX REVENUES", "TOTAL REVENUES", "TOTAL EXPENDITURES"):
        m_c1 = (df["class_1"] == c1)
        if not m_c1.any():
            continue
        sub_gf  = df[m_c1 & (df["column_index"] == 1)]
        sub_all = df[m_c1 & (df["column_index"] == -1)]
        if not sub_gf.empty:  derived_frames[(c1, "gf")].append(sub_gf)
        if not sub_all.empty: derived_frames[(c1, "all")].append(sub_all)

print(f"\nTotal rows across all {len(csvs)} files: {total_rows:,}  (README claim: ~4.04M)")
print(f"Time: {time.time()-t0:.1f}s\n")

# Pass 2: write derived convenience files
print("Writing derived convenience files (analysis-ready subsets):\n")

CLASS_TO_NAME = {
    "PROPERTY TAX REVENUES": "property_tax",
    "TOTAL REVENUES":         "total_revenue",
    "TOTAL EXPENDITURES":     "total_expenditures",
}
SCOPE_TO_TAG  = {"gf": "gf_only", "all": "allfunds"}

def write_subset(frames, class_label, scope):
    if not frames:
        print(f"  {class_label} / {scope}: empty, skipping")
        return None
    df = pd.concat(frames, ignore_index=True)
    stem = f"muni_{CLASS_TO_NAME[class_label]}_v2_{SCOPE_TO_TAG[scope]}_FY2016_2026"
    out_csv = OUT_DERIVED / f"{stem}.csv"
    out_pq  = OUT_DERIVED / f"{stem}.parquet"
    df.to_csv(out_csv, index=False)
    df.to_parquet(out_pq, compression="zstd", index=False)
    print(f"  {stem:<60} {len(df):>7,} rows x {df.shape[1]} cols  "
          f"({out_csv.stat().st_size/1e6:.1f} MB csv, {out_pq.stat().st_size/1e6:.1f} MB pq)")
    return df

results = {}
for c1 in ("PROPERTY TAX REVENUES", "TOTAL REVENUES", "TOTAL EXPENDITURES"):
    for scope in ("gf", "all"):
        results[(c1, scope)] = write_subset(derived_frames[(c1, scope)], c1, scope)

# Sanity checks on property-tax (the main research variable)
print("\nSanity checks — property-tax subset:")
pt_gf  = results[("PROPERTY TAX REVENUES", "gf")]
pt_all = results[("PROPERTY TAX REVENUES", "all")]
if pt_gf is not None:
    print(f"  GF-only:    {len(pt_gf):>6,} rows  |  distinct counties: {pt_gf['county_fips'].nunique():>5}  "
          f"|  distinct EINs: {pt_gf['auditee_ein'].nunique():>5}")
    print(f"  All-funds:  {len(pt_all):>6,} rows  |  distinct counties: {pt_all['county_fips'].nunique():>5}  "
          f"|  distinct EINs: {pt_all['auditee_ein'].nunique():>5}")
    print(f"  Fiscal years (GF):     {sorted(pt_gf['fiscal_year'].unique().tolist())}")
    print(f"  Top states by row count (GF):")
    print(pt_gf["state"].value_counts().head(8).to_string())

# Total parquet size vs source
total_pq_mb  = sum(p.stat().st_size for p in OUT_PARQUET.rglob("*.parquet")) / 1e6
total_csv_mb = sum(p.stat().st_size for p in csvs) / 1e6
print(f"\nDisk usage: {total_csv_mb:,.0f} MB CSV -> {total_pq_mb:,.0f} MB Parquet "
      f"({total_pq_mb/total_csv_mb*100:.0f}% of CSV)")

print("\nDone. Examples:")
print("  pd.read_parquet('data/munispot/parquet_v2',")
print("                  filters=[('statement_type','==','income_statement'),")
print("                           ('fiscal_year','==',2024)])")
print("  pd.read_parquet('data/derived/muni_property_tax_v2_gf_only_FY2016_2026.parquet')")
print("  pd.read_parquet('data/derived/muni_property_tax_v2_allfunds_FY2016_2026.parquet')")
