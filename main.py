from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import httpx
import json

from config import settings
from database import get_db, init_db
from models import Farm, Field, Sensor, SensorReading, CropMonitoring, WeatherData
from schemas import (
    FarmCreate, FarmResponse,
    FieldCreate, FieldResponse,
    SensorCreate, SensorResponse,
    SensorReadingCreate, SensorReadingResponse,
    CropMonitoringCreate, CropMonitoringResponse,
    WeatherDataResponse, FieldAnalysisResponse
)
from gemini_ai import (
    GeminiAI, get_ai_crop_recommendation, get_ai_field_analysis,
    get_ai_rotation_plan, get_ai_fertilizer_plan
)
from local_data_api import router as local_data_router

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Interactive WebGIS Application for Precision Agriculture"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    print(f"Warning: Could not mount static directory: {e}")

# Include Local Data router
app.include_router(local_data_router, prefix="/api", tags=["Iowa Local Data"])


# ==================== STUB FUNCTIONS (for legacy endpoints) ====================
def calculate_ndvi(nir, red):
    """Calculate NDVI - stub for legacy endpoints"""
    if red == 0:
        return 0
    return (nir - red) / (nir + red)

def classify_health_status(ndvi):
    """Classify health based on NDVI - stub for legacy endpoints"""
    if ndvi > 0.6:
        return "Excellent"
    elif ndvi > 0.4:
        return "Good"
    elif ndvi > 0.2:
        return "Fair"
    else:
        return "Poor"

def calculate_polygon_area(geometry):
    """Calculate area - stub for legacy endpoints"""
    return 0.0

def generate_recommendations(field_data):
    """Generate recommendations - stub for legacy endpoints"""
    return ["Legacy endpoint - use Iowa Local Data system instead"]

async def get_current_conditions(lat, lon):
    """Get weather - stub for legacy endpoints"""
    return {"weathercode": 0, "temperature": 0, "humidity": 0}

async def get_farm_weather_forecast(lat, lon, days):
    """Get forecast - stub for legacy endpoints"""
    return {"daily": []}

class OpenMeteoAPI:
    """Stub class for legacy weather endpoints"""
    @staticmethod
    def decode_weather_code(code):
        return "Clear sky"


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print(f"{settings.app_name} v{settings.app_version} started successfully!")


# ==================== FARM ENDPOINTS ====================

