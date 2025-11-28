import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import os

# Directories
input_base_dir = r"C:\LST_G\Lsat_LST\ERA5_Land_LST"
output_base_dir = r"C:\LST_G\Lsat_LST\ERA5_Land_LST_Projected"

# target CRS
target_crs = "EPSG:4326"

# Loop years
for year in range(1950, 2025):
    input_dir = os.path.join(input_base_dir, str(year))
    output_dir = os.path.join(output_base_dir, str(year))

    # Skip if input folder does not exist
    if not os.path.exists(input_dir):
        continue

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process each GeoTIFF in the year's folder
    for filename in os.listdir(input_dir):
        if filename.endswith(".tif"):
            input_tif = os.path.join(input_dir, filename)
            output_tif = os.path.join(output_dir, filename)

            # Open the input GeoTIFF file
            with rasterio.open(input_tif) as src:
                transform, width, height = calculate_default_transform(
                    src.crs, target_crs, src.width, src.height, *src.bounds
                )

                # Define metadata
                kwargs = src.meta.copy()
                kwargs.update({
                    "crs": target_crs,
                    "transform": transform,
                    "width": width,
                    "height": height
                })

                # Create and write the reprojected file
                with rasterio.open(output_tif, "w", **kwargs) as dst:
                    for i in range(1, src.count + 1):
                        reproject(
                            source=rasterio.band(src, i),
                            destination=rasterio.band(dst, i),
                            src_transform=src.transform,
                            src_crs=src.crs,
                            dst_transform=transform,
                            dst_crs=target_crs,
                            resampling=Resampling.nearest
                        )

            print(f"Reprojected {filename} for {year} saved to {output_tif}")
