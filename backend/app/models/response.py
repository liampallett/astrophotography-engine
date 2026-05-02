from pydantic import BaseModel, Field
from typing import List, Optional

class VisibilityModel(BaseModel):
    """Visibility information for a target"""
    peak_time: str = Field(..., description="Time of peak altitude (ISO format)")
    peak_altitude: float = Field(..., description="Peak altitude in degrees")
    duration_hours: float = Field(..., description="Duration above minimum altitude")

class TargetModel(BaseModel):
    """Complete target information with scoring"""
    id: str = Field(..., description="Messier object ID (e.g., M31)")
    name: str = Field(..., description="Common name")
    type: str = Field(..., description="Object type (galaxy, nebula, etc.)")
    score: float = Field(..., description="Overall suitability score (0-100)")
    visibility: VisibilityModel
    moon_separation: float = Field(..., description="Angular separation from moon in degrees")
    weather_score: Optional[float] = Field(None, description="Weather suitability score (0-100)")
    equipment_match: str = Field(..., description="Equipment compatibility (excellent, good, fair, poor)")
    magnitude: float = Field(..., description="Visual magnitude")
    size_arcmin: float = Field(..., description="Angular size in arcminutes")
    constellation: str = Field(..., description="Constellation")
    difficulty: str = Field(..., description="Difficulty level (easy, moderate, challenging)")
    description: str = Field(..., description="Object description")
    imaging_notes: Optional[str] = Field(None, description="Astrophotography tips")

class MoonDataModel(BaseModel):
    """Moon information for the observation period"""
    phase: str = Field(..., description="Moon phase name")
    illumination: float = Field(..., ge=0, le=1, description="Illumination fraction (0-1)")
    rise_time: Optional[str] = Field(None, description="Moonrise time (ISO format)")
    set_time: Optional[str] = Field(None, description="Moonset time (ISO format)")
    altitude: Optional[float] = Field(None, description="Current altitude in degrees")
    azimuth: Optional[float] = Field(None, description="Current azimuth in degrees")

class TargetCalculationResponse(BaseModel):
    """Response containing recommended targets and conditions"""
    targets: List[TargetModel] = Field(..., description="List of recommended targets")
    moon: MoonDataModel = Field(..., description="Moon data for the observation period")
    observation_date: str = Field(..., description="Observation date")
    location_name: Optional[str] = Field(None, description="Location name if available")
    
    class Config:
        json_schema_extra = {
            "example": {
                "targets": [
                    {
                        "id": "M31",
                        "name": "Andromeda Galaxy",
                        "type": "galaxy",
                        "score": 95.0,
                        "visibility": {
                            "peak_time": "2026-05-01T23:30:00",
                            "peak_altitude": 65.0,
                            "duration_hours": 3.5
                        },
                        "moon_separation": 85.0,
                        "weather_score": 80.0,
                        "equipment_match": "excellent",
                        "magnitude": 3.4,
                        "size_arcmin": 178.0,
                        "constellation": "Andromeda",
                        "difficulty": "easy",
                        "description": "The nearest major galaxy to the Milky Way",
                        "imaging_notes": "Wide field recommended"
                    }
                ],
                "moon": {
                    "phase": "waxing_gibbous",
                    "illumination": 0.73,
                    "rise_time": "2026-05-01T18:45:00",
                    "set_time": "2026-05-02T04:30:00",
                    "altitude": 45.0,
                    "azimuth": 180.0
                },
                "observation_date": "2026-05-01",
                "location_name": "London, UK"
            }
        }

class MessierObjectResponse(BaseModel):
    """Single Messier object details"""
    id: str
    messier_number: int
    ngc_id: Optional[str]
    name: str
    type: str
    ra_hours: float
    dec_degrees: float
    magnitude: float
    size_arcmin: float
    constellation: str
    best_months: List[str]
    min_aperture_mm: int
    difficulty: str
    description: str
    imaging_notes: Optional[str]
    distance_ly: Optional[float]

class MessierCatalogueResponse(BaseModel):
    """Response containing multiple Messier objects"""
    objects: List[MessierObjectResponse]
    count: int

# Made with Bob