@app.post("/api/farms/", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
async def create_farm(farm: FarmCreate, db: Session = Depends(get_db)):
    """Create a new farm"""
    db_farm = Farm(**farm.dict())
    db.add(db_farm)
    db.commit()
    db.refresh(db_farm)
    return db_farm


@app.get("/api/farms/", response_model=List[FarmResponse])
async def get_farms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all farms"""
    farms = db.query(Farm).offset(skip).limit(limit).all()
    return farms


@app.get("/api/farms/{farm_id}", response_model=FarmResponse)
async def get_farm(farm_id: int, db: Session = Depends(get_db)):
    """Get a specific farm by ID"""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm


@app.put("/api/farms/{farm_id}", response_model=FarmResponse)
async def update_farm(farm_id: int, farm: FarmCreate, db: Session = Depends(get_db)):
    """Update a farm"""
    db_farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not db_farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    for key, value in farm.dict().items():
        setattr(db_farm, key, value)
    
    db.commit()
    db.refresh(db_farm)
    return db_farm


@app.delete("/api/farms/{farm_id}")
async def delete_farm(farm_id: int, db: Session = Depends(get_db)):
    """Delete a farm"""
    db_farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not db_farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    db.delete(db_farm)
    db.commit()
    return {"message": "Farm deleted successfully"}


# ==================== FIELD ENDPOINTS ====================

@app.post("/api/fields/", response_model=FieldResponse, status_code=status.HTTP_201_CREATED)
async def create_field(field: FieldCreate, db: Session = Depends(get_db)):
    """Create a new field"""
    # Calculate area if geometry is provided
    if field.geometry and not field.area:
        field.area = calculate_polygon_area(field.geometry)
    
    db_field = Field(**field.dict())
    db.add(db_field)
    db.commit()
    db.refresh(db_field)
    return db_field


@app.get("/api/fields/")
async def get_fields(farm_id: Optional[int] = None, skip: int = 0, 
                     limit: int = 100, db: Session = Depends(get_db)):
    """Get all fields, optionally filtered by farm"""
    query = db.query(Field)
    if farm_id:
        query = query.filter(Field.farm_id == farm_id)
    fields = query.offset(skip).limit(limit).all()
    
    # Parse geometry JSON strings to objects
    result = []
    for field in fields:
        try:
            geometry_data = json.loads(field.geometry) if field.geometry else None
        except (json.JSONDecodeError, TypeError):
            geometry_data = None
            
        field_dict = {
            'id': field.id,
            'farm_id': field.farm_id,
            'name': field.name,
            'area': field.area,
            'crop_type': field.crop_type,
            'geometry': geometry_data,
            'soil_type': field.soil_type,
            'soil_ph': field.soil_ph,
            'soil_nitrogen': field.soil_nitrogen,
            'soil_phosphorus': field.soil_phosphorus,
            'soil_potassium': field.soil_potassium,
            'created_at': field.created_at
        }
        result.append(field_dict)
    
    return result


@app.get("/api/fields/{field_id}", response_model=FieldResponse)
async def get_field(field_id: int, db: Session = Depends(get_db)):
    """Get a specific field by ID"""
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field


@app.put("/api/fields/{field_id}", response_model=FieldResponse)
async def update_field(field_id: int, field: FieldCreate, db: Session = Depends(get_db)):
    """Update a field"""
    db_field = db.query(Field).filter(Field.id == field_id).first()
    if not db_field:
        raise HTTPException(status_code=404, detail="Field not found")
    
    for key, value in field.dict().items():
        setattr(db_field, key, value)
    
    db.commit()
    db.refresh(db_field)
    return db_field


@app.delete("/api/fields/{field_id}")
async def delete_field(field_id: int, db: Session = Depends(get_db)):
    """Delete a field"""
    db_field = db.query(Field).filter(Field.id == field_id).first()
    if not db_field:
        raise HTTPException(status_code=404, detail="Field not found")
    
    db.delete(db_field)
    db.commit()
    return {"message": "Field deleted successfully"}


# ==================== SENSOR ENDPOINTS ====================

@app.post("/api/sensors/", response_model=SensorResponse, status_code=status.HTTP_201_CREATED)
async def create_sensor(sensor: SensorCreate, db: Session = Depends(get_db)):
    """Create a new sensor"""
    db_sensor = Sensor(**sensor.dict())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor


@app.get("/api/sensors/", response_model=List[SensorResponse])
async def get_sensors(field_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get all sensors, optionally filtered by field"""
    query = db.query(Sensor)
    if field_id:
        query = query.filter(Sensor.field_id == field_id)
    sensors = query.all()
    return sensors


@app.post("/api/sensors/readings/", response_model=SensorReadingResponse, 
         status_code=status.HTTP_201_CREATED)
async def create_sensor_reading(reading: SensorReadingCreate, db: Session = Depends(get_db)):
    """Add a sensor reading"""
    db_reading = SensorReading(**reading.dict())
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading


@app.get("/api/sensors/{sensor_id}/readings/", response_model=List[SensorReadingResponse])
async def get_sensor_readings(sensor_id: int, limit: int = 100, db: Session = Depends(get_db)):
    """Get recent readings for a sensor"""
    readings = (db.query(SensorReading)
                .filter(SensorReading.sensor_id == sensor_id)
                .order_by(SensorReading.timestamp.desc())
                .limit(limit)
                .all())
    return readings


# ==================== CROP MONITORING ENDPOINTS ====================

@app.post("/api/crop-monitoring/", response_model=CropMonitoringResponse, 
         status_code=status.HTTP_201_CREATED)
async def create_crop_monitoring(monitoring: CropMonitoringCreate, 
                                 db: Session = Depends(get_db)):
    """Create a crop monitoring record"""
    # Auto-classify health status if NDVI is provided
    if monitoring.ndvi and not monitoring.health_status:
        monitoring.health_status = classify_health_status(monitoring.ndvi)
    
    db_monitoring = CropMonitoring(**monitoring.dict())
    db.add(db_monitoring)
    db.commit()
    db.refresh(db_monitoring)
    return db_monitoring


@app.get("/api/crop-monitoring/", response_model=List[CropMonitoringResponse])
async def get_crop_monitoring(field_id: Optional[int] = None, 
                              db: Session = Depends(get_db)):
    """Get crop monitoring records"""
    query = db.query(CropMonitoring)
    if field_id:
        query = query.filter(CropMonitoring.field_id == field_id)
    records = query.order_by(CropMonitoring.created_at.desc()).all()
    return records


@app.post("/api/crop-monitoring/calculate-ndvi/")
async def calculate_ndvi_endpoint(nir: float, red: float, blue: Optional[float] = None):
    """Calculate vegetation indices from band values"""
    ndvi = calculate_ndvi(nir, red)
    health_status = classify_health_status(ndvi)
    
    response = {
        "ndvi": round(ndvi, 3),
        "health_status": health_status
    }
    
    return response


# ==================== ANALYSIS ENDPOINTS ====================

@app.get("/api/analysis/field/{field_id}", response_model=FieldAnalysisResponse)
async def analyze_field(field_id: int, db: Session = Depends(get_db)):
    """Get comprehensive analysis for a field"""
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    
    # Get latest crop monitoring data
    latest_monitoring = (db.query(CropMonitoring)
                        .filter(CropMonitoring.field_id == field_id)
                        .order_by(CropMonitoring.created_at.desc())
                        .first())
    
    # Prepare field data for recommendations
    field_data = {
        'ndvi': latest_monitoring.ndvi if latest_monitoring else None,
        'soil_ph': field.soil_ph,
        'soil_nitrogen': field.soil_nitrogen,
        'soil_phosphorus': field.soil_phosphorus,
        'soil_potassium': field.soil_potassium
    }
    
    recommendations = generate_recommendations(field_data)
    
    # Prepare soil quality data
    soil_quality = {
        'ph': field.soil_ph,
        'nitrogen': field.soil_nitrogen,
        'phosphorus': field.soil_phosphorus,
        'potassium': field.soil_potassium,
        'type': field.soil_type
    }
    
    return FieldAnalysisResponse(
        field_id=field.id,
        field_name=field.name,
        crop_type=field.crop_type or "Unknown",
        area=field.area or 0.0,
        avg_ndvi=latest_monitoring.ndvi if latest_monitoring else None,
        health_status=latest_monitoring.health_status if latest_monitoring else "No data",
        recommendations=recommendations,
        soil_quality=soil_quality,
        last_monitoring=latest_monitoring.created_at if latest_monitoring else None
    )


# ==================== WEATHER ENDPOINTS ====================

@app.get("/api/weather/{farm_id}")
async def get_weather(farm_id: int, db: Session = Depends(get_db)):
    """Get current weather for a farm location using Open-Meteo (FREE)"""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    if not farm.latitude or not farm.longitude:
        raise HTTPException(status_code=400, detail="Farm coordinates not available")
    
    try:
        # Use Open-Meteo API (free, no key needed)
        current_weather = await get_current_conditions(farm.latitude, farm.longitude)
        
        # Store weather data
        weather = WeatherData(
            farm_id=farm_id,
            temperature=current_weather.get('temperature', 0.0),
            humidity=0.0,  # Not available in current weather endpoint
            precipitation=0.0,
            wind_speed=current_weather.get('windspeed', 0.0),
            conditions=OpenMeteoAPI.decode_weather_code(current_weather.get('weathercode', 0)),
            timestamp=datetime.utcnow()
        )
        db.add(weather)
        db.commit()
        
        return {
            "source": "Open-Meteo (Free)",
            "temperature": current_weather.get('temperature'),
            "wind_speed": current_weather.get('windspeed'),
            "wind_direction": current_weather.get('winddirection'),
            "conditions": OpenMeteoAPI.decode_weather_code(current_weather.get('weathercode', 0)),
            "time": current_weather.get('time')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather data: {str(e)}")


@app.get("/api/weather/{farm_id}/forecast")
async def get_weather_forecast(farm_id: int, days: int = 7, db: Session = Depends(get_db)):
    """
    Get weather forecast for a farm location (1-16 days)
    Uses Open-Meteo API - Free, no API key needed
    """
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    if not farm.latitude or not farm.longitude:
        raise HTTPException(status_code=400, detail="Farm coordinates not available")
    
    if days < 1 or days > 16:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 16")
    
    try:
        forecast = await get_farm_weather_forecast(farm.latitude, farm.longitude, days)
        forecast["farm_id"] = farm_id
        forecast["farm_name"] = farm.name
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch forecast: {str(e)}")


@app.get("/api/weather/{farm_id}/climate-history")
async def get_climate_history(farm_id: int, days_back: int = 30, db: Session = Depends(get_db)):
    """
    Get historical climate data for a farm location
    Uses NASA POWER API - Free, no API key needed
    """
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    if not farm.latitude or not farm.longitude:
        raise HTTPException(status_code=400, detail="Farm coordinates not available")
    
    if days_back < 1 or days_back > 365:
        raise HTTPException(status_code=400, detail="Days back must be between 1 and 365")
    
    try:
        climate_data = await get_farm_climate_data(farm.latitude, farm.longitude, days_back)
        climate_data["farm_id"] = farm_id
        climate_data["farm_name"] = farm.name
        return climate_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch climate data: {str(e)}")


# ==================== AGROMONITORING ENDPOINTS ====================

@app.post("/api/agromonitoring/register-field/{field_id}")
async def register_field_satellite(field_id: int, db: Session = Depends(get_db)):
    """
    Register a field with Agromonitoring for satellite monitoring
    Requires field to have geometry (polygon) defined
    """
    if not settings.agromonitoring_api_key:
        raise HTTPException(
            status_code=503,
            detail="Agromonitoring API key not configured. Add AGROMONITORING_API_KEY to .env file"
        )
    
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    
    if not field.geometry:
        raise HTTPException(
            status_code=400,
            detail="Field must have geometry (polygon) defined before registering for satellite monitoring"
        )
    
    # Check if already registered
    if field.agromonitoring_polygon_id:
        return {
            "message": "Field already registered",
            "polygon_id": field.agromonitoring_polygon_id,
            "field_id": field_id
        }
    
    try:
        # Register with Agromonitoring
        result = await register_field_for_monitoring(
            settings.agromonitoring_api_key,
            field.name,
            field.geometry
        )
        
        # Store polygon ID
        field.agromonitoring_polygon_id = result.get('id')
        db.commit()
        
        return {
            "message": "Field successfully registered for satellite monitoring",
            "polygon_id": result.get('id'),
            "field_id": field_id,
            "note": "Satellite data will be available in 2-3 days"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to register field: {str(e)}"
        )


@app.get("/api/agromonitoring/satellite-ndvi/{field_id}")
async def get_field_satellite_data(
    field_id: int,
    days_back: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get satellite NDVI data for a registered field
    Returns real NDVI from Sentinel-2 satellites
    """
    if not settings.agromonitoring_api_key:
        raise HTTPException(
            status_code=503,
            detail="Agromonitoring API key not configured"
        )
    
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    
    if not field.agromonitoring_polygon_id:
        raise HTTPException(
            status_code=400,
            detail="Field not registered for satellite monitoring. Use POST /api/agromonitoring/register-field/{field_id} first"
        )
    
    try:
        # Get satellite data
        data = await get_field_satellite_ndvi(
            settings.agromonitoring_api_key,
            field.agromonitoring_polygon_id,
            days_back
        )
        
        data["field_id"] = field_id
        data["field_name"] = field.name
        
        # Auto-update crop monitoring if we have fresh NDVI data
        if data.get('latest_ndvi'):
            latest = data['latest_ndvi']
            ndvi_value = latest.get('data', {}).get('mean', 0)
            
            if ndvi_value > 0:  # Valid NDVI
                # Create new monitoring record
                monitoring = CropMonitoring(
                    field_id=field_id,
                    ndvi=ndvi_value,
                    health_status=data['health_status'],
                    image_date=datetime.fromtimestamp(latest.get('dt', 0)),
                    data_source="Agromonitoring (Sentinel-2)",
                    notes=f"Satellite NDVI - Cloud coverage: {latest.get('cl', 0)}%"
                )
                db.add(monitoring)
                db.commit()
        
        return data
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch satellite data: {str(e)}"
        )


@app.get("/api/agromonitoring/polygons")
async def list_registered_fields(db: Session = Depends(get_db)):
    """
    List all fields registered with Agromonitoring
    """
    if not settings.agromonitoring_api_key:
        raise HTTPException(
            status_code=503,
            detail="Agromonitoring API key not configured"
        )
    
    try:
        api = AgromonitoringAPI(settings.agromonitoring_api_key)
        polygons = await api.get_polygons()
        
        # Match with local fields
        registered_fields = []
        for polygon in polygons:
            field = db.query(Field).filter(
                Field.agromonitoring_polygon_id == polygon.get('id')
            ).first()
            
            registered_fields.append({
                "polygon_id": polygon.get('id'),
                "polygon_name": polygon.get('name'),
                "field_id": field.id if field else None,
                "field_name": field.name if field else None,
                "area": polygon.get('area', 0),
                "created_at": polygon.get('created_at')
            })
        
        return {
            "total": len(registered_fields),
            "fields": registered_fields
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch registered fields: {str(e)}"
        )


@app.delete("/api/agromonitoring/unregister-field/{field_id}")
async def unregister_field_satellite(field_id: int, db: Session = Depends(get_db)):
    """
    Unregister a field from Agromonitoring satellite monitoring
    """
    if not settings.agromonitoring_api_key:
        raise HTTPException(
            status_code=503,
            detail="Agromonitoring API key not configured"
        )
    
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    
    if not field.agromonitoring_polygon_id:
        raise HTTPException(
            status_code=400,
            detail="Field not registered for satellite monitoring"
        )
    
    try:
        api = AgromonitoringAPI(settings.agromonitoring_api_key)
        await api.delete_polygon(field.agromonitoring_polygon_id)
        
        # Clear polygon ID
        polygon_id = field.agromonitoring_polygon_id
        field.agromonitoring_polygon_id = None
        db.commit()
        
        return {
            "message": "Field unregistered from satellite monitoring",
            "polygon_id": polygon_id,
            "field_id": field_id
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to unregister field: {str(e)}"
        )


# ==================== INSTANT SATELLITE DATA (FREE) ====================

@app.get("/api/satellite/instant-ndvi/{field_id}")
async def get_instant_satellite_data(
    field_id: int,
    days_back: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get INSTANT satellite NDVI data using FREE Microsoft Planetary Computer
    ⚡ NO WAITING! NO API KEY REQUIRED!
    
    This endpoint provides immediate access to historical Sentinel-2 satellite data.
    Unlike Agromonitoring, there's NO 2-3 day waiting period!
    
    Args:
        field_id: Field ID
        days_back: Number of days to analyze (default: 30)
    
    Returns:
        Instant NDVI analysis with health status and trends
    """
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    
    if not field.geometry:
        raise HTTPException(
            status_code=400,
            detail="Field has no geometry defined. Cannot calculate satellite data."
        )
    
    try:
        # Convert field geometry to bounding box
        bbox = geometry_to_bbox(field.geometry)
        
        # Get instant NDVI data from Microsoft Planetary Computer (FREE!)
        result = await get_instant_ndvi_free(bbox, days_back)
        
        # Add field information
        result["field_info"] = {
            "field_id": field_id,
            "field_name": field.name,
            "crop_type": field.crop_type or "Unknown",
            "area": field.area
        }
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch instant satellite data: {str(e)}"
        )


@app.get("/api/satellite/quick-analysis")
async def get_quick_satellite_analysis(
    lat: float,
    lon: float,
    radius_km: float = 0.5,
    days_back: int = 30
):
    """
    Quick satellite analysis for any location - NO FIELD REQUIRED!
    ⚡ INSTANT results from Microsoft Planetary Computer (FREE)
    
    Perfect for exploring satellite data before creating fields.
    
    Args:
        lat: Latitude
        lon: Longitude
        radius_km: Search radius in kilometers (default: 0.5 km)
        days_back: Number of days to analyze (default: 30)
    
    Returns:
        Instant NDVI analysis for the location
    """
    try:
        # Create bounding box around point
        # Rough conversion: 1 degree ≈ 111 km
        km_to_deg = 1 / 111
        radius_deg = radius_km * km_to_deg
        
        bbox = [
            lon - radius_deg,  # min_lon
            lat - radius_deg,  # min_lat
            lon + radius_deg,  # max_lon
            lat + radius_deg   # max_lat
        ]
        
        # Get instant NDVI data
        result = await get_instant_ndvi_free(bbox, days_back)
        
        # Add location info
        result["location"] = {
            "latitude": lat,
            "longitude": lon,
            "radius_km": radius_km
        }
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch satellite analysis: {str(e)}"
        )


# ==================== STATISTICS ENDPOINTS ====================

@app.get("/api/statistics/dashboard")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    total_farms = db.query(Farm).count()
    total_fields = db.query(Field).count()
    total_sensors = db.query(Sensor).filter(Sensor.is_active == True).count()
    
    # Calculate total area
    total_area = db.query(Field).with_entities(Field.area).all()
    total_area_sum = sum([area[0] for area in total_area if area[0]])
    
    # Get fields by health status
    latest_monitoring = (db.query(CropMonitoring)
                        .order_by(CropMonitoring.field_id, 
                                 CropMonitoring.created_at.desc())
                        .all())
    
    health_distribution = {"Excellent": 0, "Good": 0, "Fair": 0, "Poor": 0, "No data": 0}
    monitored_fields = set()
    
    for record in latest_monitoring:
        if record.field_id not in monitored_fields:
            health_distribution[record.health_status] = health_distribution.get(record.health_status, 0) + 1
            monitored_fields.add(record.field_id)
    
    # Fields without monitoring
    health_distribution["No data"] = total_fields - len(monitored_fields)
    
    return {
        "total_farms": total_farms,
        "total_fields": total_fields,
        "total_sensors": total_sensors,
        "total_area_hectares": round(total_area_sum, 2),
        "health_distribution": health_distribution
    }


# ==================== ROOT ENDPOINT ====================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main application page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Precision Agriculture WebGIS</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
            }
            h1 { color: #2c5530; }
            .card {
                background: #f5f5f5;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
            }
            a {
                color: #2c5530;
                text-decoration: none;
                font-weight: bold;
            }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>🌾 Precision Agriculture WebGIS</h1>
        <p>Welcome to the Interactive WebGIS Application for Precision Agriculture!</p>
        
        <div class="card">
            <h2>📚 API Documentation</h2>
            <p>Interactive API documentation: <a href="/docs">/docs</a></p>
            <p>Alternative API docs: <a href="/redoc">/redoc</a></p>
        </div>
        
        <div class="card">
            <h2>🗺️ Web Interface</h2>
            <p>Access the interactive map interface: <a href="/static/index.html">Open Map Application</a></p>
        </div>
        
        <div class="card">
            <h2>🚀 Quick Start</h2>
            <ul>
                <li>Create farms and fields via the API</li>
                <li>Add sensors for real-time monitoring</li>
                <li>Upload or calculate NDVI data</li>
                <li>Get agricultural recommendations</li>
                <li>Visualize data on interactive maps</li>
            </ul>
        </div>
    </body>
    </html>
    """


# ==================== SOIL DATA ENDPOINTS ====================

@app.get("/api/soil/analysis/{field_id}")
async def get_field_soil_analysis(field_id: int, db: Session = Depends(get_db)):
    """
    Get comprehensive soil analysis for a field
    Includes: pH, moisture, fertility, texture, crop suitability
    """
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    
    # Try to get location from farm first
    farm = db.query(Farm).filter(Farm.id == field.farm_id).first()
    
    # If farm location not available, calculate from field geometry
    if not farm or not farm.latitude or not farm.longitude:
        if field.geometry and 'coordinates' in field.geometry:
            coords = field.geometry['coordinates'][0]
            # Calculate centroid
            lon = sum(c[0] for c in coords) / len(coords)
            lat = sum(c[1] for c in coords) / len(coords)
        else:
            raise HTTPException(status_code=400, detail="Location not available")
    else:
        lat = farm.latitude
        lon = farm.longitude
    
    try:
        soil_analysis = await get_soil_analysis(lat, lon)
        
        # Add field context
        soil_analysis['field_info'] = {
            'field_id': field_id,
            'field_name': field.name,
            'crop_type': field.crop_type or 'Unknown',
            'area': field.area
        }
        
        return soil_analysis
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch soil analysis: {str(e)}"
        )


@app.get("/api/soil/quick-analysis")
async def get_quick_soil_analysis(lat: float, lon: float):
    """
    Quick soil analysis for any location
    No field required - useful for exploration
    """
    try:
        return await get_soil_analysis(lat, lon)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch soil analysis: {str(e)}"
        )


# ==================== GEMINI AI ENDPOINTS ====================

@app.post("/api/ai/crop-recommendation/{field_id}")
async def get_ai_crop_recommendation_endpoint(
    field_id: int,
    db: Session = Depends(get_db)
):
    """
    Get AI-powered crop recommendations using Gemini AI
    Analyzes soil, weather, and field conditions
    """
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=503,
            detail="Gemini AI not configured"
        )
    
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    
    farm = db.query(Farm).filter(Farm.id == field.farm_id).first()
    if not farm or not farm.latitude or not farm.longitude:
        raise HTTPException(status_code=400, detail="Farm location not available")
    
    try:
        # Get soil analysis
        soil_data = await get_soil_analysis(farm.latitude, farm.longitude)
        
        # Get weather forecast
        try:
            weather_data = await get_farm_weather_forecast(farm.latitude, farm.longitude, 7)
        except:
            weather_data = None
        
        # Field data
        field_data = {
            'location': {
                'latitude': farm.latitude,
                'longitude': farm.longitude
            },
            'area': field.area,
            'name': field.name
        }
        
        # Get AI recommendations
        recommendation = await get_ai_crop_recommendation(
            settings.gemini_api_key,
            soil_data,
            weather_data,
            field_data,
            field.crop_type
        )
        
        return {
            'field_id': field_id,
            'field_name': field.name,
            'current_crop': field.crop_type,
            'ai_recommendation': recommendation,
            'soil_summary': {
                'fertility_index': soil_data.get('fertility_index'),
                'ph': soil_data.get('soil_properties', {}).get('ph'),
                'texture': soil_data.get('soil_properties', {}).get('texture')
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate AI recommendation: {str(e)}"
        )


@app.post("/api/ai/field-health-analysis/{field_id}")
async def get_ai_health_analysis_endpoint(
    field_id: int,
    db: Session = Depends(get_db)
):
    """
    Get AI-powered field health analysis
    Combines satellite NDVI, soil data, and weather
    """
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=503,
            detail="Gemini AI not configured"
        )
    
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    
    farm = db.query(Farm).filter(Farm.id == field.farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    try:
        # Get NDVI data
        if field.geometry:
            bbox = geometry_to_bbox(field.geometry)
            ndvi_data = await get_instant_ndvi_free(bbox, 30)
        else:
            ndvi_data = {}
        
        # Get soil data
        soil_data = await get_soil_analysis(farm.latitude, farm.longitude)
        
        # Get weather
        try:
            weather_data = await get_current_conditions(farm.latitude, farm.longitude)
        except:
            weather_data = None
        
        # Get AI analysis
        analysis = await get_ai_field_analysis(
            settings.gemini_api_key,
            ndvi_data,
            soil_data,
            weather_data
        )
        
        return {
            'field_id': field_id,
            'field_name': field.name,
            'crop_type': field.crop_type,
            'ai_analysis': analysis,
            'current_ndvi': ndvi_data.get('estimated_ndvi'),
            'health_status': ndvi_data.get('health_status'),
            'soil_fertility': soil_data.get('fertility_index')
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate AI health analysis: {str(e)}"
        )


@app.post("/api/ai/fertilizer-plan/{field_id}")
async def get_ai_fertilizer_plan_endpoint(
    field_id: int,
    target_yield: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Get AI-powered fertilizer application plan
    Optimized for crop type and soil conditions
    """
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=503,
            detail="Gemini AI not configured"
        )
    
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    
    if not field.crop_type:
        raise HTTPException(
            status_code=400,
            detail="Field must have a crop type defined"
        )
    
    farm = db.query(Farm).filter(Farm.id == field.farm_id).first()
    if not farm or not farm.latitude or not farm.longitude:
        raise HTTPException(status_code=400, detail="Farm location not available")
    
    try:
        # Get soil data
        soil_data = await get_soil_analysis(farm.latitude, farm.longitude)
        
        # Get AI fertilizer plan
        plan = await get_ai_fertilizer_plan(
            settings.gemini_api_key,
            soil_data,
            field.crop_type,
            target_yield
        )
        
        return {
            'field_id': field_id,
            'field_name': field.name,
            'crop_type': field.crop_type,
            'target_yield': target_yield,
            'fertilizer_plan': plan,
            'soil_status': {
                'ph': soil_data.get('soil_properties', {}).get('ph'),
                'organic_carbon': soil_data.get('soil_properties', {}).get('organic_carbon'),
                'nitrogen': soil_data.get('soil_properties', {}).get('nitrogen')
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate fertilizer plan: {str(e)}"
        )


@app.post("/api/ai/location-insights")
async def get_ai_location_insights(
    request: dict
):
    """
    Get AI-powered insights for any location in Iowa
    Analyzes local datasets (CDL, NDVI, rainfall, soil moisture, etc.)
    """
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=503,
            detail="Gemini AI not configured"
        )
    
    latitude = request.get('latitude')
    longitude = request.get('longitude')
    location_data = request.get('data', {})
    
    if not latitude or not longitude:
        raise HTTPException(
            status_code=400,
            detail="Latitude and longitude required"
        )
    
    # Debug: Print what data we received
    print(f"\n=== AI REQUEST DEBUG ===")
    print(f"Location: {latitude}, {longitude}")
    print(f"Data received: {location_data}")
    print(f"Datasets: {location_data.get('datasets', {})}")
    print("========================\n")
    
    try:
        # Build comprehensive prompt for Gemini
        prompt = build_iowa_location_prompt(latitude, longitude, location_data)
        print(f"\n=== PROMPT TO AI ===\n{prompt}\n==================\n")
        
        # Call Gemini AI
        ai = GeminiAI(settings.gemini_api_key)
        response = await ai._call_gemini(prompt)
        
        return {
            'location': {
                'latitude': latitude,
                'longitude': longitude
            },
            'recommendation': response,
            'source': 'Google Gemini AI',
            'timestamp': datetime.now().isoformat(),
            'datasets_analyzed': list(location_data.get('datasets', {}).keys())
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate location insights: {str(e)}"
        )


