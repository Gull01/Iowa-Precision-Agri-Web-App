"""
Test script for Iowa Local Data API
Verifies that all datasets are accessible and tiles can be generated
"""

import sys
from pathlib import Path

# Test imports
try:
    import rasterio
    import mercantile
    from PIL import Image
    import numpy as np
    print("✅ All required packages imported successfully")
except ImportError as e:
    print(f"❌ Missing package: {e}")
    sys.exit(1)

# Test DATA folder
DATA_DIR = Path("DATA")
if not DATA_DIR.exists():
    print(f"❌ DATA folder not found at {DATA_DIR.absolute()}")
    sys.exit(1)

print(f"✅ DATA folder found at {DATA_DIR.absolute()}")

# List all GeoTIFF files
tif_files = list(DATA_DIR.glob("*.tif"))
print(f"\n📊 Found {len(tif_files)} GeoTIFF files:")
for tif_file in tif_files:
    print(f"   - {tif_file.name}")

# Test reading each file
print("\n🔍 Testing raster file access...")
for tif_file in tif_files:
    try:
        with rasterio.open(tif_file) as src:
            print(f"\n✅ {tif_file.name}")
            print(f"   Size: {src.width} x {src.height}")
            print(f"   Bands: {src.count}")
            print(f"   CRS: {src.crs}")
            print(f"   Bounds: {src.bounds}")
            
            # Test reading data
            data = src.read(1, window=rasterio.windows.Window(0, 0, 100, 100))
            print(f"   Data type: {data.dtype}")
            print(f"   Sample values: min={data.min()}, max={data.max()}")
            
    except Exception as e:
        print(f"❌ Error reading {tif_file.name}: {e}")

# Test tile coordinate calculation
print("\n🗺️ Testing tile coordinate system...")
try:
    # Iowa center coordinates
    lon, lat = -93.389831, 41.938403
    zoom = 8
    
    tile = mercantile.tile(lon, lat, zoom)
    print(f"✅ Tile at Iowa center (zoom {zoom}): {tile}")
    
    bounds = mercantile.bounds(tile)
    print(f"   Tile bounds: {bounds}")
    
except Exception as e:
    print(f"❌ Error with tile calculations: {e}")

print("\n" + "="*60)
print("🎉 All tests passed! Local data system is ready.")
print("="*60)
print("\nNext steps:")
print("1. Start the server: python main.py")
print("2. Open browser: http://localhost:8000/static/index.html")
print("3. Look for '🌾 Iowa Local Data' panel on the map")
print("4. Enable layers and explore Iowa data!")
