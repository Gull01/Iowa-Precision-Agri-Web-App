# 🚀 Iowa Local Data - Quick Reference Card

## Start Server
```powershell
python main.py
```

## Open Browser
```
http://localhost:8000/static/index.html
```

## Available Layers (7 Total)

### 🌾 LULC
- `Iowa CDL` - Crop types
- `Iowa NLCD` - Land cover

### 🌿 Vegetation  
- `Iowa NDVI` - Plant health

### 🌦️ Climate
- `Iowa Rainfall` - Precipitation
- `Iowa Max Temp` - Summer temps
- `Iowa ET` - Evapotranspiration

### 🌱 Soil
- `Iowa Soil Moisture` - SMAP data

## Map Controls

| Action | Result |
|--------|--------|
| ☑️ Check layer | Enable layer |
| ℹ️ Info button | View metadata |
| 🗺️ Click map | Get data values |
| 📍 Zoom to Iowa | Center on Iowa |
| 📊 View Stats | See statistics |

## API Quick Reference

```
/api/local-data/datasets           # List all
/api/local-data/info/{id}          # Metadata
/api/local-data/tiles/{id}/{z}/{x}/{y}.png  # Tiles
/api/local-data/point-value/{id}?lat=41&lon=-93  # Value
/api/local-data/stats/{id}         # Statistics
```

## Dataset IDs
```
iowa_cdl          iowa_rainfall
iowa_nlcd         iowa_tmax
iowa_ndvi         iowa_et
iowa_soil_moisture
```

## Example Queries

### Python
```python
import requests
r = requests.get('http://localhost:8000/api/local-data/datasets')
print(r.json())
```

### JavaScript
```javascript
fetch('/api/local-data/info/iowa_cdl')
  .then(r => r.json())
  .then(data => console.log(data));
```

### cURL
```bash
curl http://localhost:8000/api/local-data/iowa-bounds
```

## Tips

✅ **Enable multiple layers** for comparison  
✅ **Click map** for instant values  
✅ **No internet needed** - all local  
✅ **Data cached** after first load  

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No layers showing | Zoom to Iowa (📍 button) |
| Slow loading | First load takes 2-3 sec (normal) |
| API error | Check server running on port 8000 |
| No data files | Verify DATA folder exists |

## Color Schemes

- **NDVI**: 🔴 Red → 🟡 Yellow → 🟢 Green
- **Climate**: 🔵 Blue → 🔴 Red
- **LULC**: 🎨 Categorical colors
- **Other**: ⚫ Grayscale

## Coverage

📍 **State**: Iowa  
📏 **Bounds**: -96.64°W to -90.12°W, 40.32°N to 43.58°N  
🎯 **Center**: 41.94°N, -93.39°W  
🔍 **Best Zoom**: 7-12  

## File Locations

```
DATA/              # GeoTIFF files
local_data_api.py  # Backend
static/
  iowa-local-layers.js   # Frontend
  iowa-local-layers.css  # Styles
```

## Documentation

📄 **Full Guide**: `IOWA_LOCAL_DATA_GUIDE.md`  
📝 **Summary**: `IOWA_LOCAL_DATA_SUMMARY.md`  
🧪 **Test**: `test_iowa_local_data.py`  

---

**Need Help?** Check the full documentation or run the test script!