def build_iowa_location_prompt(lat: float, lng: float, location_data: dict) -> str:
    """Build comprehensive prompt for Iowa location analysis"""
    
    datasets = location_data.get('datasets', {})
    
    # Check if location is urban/developed (non-agricultural)
    land_use = str(datasets.get('Iowa CDL 2023', '')).lower()
    land_cover = str(datasets.get('Iowa NLCD 2021', '')).lower()
    is_urban = ('developed' in land_use or 'developed' in land_cover or 
                'urban' in land_use or 'urban' in land_cover or
                'water' in land_use or 'water' in land_cover or
                'barren' in land_use or 'barren' in land_cover)
    
    prompt = f"""You are an expert precision agriculture consultant analyzing a SPECIFIC location in Iowa.

📍 LOCATION: {lat:.4f}°N, {lng:.4f}°W

⚠️ READ THIS DATA CAREFULLY - These are REAL measurements from this exact location:

"""
    
    # Add all available dataset information with emphasis
    if 'Iowa CDL 2023' in datasets:
        prompt += f"✓ LAND USE (Cropland Data Layer 2023): {datasets['Iowa CDL 2023']}\n"
    
    if 'Iowa NLCD 2021' in datasets:
        prompt += f"✓ LAND COVER (National Land Cover Database): {datasets['Iowa NLCD 2021']}\n"
    
    if 'Iowa NDVI' in datasets:
        ndvi_value = datasets['Iowa NDVI']
        prompt += f"✓ VEGETATION INDEX (NDVI): {ndvi_value}"
        try:
            ndvi_float = float(ndvi_value)
            if ndvi_float > 0.6:
                prompt += f" (Excellent vegetation)\n"
            elif ndvi_float > 0.3:
                prompt += f" (Moderate vegetation)\n"
            elif ndvi_float > 0.0:
                prompt += f" (Low vegetation)\n"
            else:
                prompt += f" (Bare soil)\n"
        except:
            prompt += "\n"
    
    if 'Iowa GridMET Rainfall' in datasets:
        prompt += f"✓ RAINFALL: {datasets['Iowa GridMET Rainfall']} mm\n"
    
    if 'Iowa GridMET Max Temp' in datasets:
        prompt += f"✓ MAX TEMPERATURE: {datasets['Iowa GridMET Max Temp']}°C\n"
    
    if 'Iowa SMAP Soil Moisture' in datasets:
        prompt += f"✓ SOIL MOISTURE: {datasets['Iowa SMAP Soil Moisture']} m³/m³"
        try:
            moisture = float(datasets['Iowa SMAP Soil Moisture'])
            if moisture > 0.35:
                prompt += f" (Saturated)\n"
            elif moisture > 0.25:
                prompt += f" (Optimal)\n"
            elif moisture > 0.15:
                prompt += f" (Adequate)\n"
            else:
                prompt += f" (Low - irrigation recommended)\n"
        except:
            prompt += "\n"
    
    if 'Iowa Landsat ET' in datasets:
        prompt += f"✓ EVAPOTRANSPIRATION: {datasets['Iowa Landsat ET']} mm\n"
    
    # Different prompt structure for urban/non-agricultural areas
    if is_urban:
        cdl_value = datasets.get('Iowa CDL 2023', 'Unknown')
        nlcd_value = datasets.get('Iowa NLCD 2021', 'Unknown')
        
        prompt += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚫 CRITICAL: This location is NOT AGRICULTURAL LAND

