#!/usr/bin/env python3
"""
33_convert_msrb_to_parquet.py

Convert data/msrb/msrb.sas7bdat (60.7 GB, 215,791,679 rows x 25 cols) to a
single zstd-compressed Parquet file (~4.5 GB projected, ~13.5x smaller).

Size discipline (memos/2026-05-16_data_inventory.md): the 60 GB file is NEVER
loaded in memory — it is streamed in row-chunks via pandas.read_sas and written
one Parquet row-group per chunk through a single ParquetWriter.

Faithful round-trip:
- SAS char cols -> str via encoding="latin-1" (byte-lossless, never raises)
- SAS numeric -> float64 ; SAS dates -> timestamp[s]
- Schema pinned from the first chunk; later chunks cast to it for stability.

The original .sas7bdat is LEFT UNTOUCHED. Row count is verified against the SAS
header (215,791,679) before you decide to remove the original.

Why Parquet (same rationale as 32_convert_muni_csv_to_parquet.py):
- ~13x smaller on disk, open cross-tool format (pandas / polars / DuckDB / R / Arrow)
- predicate pushdown -> the deferred "filter to DC-host-county CUSIPs" Stage-2
  pass (memo's most expensive step) becomes a fast columnar scan.

Run:
  ~/.pyenv/versions/3.12.0/bin/python3 scripts/python/33_convert_msrb_to_parquet.py
"""
from pathlib import Path
import sys, time
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
SRC  = ROOT / "data" / "msrb" / "msrb.sas7bdat"
OUT  = ROOT / "data" / "msrb" / "msrb.parquet"
CHUNK = 2_000_000
COMPRESSION = "zstd"
EXPECTED_ROWS = 215_791_679

if not SRC.exists():
    sys.exit(f"ABORT: source not found: {SRC}")
if OUT.exists():
    sys.exit(f"ABORT: {OUT} already exists — remove it first to re-convert.")

print(f"SRC {SRC}  ({SRC.stat().st_size/1e9:.1f} GB)", flush=True)
print(f"OUT {OUT}  [{COMPRESSION}]  chunk={CHUNK:,}", flush=True)

t0 = time.time()
writer = None
schema = None
total = 0
try:
    it = pd.read_sas(SRC, format="sas7bdat", chunksize=CHUNK, encoding="latin-1")
    for i, chunk in enumerate(it):
        if schema is None:
            tbl = pa.Table.from_pandas(chunk, preserve_index=False)
            schema = tbl.schema
            writer = pq.ParquetWriter(OUT, schema, compression=COMPRESSION,
                                      use_dictionary=True)
        else:
            tbl = pa.Table.from_pandas(chunk, schema=schema, preserve_index=False)
        writer.write_table(tbl)
        total += len(chunk)
        if i % 5 == 0 or len(chunk) < CHUNK:
            el = time.time() - t0
            sz = OUT.stat().st_size / 1e9
            rate = total / el if el else 0
            print(f"  chunk {i:3d}  rows={total:>13,}  {el:6.0f}s  "
                  f"{rate/1e6:.1f}M row/s  parquet={sz:.2f} GB", flush=True)
finally:
    if writer is not None:
        writer.close()

el = time.time() - t0
sz = OUT.stat().st_size
print(f"\nDONE  rows_written={total:,}  expected={EXPECTED_ROWS:,}  "
      f"match={total == EXPECTED_ROWS}", flush=True)
print(f"parquet size: {sz/1e9:.2f} GB  ({SRC.stat().st_size/sz:.1f}x smaller)  "
      f"in {el/60:.1f} min", flush=True)

md = pq.ParquetFile(OUT).metadata
print(f"parquet footer: num_rows={md.num_rows:,}  row_groups={md.num_row_groups}  "
      f"cols={md.num_columns}", flush=True)
if md.num_rows != EXPECTED_ROWS or total != EXPECTED_ROWS:
    sys.exit("ROW COUNT MISMATCH — DO NOT remove the original .sas7bdat.")
print("VERIFIED ✓  original .sas7bdat left untouched.", flush=True)
