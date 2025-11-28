import rasterio
import xarray as xr
import numpy as np
import os
import re

# === USER INPUTS ===
base_dir = r"C:\LST_G\Lsat_LST\ERA5_Land_LST_Projected"
output_base_dir = r"C:\LST_G\Lsat_LST\2m_Air_Temperature"
os.makedirs(output_base_dir, exist_ok=True)

# Loop through folders for each year
for year in range(1950, 2025):
    input_year_dir = os.path.join(base_dir, str(year))
    output_year_dir = os.path.join(output_base_dir, str(year))
    os.makedirs(output_year_dir, exist_ok=True)

    if not os.path.isdir(input_year_dir):
        continue

    for filename in os.listdir(input_year_dir):
        if filename.endswith(".tif") or filename.endswith(".tiff"):
           
            match = re.search(r"\d{4}-\d{2}-\d{2}", filename)
            if not match:
                continue
            date_str = match.group(0)
            date_nodash = date_str.replace("-", "")

            input_path = os.path.join(input_year_dir, filename)

            with rasterio.open(input_path) as src:
           
                data = src.read(1).astype(float)
                nodata_val = src.nodata
                if nodata_val is not None:
                    data[data == nodata_val] = np.nan

                # Create coordinate arrays
                transform = src.transform
                lon_start = transform.c
                lat_start = transform.f
                lon_res = transform.a
                lat_res = -transform.e

                lons = np.arange(lon_start, lon_start + src.width * lon_res, lon_res)
                lats = np.arange(lat_start, lat_start - src.height * lat_res, -lat_res)

                # Create DataArray
                da = xr.DataArray(
                    data,
                    dims=["lat", "lon"],
                    coords={"lat": lats, "lon": lons},
                    name="t2m"
                )

                # Create Dataset
                ds = xr.Dataset({"t2m": da})

                # Define output filename
                out_filename = f"Guyana_t2m_ERA5_1km_NearestNeighbour_Daily_{date_nodash}.nc"
                out_path = os.path.join(output_year_dir, out_filename)

                # Save NetCDF
                ds.to_netcdf(out_path)
                print(f"Saved: {out_path}")