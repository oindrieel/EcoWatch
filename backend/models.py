from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# --- DATA MODELS ---

class AQIData(BaseModel):
    """
    This is the data structure we expect to receive from the ESP32.
    """
    device_id: str = Field(..., description="Unique ID of the ESP32 device")
    pm25: float = Field(..., description="Particulate Matter 2.5 concentration")
    pm10: float = Field(..., description="Particulate Matter 10 concentration")
    co2: float = Field(..., description="CO2 level in ppm")
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., description="Humidity percentage")
    lat: Optional[float] = Field(None, description="Latitude (optional if fixed location)")
    lon: Optional[float] = Field(None, description="Longitude (optional if fixed location)")

    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "esp32_001",
                "pm25": 12.5,
                "pm10": 25.0,
                "co2": 450.0,
                "temperature": 28.5,
                "humidity": 60.0,
                "lat": 28.6139,
                "lon": 77.2090
            }
        }


class AQIResponse(BaseModel):
    """
    Standard response model for API endpoints.
    """
    status: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Optional[dict] = None