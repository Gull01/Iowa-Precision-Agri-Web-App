from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Farm Schemas
class FarmBase(BaseModel):
    name: str
    owner: str
    total_area: Optional[float] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class FarmCreate(FarmBase):
    pass


class FarmResponse(FarmBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Field Schemas
class FieldBase(BaseModel):
    farm_id: int
    name: str
    area: Optional[float] = None
    crop_type: Optional[str] = None
    geometry: Optional[str] = None  # GeoJSON string
    soil_type: Optional[str] = None
    soil_ph: Optional[float] = None
    soil_nitrogen: Optional[float] = None
    soil_phosphorus: Optional[float] = None
    soil_potassium: Optional[float] = None


class FieldCreate(FieldBase):
    pass


class FieldResponse(FieldBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Sensor Schemas
class SensorBase(BaseModel):
    field_id: int
    sensor_type: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: bool = True


class SensorCreate(SensorBase):
    pass


class SensorResponse(SensorBase):
    id: int
    installed_at: datetime
    
    class Config:
        from_attributes = True


# Sensor Reading Schemas
class SensorReadingBase(BaseModel):
    sensor_id: int
    value: float
    unit: str


class SensorReadingCreate(SensorReadingBase):
    pass


class SensorReadingResponse(SensorReadingBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


# Crop Monitoring Schemas
class CropMonitoringBase(BaseModel):
    field_id: int
    ndvi: Optional[float] = None
    evi: Optional[float] = None
    savi: Optional[float] = None
    health_status: Optional[str] = None
    biomass_estimate: Optional[float] = None
    image_date: Optional[datetime] = None
    data_source: Optional[str] = None
    irrigation_needed: bool = False
    fertilizer_needed: bool = False
    notes: Optional[str] = None


class CropMonitoringCreate(CropMonitoringBase):
    pass


class CropMonitoringResponse(CropMonitoringBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Weather Data Schemas
class WeatherDataResponse(BaseModel):
    temperature: float
    humidity: float
    precipitation: float
    wind_speed: float
    conditions: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


# Analysis Response
class FieldAnalysisResponse(BaseModel):
    field_id: int
    field_name: str
    crop_type: str
    area: float
    avg_ndvi: Optional[float] = None
    health_status: str
    recommendations: List[str] = []
    soil_quality: dict = {}
    last_monitoring: Optional[datetime] = None
