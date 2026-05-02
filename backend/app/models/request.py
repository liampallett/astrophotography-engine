from pydantic import BaseModel, Field
from typing import Optional
from datetime import date as DateType, time as TimeType

class LocationModel(BaseModel):
    """Location information for observation"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    timezone: str = Field(..., example="Europe/London", description="IANA timezone identifier")
    elevation: Optional[float] = Field(0, ge=0, description="Elevation in meters")

class EquipmentModel(BaseModel):
    """Telescope, lens, and camera equipment specifications"""
    equipment_type: str = Field("telescope", example="telescope", description="Equipment type: 'telescope' or 'lens'")
    aperture_mm: Optional[float] = Field(None, gt=0, example=200, description="Aperture diameter in millimeters (optional if f_number provided)")
    focal_length_mm: float = Field(..., gt=0, example=1000, description="Focal length in millimeters")
    f_number: Optional[float] = Field(None, gt=0, example=2.0, description="Aperture ratio (f-number), e.g., f/2.0 (optional if aperture_mm provided)")
    sensor_width_mm: float = Field(..., gt=0, example=23.5, description="Camera sensor width in millimeters")
    sensor_height_mm: float = Field(..., gt=0, example=15.6, description="Camera sensor height in millimeters")
    
    def get_aperture_mm(self) -> float:
        """Calculate aperture in mm from either direct value or f-number"""
        if self.aperture_mm is not None:
            return self.aperture_mm
        elif self.f_number is not None:
            # aperture = focal_length / f_number
            return self.focal_length_mm / self.f_number
        else:
            raise ValueError("Either aperture_mm or f_number must be provided")

class ObservationModel(BaseModel):
    """Observation session parameters"""
    date: DateType = Field(..., description="Observation date")
    start_time: TimeType = Field(..., description="Start time of observation")
    duration_hours: float = Field(..., gt=0, le=12, example=4, description="Duration in hours")

class PreferencesModel(BaseModel):
    """User preferences for target selection"""
    min_altitude: float = Field(30, ge=0, le=90, description="Minimum altitude in degrees")
    moon_avoidance_deg: float = Field(30, ge=0, le=90, description="Minimum moon separation in degrees")
    include_planets: bool = Field(True, description="Include planets in recommendations")

class TargetCalculationRequest(BaseModel):
    """Complete request for target calculation"""
    location: LocationModel
    equipment: EquipmentModel
    observation: ObservationModel
    preferences: PreferencesModel
    
    class Config:
        json_schema_extra = {
            "example": {
                "location": {
                    "latitude": 51.5074,
                    "longitude": -0.1278,
                    "timezone": "Europe/London",
                    "elevation": 11
                },
                "equipment": {
                    "equipment_type": "telescope",
                    "aperture_mm": 200,
                    "focal_length_mm": 1000,
                    "sensor_width_mm": 23.5,
                    "sensor_height_mm": 15.6
                },
                "observation": {
                    "date": "2026-05-01",
                    "start_time": "21:00",
                    "duration_hours": 4
                },
                "preferences": {
                    "min_altitude": 30,
                    "moon_avoidance_deg": 30,
                    "include_planets": True
                }
            }
        }

# Made with Bob
