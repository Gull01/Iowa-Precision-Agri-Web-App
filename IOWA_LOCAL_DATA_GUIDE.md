# Iowa Local Data Layers - No Internet Required! 🌾

## Overview

This feature allows you to display locally downloaded GIS data for Iowa **without any internet connection**. All data is served from the `DATA` folder and rendered dynamically as map tiles.

## Available Datasets

Your DATA folder contains the following Iowa-specific datasets:

### 📊 Land Use / Land Cover (LULC)

1. **Iowa CDL (Cropland Data Layer)** - `Iowa_CDL.tif`
   - USDA NASS detailed crop type classification
   - Shows corn, soybeans, wheat, and other crops
   - Annual land cover data

2. **Iowa NLCD (National Land Cover Database)** - `Iowa_NLCD.tif`
   - Comprehensive land cover classification
   - Includes urban, forest, wetlands, water bodies
   - 30-meter resolution

### 🌿 Vegetation Indices

3. **Iowa Landsat NDVI** - `Iowa_Landsat_NDVI.tif`
   - Normalized Difference Vegetation Index
   - Measures vegetation health and density
   - Landsat satellite-derived

### 🌦️ Climate Data

4. **Iowa GridMET Rainfall** - `Iowa_Gridmet_Rainfall.tif`
   - Gridded precipitation data
   - High-resolution climate dataset
   - GridMET product

5. **Iowa Summer Max Temperature** - `Iowa_Gridmet_Tmax_Summer.tif`
   - Maximum temperature during summer
   - GridMET climate analysis
   - Useful for heat stress assessment

6. **Iowa Evapotranspiration** - `Iowa_Gridmet_ET.tif`
   - Reference evapotranspiration (ET₀)
   - Water demand analysis
   - Irrigation planning

### 🌱 Soil Data

7. **Iowa SMAP Soil Moisture** - `Iowa_SMAP_SoilMoisture.tif`
   - NASA SMAP satellite soil moisture
   - Surface soil moisture content
   - Agricultural water management

## Features

### 🗺️ Interactive Map Layers

- **Layer Toggle**: Enable/disable individual layers with checkboxes
- **Layer Information**: Click ℹ️ button for detailed dataset metadata
- **Point Values**: Click anywhere on the map to see values from active layers
- **Iowa Boundary**: Visual indicator showing Iowa state bounds
- **Zoom to Iowa**: Quick button to focus map on Iowa

### 📊 Statistics Dashboard

- View min, max, mean, and standard deviation for each dataset
- Data point counts
- Quick overview of all available data

### 🎨 Custom Colormaps

- **NDVI**: Red (low vegetation) → Green (high vegetation)
- **Climate**: Blue (low) → Red (high) gradient
- **LULC**: Categorical colors for different land cover types
- **Grayscale**: Default for other datasets

## How to Use

### 1. Start the Application

```powershell
# Make sure you're in the project directory
cd E:\work_projects\N-IGIS-WORK\WEB

# Start the server
python main.py
```

### 2. Open the Web Interface

Navigate to: http://localhost:8000/static/index.html

### 3. Access Iowa Local Data

Look for the **🌾 Iowa Local Data** panel on the top-right of the map.

### 4. Enable Layers

- Click checkboxes to enable/disable layers
- Multiple layers can be active simultaneously
- Adjust layer opacity if needed

### 5. Explore Data

- **Click on map**: Get values at clicked location for all active layers
- **Click ℹ️**: View detailed information about a dataset
- **Click 📍 Zoom to Iowa**: Center map on Iowa
- **Click 📊 View Statistics**: See statistical summary of all datasets

## API Endpoints

All endpoints are served locally - no internet required!

### List All Datasets
```
GET /api/local-data/datasets
```

Returns list of all available Iowa datasets with metadata.

### Get Dataset Information
```
GET /api/local-data/info/{dataset_id}
```

Get detailed information about a specific dataset including:
- Bounds
- CRS (Coordinate Reference System)
- Dimensions
- Statistics
- Data type

### Get Map Tiles
```
GET /api/local-data/tiles/{dataset_id}/{z}/{x}/{y}.png
```

Dynamically generates map tiles from GeoTIFF files.
- `{z}`: Zoom level
- `{x}`: Tile X coordinate
- `{y}`: Tile Y coordinate

### Get Point Value
```
GET /api/local-data/point-value/{dataset_id}?lat=41.5&lon=-93.5
```

Get the data value at a specific location.

### Get Dataset Statistics
```
GET /api/local-data/stats/{dataset_id}
```

Get comprehensive statistics including histogram data.

### Get Iowa Bounds
```
GET /api/local-data/iowa-bounds
```

Get Iowa state geographic boundaries and center point.

## Dataset IDs

Use these IDs in API calls:

- `iowa_cdl` - Cropland Data Layer
- `iowa_nlcd` - National Land Cover Database
- `iowa_ndvi` - Landsat NDVI
- `iowa_rainfall` - GridMET Rainfall
- `iowa_tmax` - Summer Max Temperature
- `iowa_et` - Evapotranspiration
- `iowa_soil_moisture` - SMAP Soil Moisture

