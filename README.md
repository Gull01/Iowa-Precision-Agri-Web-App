# 🌾 Iowa Precision Agriculture WebGIS

AI-powered precision agriculture platform for Iowa with local datasets and intelligent insights.

## ⚡ Quick Start

**No API key setup needed - everything is pre-configured!**

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate it
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python main.py

# 5. Open browser
# http://localhost:8000/static/index.html
```

**That's it! The app is ready to use.** 🎉

---

## 🎯 Features

✅ **7 Iowa Datasets** - CDL, NLCD, NDVI, Rainfall, Temperature, Soil Moisture, ET  
✅ **AI-Powered Insights** - Click anywhere to get crop recommendations  
✅ **Urban Detection** - Smart detection of non-agricultural areas  
✅ **Interactive Map** - Toggle layers, zoom, analyze  
✅ **Export Reports** - Save AI insights as text files  
✅ **No Internet Required** - All data stored locally (except AI calls)

---

## 📖 Documentation

- **📋 SETUP_INSTRUCTIONS.md** - Detailed setup guide for your team
- **🔐 SECURITY_GUIDE.md** - Security and API key management
- **🤖 AI_INSIGHTS_GUIDE.md** - How AI insights work
- **🗺️ IOWA_LOCAL_DATA_GUIDE.md** - Dataset information
- **⚡ QUICKSTART.md** - Quick reference

---

## 🗺️ How to Use

1. **Toggle Layers** - Check/uncheck datasets in left sidebar
2. **Click Map** - Click anywhere in Iowa to get AI analysis
3. **Read Insights** - AI provides field status, recommendations, action items
4. **Export Data** - Save insights for later reference

---

## 🛠️ Technology Stack

- **Backend:** FastAPI + SQLAlchemy + GDAL
- **Frontend:** Vanilla JavaScript + Leaflet Maps
- **AI:** Google Gemini AI 2.0 Flash
- **Data:** Local GeoTIFF files (500MB)

---

## 📂 Project Structure

```
WEB/
├── main.py                    # FastAPI server
├── local_data_api.py          # Dataset endpoints
├── gemini_ai.py               # AI integration
├── DATA/                      # 7 Iowa GeoTIFF files
└── static/
    ├── index.html            # Main UI
    ├── iowa-local-layers.js  # Layer management
    └── ai-insights.js        # AI panel
