"""
Local Iowa Data API - Serve locally downloaded GIS data
No web access required - all data served from DATA folder
"""

from fastapi import APIRouter, HTTPException, Response
from pathlib import Path
import json
from typing import Optional
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.windows import Window, from_bounds
from rasterio.transform import from_bounds as transform_from_bounds
from rasterio.features import geometry_mask
import numpy as np
from io import BytesIO
from PIL import Image
import mercantile
import math
import geopandas as gpd
from shapely.geometry import box, mapping
from affine import Affine

router = APIRouter()

# Data directory
DATA_DIR = Path("DATA")

# Available local datasets for Iowa
IOWA_DATASETS = {
    # Land Use/Land Cover
    "iowa_cdl": {
        "file": "Iowa_CDL.tif",
        "name": "Cropland Layer (CDL)",
        "description": "USDA NASS Cropland Data Layer - detailed crop types",
        "category": "LULC",
        "legend_url": "https://www.nass.usda.gov/Research_and_Science/Cropland/docs/cdl_legend.pdf"
    },
    "iowa_nlcd": {
        "file": "Iowa_NLCD.tif",
        "name": "Land Cover (NLCD)",
        "description": "National Land Cover Database - land cover classification",
        "category": "LULC"
    },
    
    # Satellite/Vegetation
    "iowa_ndvi": {
        "file": "Iowa_Landsat_NDVI.tif",
        "name": "Vegetation Index (NDVI)",
        "description": "Landsat-derived NDVI vegetation index",
        "category": "Vegetation"
    },
    
    # Climate/Weather
    "iowa_rainfall": {
        "file": "Iowa_Gridmet_Rainfall.tif",
        "name": "Rainfall",
        "description": "GridMET gridded precipitation data",
        "category": "Climate"
    },
    "iowa_tmax": {
        "file": "Iowa_Gridmet_Tmax_Summer.tif",
        "name": "Max Temperature",
        "description": "GridMET maximum temperature (summer)",
        "category": "Climate"
    },
    "iowa_et": {
        "file": "Iowa_Gridmet_ET.tif",
        "name": "Evapotranspiration",
        "description": "GridMET reference evapotranspiration",
        "category": "Climate"
    },
    
    # Soil Moisture
    "iowa_soil_moisture": {
        "file": "Iowa_SMAP_SoilMoisture.tif",
        "name": "Soil Moisture",
        "description": "NASA SMAP satellite soil moisture data",
        "category": "Soil"
    },
    
    # Vector Boundaries
    "iowa_boundary": {
        "file": "Iowa.shp",
        "name": "Iowa State Boundary",
        "description": "Iowa state boundary polygon",
        "category": "Boundary",
        "type": "vector"
    },
    "iowa_fields": {
        "file": "IowaFieldBoundaries.shp",
        "name": "Iowa Field Boundaries",
        "description": "Iowa agricultural field boundaries",
        "category": "Boundary",
        "type": "vector"
    }
}

# Load Iowa boundary for clipping
IOWA_BOUNDARY = None
def get_iowa_boundary():
    """Load and cache Iowa boundary"""
    global IOWA_BOUNDARY
    if IOWA_BOUNDARY is None:
        boundary_path = DATA_DIR / "Iowa.shp"
        if boundary_path.exists():
            gdf = gpd.read_file(boundary_path)
            IOWA_BOUNDARY = gdf.to_crs("EPSG:4326").unary_union
    return IOWA_BOUNDARY


def get_raster_info(dataset_id: str) -> dict:
    """Get metadata information about a raster dataset"""
    if dataset_id not in IOWA_DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    dataset = IOWA_DATASETS[dataset_id]
    file_path = DATA_DIR / dataset["file"]
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Data file not found: {dataset['file']}")
    
    try:
        with rasterio.open(file_path) as src:
            bounds = src.bounds
            crs = str(src.crs)
            
            info = {
                "id": dataset_id,
                "name": dataset["name"],
                "description": dataset["description"],
                "category": dataset["category"],
                "bounds": {
                    "west": bounds.left,
                    "south": bounds.bottom,
                    "east": bounds.right,
                    "north": bounds.top
                },
                "crs": crs,
                "width": src.width,
                "height": src.height,
                "bands": src.count,
                "dtype": str(src.dtypes[0]),
                "nodata": src.nodata
            }
            
            # Add statistics if available
            if src.count > 0:
                data = src.read(1, masked=True)
                info["statistics"] = {
                    "min": float(data.min()),
                    "max": float(data.max()),
                    "mean": float(data.mean()),
                    "std": float(data.std())
                }
            
            return info
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading raster: {str(e)}")


