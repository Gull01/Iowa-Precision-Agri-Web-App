# 🌾 Iowa Precision Agriculture - Setup Instructions

## 📦 What You Received

This is a complete precision agriculture web application with AI-powered insights for Iowa.

## ✅ Prerequisites

- Python 3.8 or higher
- No API keys needed - everything is pre-configured!

## 🚀 Quick Start (5 minutes)

### Step 1: Extract the Files
Unzip the `WEB` folder to any location on your computer.

### Step 2: Open Terminal/Command Prompt
Navigate to the WEB folder:
```bash
cd path/to/WEB
```

### Step 3: Create Virtual Environment
```bash
python -m venv .venv
```

### Step 4: Activate Virtual Environment

**Windows:**
```bash
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

### Step 5: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 6: Run the Application
```bash
python main.py
```

### Step 7: Open in Browser
Go to: **http://localhost:8000/static/index.html**

That's it! 🎉

---

## 🎯 Features Available

### 1. **Iowa Local Datasets** (Left Sidebar)
- 🌍 Land Use / Land Cover (CDL 2023, NLCD 2021)
- 🌱 Vegetation Indices (NDVI)
- 🌤️ Climate Data (Rainfall, Max Temperature, Evapotranspiration)
- 🏔️ Soil Data (Soil Moisture)

**How to use:**
- Toggle layers on/off using checkboxes
- Zoom into Iowa to see data clearly

### 2. **AI-Powered Insights** (Right Panel)
- Click anywhere on the Iowa map
- AI analyzes all 7 datasets at that location
- Get crop-specific recommendations
- Urban area detection (no farming advice for cities)

**What AI provides:**
- 🎯 Field Status
- 💡 Key Insights
- 🌱 Management Recommendations
- 💧 Water Management
- ⚡ Action Items
- 📈 Outlook

### 3. **Export & Refresh**
- Export AI insights as text file
- Refresh to analyze new location

---

## 🗺️ How to Use

1. **View the Map**
   - Map automatically loads Iowa
   - Red dashed line shows Iowa boundary

2. **Toggle Layers**
   - Check/uncheck layers in "Iowa Local Datasets" panel
   - CDL 2023 is on by default

3. **Get AI Insights**
   - Click any location in Iowa
   - Wait 2-3 seconds for AI analysis
   - Read recommendations in right panel

4. **Analyze Different Crops**
   - Green areas = Corn/Soybeans/Crops
   - Brown areas = Pasture/Grassland
   - Gray/Pink areas = Urban (AI won't suggest farming)

---

## 📁 Project Structure

```
WEB/
├── main.py                    # Backend server
├── config.py                  # Configuration (API key included)
├── database.py                # Database setup
├── models.py                  # Data models
├── schemas.py                 # API schemas
├── local_data_api.py          # Iowa data endpoints
├── gemini_ai.py               # AI integration
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (API key here)
├── DATA/                      # Iowa datasets (7 GeoTIFF files)
└── static/
    ├── index.html            # Main page
    ├── app.js                # Main JavaScript
    ├── iowa-local-layers.js  # Layer management
    ├── iowa-local-layers.css # Layer styling
    ├── ai-insights.js        # AI panel
    └── ai-insights.css       # AI panel styling
```

---

## 🔧 Adding Your Own Features

### Example 1: Add a New Layer

1. Add GeoTIFF file to `DATA/` folder
2. Update `local_data_api.py`:
```python
{
    "id": "my_new_layer",
    "name": "My New Layer",
    "category": "Custom",
    "file": "my_data.tif"
}
```

### Example 2: Customize AI Prompt

Edit `main.py` - function `build_iowa_location_prompt()` (line ~1170)

### Example 3: Change Map Style

Edit `static/app.js` - change the tile layer URL

---

## ❓ Troubleshooting

### Problem: "Module not found" error
**Solution:** Make sure virtual environment is activated and run:
```bash
pip install -r requirements.txt
```

### Problem: Port 8000 already in use
**Solution:** Change port in `main.py` (last line):
```python
uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
```

### Problem: AI not responding
**Solution:** 
1. Check internet connection (AI requires internet)
2. Verify API key is in `.env` file
3. Check terminal for error messages

### Problem: No data showing on map
**Solution:**
1. Make sure you're zoomed into Iowa
2. Check that DATA/ folder contains GeoTIFF files
3. Toggle layers on/off in sidebar

### Problem: Datasets panel not showing
**Solution:** 
1. Hard refresh browser (Ctrl+Shift+R)
2. Clear browser cache
3. Check browser console for errors (F12)

---

## 🔑 API Key Information

**Good News:** API key is already configured in the `.env` file!

You don't need to:
- Sign up for Google Gemini
- Generate your own API key
- Modify any configuration

**The AI will work immediately after setup!**

---

## 📊 Dataset Information

All datasets are pre-downloaded and stored locally in the `DATA/` folder:

1. **Iowa_CDL_2023.tif** - Cropland Data Layer (30m resolution)
2. **Iowa_NLCD_2021.tif** - National Land Cover Database (30m)
3. **Iowa_NDVI_2023.tif** - Vegetation health index (30m)
4. **Iowa_GridMET_Rainfall_2023.tif** - Annual rainfall (4km)
5. **Iowa_GridMET_Tmax_2023.tif** - Maximum temperature (4km)
6. **Iowa_SMAP_Soil_Moisture_2023.tif** - Soil moisture (10km)
7. **Iowa_Landsat_ET_2023.tif** - Evapotranspiration (30m)

**Total Size:** ~500 MB

---

## 💻 System Requirements

- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 1GB free space
- **Browser:** Chrome, Firefox, Edge (latest versions)
- **Internet:** Required for AI insights, not for viewing datasets

---

## 🤝 Contributing

Want to improve the system? Here's what you can do:

1. **Add More Datasets**
   - Download GeoTIFF files for Iowa
   - Place in DATA/ folder
   - Update `local_data_api.py`

2. **Improve AI Prompts**
   - Edit `build_iowa_location_prompt()` in `main.py`
   - Test with different locations

3. **Enhance UI**
   - Modify `static/index.html`
   - Update CSS in `static/*.css`
   - Add features in `static/*.js`

4. **Add New Features**
   - Weather forecasts
   - Soil analysis tools
   - Crop yield predictions
   - Export to PDF/Excel

---

## 📞 Support

If you encounter any issues:

1. Check the terminal/console for error messages
2. Verify all files are present in DATA/ folder
3. Make sure Python 3.8+ is installed
4. Ensure virtual environment is activated

---

## 🎓 Learning Resources

- **FastAPI:** https://fastapi.tiangolo.com/
- **Leaflet Maps:** https://leafletjs.com/
- **Google Gemini AI:** https://ai.google.dev/
- **GDAL (Geospatial):** https://gdal.org/

---

## 📝 License

This is an educational/research project. Feel free to modify and extend it!

---

## 🎉 You're All Set!

Run `python main.py` and start exploring Iowa's agricultural data with AI insights!

**Happy Farming! 🚜🌾**
