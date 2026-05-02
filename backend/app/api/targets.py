"""
Target calculation and recommendation API endpoints.

This is the main endpoint that integrates visibility calculations, moon data,
target ranking, and equipment matching to provide personalized recommendations.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import List, Dict
import sqlite3
import json
from pathlib import Path

from app.models.request import TargetCalculationRequest
from app.models.response import TargetCalculationResponse, TargetModel, VisibilityModel, MoonDataModel
from app.services.visibility import (
    calculate_target_visibility,
    calculate_moon_separation,
    calculate_moon_data,
    calculate_sun_position
)
from app.services.ranking import (
    calculate_target_score,
    determine_difficulty,
    get_equipment_match_description,
    calculate_field_of_view
)

router = APIRouter()


def get_db_connection():
    """Get database connection."""
    db_path = Path(__file__).parent.parent / "database" / "messier.db"
    return sqlite3.connect(db_path)


@router.post("/calculate", response_model=TargetCalculationResponse)
def calculate_targets(request: TargetCalculationRequest):
    """
    Calculate optimal astrophotography targets based on location, equipment, and preferences.
    
    This endpoint:
    1. Retrieves Messier objects from the database
    2. Calculates visibility for each object
    3. Calculates moon separation and interference
    4. Scores and ranks targets
    5. Returns top recommendations
    
    Returns:
    - targets: List of recommended targets with scores and visibility data
    - moon: Moon phase and position information
    """
    try:
        # Convert request models to dictionaries
        location = request.location.model_dump()
        equipment_dict = request.equipment.model_dump()
        # Ensure aperture_mm is calculated if using f_number
        equipment_dict['aperture_mm'] = request.equipment.get_aperture_mm()
        equipment = equipment_dict
        observation = request.observation.model_dump()
        preferences = request.preferences.model_dump()
        
        # Create observation datetime
        observation_datetime = datetime.combine(
            observation['date'],
            observation['start_time']
        )
        
        # Check if it's nighttime
        sun_data = calculate_sun_position(location, observation_datetime)
        if not sun_data['is_night']:
            raise HTTPException(
                status_code=400,
                detail=f"Observation time is during {sun_data['twilight_type']}. "
                       "Please choose a time when the sun is below -18° (astronomical night)."
            )
        
        # Get moon data
        moon_data = calculate_moon_data(location, observation_datetime)
        
        # Get all Messier objects from database
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM messier_objects ORDER BY messier_number")
        db_objects = cursor.fetchall()
        conn.close()
        
        # Calculate visibility and score for each target
        scored_targets = []
        
        for db_obj in db_objects:
            target = dict(db_obj)
            target['best_months'] = json.loads(target['best_months'])
            
            # Calculate visibility
            visibility = calculate_target_visibility(
                target,
                location,
                observation_datetime,
                observation['duration_hours']
            )
            
            # Skip if not visible (below minimum altitude)
            if not visibility['is_visible']:
                continue
            
            # Check minimum altitude preference
            if visibility['peak_altitude'] < preferences['min_altitude']:
                continue
            
            # Calculate moon separation
            moon_separation = calculate_moon_separation(
                target,
                location,
                observation_datetime
            )
            
            # Check moon avoidance preference
            if moon_separation < preferences['moon_avoidance_deg']:
                continue
            
            # Calculate score
            score = calculate_target_score(
                target,
                visibility,
                moon_separation,
                equipment,
                weather=None  # Weather integration can be added later
            )
            
            # Determine difficulty
            difficulty = determine_difficulty(target, equipment)
            
            # Calculate equipment match
            fov = calculate_field_of_view(equipment)
            size_ratio = target['size_arcmin'] / fov if fov > 0 else 0
            equipment_match = get_equipment_match_description(
                calculate_target_score(target, visibility, moon_separation, equipment)
            )
            
            # Create target model
            target_model = TargetModel(
                id=target['id'],
                name=target['name'],
                type=target['type'],
                score=score,
                visibility=VisibilityModel(
                    peak_time=visibility['peak_time'],
                    peak_altitude=visibility['peak_altitude'],
                    duration_hours=visibility['duration_hours']
                ),
                moon_separation=moon_separation,
                weather_score=None,
                equipment_match=equipment_match,
                magnitude=target['magnitude'],
                size_arcmin=target['size_arcmin'],
                constellation=target['constellation'],
                difficulty=difficulty,
                description=target['description']
            )
            
            scored_targets.append(target_model)
        
        # Sort by score (highest first) and take top 10
        scored_targets.sort(key=lambda t: t.score, reverse=True)
        top_targets = scored_targets[:10]
        
        if not top_targets:
            raise HTTPException(
                status_code=404,
                detail="No suitable targets found for the given criteria. "
                       "Try adjusting your preferences or observation time."
            )
        
        # Create moon data model
        moon_model = MoonDataModel(
            phase=moon_data['phase'],
            illumination=moon_data['illumination'],
            rise_time=None,  # Rise/set times would require additional calculation
            set_time=None
        )
        
        # Return response
        return TargetCalculationResponse(
            targets=top_targets,
            moon=moon_model,
            observation_date=observation['date'].isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating targets: {str(e)}"
        )


@router.get("/visibility/{object_id}")
def get_target_visibility(
    object_id: str,
    latitude: float,
    longitude: float,
    date: str,
    time: str = "21:00:00",
    duration_hours: float = 4,
    elevation: float = 0
):
    """
    Get detailed visibility information for a specific target.
    
    Returns:
    - Visibility data over the observation window
    - Peak altitude and time
    - Moon separation
    - Sun position (to verify it's nighttime)
    """
    try:
        # Get target from database
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM messier_objects WHERE id = ?", (object_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"Object {object_id} not found"
            )
        
        target = dict(row)
        
        # Create location and observation time
        location = {
            'latitude': latitude,
            'longitude': longitude,
            'elevation': elevation
        }
        
        observation_time = datetime.fromisoformat(f"{date}T{time}")
        
        # Calculate visibility
        visibility = calculate_target_visibility(
            target,
            location,
            observation_time,
            duration_hours
        )
        
        # Calculate moon data
        moon_data = calculate_moon_data(location, observation_time)
        moon_separation = calculate_moon_separation(target, location, observation_time)
        
        # Calculate sun position
        sun_data = calculate_sun_position(location, observation_time)
        
        return {
            'object': {
                'id': target['id'],
                'name': target['name'],
                'type': target['type'],
                'magnitude': target['magnitude'],
                'size_arcmin': target['size_arcmin']
            },
            'visibility': visibility,
            'moon': {
                **moon_data,
                'separation_from_target': moon_separation
            },
            'sun': sun_data,
            'observation_time': observation_time.isoformat(),
            'location': location
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating visibility: {str(e)}")


@router.get("/tonight")
def get_tonight_targets(
    latitude: float,
    longitude: float,
    aperture_mm: float = 200,
    focal_length_mm: float = 1000,
    sensor_width_mm: float = 23.5,
    sensor_height_mm: float = 15.6,
    elevation: float = 0
):
    """
    Quick endpoint to get tonight's best targets with minimal input.
    
    Uses sensible defaults:
    - Observation starts at 21:00 local time
    - Duration: 4 hours
    - Minimum altitude: 30°
    - Moon avoidance: 30°
    """
    try:
        # Use today's date and 21:00 as start time
        today = datetime.now().date()
        start_time = datetime.strptime("21:00:00", "%H:%M:%S").time()
        
        # Create request
        from app.models.request import (
            LocationModel, EquipmentModel, ObservationModel, PreferencesModel
        )
        
        request = TargetCalculationRequest(
            location=LocationModel(
                latitude=latitude,
                longitude=longitude,
                timezone="UTC",  # Simplified for quick query
                elevation=elevation
            ),
            equipment=EquipmentModel(
                aperture_mm=aperture_mm,
                focal_length_mm=focal_length_mm,
                sensor_width_mm=sensor_width_mm,
                sensor_height_mm=sensor_height_mm
            ),
            observation=ObservationModel(
                date=today,
                start_time=start_time,
                duration_hours=4
            ),
            preferences=PreferencesModel(
                min_altitude=30,
                moon_avoidance_deg=30,
                include_planets=False
            )
        )
        
        # Calculate targets
        return calculate_targets(request)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting tonight's targets: {str(e)}"
        )

# Made with Bob
