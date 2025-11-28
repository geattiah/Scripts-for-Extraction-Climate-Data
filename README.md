
# README: ERA5-Land Precipitation & Temperature Processing Pipeline

This repository contains a set of Python scripts used to download, preprocess, reproject, clip, and convert **ERA5-Land daily precipitation** and **2-m air temperature** data for Guyana into clean, georeferenced **NetCDF** files at ~1 km resolution.

The workflow is organized into two core pipelines:

- **A. Total Daily Precipitation**
- **B. 2-m Air Temperature**

There is also a standalone script to add time dimensions to NetCDF files.

---

## A. TOTAL PRECIPITATION PIPELINE

### 1. ERA5-Land Precipitation Retrieval from GEE
**File:** `1_ERA_Land_2m_P_retrieval_from_GEE.py`  
This script:
- Loads a Guyana boundary shapefile  
- Retrieves ERA5-Land DAILY_AGGR total_precipitation_sum using Google Earth Engine  
- Clips data to the Guyana region  
- Exports one GeoTIFF file per day  
- Organizes files into year-based folders  

Output example:
```
ERA5_Total_Prep_YYYY-MM-DD.tif
```

### 2. Reproject & Clip Precipitation TIFFs
**File:** `2_Reproject_precipitation.py`  
This script:
- Reads all annual TIFFs produced in Step 1  
- Reprojects data to EPSG:4326  
- Clips output to the Guyana shapefile  
- Converts precipitation from metres to millimetres  
- Applies nodata masking  
- Saves cleaned TIFF files  

### 3. Convert Processed Precipitation to NetCDF
**File:** `3_Convert_precipitation_to_netcdf.py`  
This script:
- Reads each clipped & reprojected precipitation TIFF  
- Extracts the date from the filename  
- Rebuilds latitude/longitude coordinate arrays  
- Saves each day as a NetCDF file with variable name `tp`  

Output example:
```
Guyana_tp_ERA5_1km_NearestNeighbour_Daily_YYYYMMDD.nc
```

---

## B. 2-M AIR TEMPERATURE PIPELINE

### 1. ERA5-Land 2-m Air Temperature Retrieval from GEE
**File:** `1_ERA_Land_2m_TA_retrieval_from_GEE copy.py`  
This script:
- Loads the Guyana shapefile  
- Fetches ERA5-Land DAILY_AGGR temperature_2m  
- Converts temperature from Kelvin to Celsius  
- Clips to Guyana and saves daily TIFFs  

Output example:
```
ERA5_Mean_Temp_YYYY-MM-DD.tif
```

### 2. Reproject Temperature TIFFs
**File:** `2_Reproject_temperature.py`  
This script:
- Reprojects temperature TIFFs to EPSG:4326  
- Writes reprojected temperature TIFFs into year folders  

### 3. Convert Temperature TIFFs to NetCDF
**File:** `3_Convert_tempurature_to_netcdf.py`  
This script:
- Reads each processed TIFF  
- Extracts date  
- Constructs lat/lon coordinate arrays  
- Generates one NetCDF file per day with variable name `t2m`  

Output example:
```
Guyana_t2m_ERA5_1km_NearestNeighbour_Daily_YYYYMMDD.nc
```

---

## C. ADD TIME DIMENSIONS TO NETCDF FILES

### Script: `Add_time_dimension_to_netcdf.py`
This script:
- Scans folders of existing NetCDF files  
- Extracts date from filename or metadata  
- Adds a time dimension if missing  
- Outputs files sorted into /YYYY/MM/ folders  

---

## DIRECTORY WORKFLOW

```
/Step1_Raw_TIFFs/
    /year/
        ERA5_Total_Prep_YYYY-MM-DD.tif
        ERA5_Mean_Temp_YYYY-MM-DD.tif

/Step2_Projected_TIFFs/
    /year/
        projected_precip.tif
        projected_temperature.tif

/Step3_NetCDF/
    /year/
        Guyana_tp_ERA5_1km_YYYYMMDD.nc
        Guyana_t2m_ERA5_1km_YYYYMMDD.nc
```

---

## DEPENDENCIES

- Python 3.8+
- Google Earth Engine (Python API)
- geemap
- xarray
- rasterio
- numpy
- pandas
- geopandas

Install dependencies:
```
pip install geemap rasterio xarray numpy pandas geopandas
```

---

## HOW TO RUN

1. Run the two GEE retrieval scripts  
2. Run the reprojection scripts  
3. Run the NetCDF conversion scripts  
4. (Optional) Run the time-dimension script  

---

## NOTES

- TIFF outputs maintain ERA5-Land 1 km resolution.  
- NetCDF files follow naming conventions suitable for climate/hydrology workflows.

