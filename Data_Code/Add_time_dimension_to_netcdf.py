
import re
from pathlib import Path
import pandas as pd
import xarray as xr

IN_DIR = Path(r"C:\Users\gattiah\University of Waterloo\UW GWF O - Data_P - Data_P\Final_Dataset\Total_Precipitation")      # folder with many .nc files
OUT_BASE = Path(r"C:\Users\gattiah\University of Waterloo\UW GWF O - Data_P - Data_P\Final_Dataset_With_Time_Dimension\Total_Precipitation")   # we will create OUT_BASE\YYYY\MM\

OUT_BASE.mkdir(parents=True, exist_ok=True)

def parse_date_from_name(name: str):
    """Parse YYYYMMDD (or YYYYMMDDHH) from filename into pandas.Timestamp."""
    m = re.search(r"(19|20)\d{6,7}", name)
    if not m:
        return None
    s = m.group(0)
    date_str = f"{s[:4]}-{s[4:6]}-{s[6:8]}"
    if len(s) >= 10:
        date_str += f" {s[8:10]}:00:00"
    return pd.to_datetime(date_str)

# -------------------
# MAIN LOOP
# -------------------
for fp in IN_DIR.rglob("*.nc"):   # <== rglob means recurse into all subfolders
    try:
        ds = xr.open_dataset(fp)

        # 1. Find the timestamp
        ts = None
        if "time" in ds.coords:
            try:
                tvals = pd.to_datetime(ds["time"].values)
                ts = pd.to_datetime(tvals[0]) if hasattr(tvals, "__len__") else pd.to_datetime(tvals)
            except Exception:
                ts = None
        if ts is None:
            ts = parse_date_from_name(fp.name)
        if ts is None:
            print(f"⚠️ Skipped {fp} (no time found)")
            ds.close()
            continue

        # 2. Ensure a time dimension
        if "time" not in ds.dims and "time" not in ds.coords:
            ds = ds.expand_dims(time=[ts])
            order = ["time"] + [d for d in ds.dims if d != "time"]
            ds = ds.transpose(*order)

        # 3. Build output path OUT_BASE/YYYY/MM/filename.nc
        out_dir = OUT_BASE / f"{ts.year:04d}" / f"{ts.month:02d}"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / fp.name

        # 4. Save
        ds.to_netcdf(out_path)
        ds.close()
        print(f"✅ {fp} → {out_path}")
    except Exception as e:
        print(f"❌ Failed {fp}: {e}")