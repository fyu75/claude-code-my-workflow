"""
32_convert_muni_csv_to_parquet.py

Convert the 18 MuniSpot Academic License CSVs (gf_income_statement_FY{16..24}.csv
and gf_balance_sheet_FY{16..24}.csv, ~4.33M rows, ~1.1 GB total) to a single
Parquet dataset partitioned by (statement_type, fiscal_year).

Why Parquet:
- ~5-10× smaller on disk
- Preserves FIPS dtypes as strings (no leading-zero loss risk on future reads)
- Predicate pushdown for filtering by class_1, state_fips, etc.

Also produces three convenience derived files:
  - data/derived/muni_property_tax_FY2016_2024.csv     ← all rows with class_1=='PROPERTY TAX REVENUES' (~38k rows)
  - data/derived/muni_total_revenue_FY2016_2024.csv    ← rows with class_1=='TOTAL REVENUES'
  - data/derived/muni_total_expenditures_FY2016_2024.csv

Run:
  python3 scripts/python/32_convert_muni_csv_to_parquet.py
"""
from pathlib import Path
import shutil
import sys
import time
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as pa_ds

ROOT = Path(__file__).resolve().parents[2]
SRC  = ROOT / "data" / "muni" / "data"
OUT_PARQUET = ROOT / "data" / "muni" / "parquet"
OUT_DERIVED = ROOT / "data" / "derived"

OUT_PARQUET.mkdir(parents=True, exist_ok=True)
OUT_DERIVED.mkdir(parents=True, exist_ok=True)

# README explicitly warns: these MUST be loaded as strings to preserve leading zeros
FIPS_COLS = ["state_fips", "fips_county", "fips_place", "cbsa_code", "metrodiv_code"]
STR_COLS  = FIPS_COLS + [
    "munispot_id", "report_id", "fiscal_year_type", "statement_type",
    "fund_name", "class_1", "class_2", "statement_section",
    "basis_of_accounting", "municipality_name", "state", "county_name",
    "municipality_type", "csa_name",
]

def load_csv(path: Path) -> pd.DataFrame:
    """Read a MuniSpot CSV with the dtype contract the README warned about."""
    dtype = {c: "string" for c in STR_COLS}
    df = pd.read_csv(path, dtype=dtype, low_memory=False)
    # reported_value: ensure numeric (already in raw USD per README §4.5)
    df["reported_value"] = pd.to_numeric(df["reported_value"], errors="coerce")
    # Use plain int64 (not pandas-nullable Int32) so the partition key roundtrips
    # cleanly through pyarrow.dataset without dictionary-encoding coercion issues.
    df["fiscal_year"]    = pd.to_numeric(df["fiscal_year"], errors="coerce").astype("int64")
    # Derived 5-digit county GEOID — what our existing DC / SDC data joins on
    df["county_fips"] = (df["state_fips"].fillna("") + df["fips_county"].fillna("")).where(
        df["state_fips"].notna() & df["fips_county"].notna()
    )
    return df

# Pass 1: convert each CSV → Parquet (per-file), accumulate row counts
print(f"Source: {SRC}")
print(f"Target: {OUT_PARQUET}\n")
csvs = sorted(SRC.glob("gf_*.csv"))
print(f"Files to convert: {len(csvs)}\n")

total_rows = 0
property_tax_frames = []
total_rev_frames    = []
total_exp_frames    = []

# Clean any prior partial output so the partition layout is consistent
if OUT_PARQUET.exists():
    shutil.rmtree(OUT_PARQUET)
OUT_PARQUET.mkdir(parents=True, exist_ok=True)

