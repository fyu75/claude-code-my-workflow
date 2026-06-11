"""
72_slice_msrb_to_working_panel.py

Phase 2 of the MSRB secondary-market analysis: slice the full trade tape
(data/msrb/msrb.parquet, 215.8M rows, 216 row groups) down to the bonds of the
treated + placebo-metro + clean-control counties, using the issuer-level CUSIP6 ->
county mapping built from SDC ISSUECUSIP1 (data/derived/msrb_cusip6_county_map.csv:
21,294 CUSIP6 across 2,465 counties; multi-county conduit CUSIP6s dropped).

Streamed row-group by row-group (never loads the full tape); keeps only the columns
the event study needs; writes a single zstd parquet working panel.

Output: data/msrb/msrb_working_slice.parquet  (+ console coverage stats)
"""
from pathlib import Path
import time
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "msrb" / "msrb.parquet"
OUT = ROOT / "data" / "msrb" / "msrb_working_slice.parquet"
MAP = ROOT / "data" / "derived" / "msrb_cusip6_county_map.csv"

COLS = ["CUSIP", "CUSIP6", "TRADE_DATE", "YIELD", "DOLLAR_PRICE", "PAR_TRADED",
        "TRADE_TYPE_INDICATOR", "MATURITY_DATE", "DATED_DATE", "COUPON",
        "WHEN_ISSUED_INDICATOR", "BROKERS_BROKER_INDICATOR"]

m = pd.read_csv(MAP, dtype=str)
keep = set(m["cusip6"])
print(f"CUSIP6 filter set: {len(keep):,}", flush=True)

pf = pq.ParquetFile(SRC)
writer, total_in, total_out, t0 = None, 0, 0, time.time()
for i in range(pf.metadata.num_row_groups):
    tbl = pf.read_row_group(i, columns=COLS)
    df = tbl.to_pandas()
    total_in += len(df)
    sub = df[df["CUSIP6"].isin(keep)]
    total_out += len(sub)
    if len(sub):
        t = pa.Table.from_pandas(sub, preserve_index=False)
        if writer is None:
            writer = pq.ParquetWriter(OUT, t.schema, compression="zstd")
        writer.write_table(t)
    if (i + 1) % 20 == 0:
        print(f"  rg {i+1}/{pf.metadata.num_row_groups}  in={total_in/1e6:.0f}M  "
              f"kept={total_out/1e6:.2f}M  ({time.time()-t0:.0f}s)", flush=True)
if writer: writer.close()
print(f"\nDONE: {total_out:,} of {total_in:,} trades kept "
      f"({total_out/total_in*100:.1f}%) -> {OUT.name} "
      f"({OUT.stat().st_size/1e9:.2f} GB, {time.time()-t0:.0f}s)", flush=True)

# coverage stats by group
sl = pq.read_table(OUT, columns=["CUSIP6"]).to_pandas()
sl = sl.merge(m, left_on="CUSIP6", right_on="cusip6", how="left")
print("\ntrades by group:")
print(sl.group.value_counts().to_string())
print("\ntreated counties with >=1 trade:",
      sl.loc[sl.group == "treated", "county_fips"].nunique())
