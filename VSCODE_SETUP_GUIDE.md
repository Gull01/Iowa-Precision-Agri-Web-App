# VS Code Setup Guide

## Complete Step-by-Step Guide

---

## Step 1: Prepare Your Project Folder

### Files to Share:
```
WEB/
├─ main.py
├─ local_data_api.py
├─ gemini_ai.py
├─ config.py
├─ database.py
├─ models.py
├─ schemas.py
├─ requirements.txt  ➜ Important!
├─ .env              ➜ Important! (Contains API keys)
├─ DATA/             ➜ All 7 GeoTIFF files
└─ static/
    ├─ index.html
    ├─ app.js
    ├─ iowa-local-layers.js
    ├─ ai-insights.js
    ├─ ai-insights.css
    └─ styles.css
```

### Double-Check These Files:
✅ `.env` file exists (contains API keys)  
✅ `requirements.txt` exists  
✅ `DATA/` folder is complete (7 GeoTIFF files)  
✅ `static/` folder is complete (all HTML/JS/CSS files)

---

## Step 2: Share Your Project

**Option A: USB Drive**
- Copy entire `WEB` folder to USB
- Give to friend

**Option B: Google Drive / OneDrive**
- Zip the `WEB` folder
- Upload and share link

**Option C: GitHub**
```bash
git add .
git commit -m "Complete Iowa AI app"
git push
```

---

## Step 3: Setup on Friend's Laptop

### 3.1 - Copy WEB Folder
Example location:
```
D:\Projects\WEB\
```

### 3.2 - Open VS Code
1. Open VS Code
2. `File ➜ Open Folder`
3. Select WEB folder

### 3.3 - Open Terminal
In VS Code:
- `Terminal ➜ New Terminal` (or `Ctrl + ~`)
- PowerShell terminal will open

### 3.4 - Create Virtual Environment
Type in terminal:
```powershell
python -m venv .venv
```
*Wait 10-20 seconds*

### 3.5 - Activate Virtual Environment
```powershell
.venv\Scripts\activate
```

**Success sign:** You'll see `(.venv)` in terminal:
```
(.venv) PS D:\Projects\WEB>
```

### 3.6 - Install Requirements
```powershell
pip install -r requirements.txt
```

*Wait 2-3 minutes*

**Packages that will install:**
- fastapi
- uvicorn
- sqlalchemy
- google-generativeai
- gdal (this is slower)
- rasterio
- numpy
- shapely
- etc...

### 3.7 - Start Server
```powershell
python main.py
```

**Success messages you'll see:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3.8 - Open Browser
Navigate to:
```
http://localhost:8000/static/index.html
```

### 3.9 - Hard Refresh (Important!)
In browser:
```
Ctrl + Shift + R
```
(Or `Ctrl + F5`)

---

## What You'll See

### Left Sidebar:
```
┌────────────────────────────────────┐
│ 🗺️ Iowa Local Datasets            │
├────────────────────────────────────┤
│ 📍                                 │
│ 🌾 Land Use / Land Cover           │
├────────────────────────────────────┤
│ 📍                                 │
│ 🛰️ Iowa CDL 2023                  │
│ 🛰️ Iowa NLCD 2021                 │
├────────────────────────────────────┤
│ 📍                                 │
│ 🌱 Vegetation Indices              │
│ 🛰️ Iowa NDVI 2023                 │
├────────────────────────────────────┤
│ 📍                                 │
│ 🌦️ Climate Data                   │
│ 🛰️ Iowa Rainfall 2023              │
│ 🛰️ Iowa Max Temperature 2023       │
├────────────────────────────────────┤
│ 📍                                 │
│ 🌍 Soil Data                       │
│ 🛰️ Iowa Soil Moisture 2023         │
│ 🛰️ Iowa ET 2023                    │
├────────────────────────────────────┤
│ [📊 Dataset Information]           │
└────────────────────────────────────┘
```

### Map Features:
- Iowa state boundary will be displayed
- CDL 2023 layer will be ON by default
- Click on map to get AI insights (right side panel)

---

## Troubleshooting

### Problem 1: `python: command not found`
**Solution:**
```powershell
python3 -m venv .venv
python3 main.py
```

### Problem 2: `.venv\Scripts\activate` not working
**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\activate
```

### Problem 3: `pip install` errors
**Solution:**
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Problem 4: Port 8000 already in use
**Solution:**
Stop previous server:
```
Ctrl + C
```
Then restart:
```powershell
python main.py
```

### Problem 5: Dataset Panel not showing
**Solution:**
1. Hard refresh browser: `Ctrl + Shift + R`
2. Open Developer Console: `F12`
3. Check Console tab for errors
4. Send screenshot if error occurs

### Problem 6: AI insights not working
**Solution:**
Check `.env` file has API key:
```
GEMINI_API_KEY=your_google_gemini_api_key_here
```

**Note:** Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey). Never commit real keys to GitHub.

### Problem 7: GDAL installation error
**Solution:**
```powershell
pip install gdal==3.4.3
```

If still fails:
```powershell
pip install --find-links=https://github.com/cgohlke/geospatial-wheels/releases/latest GDAL
```

---

## Testing Your Setup

### Test 1: Is Server Running?
Terminal should show:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Test 2: Does Homepage Load?
Navigate to:
```
http://localhost:8000/static/index.html
```

### Test 3: Is Dataset Panel Visible?
Check left sidebar for "🗺️ Iowa Local Datasets" section.

### Test 4: Does AI Work?
1. Click anywhere on map (inside Iowa)
2. Wait 5-10 seconds
3. Right side panel should show AI recommendations

### Test 5: Check Console
Press `F12` ➜ Console tab should show:
```
✅ Iowa boundary loaded
✅ Iowa layers sidebar panel created
```

---

## Quick Commands Reference

### Start Server:
```powershell
cd D:\Projects\WEB
.venv\Scripts\activate
python main.py
```

### Stop Server:
```
Ctrl + C
```

### Update Packages:
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Deactivate Virtual Environment:
```powershell
deactivate
```

---

## Pro Tips

1. **Always activate virtual environment** before running server
2. **Hard refresh** (Ctrl+Shift+R) if UI doesn't update
3. **Check Console** (F12) if something doesn't work
4. **Keep server terminal running** while using app
5. **Never delete .env file** (it contains API keys)

---

## Success Checklist

✅ Virtual environment created  
✅ Requirements installed  
✅ Server running (port 8000)  
✅ Map visible in browser  
✅ Dataset panel showing on left  
✅ Layer checkboxes working  
✅ AI insights appear on map click  
✅ Export button functional  

**If all ✅, you're ready to go! 🎉**

---

## Additional Resources

- **Python Installation**: [python.org](https://www.python.org)
- **VS Code Download**: [code.visualstudio.com](https://code.visualstudio.com)
- **Google AI Studio**: [aistudio.google.com](https://aistudio.google.com/app/apikey)
- **FastAPI Docs**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)

---

**Questions? Problems? Errors? Share screenshots or error messages!**