```

---

## 🤝 For Your Teammate

**Just share the entire WEB folder!**

They don't need to:
- ❌ Get their own API key
- ❌ Configure anything
- ❌ Download datasets

They just need to:
1. ✅ Run the 5 commands above
2. ✅ Open the browser
3. ✅ Start using it!

**See SETUP_INSTRUCTIONS.md for detailed guide.**

---

## 🔧 Customization

Want to add features? Check these files:

- **Add datasets:** Update `local_data_api.py`
- **Customize AI:** Edit `build_iowa_location_prompt()` in `main.py`
- **Change UI:** Modify `static/*.html` and `static/*.css`
- **Add features:** Extend `static/*.js`

---

## 📊 Datasets Included

1. Iowa CDL 2023 (Cropland Data Layer)
2. Iowa NLCD 2021 (Land Cover)
3. Iowa NDVI 2023 (Vegetation Index)
4. Iowa Rainfall 2023 (GridMET)
5. Iowa Max Temperature 2023 (GridMET)
6. Iowa Soil Moisture 2023 (SMAP)
7. Iowa Evapotranspiration 2023 (Landsat)

---

## ⚠️ Requirements

- Python 3.8+
- 1GB disk space
- Internet (for AI only)

---

## 📞 Troubleshooting

**Port already in use?**
Change port in `main.py` (last line): `port=8001`

**AI not working?**
Check internet connection and `.env` file

**Datasets not showing?**
Hard refresh browser (Ctrl+Shift+R)

**More help?**
See SETUP_INSTRUCTIONS.md

---

## 📝 License

Educational/Research Project - Free to use and modify!

---

**Ready to explore Iowa agriculture with AI? Run `python main.py` and go! 🚜🌾**

Copy `.env.example` to `.env` and configure your settings:

```powershell
copy .env.example .env
```

Edit `.env` and add your API keys (optional but recommended):
- `OPENWEATHER_API_KEY`: Get from https://openweathermap.org/api
- `SENTINEL_HUB_CLIENT_ID`: Get from https://www.sentinel-hub.com/

## 🎯 Quick Start

### Start the Application

```powershell
python main.py
```

Or using uvicorn directly:

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Access the Application

- **Web Interface**: http://localhost:8000/static/index.html
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Root Endpoint**: http://localhost:8000/

## 📁 Project Structure

```
d:\WEB\
├── main.py              # FastAPI application and endpoints
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic schemas for validation
├── database.py          # Database configuration
├── config.py            # Application settings
├── gis_utils.py         # GIS and spatial analysis utilities
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore file
└── static/             # Frontend files
    ├── index.html      # Main web interface
    └── app.js          # JavaScript application logic
```

## 🔌 API Endpoints

### Farms
- `POST /api/farms/` - Create a new farm
- `GET /api/farms/` - List all farms
- `GET /api/farms/{id}` - Get farm details
- `PUT /api/farms/{id}` - Update farm
- `DELETE /api/farms/{id}` - Delete farm

### Fields
- `POST /api/fields/` - Create a new field
- `GET /api/fields/` - List all fields
- `GET /api/fields/{id}` - Get field details
- `PUT /api/fields/{id}` - Update field
- `DELETE /api/fields/{id}` - Delete field

### Sensors
- `POST /api/sensors/` - Register a new sensor
- `GET /api/sensors/` - List sensors
- `POST /api/sensors/readings/` - Add sensor reading
- `GET /api/sensors/{id}/readings/` - Get sensor readings

### Crop Monitoring
- `POST /api/crop-monitoring/` - Add monitoring data
- `GET /api/crop-monitoring/` - List monitoring records
- `POST /api/crop-monitoring/calculate-ndvi/` - Calculate NDVI

### Analysis
- `GET /api/analysis/field/{id}` - Get comprehensive field analysis
- `GET /api/statistics/dashboard` - Get dashboard statistics

### Weather (FREE APIs - No Keys Required!)
- `GET /api/weather/{farm_id}` - Get current weather (Open-Meteo)
- `GET /api/weather/{farm_id}/forecast?days=7` - Get 7-day forecast with agricultural insights
- `GET /api/weather/{farm_id}/climate-history?days_back=30` - Get historical climate data (NASA POWER)

### Agromonitoring (Satellite NDVI Monitoring)
- `POST /api/agromonitoring/register-field/{field_id}` - Register field for satellite monitoring
- `GET /api/agromonitoring/satellite-ndvi/{field_id}?days_back=30` - Get real satellite NDVI data
- `GET /api/agromonitoring/polygons` - List all registered fields
- `DELETE /api/agromonitoring/unregister-field/{field_id}` - Unregister field

## 🧮 GIS Utilities

### Vegetation Indices
- **NDVI** (Normalized Difference Vegetation Index): `(NIR - Red) / (NIR + Red)`
- **EVI** (Enhanced Vegetation Index): More accurate in high biomass areas
- **SAVI** (Soil Adjusted Vegetation Index): Corrects for soil brightness

### Health Classification
- **Excellent**: NDVI ≥ 0.6
- **Good**: NDVI ≥ 0.4
- **Fair**: NDVI ≥ 0.2
- **Poor**: NDVI < 0.2

### Spatial Operations
- Polygon area calculation (hectares)
- Point-in-polygon tests
- Field centroid calculation
- Sensor data interpolation

## 💡 Usage Examples

### Creating a Farm via API

```python
import requests

farm_data = {
    "name": "Green Valley Farm",
    "owner": "John Doe",
    "location": "Iowa, USA",
    "latitude": 41.8781,
    "longitude": -93.0977,
    "total_area": 150.5
}

response = requests.post("http://localhost:8000/api/farms/", json=farm_data)
farm = response.json()
print(f"Created farm with ID: {farm['id']}")
```

### Creating a Field

```python
field_data = {
    "farm_id": 1,
    "name": "North Field",
    "crop_type": "Corn",
    "area": 25.3,
    "soil_type": "Loamy",
    "soil_ph": 6.5,
    "soil_nitrogen": 30,
    "soil_phosphorus": 15,
    "soil_potassium": 150
}

response = requests.post("http://localhost:8000/api/fields/", json=field_data)
field = response.json()
```

### Calculating NDVI

```python
# Calculate NDVI from satellite band values
response = requests.post(
    "http://localhost:8000/api/crop-monitoring/calculate-ndvi/",
    params={"nir": 0.45, "red": 0.15}
)
result = response.json()
print(f"NDVI: {result['ndvi']}, Health: {result['health_status']}")
```

### Getting Field Analysis

```python
response = requests.get("http://localhost:8000/api/analysis/field/1")
analysis = response.json()
print(f"Field Health: {analysis['health_status']}")
print(f"Recommendations: {analysis['recommendations']}")
```

## 🗺️ Frontend Usage

1. **Open the web interface** at http://localhost:8000/static/index.html
2. **Create a farm** using the "Add New Farm" button
3. **Add fields** to the farm with soil and crop information
4. **Draw field boundaries** on the map using the drawing tools
5. **View analytics** by clicking on fields in the list
6. **Monitor health** through the color-coded field boundaries

## 🔐 Security Notes

- Change `SECRET_KEY` in `.env` for production
- Use HTTPS in production environments
- Configure proper CORS origins
- Implement authentication for production use
- Secure API keys and credentials

## 📊 Database Schema

### Tables
- **farms**: Farm properties and locations
- **fields**: Agricultural fields with soil data
- **sensors**: IoT sensor deployments
- **sensor_readings**: Time-series sensor data
- **crop_monitoring**: Vegetation indices and health data
- **weather_data**: Historical weather records

## 🌐 API Integration Examples

### OpenWeatherMap Integration
The application can fetch real-time weather data when configured with an API key.

### Sentinel Hub (Optional)
For satellite imagery and advanced NDVI calculations, configure Sentinel Hub credentials.

## 🐛 Troubleshooting

### Port Already in Use
```powershell
# Kill process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Import Errors
```powershell
pip install --upgrade -r requirements.txt
```

### Database Errors
```powershell
# Delete and recreate database
del precision_agriculture.db
python main.py
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Leaflet.js](https://leafletjs.com/)
- [NDVI Explained](https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index)
- [Precision Agriculture](https://en.wikipedia.org/wiki/Precision_agriculture)

## 🤝 Contributing

This is a professional template for precision agriculture applications. Feel free to extend it with:
- Machine learning models for yield prediction
- Advanced satellite imagery processing
- Real-time sensor integration
- Mobile app integration
- Multi-user authentication
- Advanced reporting and analytics

## 📝 License

This project is provided as-is for educational and commercial use.

## 👨‍💻 Author

Created with FastAPI, Leaflet.js, and modern web technologies for precision agriculture applications.

---

**Happy Farming! 🌾🚜**