def generate_tile_from_raster(dataset_id: str, z: int, x: int, y: int, colormap: str = "viridis") -> bytes:
    """Generate a PNG tile from a raster dataset using XYZ tile coordinates, clipped to Iowa boundary"""
    if dataset_id not in IOWA_DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    dataset = IOWA_DATASETS[dataset_id]
    file_path = DATA_DIR / dataset["file"]
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Data file not found: {dataset['file']}")
    
    try:
        # Get tile bounds in Web Mercator
        tile = mercantile.Tile(x, y, z)
        tile_bounds = mercantile.bounds(tile)
        
        # Load Iowa boundary for clipping
        iowa_boundary = get_iowa_boundary()
        
        with rasterio.open(file_path) as src:
            # Calculate window in source coordinates
            window = from_bounds(
                tile_bounds.west, tile_bounds.south,
                tile_bounds.east, tile_bounds.north,
                transform=src.transform
            )
            
            # Read data
            data = src.read(1, window=window, out_shape=(256, 256), resampling=Resampling.bilinear)
            
            # Create mask for pixels outside Iowa boundary
            if iowa_boundary:
                # Create transform for the tile
                tile_transform = transform_from_bounds(
                    tile_bounds.west, tile_bounds.south,
                    tile_bounds.east, tile_bounds.north,
                    256, 256
                )
                
                # Create mask (True = outside boundary, False = inside)
                mask = geometry_mask(
                    [iowa_boundary],
                    out_shape=(256, 256),
                    transform=tile_transform,
                    invert=False
                )
                
                # Apply mask - set pixels outside Iowa to NaN
                data = np.where(mask, np.nan, data)
            
            # Apply colormap based on category
            if dataset["category"] == "Vegetation":
                # NDVI colormap (red to green)
                img_array = apply_ndvi_colormap(data)
            elif dataset["category"] == "Climate":
                # Temperature/rainfall colormap
                img_array = apply_climate_colormap(data)
            elif dataset["category"] == "LULC":
                # Categorical colormap
                img_array = apply_categorical_colormap(data)
            else:
                # Default grayscale
                img_array = apply_grayscale(data)
            
            # Convert to PNG
            img = Image.fromarray(img_array, mode='RGBA')
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            return buffer.getvalue()
    
    except Exception as e:
        # Return transparent tile on error
        img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer.getvalue()


def apply_ndvi_colormap(data: np.ndarray) -> np.ndarray:
    """Apply NDVI colormap (red = low, yellow = medium, green = high)"""
    # Normalize to 0-1
    normalized = np.clip((data - (-1)) / 2, 0, 1)
    
    # Create RGBA array
    rgba = np.zeros((*data.shape, 4), dtype=np.uint8)
    
    # Red channel: high for low NDVI
    rgba[:, :, 0] = (255 * (1 - normalized)).astype(np.uint8)
    # Green channel: high for high NDVI
    rgba[:, :, 1] = (255 * normalized).astype(np.uint8)
    # Blue channel: minimal
    rgba[:, :, 2] = 50
    # Alpha: full opacity for valid data
    rgba[:, :, 3] = np.where(np.isnan(data), 0, 200)
    
    return rgba


def apply_climate_colormap(data: np.ndarray) -> np.ndarray:
    """Apply climate data colormap (blue to red)"""
    # Normalize to 0-1
    valid_data = data[~np.isnan(data)]
    if len(valid_data) == 0:
        return np.zeros((*data.shape, 4), dtype=np.uint8)
    
    vmin, vmax = valid_data.min(), valid_data.max()
    normalized = np.clip((data - vmin) / (vmax - vmin + 0.001), 0, 1)
    
    # Create RGBA array
    rgba = np.zeros((*data.shape, 4), dtype=np.uint8)
    
    # Blue to red gradient
    rgba[:, :, 0] = (255 * normalized).astype(np.uint8)  # Red
    rgba[:, :, 1] = (128 * (1 - np.abs(normalized - 0.5) * 2)).astype(np.uint8)  # Green (peaks at middle)
    rgba[:, :, 2] = (255 * (1 - normalized)).astype(np.uint8)  # Blue
    rgba[:, :, 3] = np.where(np.isnan(data), 0, 200)  # Alpha
    
    return rgba