The data above shows:
- CDL Land Use: {cdl_value}
- NLCD Land Cover: {nlcd_value}

This is DEVELOPED/URBAN/WATER/BARREN - NOT suitable for farming.

YOUR TASK:
You MUST analyze this as NON-AGRICULTURAL land. DO NOT suggest crops or farming.

Provide this analysis:

**🏘️ Location Type**
State exactly: "This location is classified as {cdl_value} (CDL) and {nlcd_value} (NLCD)."

**🚫 Not Agricultural Land**
Explain: "This is not farmland. It is [describe what type of developed/urban/water/barren area this is]."

**🌳 Appropriate Uses**
List 2-3 appropriate uses for this land type (urban development, parks, conservation, water management, etc.).

**ℹ️ User Guidance**
State: "For crop and farming insights, please click on a location showing Corn, Soybeans, Pasture, or other agricultural land use."

Be clear and direct. Base your response on the EXACT data shown above.
"""
    else:
        # Get land use information for agricultural areas
        cdl_value = datasets.get('Iowa CDL 2023', 'Unknown')
        nlcd_value = datasets.get('Iowa NLCD 2021', 'Unknown')
        
        prompt += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ AGRICULTURAL LAND DETECTED

The data above shows:
- CDL Land Use: {cdl_value}
- NLCD Land Cover: {nlcd_value}

YOUR TASK:
Analyze this SPECIFIC crop/land use based on the EXACT data provided above.

CRITICAL RULES:
1. If CDL shows "Corn" → Provide CORN-specific management advice
2. If CDL shows "Soybeans" → Provide SOYBEAN-specific management advice
3. If CDL shows "Wheat" → Provide WHEAT-specific management advice
4. If CDL shows "Pasture/Hay/Grassland" → Provide grazing/hay management advice
5. If CDL shows "Forest/Wetland" → Provide conservation/environmental management advice
6. DO NOT make generic crop suggestions - tailor everything to the crop shown above
7. Use the NDVI, moisture, rainfall, and temperature data to assess current field conditions

Provide this analysis format:

**🎯 Field Status**
State: "This is a {cdl_value} field." Then describe current conditions using the NDVI, moisture, and weather data above.

**💡 Key Insight**
The most critical finding for THIS SPECIFIC CROP based on the data (not generic advice).

**🌱 Management Recommendations**
2-3 specific management tips for {cdl_value} based on the actual conditions shown in the data.

**💧 Water Management**
Irrigation/moisture guidance for {cdl_value} considering the soil moisture ({datasets.get('Iowa SMAP Soil Moisture', 'N/A')}) and rainfall data.

**⚡ Action Items**
• Immediate action for this land use type
• 2-4 week management for this specific crop/use
• Monitoring tip

**📈 Outlook**
Forecast and optimization for THIS land use (not conversion to something else).

IMPORTANT: Your entire response must match the land use data provided. No generic crop lists.
"""
    
    return prompt


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
