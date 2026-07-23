# 🗺️ Iowa Local Data System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     🌐 Web Browser                               │
│  http://localhost:8000/static/index.html                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              📱 Frontend (JavaScript + CSS)                      │
├─────────────────────────────────────────────────────────────────┤
│  • iowa-local-layers.js   ← Layer control & UI                  │
│  • iowa-local-layers.css  ← Styling                             │
│  • app.js                 ← Map initialization                  │
│  • index.html             ← Main interface                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ API Calls
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              🔧 Backend API (FastAPI)                            │
├─────────────────────────────────────────────────────────────────┤
│  local_data_api.py - Router with endpoints:                     │
│                                                                  │
│  GET /api/local-data/datasets                                   │
│  GET /api/local-data/info/{dataset_id}                          │
│  GET /api/local-data/tiles/{dataset_id}/{z}/{x}/{y}.png         │
│  GET /api/local-data/point-value/{dataset_id}                   │
│  GET /api/local-data/stats/{dataset_id}                         │
│  GET /api/local-data/iowa-bounds                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Read/Process
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              📂 Local Data Storage (DATA/)                       │
├─────────────────────────────────────────────────────────────────┤
│  🌾 LULC                    🌦️ Climate                          │
│  ├─ Iowa_CDL.tif            ├─ Iowa_Gridmet_Rainfall.tif        │
│  └─ Iowa_NLCD.tif           ├─ Iowa_Gridmet_Tmax_Summer.tif     │
│                             └─ Iowa_Gridmet_ET.tif              │
│  🌿 Vegetation              🌱 Soil                              │
│  └─ Iowa_Landsat_NDVI.tif   └─ Iowa_SMAP_SoilMoisture.tif      │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 Data Flow

```
User Action → Frontend → API → GeoTIFF → Processing → Response → Display
```

### Example: Enabling a Layer

```
1. User clicks checkbox ☑️
   ↓
2. JavaScript sends tile requests
   GET /api/local-data/tiles/iowa_cdl/{z}/{x}/{y}.png
   ↓
3. Backend API (local_data_api.py)
   - Reads Iowa_CDL.tif with rasterio
   - Extracts tile region
   - Applies colormap
   - Generates PNG
   ↓
4. Browser receives PNG tile
   ↓
5. Leaflet displays tile on map 🗺️
```

### Example: Clicking on Map

```
1. User clicks map at (lat, lon) 📍
   ↓
2. JavaScript sends requests for active layers
   GET /api/local-data/point-value/iowa_ndvi?lat=41.5&lon=-93.5
   GET /api/local-data/point-value/iowa_cdl?lat=41.5&lon=-93.5
   ↓
3. Backend reads values at coordinates
   ↓
4. Returns JSON with values
   { "value": 0.75, "unit": "NDVI" }
   ↓
5. JavaScript displays popup with data 💬
```

## 🔧 Technology Stack

### Backend
- **FastAPI** - Web framework
- **Rasterio** - GeoTIFF reading
- **Mercantile** - Tile coordinates
- **NumPy** - Data processing
- **Pillow** - Image generation

### Frontend
- **Leaflet** - Map library
- **JavaScript** - Interactivity
- **CSS** - Styling
- **HTML** - Structure

### Data Format
- **GeoTIFF** - Raster data storage
- **WGS84** - Coordinate system
- **PNG** - Tile format

## 🎨 Rendering Pipeline

```
GeoTIFF File
    ↓
Read with Rasterio
    ↓
Extract Tile Window (256x256)
    ↓
Apply Resampling (Bilinear)
    ↓
Apply Colormap
    ├─ NDVI: Red → Green
    ├─ Climate: Blue → Red
    └─ LULC: Categorical
    ↓
Generate RGBA Array
    ↓
Create PNG with Pillow
    ↓
Send to Browser
```

## 📁 Component Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                     IOWA LOCAL DATA SYSTEM                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │   Frontend    │  │    Backend    │  │     Data      │       │
│  │  (Browser)    │  │     (API)     │  │  (GeoTIFF)    │       │
│  └───────────────┘  └───────────────┘  └───────────────┘       │
│         │                   │                   │                │
│         │ HTTP Requests     │ File I/O          │                │
│         └──────────────────►└──────────────────►                │
│                                                                  │
│  Layer Control ──► Tile Requests ──► Raster Processing          │
│  Info Buttons  ──► Metadata API  ──► File Inspection            │
│  Map Clicks    ──► Point Query   ──► Spatial Lookup             │
│  Statistics    ──► Stats API     ──► Data Analysis              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Request Flow Examples

### 1. Loading a Layer
```
Browser: "Show me Iowa CDL"
   ↓
JavaScript: Generate tile URLs for viewport
   ↓
API: Read Iowa_CDL.tif, generate tiles
   ↓
Browser: Display tiles on map
   ↓
User: Sees crop types! 🌾
```

### 2. Getting Statistics
```
Browser: Click "📊 View Statistics"
   ↓
JavaScript: Fetch stats for all datasets
   ↓
API: Calculate min/max/mean/std for each
   ↓
Browser: Display in modal
   ↓
User: Sees data summary! 📈
```

### 3. Point Query
```
Browser: User clicks map at (41.5°N, 93.5°W)
   ↓
JavaScript: Request values from active layers
   ↓
API: Look up pixel values at coordinates
   ↓
Browser: Show popup with values
   ↓
User: Sees NDVI=0.75, Crop=Corn! 🌽
```

## 🎯 Key Features

### Offline Operation
- ✅ No internet required
- ✅ All data local
- ✅ No external dependencies
- ✅ Complete privacy

### Performance
- ⚡ On-demand tile generation
- 💾 Browser caching
- 🔄 Lazy loading
- 📊 Efficient data access

### Scalability
- 📈 Handles large rasters (24k × 12k pixels)
- 🗺️ Multiple zoom levels
- 🔀 Multiple simultaneous layers
- 🎨 Real-time colormap application

### User Experience
- 🖱️ Click for instant data values
- 🔍 Zoom controls
- 📋 Layer information
- 📊 Statistics dashboard

## 🔒 Security & Privacy

```
┌─────────────────────────────────────┐
│   Your Computer (Localhost)         │
├─────────────────────────────────────┤
│  ✅ All data stored locally          │
│  ✅ No external API calls            │
│  ✅ No data uploaded                 │
│  ✅ Complete user control            │
│  ✅ Works offline                    │
└─────────────────────────────────────┘
```

## 📏 Scale & Capacity

```
Data Volume
├─ Iowa CDL: 280 MB (24k × 12k)
├─ Iowa NLCD: 200 MB (24k × 12k)
├─ Iowa NDVI: 200 MB (24k × 12k)
├─ Climate Data: ~150 KB total
└─ Soil Moisture: 8 KB

Processing Speed
├─ First tile: 2-3 seconds
├─ Cached tile: <100ms
└─ Point query: <50ms

Coverage
├─ Geographic: Entire Iowa state
├─ Zoom levels: 7-18
└─ Resolution: 30m to 9km
```

## 🎓 Usage Patterns

### Research
```
Load NDVI + CDL → Analyze crop health by type
```

### Planning
```
Load NLCD + Rainfall → Land use and water availability
```

### Monitoring
```
Load Soil Moisture + ET → Irrigation needs
```

### Analysis
```
Load all layers → Comprehensive field assessment
```

---

**This system provides complete, offline access to Iowa agricultural and environmental data!** 🌾🗺️
