# Quick Checklist - Before Sharing

## Files to Share

### Core Files
- [ ] `main.py`
- [ ] `local_data_api.py`
- [ ] `gemini_ai.py`
- [ ] `config.py`
- [ ] `database.py`
- [ ] `models.py`
- [ ] `schemas.py`

### Configuration
- [ ] `requirements.txt` ← **MUST HAVE**
- [ ] `.env` ← **MUST HAVE** (API key)
- [ ] `.gitignore`

### Data Folder
- [ ] `DATA/iowa_cdl_2023.tif`
- [ ] `DATA/iowa_nlcd_2021.tif`
- [ ] `DATA/iowa_ndvi_2023.tif`
- [ ] `DATA/iowa_rainfall_2023.tif`
- [ ] `DATA/iowa_tmax_2023.tif`
- [ ] `DATA/iowa_soil_moisture_2023.tif`
- [ ] `DATA/iowa_et_2023.tif`

### Static Files
- [ ] `static/index.html`
- [ ] `static/styles.css`
- [ ] `static/app.js`
- [ ] `static/iowa-local-layers.js`
- [ ] `static/ai-insights.js`
- [ ] `static/ai-insights.css`

### Documentation
- [ ] `README.md`
- [ ] `VSCODE_SETUP_GUIDE.md` ← **Give this to friend**
- [ ] `SETUP_INSTRUCTIONS.md`
- [ ] `CHECK_PANEL.md`

---

## Double Check These

### 1. Check `.env` file exists:
```powershell
cat .env
```

Should show a placeholder value or an empty field, not a real API key.

### 2. Check `requirements.txt` exists:
```powershell
cat requirements.txt
```

Should have ~20-30 packages listed.

### 3. Check DATA folder size:
```powershell
Get-ChildItem -Path DATA -Recurse | Measure-Object -Property Length -Sum
```

Should be ~500MB to 1GB.

### 4. Verify all static files:
```powershell
Get-ChildItem -Path static -Name
```

Should show all HTML, JS, CSS files.

---

## How to Share

### Option 1: Zip the Folder
```powershell
# Right-click WEB folder → Send to → Compressed folder
# Or use this command:
Compress-Archive -Path "E:\work_projects\N-IGIS-WORK\WEB" -DestinationPath "E:\WEB_Complete.zip"
```

### Option 2: Copy to USB
```powershell
# Just copy entire WEB folder to USB drive
Copy-Item -Path "E:\work_projects\N-IGIS-WORK\WEB" -Destination "F:\" -Recurse
```

### Option 3: Google Drive
1. Right-click WEB folder → Send to → Compressed folder
2. Upload `WEB.zip` to Google Drive
3. Share link with friend

---

## What to Tell Your Friend

Send this message:

---

Hi,

I prepared a complete Iowa Agriculture AI app setup.

**Steps:**

1. Download or copy the WEB folder
2. Open VS Code
3. Open the WEB folder in VS Code
4. Follow the VSCODE_SETUP_GUIDE.md file

**Important:**
- Use your own API key in the local .env file
- Data files are included
- Run the setup commands listed above

**Time:** Total 5-10 minutes, depending on install speed

Questions can be sent anytime.

---

## Final Verification

Before sharing, run these:

### Test 1: Fresh Install
```powershell
# Create new test folder
mkdir E:\TEST_WEB
Copy-Item -Path "E:\work_projects\N-IGIS-WORK\WEB\*" -Destination "E:\TEST_WEB\" -Recurse

# Try setup
cd E:\TEST_WEB
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Test 2: Check .env
```powershell
cat .env | Select-String "GEMINI"
```

Should show your local secret value, not a public example.

### Test 3: Check DATA folder
```powershell
Get-ChildItem DATA
```

Should show 7 .tif files.

---

## Ready to Share When

- Tested on your PC
- `.env` file is present with your own secret values
- `requirements.txt` is present
- All 7 DATA files are present
- All static files are present
- VSCODE_SETUP_GUIDE.md is present
- Folder size is about 500MB to 1GB

If everything above is ready, share it.