## Example API Usage

### Python
```python
import requests

# List all datasets
response = requests.get('http://localhost:8000/api/local-data/datasets')
datasets = response.json()

# Get NDVI value at a location
response = requests.get(
    'http://localhost:8000/api/local-data/point-value/iowa_ndvi',
    params={'lat': 41.5, 'lon': -93.5}
)
value = response.json()
print(f"NDVI at location: {value['value']}")
```

### JavaScript
```javascript
// Get dataset information
fetch('/api/local-data/info/iowa_cdl')
    .then(response => response.json())
    .then(info => console.log(info));

// Get statistics
fetch('/api/local-data/stats/iowa_rainfall')
    .then(response => response.json())
    .then(stats => console.log(stats));
```

## File Structure

```
WEB/
├── DATA/                          # Your local GIS data
│   ├── Iowa_CDL.tif              # Cropland Data Layer
│   ├── Iowa_NLCD.tif             # Land Cover
│   ├── Iowa_Landsat_NDVI.tif     # NDVI
│   ├── Iowa_Gridmet_Rainfall.tif # Rainfall
│   ├── Iowa_Gridmet_Tmax_Summer.tif # Temperature
│   ├── Iowa_Gridmet_ET.tif       # Evapotranspiration
│   └── Iowa_SMAP_SoilMoisture.tif # Soil Moisture
│
├── local_data_api.py              # API for serving local data
│
└── static/
    ├── iowa-local-layers.js       # JavaScript layer control
    ├── iowa-local-layers.css      # Styling
    └── index.html                 # Main interface
```

## Technical Details

### Tile Generation

- **On-the-fly rendering**: Tiles are generated dynamically from GeoTIFF files
- **Caching**: Browser caches tiles for better performance
- **Resolution**: 256×256 pixel tiles at various zoom levels
- **Resampling**: Bilinear interpolation for smooth display

### Coordinate Systems

- **Input**: Native CRS of each GeoTIFF (usually UTM or Albers Equal Area)
- **Output**: Web Mercator (EPSG:3857) for web display
- **Reprojection**: Automatic coordinate transformation

### Performance

- **First load**: May take a few seconds to generate tiles
- **Subsequent views**: Cached tiles load instantly
- **Memory usage**: Tiles generated on-demand, minimal RAM usage
- **Disk space**: Only source GeoTIFF files stored

## Benefits of Local Data

✅ **No Internet Required**: Work completely offline  
✅ **Fast Access**: No API rate limits or delays  
✅ **Privacy**: Data stays on your local machine  
✅ **Full Control**: Customize colormaps and display  
✅ **Cost-Free**: No API subscription fees  
✅ **Reliable**: No external service dependencies  

## Troubleshooting

### Layers Not Showing

1. **Check data files exist**: Ensure all .tif files are in the DATA folder
2. **Check console**: Open browser developer tools (F12) and look for errors
3. **Verify zoom level**: Layers only display between zoom 7-18 for Iowa
4. **Check bounds**: Make sure you're viewing Iowa region

### Tiles Loading Slowly

1. **First time**: Initial tile generation takes a few seconds
2. **Large files**: Some GeoTIFF files are very large
3. **Zoom level**: Higher zoom levels require more tiles
4. **Solution**: Wait for initial load, then tiles will cache

### API Errors

1. **Check server running**: Make sure `python main.py` is active
2. **Check port**: Default is 8000, ensure it's not in use
3. **Check file paths**: Verify DATA folder location
4. **Check dependencies**: Run `pip install mercantile rasterio pillow`

## Adding New Datasets

To add your own local Iowa data:

1. Place GeoTIFF file in `DATA/` folder
2. Edit `local_data_api.py`:
   ```python
   IOWA_DATASETS = {
       "your_dataset_id": {
           "file": "Your_Data.tif",
           "name": "Your Dataset Name",
           "description": "Description here",
           "category": "LULC"  # or Climate, Vegetation, Soil
       }
   }
   ```
3. Restart the server
4. New layer will appear in the control panel

## Integration with Other Features

The Iowa local data integrates seamlessly with other app features:

- **Field Analysis**: Combine with field boundaries
- **Weather Data**: Compare with real-time weather
- **Crop Monitoring**: Cross-reference with NDVI analysis
- **Soil Analysis**: Validate with soil moisture data

## Future Enhancements

Planned improvements:

- [ ] Time series support (multiple dates)
- [ ] Raster calculator (combine layers)
- [ ] Export data as GeoJSON
- [ ] Download tile cache
- [ ] Custom colormap editor
- [ ] Legend for categorical data
- [ ] Animated climate data
- [ ] Field-level statistics

## Support

For issues or questions:
1. Check browser console for errors
2. Verify all dependencies installed
3. Ensure DATA files are present
4. Check API endpoint responses

---

**Note**: This feature is designed specifically for Iowa data but can be adapted for any geographic region by adding appropriate GeoTIFF files to the DATA folder.
