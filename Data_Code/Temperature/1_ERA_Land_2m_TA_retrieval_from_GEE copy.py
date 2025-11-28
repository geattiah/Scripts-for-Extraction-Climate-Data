import ee
import geemap
import os

ee.Initialize()

# Directories
shapefile = r"C:\Users\gattiah\OneDrive - Wilfrid Laurier University\Projects\LST_G\Guyana_Shape\Gayana_Outline.shp" 
output_dir = r"C:\LST_G\Lsat_LST\ERA5_Land_LST"
os.makedirs(output_dir, exist_ok=True)

region = geemap.shp_to_ee(shapefile).geometry().simplify(maxError=10)

# Start and end date
start_date = '2005-04-04'
end_date = '2005-04-05'

# Dataset from GEE
era5 = ee.ImageCollection('ECMWF/ERA5_LAND/DAILY_AGGR') \
    .filterBounds(region) \
    .filterDate(start_date, end_date)

# Calculate Temp to celcius
def calc_daily_mean_temp(image):
    temp = image.select('temperature_2m')
    temp = temp.subtract(273.15).rename('Mean_Temperature')  

    date = ee.Date(image.date()).format('YYYY-MM-dd')
    return temp.set({'date': date})

# Apply function
era5_temp = era5.map(calc_daily_mean_temp)

# Export data
def export_image(image):
    date = image.get('date').getInfo()

    year = date[:4]  # Extract year

    # Create yearly folders
    year_folder = os.path.join(output_dir, year)
    os.makedirs(year_folder, exist_ok=True)

    filename = os.path.join(year_folder, f'ERA5_Mean_Temp_{date}.tif')

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