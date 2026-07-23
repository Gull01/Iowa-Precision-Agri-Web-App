# 🚀 Quick Setup Guide - Precision Agriculture WebGIS

## Step-by-Step Installation

### 1. Open PowerShell in the project directory
```powershell
cd d:\WEB
```

### 2. Run the startup script
```powershell
.\start.ps1
```

This will automatically:
- Create a virtual environment
- Install all dependencies
- Start the FastAPI server

### 3. Access the Application

**Main Web Interface:**
- Open your browser: http://localhost:8000/static/index.html

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📝 First Steps

1. **Create Your First Farm**
   - Click "Add New Farm"
   - Enter farm details (name, owner, location)
   - Add GPS coordinates for mapping

2. **Add Fields to Your Farm**
   - Click "Add New Field"
   - Select the farm
   - Enter field details and soil properties
   - Draw field boundaries on the map

3. **Monitor Field Health**
   - Click on fields to view analysis
   - Get automated recommendations
   - Track NDVI and vegetation health

## 🧪 Test the API

Run the test script in a separate terminal:
```powershell
python test_api.py
```

## ⚙️ Optional: Configure API Keys

1. Copy `.env.example` to `.env`
2. Add your API keys:
   - OpenWeatherMap: https://openweathermap.org/api
   - Sentinel Hub: https://www.sentinel-hub.com/

## 📊 Features Overview

✅ Farm & Field Management
✅ Interactive Mapping with Leaflet.js
✅ NDVI Vegetation Index Calculation
✅ Soil Analysis & NPK Tracking
✅ Weather Integration
✅ Smart Agricultural Recommendations
✅ Sensor Data Management
✅ Real-time Dashboard Statistics

## 🔧 Troubleshooting

**If port 8000 is busy:**
```powershell
# Edit main.py and change port in last line:
uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
```

**If dependencies fail:**
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

## 📚 Next Steps

- Explore the API documentation
- Create multiple farms and fields
- Draw field boundaries on the map
- Add sensor data
- Generate field analysis reports

## 💡 Tips

- Use the drawing tools on the map to outline fields
- Click fields to see detailed analysis
- Monitor the dashboard for overview statistics
- API is fully RESTful - integrate with other systems

---

**Need Help?** Check README.md for detailed documentation.
