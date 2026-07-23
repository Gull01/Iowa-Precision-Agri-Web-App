# 🚀 VS Code Setup Guide (Urdu/English)

## ✅ Complete Step-by-Step Guide for Your Friend

---

## 📦 **Step 1: Aap (Office PC) - Folder Ready Karo**

### Files to Share:
```
WEB/
├── main.py
├── local_data_api.py
├── gemini_ai.py
├── config.py
├── database.py
├── models.py
├── schemas.py
├── requirements.txt    ← Important!
├── .env               ← Important! (API key hai isme)
├── DATA/              ← All 7 GeoTIFF files
└── static/
    ├── index.html
    ├── app.js
    ├── iowa-local-layers.js
    ├── ai-insights.js
    ├── ai-insights.css
    └── styles.css
```

### Double-Check These Files:
✅ `.env` file exists (API key hai isme)  
✅ `requirements.txt` exists  
✅ `DATA/` folder complete hai (7 GeoTIFF files)  
✅ `static/` folder complete hai (all HTML/JS/CSS)

---

## 📤 **Step 2: Share Karo**

**Option A: USB Drive**
- Copy entire `WEB` folder to USB
- Friend ko de do

**Option B: Google Drive / OneDrive**
- Zip the `WEB` folder
- Upload and share link

**Option C: GitHub (if you use it)**
```bash
git add .
git commit -m "Complete Iowa AI app"
git push
```

---

## 📥 **Step 3: Friend (Laptop) - Setup Kare**

### 3.1 - WEB Folder Ko Copy Karo
Example location:
```
D:\Projects\WEB\
```

### 3.2 - VS Code Open Karo
1. VS Code open karo
2. `File → Open Folder`
3. WEB folder select karo

### 3.3 - Terminal Open Karo
VS Code me:
- `Terminal → New Terminal` (ya `Ctrl + ~`)
- PowerShell terminal khulega

### 3.4 - Virtual Environment Banao
Terminal me type karo:
```powershell
python -m venv .venv
```
*Wait karo... 10-20 seconds lagenge*

### 3.5 - Virtual Environment Activate Karo
```powershell
.venv\Scripts\activate
```

**Success sign:** Terminal me `(.venv)` dikhai dega:
```
(.venv) PS D:\Projects\WEB>
```

### 3.6 - Requirements Install Karo
```powershell
pip install -r requirements.txt
```

*Wait karo... 2-3 minutes lagenge (ye sabse zyada time leta hai)*

**Packages install honge:**
- fastapi
- uvicorn
- sqlalchemy
- google-generativeai
- gdal (ye thoda slow hai)
- rasterio
- numpy
- shapely
- etc...

### 3.7 - Server Start Karo
```powershell
python main.py
```

**Success messages dikhenge:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3.8 - Browser Open Karo
Browser me jao:
```
http://localhost:8000/static/index.html
```

### 3.9 - Hard Refresh Karo (Important!)
Browser me:
```
Ctrl + Shift + R
```
(Ya `Ctrl + F5`)

---

## ✅ **Kya Dikhega (What to Expect)**

### Left Sidebar:
```
┌────────────────────────────────┐
│ 🗺️ Iowa Local Datasets         │
│                                │
│ 🌍 Land Use / Land Cover       │
│ ☑ Iowa CDL 2023                │
│ ☐ Iowa NLCD 2021               │
│                                │
│ 🌱 Vegetation Indices          │
│ ☐ Iowa NDVI 2023               │
│                                │
│ 🌤️ Climate Data                │
│ ☐ Iowa Rainfall 2023           │
│ ☐ Iowa Max Temperature 2023    │
│                                │
│ 🏔️ Soil Data                   │
│ ☐ Iowa Soil Moisture 2023      │
│ ☐ Iowa ET 2023                 │
│                                │
│ [ℹ️ Dataset Information]       │
└────────────────────────────────┘
```

### Map:
- Iowa state boundary dikhega
- CDL 2023 layer by default ON hoga
- Click karoge toh AI insights dikhenge (right side panel)

---

## 🔧 **Agar Kuch Problem Ho**

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

