from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Farm(Base):
    """Farm entity representing a complete agricultural property"""
    __tablename__ = "farms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    total_area = Column(Float)  # in hectares
    location = Column(String)  # City/Region
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    fields = relationship("Field", back_populates="farm", cascade="all, delete-orphan")


class Field(Base):
    """Agricultural field/parcel within a farm"""
    __tablename__ = "fields"
    
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    name = Column(String, nullable=False)
    area = Column(Float)  # in hectares
    crop_type = Column(String)  # e.g., "Wheat", "Corn", "Soybean"
    
    # GeoJSON polygon string
    geometry = Column(Text)  # Store as GeoJSON string
    
    # Agromonitoring integration
    agromonitoring_polygon_id = Column(String)  # Agromonitoring polygon ID for satellite monitoring
    
    # Soil properties
    soil_type = Column(String)
    soil_ph = Column(Float)
    soil_nitrogen = Column(Float)  # N content
    soil_phosphorus = Column(Float)  # P content
    soil_potassium = Column(Float)  # K content
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    farm = relationship("Farm", back_populates="fields")
    sensors = relationship("Sensor", back_populates="field", cascade="all, delete-orphan")
    crop_monitoring = relationship("CropMonitoring", back_populates="field", cascade="all, delete-orphan")


class Sensor(Base):
    """IoT sensors deployed in fields"""
    __tablename__ = "sensors"
    
    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    sensor_type = Column(String)  # e.g., "soil_moisture", "temperature", "humidity"
    latitude = Column(Float)
    longitude = Column(Float)
    is_active = Column(Boolean, default=True)
    installed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    field = relationship("Field", back_populates="sensors")
    readings = relationship("SensorReading", back_populates="sensor", cascade="all, delete-orphan")


class SensorReading(Base):
    """Sensor data readings"""
    __tablename__ = "sensor_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=False)
    value = Column(Float)
    unit = Column(String)  # e.g., "%", "°C", "hPa"
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sensor = relationship("Sensor", back_populates="readings")


class CropMonitoring(Base):
    """Crop health monitoring and NDVI data"""
    __tablename__ = "crop_monitoring"
    
    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    
    # Vegetation indices
    ndvi = Column(Float)  # Normalized Difference Vegetation Index (-1 to 1)
    evi = Column(Float)   # Enhanced Vegetation Index
    savi = Column(Float)  # Soil Adjusted Vegetation Index
    
    # Health status
    health_status = Column(String)  # "Excellent", "Good", "Fair", "Poor"
    biomass_estimate = Column(Float)  # Estimated biomass in tons/hectare
    
    # Data source
    image_date = Column(DateTime)
    data_source = Column(String)  # e.g., "Sentinel-2", "Landsat", "Drone"
    
    # Recommendations
    irrigation_needed = Column(Boolean, default=False)
    fertilizer_needed = Column(Boolean, default=False)
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    field = relationship("Field", back_populates="crop_monitoring")


class WeatherData(Base):
    """Weather data for farms"""
    __tablename__ = "weather_data"
    
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    
    temperature = Column(Float)  # °C
    humidity = Column(Float)  # %
    precipitation = Column(Float)  # mm
    wind_speed = Column(Float)  # m/s
    conditions = Column(String)  # "Clear", "Cloudy", "Rain", etc.
    
    timestamp = Column(DateTime, default=datetime.utcnow)
