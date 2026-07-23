# 🔍 Dataset Panel Troubleshooting Guide

If the Iowa Datasets Panel is not showing, follow these steps:

## Step 1: Hard Refresh Browser
Press **Ctrl + Shift + R** (or **Ctrl + F5**) to clear cache and reload.

## Step 2: Check Browser Console
1. Press **F12** to open Developer Tools
2. Click the **Console** tab
3. Look for these messages:

**✅ GOOD - Panel should be working:**
```
✅ Iowa boundary loaded
✅ Iowa layers sidebar panel created
```

**❌ BAD - Panel won't show:**
```
⚠️ Iowa layers panel container not found in sidebar
```

## Step 3: Check Network Tab
1. In Developer Tools, click **Network** tab
2. Reload page (F5)
3. Check if these files load (Status should be 200):
   - `index.html`
   - `iowa-local-layers.js`
   - `ai-insights.js`

If you see **304 Not Modified** → Do hard refresh again!

## Step 4: Manual Check in Console
Open browser console (F12) and type:

```javascript
document.getElementById('iowaLayersPanel')
```

**✅ Should return:** `<div id="iowaLayersPanel">...</div>` with checkboxes inside

**❌ If null:** The HTML file wasn't updated. Copy the WEB folder again.

## Step 5: Force Reload JavaScript
In console, type:

```javascript
location.reload(true)
```

This forces a complete reload ignoring cache.

## Step 6: Check File Dates
The updated files should have date **November 24, 2025**:
- `static/index.html` (should contain `iowaLayersPanel`)
- `static/iowa-local-layers.js` (should contain `createIowaSidebarPanel`)

Right-click files → Properties → Modified Date

## Step 7: Clear All Browser Data
If nothing works:
1. Press **Ctrl + Shift + Delete**
2. Select **"Cached images and files"**
3. Click **Clear data**
4. Restart browser
5. Go to `http://localhost:8000/static/index.html`

## Step 8: Try Different Browser
Test in:
- Chrome / Edge
- Firefox
- Different incognito/private window

## Step 9: Check Server Logs
In the terminal where `python main.py` is running, you should see:
```
INFO:     127.0.0.1:XXXXX - "GET /static/index.html HTTP/1.1" 200 OK
INFO:     127.0.0.1:XXXXX - "GET /static/iowa-local-layers.js HTTP/1.1" 200 OK
```

Status **200** = Good  
Status **304** = Cached (need hard refresh)  
Status **404** = File not found (wrong path)

## What the Panel Should Look Like

```
┌─────────────────────────────────┐
│ 🗺️ Iowa Local Datasets          │
│ Toggle layers on the map...     │
│                                 │
│ 🌍 Land Use / Land Cover        │
│ ☑ Iowa CDL 2023                 │
│ ☐ Iowa NLCD 2021                │
│                                 │
│ 🌱 Vegetation Indices           │
│ ☐ Iowa NDVI 2023                │
│                                 │
│ 🌤️ Climate Data                 │
│ ☐ Iowa Rainfall 2023            │
│ ☐ Iowa Max Temperature 2023     │
│                                 │
│ 🏔️ Soil Data                    │
│ ☐ Iowa Soil Moisture 2023       │
│ ☐ Iowa ET 2023                  │
│                                 │
│ [ℹ️ Dataset Information]        │
└─────────────────────────────────┘
```

## Still Not Working?

Send screenshot of:
1. Browser console (F12 → Console tab)
2. Network tab showing loaded files
3. The actual sidebar (what they see)

This will help identify the exact issue!