t0 = time.time()
for csv_path in csvs:
    parts = csv_path.stem.split("_")
    statement_type = "_".join(parts[1:-1])   # 'income_statement' or 'balance_sheet'
    fy             = int(parts[-1].replace("FY", ""))

    t1 = time.time()
    df = load_csv(csv_path)

    # Use pyarrow.dataset.write_dataset for proper Hive partitioning. Critically,
    # the partition columns (statement_type, fiscal_year) are written to the
    # PATH only — NOT stored inside the files. This avoids the schema-merge
    # error you get when partition keys appear both in path and as file columns
    # (pyarrow infers path values as plain string; file columns may end up as
    # dictionary<string>, and a multi-file read fails to reconcile them).
    table = pa.Table.from_pandas(df, preserve_index=False)
    # Explicit partition schema avoids both the dict<string> auto-encoding (file
    # vs path schema mismatch) AND the Int32-vs-dictionary<int32> read-back error.
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
    # Sum sizes of files written for this partition (write_dataset may emit >1 file)
    part_dir = OUT_PARQUET / f"statement_type={statement_type}" / f"fiscal_year={fy}"
    dst_mb = sum(f.stat().st_size for f in part_dir.rglob("*.parquet")) / 1e6
    print(f"  {csv_path.name:<40} {n:>8,} rows  {src_mb:>6.1f} MB CSV → {dst_mb:>5.1f} MB Parquet  ({elapsed:>4.1f}s)")

    # Stash subsets for derived files
    pt   = df[df["class_1"] == "PROPERTY TAX REVENUES"]
    trev = df[df["class_1"] == "TOTAL REVENUES"]
    texp = df[df["class_1"] == "TOTAL EXPENDITURES"]
    if not pt.empty:   property_tax_frames.append(pt)
    if not trev.empty: total_rev_frames.append(trev)
    if not texp.empty: total_exp_frames.append(texp)

print(f"\nTotal rows across all 18 files: {total_rows:,}  (README claim: 4.33M)")
print(f"Time: {time.time()-t0:.1f}s\n")

# Pass 2: write derived convenience files
print("Writing derived convenience files (analysis-ready subsets):")

def write_subset(frames, name):
    if not frames:
        print(f"  {name}: empty, skipping")
        return
    df = pd.concat(frames, ignore_index=True)
    out = OUT_DERIVED / f"muni_{name}_FY2016_2024.csv"
    df.to_csv(out, index=False)
    print(f"  {name}: {len(df):,} rows × {df.shape[1]} cols → {out.name} ({out.stat().st_size/1e6:.1f} MB)")
    # Also save as parquet for fast reload
    df.to_parquet(out.with_suffix(".parquet"), compression="zstd", index=False)
    return df

pt_df   = write_subset(property_tax_frames, "property_tax")
trev_df = write_subset(total_rev_frames,    "total_revenue")
texp_df = write_subset(total_exp_frames,    "total_expenditures")

# Sanity checks
print("\nSanity checks on property-tax subset (the main research variable):")
if pt_df is not None:
    print(f"  Rows: {len(pt_df):,}  (README claim: ~38k total, ~5,131 in FY2024)")
    print(f"  FY2024 rows: {(pt_df['fiscal_year']==2024).sum():,}")
    print(f"  FY2024 distinct munispot_ids: {pt_df.loc[pt_df['fiscal_year']==2024, 'munispot_id'].nunique():,}  (README claim: 4,203)")
    print(f"  Distinct states: {pt_df['state'].nunique()}")
    print(f"  county_fips non-null: {pt_df['county_fips'].notna().sum():,} ({pt_df['county_fips'].notna().mean()*100:.1f}%)")
    print(f"  Top municipality_types:")
    print(pt_df["municipality_type"].value_counts().head(5).to_string())

# Total parquet size
total_pq_mb = sum(p.stat().st_size for p in OUT_PARQUET.rglob("*.parquet")) / 1e6
total_csv_mb = sum(p.stat().st_size for p in csvs) / 1e6
print(f"\nDisk usage: {total_csv_mb:.0f} MB CSV → {total_pq_mb:.0f} MB Parquet ({total_pq_mb/total_csv_mb*100:.0f}% of original)")
print(f"\nDone. Use:")
print(f"  pd.read_parquet('data/muni/parquet', filters=[('statement_type','==','income_statement'), ('fiscal_year','==',2024)])")
print(f"  pd.read_parquet('data/derived/muni_property_tax_FY2016_2024.parquet')")
