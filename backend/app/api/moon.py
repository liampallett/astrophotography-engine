"""
Moon data API endpoints.

Provides moon position, phase, and illumination data for astrophotography planning.
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional
from app.services.visibility import calculate_moon_data

router = APIRouter()


@router.get("/")
def get_moon_info(
    latitude: float = Query(..., ge=-90, le=90, description="Observer latitude in degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Observer longitude in degrees"),
    date: Optional[str] = Query(None, description="Date in ISO format (YYYY-MM-DD), defaults to now"),
    time: Optional[str] = Query(None, description="Time in ISO format (HH:MM:SS), defaults to now"),
    elevation: Optional[float] = Query(0, ge=0, description="Observer elevation in meters")
):
    """
    Get moon position, phase, and illumination data.
    
    Returns:
    - altitude: Moon altitude in degrees
    - azimuth: Moon azimuth in degrees
    - illumination: Fraction illuminated (0-1)
    - phase: Phase name (new, waxing_crescent, first_quarter, waxing_gibbous, full)
    - phase_angle: Phase angle in degrees
    """
    try:
        # Parse date and time
        if date and time:
            observation_time = datetime.fromisoformat(f"{date}T{time}")
        elif date:
            observation_time = datetime.fromisoformat(f"{date}T00:00:00")
        else:
            observation_time = datetime.now()
        
        # Create location dictionary
        location = {
            'latitude': latitude,
            'longitude': longitude,
            'elevation': elevation
        }
        
        # Calculate moon data
        moon_data = calculate_moon_data(location, observation_time)
        
        return {
            **moon_data,
            'observation_time': observation_time.isoformat(),
            'location': {
                'latitude': latitude,
                'longitude': longitude,
                'elevation': elevation
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating moon data: {str(e)}")


@router.get("/phase")
def get_moon_phase(
    date: Optional[str] = Query(None, description="Date in ISO format (YYYY-MM-DD), defaults to now")
):
    """
    Get simplified moon phase information for a given date.
    
    This endpoint doesn't require location since phase is the same everywhere on Earth.
    
    Returns:
    - phase: Phase name
    - illumination: Fraction illuminated (0-1)
    - phase_angle: Phase angle in degrees
    """
    try:
        # Parse date
        if date:
            observation_time = datetime.fromisoformat(f"{date}T12:00:00")
        else:
            observation_time = datetime.now()
        
        # Use a default location (doesn't affect phase calculation significantly)
        location = {
            'latitude': 0,
            'longitude': 0,
            'elevation': 0
        }
        
        # Calculate moon data
        moon_data = calculate_moon_data(location, observation_time)
        
        return {
            'phase': moon_data['phase'],
            'illumination': moon_data['illumination'],
            'phase_angle': moon_data['phase_angle'],
            'date': observation_time.date().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating moon phase: {str(e)}")

# Made with Bob