# CDL Crop type codes
CDL_CLASSES = {
    1: "Corn", 2: "Cotton", 3: "Rice", 4: "Sorghum", 5: "Soybeans",
    6: "Sunflower", 10: "Peanuts", 11: "Tobacco", 12: "Sweet Corn", 13: "Pop Corn",
    14: "Mint", 21: "Barley", 22: "Durum Wheat", 23: "Spring Wheat", 24: "Winter Wheat",
    25: "Other Small Grains", 26: "Dbl Crop WinWht/Soybeans", 27: "Rye",
    28: "Oats", 29: "Millet", 30: "Speltz", 31: "Canola", 32: "Flaxseed",
    33: "Safflower", 34: "Rape Seed", 35: "Mustard", 36: "Alfalfa",
    37: "Other Hay/Non Alfalfa", 38: "Camelina", 39: "Buckwheat",
    41: "Sugarbeets", 42: "Dry Beans", 43: "Potatoes", 44: "Other Crops",
    45: "Sugarcane", 46: "Sweet Potatoes", 47: "Misc Vegs & Fruits",
    48: "Watermelons", 49: "Onions", 50: "Cucumbers", 51: "Chick Peas",
    52: "Lentils", 53: "Peas", 54: "Tomatoes", 55: "Caneberries",
    56: "Hops", 57: "Herbs", 58: "Clover/Wildflowers", 59: "Sod/Grass Seed",
    60: "Switchgrass", 61: "Fallow/Idle Cropland", 63: "Forest",
    64: "Shrubland", 65: "Barren", 66: "Cherries", 67: "Peaches",
    68: "Apples", 69: "Grapes", 70: "Christmas Trees", 71: "Other Tree Crops",
    72: "Citrus", 74: "Pecans", 75: "Almonds", 76: "Walnuts",
    77: "Pears", 81: "Clouds/No Data", 82: "Developed", 83: "Water",
    87: "Wetlands", 88: "Nonag/Undefined", 92: "Aquaculture",
    111: "Open Water", 112: "Perennial Ice/Snow", 121: "Developed/Open Space",
    122: "Developed/Low Intensity", 123: "Developed/Med Intensity",
    124: "Developed/High Intensity", 131: "Barren", 141: "Deciduous Forest",
    142: "Evergreen Forest", 143: "Mixed Forest", 152: "Shrubland",
    176: "Grass/Pasture", 190: "Woody Wetlands", 195: "Herbaceous Wetlands",
    204: "Pistachios", 205: "Triticale", 206: "Carrots",
    207: "Asparagus", 208: "Garlic", 209: "Cantaloupes",
    210: "Prunes", 211: "Olives", 212: "Oranges", 213: "Honeydew Melons",
    214: "Broccoli", 216: "Peppers", 217: "Pomegranates",
    218: "Nectarines", 219: "Greens", 220: "Plums", 221: "Strawberries",
    222: "Squash", 223: "Apricots", 224: "Vetch", 225: "Dbl Crop WinWht/Corn",
    226: "Dbl Crop Oats/Corn", 227: "Lettuce", 229: "Pumpkins",
    230: "Dbl Crop Lettuce/Durum Wht", 231: "Dbl Crop Lettuce/Cantaloupe",
    232: "Dbl Crop Lettuce/Cotton", 233: "Dbl Crop Lettuce/Barley",
    234: "Dbl Crop Durum Wht/Sorghum", 235: "Dbl Crop Barley/Sorghum",
    236: "Dbl Crop WinWht/Sorghum", 237: "Dbl Crop Barley/Corn",
    238: "Dbl Crop WinWht/Cotton", 239: "Dbl Crop Soybeans/Cotton",
    240: "Dbl Crop Soybeans/Oats", 241: "Dbl Crop Corn/Soybeans",
    242: "Blueberries", 243: "Cabbage", 244: "Cauliflower",
    245: "Celery", 246: "Radishes", 247: "Turnips", 248: "Eggplants",
    249: "Gourds", 250: "Cranberries", 254: "Dbl Crop Barley/Soybeans"
}

# NLCD Land cover codes
NLCD_CLASSES = {
    11: "Open Water", 12: "Perennial Ice/Snow",
    21: "Developed, Open Space", 22: "Developed, Low Intensity",
    23: "Developed, Medium Intensity", 24: "Developed, High Intensity",
    31: "Barren Land", 41: "Deciduous Forest", 42: "Evergreen Forest",
    43: "Mixed Forest", 52: "Shrub/Scrub", 71: "Grassland/Herbaceous",
    81: "Pasture/Hay", 82: "Cultivated Crops",
    90: "Woody Wetlands", 95: "Emergent Herbaceous Wetlands"
}

