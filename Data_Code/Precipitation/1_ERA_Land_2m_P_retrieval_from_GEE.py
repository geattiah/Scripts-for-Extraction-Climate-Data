import ee
import geemap
import os

ee.Initialize()

# Directories
shapefile = r"C:\Users\gattiah\OneDrive - Wilfrid Laurier University\Projects\LST_G\Guyana_Shape\Gayana_Outline.shp" 
output_dir = r"C:\LST_G\Lsat_LST\ERA5_Land_Precipitation"
os.makedirs(output_dir, exist_ok=True)

region = geemap.shp_to_ee(shapefile).geometry().simplify(maxError=10)

# Start and end date
start_date = '1962-01-01'
end_date = '1964-01-01'

# Dataset from GEE
era5 = ee.ImageCollection('ECMWF/ERA5_LAND/DAILY_AGGR') \
    .filterBounds(region) \
    .filterDate(start_date, end_date)

# Calculate precipation to celcius
def calc_daily_mean_temp(image):
    temp = image.select('total_precipitation_sum').rename('Total_Precipitation')

    date = ee.Date(image.date()).format('YYYY-MM-dd')
    return temp.set({'date': date})

# Apply function
era5_temp = era5.map(calc_daily_mean_temp)

# Export data
def export_image(image):
    date = image.get('date').getInfo()

    year = date[:4]  # Extract year from date

    # Create year-specific folder if it doesn't exist
    year_folder = os.path.join(output_dir, year)
    os.makedirs(year_folder, exist_ok=True)

    filename = os.path.join(year_folder, f'ERA5_Total_Prep_{date}.tif')

    geemap.ee_export_image(image.clip(region),
                            filename=filename, scale=1000, region=region, crs='EPSG:4326',file_per_band=False)
    print(f"Exported {filename}")

# Export image
images = era5_temp.toList(era5_temp.size())
for i in range(images.size().getInfo()):
    try:
        image = ee.Image(images.get(i))
        export_image(image)
    except Exception as e:
        print(f"Error exporting image {i}: {e}")

print("Daily mean surface temperature data exported successfully!")