### Problem 3: `pip install` me error
**Solution:**
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Problem 4: Port 8000 already in use
**Solution:**
Terminal me previous server ko band karo:
```
Ctrl + C
```
Phir dobara:
```powershell
python main.py
```

### Problem 5: Dataset Panel nahi dikh raha
**Solution:**
1. Browser me hard refresh: `Ctrl + Shift + R`
2. F12 press karo → Console check karo
3. Error dikhe toh screenshot bhejo

### Problem 6: AI insights not working
**Solution:**
Check `.env` file me API key hai ya nahi:
```
GEMINI_API_KEY=REMOVED_SECRET
```

### Problem 7: GDAL installation error
**Solution:**
```powershell
pip install gdal==3.4.3
```
Agar phir bhi error:
```powershell
pip install --find-links=https://github.com/cgohlke/geospatial-wheels/releases/latest GDAL
```

---

## 🎯 **Testing Kaise Karein**

### Test 1: Server Running?
Terminal me ye dikhna chahiye:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Test 2: Homepage Load?
Browser me:
```
http://localhost:8000/static/index.html
```

### Test 3: Datasets Panel Visible?
Left sidebar me "🗺️ Iowa Local Datasets" section dikhna chahiye.

### Test 4: AI Working?
1. Map pe kahi bhi click karo (Iowa ke andar)
2. Wait 5-10 seconds
3. Right side me AI panel khulega with recommendations

### Test 5: Console Check
F12 press karo → Console tab:
```
✅ Iowa boundary loaded
✅ Iowa layers sidebar panel created
```

---

## 📝 **Quick Commands Reference**

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

### Update Packages (agar kabhi zaroorat ho):
```powershell
pip install --upgrade -r requirements.txt
```

### Deactivate Virtual Environment:
```powershell
deactivate
```

---

## 🎉 **Success Checklist**

✅ Virtual environment ban gaya  
✅ Requirements install ho gaye  
✅ Server chal raha hai (port 8000)  
✅ Browser me map dikh raha hai  
✅ Dataset panel left side me hai  
✅ Checkboxes kaam kar rahe hain  
✅ Map pe click karne se AI insights aate hain  
✅ Export button kaam kar raha hai  

**Agar sab ✅ hai, toh setup complete! 🎊**

---

## 💡 **Pro Tips**

1. **Virtual environment hamesha activate karo** before running server
2. **Hard refresh** (Ctrl+Shift+R) karo agar UI update nahi dikhe
3. **Console** (F12) check karo agar kuch kaam na kare
4. **Server terminal** ko band mat karo jab tak app use kar rahe ho
5. **.env file** ko kabhi delete mat karna (API key hai usme)

---

## 📞 **Still Problems?**

Agar kuch bhi problem ho, in cheezen check karo:

1. ✅ Python installed hai? (`python --version`)
2. ✅ WEB folder complete copy hua?
3. ✅ `.env` file hai folder me?
4. ✅ `DATA/` folder empty toh nahi?
5. ✅ Virtual environment activated hai?
6. ✅ Server running hai? (terminal me check karo)
7. ✅ Browser URL sahi hai? (`localhost:8000`)
8. ✅ Hard refresh kiya? (Ctrl+Shift+R)

Screenshot bhejo:
- Terminal window (where python main.py is running)
- Browser console (F12 → Console tab)
- Left sidebar (kya dikh raha hai)

---

## 🔄 **Daily Usage (Roz Kaise Chalana Hai)**

### Morning (Jab kaam shuru karo):
```powershell
# 1. VS Code open karo
# 2. Terminal open karo
# 3. Commands:
cd D:\Projects\WEB
.venv\Scripts\activate
python main.py

# 4. Browser: http://localhost:8000/static/index.html
```

### Evening (Jab kaam khatam):
```
# Server stop karo:
Ctrl + C

# VS Code close kar do
```

---

## 🚀 **Ready to Go!**

Bas itna hi! Agar ye sab steps follow kare, toh application 100% chalegi.

**No API key setup needed - everything pre-configured! 🎉**

Questions? Problems? Screenshots bhejo!