def apply_categorical_colormap(data: np.ndarray) -> np.ndarray:
    """Apply categorical colormap for land use/land cover"""
    # Create RGBA array
    rgba = np.zeros((*data.shape, 4), dtype=np.uint8)
    
    # CDL colors
    colors = {
        1: (255, 211, 0),    # Corn - yellow
        5: (0, 175, 73),     # Soybeans - green
        24: (255, 38, 38),   # Winter wheat - red
        23: (204, 102, 0),   # Spring wheat - brown-orange
        36: (255, 0, 255),   # Alfalfa - magenta
        37: (255, 158, 11),  # Other hay - orange
        61: (171, 171, 171), # Fallow - gray
        81: (220, 217, 57),  # Pasture - light yellow
        82: (171, 208, 0),   # Cultivated crops - lime
        111: (79, 129, 189), # Open water - blue
        121: (180, 180, 180),# Developed open space
        122: (210, 210, 210),# Developed low
        123: (150, 150, 150),# Developed medium
        124: (100, 100, 100),# Developed high
        131: (222, 197, 140),# Barren - tan
        141: (65, 130, 75),  # Deciduous forest - dark green
        142: (39, 100, 45),  # Evergreen forest - darker green
        143: (102, 153, 102),# Mixed forest
        152: (179, 214, 156),# Shrubland - light green
        176: (209, 209, 130),# Grassland - yellow-green
        190: (112, 163, 186),# Woody wetlands
        195: (178, 194, 157),# Herbaceous wetlands - sage
    }
    
    # Apply colors
    for value, color in colors.items():
        mask = (data == value)
        rgba[mask, 0] = color[0]
        rgba[mask, 1] = color[1]
        rgba[mask, 2] = color[2]
        rgba[mask, 3] = 200
    
    # Set alpha to 0 for no-data
    rgba[:, :, 3] = np.where(np.isnan(data) | (data == 0), 0, rgba[:, :, 3])
    
    return rgba


def apply_grayscale(data: np.ndarray) -> np.ndarray:
    """Apply grayscale colormap"""
    valid_data = data[~np.isnan(data)]
    if len(valid_data) == 0:
        return np.zeros((*data.shape, 4), dtype=np.uint8)
    
    vmin, vmax = valid_data.min(), valid_data.max()
    normalized = np.clip((data - vmin) / (vmax - vmin + 0.001), 0, 1)
    gray = (255 * normalized).astype(np.uint8)
    
    rgba = np.zeros((*data.shape, 4), dtype=np.uint8)
    rgba[:, :, 0] = gray
    rgba[:, :, 1] = gray
    rgba[:, :, 2] = gray
    rgba[:, :, 3] = np.where(np.isnan(data), 0, 200)
    
    return rgba


# ==================== API ENDPOINTS ====================

@router.get("/local-data/datasets")
async def list_datasets():
    """List all available local Iowa datasets"""
    datasets = []
    for dataset_id, info in IOWA_DATASETS.items():
        file_path = DATA_DIR / info["file"]
        datasets.append({
            "id": dataset_id,
            "name": info["name"],
            "description": info["description"],
            "category": info["category"],
            "available": file_path.exists(),
            "tile_url": f"/api/local-data/tiles/{dataset_id}/{{z}}/{{x}}/{{y}}.png"
        })
    
    return {
        "total_datasets": len(datasets),
        "datasets": datasets,
        "data_directory": str(DATA_DIR),
        "note": "All data served locally - no internet connection required"
    }


@router.get("/local-data/info/{dataset_id}")
async def get_dataset_info(dataset_id: str):
    """Get detailed information about a dataset"""
    return get_raster_info(dataset_id)


@router.get("/local-data/tiles/{dataset_id}/{z}/{x}/{y}.png")
async def get_tile(dataset_id: str, z: int, x: int, y: int, colormap: Optional[str] = "auto"):
    """Get a map tile for a dataset"""
    tile_data = generate_tile_from_raster(dataset_id, z, x, y, colormap or "auto")
    return Response(content=tile_data, media_type="image/png")


