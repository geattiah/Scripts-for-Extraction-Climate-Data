import os
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.mask import mask
import geopandas as gpd
import numpy as np

# User inputs
base_input_dir = r"C:\LST_G\Lsat_LST\ERA5_Land_Precipitation"  
base_output_dir = r"C:\LST_G\Lsat_LST\ERA5_Land_Precipitation_Projected"
shapefile = r"C:\Users\gattiah\OneDrive - Wilfrid Laurier University\Projects\LST_G\Guyana_Shape\Gayana_Outline.shp"
target_crs = "EPSG:4326"
nodata_value = -9999  

# load shapefile 
shapes = gpd.read_file(shapefile)
shapes = shapes.to_crs(target_crs)
geometry = [feature["geometry"] for feature in shapes.__geo_interface__["features"]]

# loop years and project
for year in range(1950, 2025):
    year_str = str(year)
    input_dir = os.path.join(base_input_dir, year_str)
    output_dir = os.path.join(base_output_dir, year_str)

    if not os.path.exists(input_dir):
        print(f"Skipping {year} (no data folder)")
        continue

    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith(".tif"):
            input_tif = os.path.join(input_dir, filename)
            output_tif = os.path.join(output_dir, filename)

            with rasterio.open(input_tif) as src:

                transform, width, height = calculate_default_transform(
                    src.crs, target_crs, src.width, src.height, *src.bounds
                )
                kwargs = src.meta.copy()
                kwargs.update({
                    "crs": target_crs,
                    "transform": transform,
                    "width": width,
                    "height": height
                })

                with rasterio.io.MemoryFile() as memfile:
                    with memfile.open(**kwargs) as temp_dst:
                        for i in range(1, src.count + 1):
                            reproject(
                                source=rasterio.band(src, i),
                                destination=rasterio.band(temp_dst, i),
                                src_transform=src.transform,
                                src_crs=src.crs,
                                dst_transform=transform,
                                dst_crs=target_crs,
                                resampling=Resampling.nearest
                            )

                        # clip
                        out_image, out_transform = mask(temp_dst, geometry, crop=True)
                        out_meta = temp_dst.meta.copy()

                        # convert to mm
                        out_image = out_image * 1000
                        out_image[out_image == 0] = np.nan
                        out_image = np.where(np.isnan(out_image), nodata_value, out_image)

                        # metadata update
                        out_meta.update({
                            "height": out_image.shape[1],
                            "width": out_image.shape[2],
                            "transform": out_transform,
                            "nodata": nodata_value
                        })

                        # final output
                        with rasterio.open(output_tif, "w", **out_meta) as dst:
                            dst.write(out_image)

            print(f"✓ {year} - Processed: {filename}")