@router.get("/local-data/point-value/{dataset_id}")
async def get_point_value(dataset_id: str, lat: float, lon: float):
    """Get the value at a specific point from a dataset"""
    if dataset_id not in IOWA_DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    dataset = IOWA_DATASETS[dataset_id]
    file_path = DATA_DIR / dataset["file"]
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Data file not found: {dataset['file']}")
    
    try:
        with rasterio.open(file_path) as src:
            # Get row, col from lat/lon
            py, px = src.index(lon, lat)
            
            # Read single pixel value
            # Ensure indices are within bounds
            if 0 <= py < src.height and 0 <= px < src.width:
                value = src.read(1)[py, px]
            else:
                value = np.nan
            
            # Convert categorical values to class names
            display_value = None
            class_name = None
            
            if not np.isnan(value):
                value_int = int(value)
                if dataset_id == "iowa_cdl":
                    class_name = CDL_CLASSES.get(value_int, f"Unknown (Code {value_int})")
                    display_value = class_name
                elif dataset_id == "iowa_nlcd":
                    class_name = NLCD_CLASSES.get(value_int, f"Unknown (Code {value_int})")
                    display_value = class_name
                else:
                    # For numeric data, use the value itself
                    display_value = float(value)
            
            return {
                "dataset": dataset["name"],
                "location": {"latitude": lat, "longitude": lon},
                "value": float(value) if not np.isnan(value) else None,
                "display_value": display_value,
                "class_name": class_name,
                "unit": get_unit_for_dataset(dataset_id)
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading value: {str(e)}")


@router.get("/local-data/stats/{dataset_id}")
async def get_dataset_statistics(dataset_id: str):
    """Get statistics for a dataset"""
    if dataset_id not in IOWA_DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    dataset = IOWA_DATASETS[dataset_id]
    file_path = DATA_DIR / dataset["file"]
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Data file not found: {dataset['file']}")
    
    try:
        with rasterio.open(file_path) as src:
            data = src.read(1, masked=True)
            
            # Get valid (non-masked) data
            valid_data = data.compressed()
            
            if len(valid_data) == 0:
                raise HTTPException(status_code=404, detail="No valid data in dataset")
            
            stats = {
                "dataset": dataset["name"],
                "min": float(valid_data.min()),
                "max": float(valid_data.max()),
                "mean": float(valid_data.mean()),
                "std": float(valid_data.std()),
                "median": float(np.median(valid_data)),
                "count": int(len(valid_data)),
                "unit": get_unit_for_dataset(dataset_id)
            }
            
            # Add histogram for visualization
            hist, bins = np.histogram(valid_data, bins=20)
            stats["histogram"] = {
                "counts": hist.tolist(),
                "bins": bins.tolist()
            }
            
            return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating statistics: {str(e)}")


def get_unit_for_dataset(dataset_id: str) -> str:
    """Get the unit of measurement for a dataset"""
    units = {
        "iowa_ndvi": "NDVI (-1 to 1)",
        "iowa_rainfall": "mm",
        "iowa_tmax": "°C",
        "iowa_et": "mm",
        "iowa_soil_moisture": "m³/m³",
        "iowa_cdl": "Land Cover Class",
        "iowa_nlcd": "Land Cover Class"
    }
    return units.get(dataset_id, "")


@router.get("/local-data/boundary")
async def get_iowa_boundary_geojson():
    """Get Iowa state boundary as GeoJSON"""
    boundary_path = DATA_DIR / "Iowa.shp"
    
    if not boundary_path.exists():
        raise HTTPException(status_code=404, detail="Iowa boundary file not found")
    
    try:
        gdf = gpd.read_file(boundary_path)
        gdf = gdf.to_crs("EPSG:4326")
        return json.loads(gdf.to_json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading boundary: {str(e)}")


@router.get("/local-data/fields")
async def get_iowa_fields_geojson():
    """Get Iowa field boundaries as GeoJSON (simplified for web display)"""
    fields_path = DATA_DIR / "IowaFieldBoundaries.shp"
    
    if not fields_path.exists():
        raise HTTPException(status_code=404, detail="Iowa fields file not found")
    
    try:
        gdf = gpd.read_file(fields_path)
        gdf = gdf.to_crs("EPSG:4326")
        
        # Simplify geometries for faster rendering (tolerance in degrees)
        gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.0001, preserve_topology=True)
        
        # Limit to first 10000 fields to prevent overwhelming the browser
        if len(gdf) > 10000:
            gdf = gdf.head(10000)
        
        return json.loads(gdf.to_json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading fields: {str(e)}")


@router.get("/local-data/iowa-bounds")
async def get_iowa_bounds():
    """Get the geographic bounds for Iowa"""
    return {
        "state": "Iowa",
        "bounds": {
            "west": -96.639485,
            "south": 40.375501,
            "east": -90.140061,
            "north": 43.501196
        },
        "center": {
            "latitude": 41.938403,
            "longitude": -93.389831
        },
        "zoom_level": 7
    }
