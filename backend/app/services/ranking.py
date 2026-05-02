"""
Target ranking and scoring algorithms.

This module provides functions to score and rank astrophotography targets
based on visibility, brightness, equipment match, moon interference, and weather.
"""

from typing import Dict, List
import math


def calculate_target_score(
    target: Dict,
    visibility: Dict,
    moon_separation: float,
    equipment: Dict,
    weather: Dict = None
) -> float:
    """
    Calculate overall score for a target (0-100).
    
    Scoring factors:
    - Visibility (40%): How high in the sky
    - Brightness (25%): Easier to image
    - Size/Equipment match (15%): Fits in field of view
    - Moon impact (10%): Moon interference
    - Weather (10%): Cloud cover (if available)
    
    Args:
        target: Dictionary with magnitude, size_arcmin, etc.
        visibility: Dictionary with peak_altitude, duration_hours
        moon_separation: Angular separation from moon in degrees
        equipment: Dictionary with aperture, focal_length, sensor dimensions
        weather: Optional dictionary with cloud_cover percentage
        
    Returns:
        Overall score from 0-100
    """
    
    # Visibility score (40%) - based on peak altitude
    altitude_score = calculate_altitude_score(visibility['peak_altitude'])
    visibility_score = altitude_score * 0.4
    
    # Brightness score (25%) - based on magnitude
    brightness_score = calculate_brightness_score(target['magnitude'])
    brightness_weight = brightness_score * 0.25
    
    # Size/Equipment match score (15%)
    fov = calculate_field_of_view(equipment)
    size_score = calculate_size_match_score(target['size_arcmin'], fov)
    size_weight = size_score * 0.15
    
    # Moon impact score (10%) - higher separation is better
    moon_score = calculate_moon_impact_score(moon_separation)
    moon_weight = moon_score * 0.1
    
    # Weather score (10%) - if available
    if weather and 'cloud_cover' in weather:
        weather_score = 100 - weather['cloud_cover']
        weather_weight = weather_score * 0.1
    else:
        # If no weather data, redistribute weight to other factors
        weather_weight = 0
        # Adjust other weights proportionally
        total_weight = 0.9
        visibility_score = (visibility_score / total_weight) * 1.0
        brightness_weight = (brightness_weight / total_weight) * 1.0
        size_weight = (size_weight / total_weight) * 1.0
        moon_weight = (moon_weight / total_weight) * 1.0
    
    total_score = (
        visibility_score +
        brightness_weight +
        size_weight +
        moon_weight +
        weather_weight
    )
    
    return round(total_score, 1)


def calculate_altitude_score(altitude: float) -> float:
    """
    Calculate score based on altitude (0-100).
    
    Higher altitude = better seeing, less atmospheric distortion.
    - Below 30°: Poor (0-30 points)
    - 30-60°: Good (30-80 points)
    - Above 60°: Excellent (80-100 points)
    
    Args:
        altitude: Altitude in degrees
        
    Returns:
        Score from 0-100
    """
    if altitude < 0:
        return 0
    elif altitude < 30:
        # Linear scale from 0 to 30
        return altitude
    elif altitude < 60:
        # Linear scale from 30 to 80
        return 30 + ((altitude - 30) / 30) * 50
    else:
        # Linear scale from 80 to 100
        return 80 + ((altitude - 60) / 30) * 20


def calculate_brightness_score(magnitude: float) -> float:
    """
    Calculate score based on visual magnitude (0-100).
    
    Lower magnitude = brighter = easier to image.
    - Mag < 5: Excellent (90-100 points)
    - Mag 5-8: Good (60-90 points)
    - Mag 8-10: Moderate (30-60 points)
    - Mag > 10: Challenging (0-30 points)
    
    Args:
        magnitude: Visual magnitude
        
    Returns:
        Score from 0-100
    """
    if magnitude < 5:
        return min(100, 100 - (magnitude * 2))
    elif magnitude < 8:
        return 90 - ((magnitude - 5) / 3) * 30
    elif magnitude < 10:
        return 60 - ((magnitude - 8) / 2) * 30
    else:
        return max(0, 30 - ((magnitude - 10) * 3))


def calculate_size_match_score(object_size: float, fov: float) -> float:
    """
    Calculate how well object size matches field of view (0-100).
    
    Ideal: Object takes up 30-70% of FOV
    - Too small: Hard to see details
    - Too large: Won't fit in frame
    
    Args:
        object_size: Object size in arcminutes
        fov: Field of view in arcminutes
        
    Returns:
        Score from 0-100
    """
    if fov == 0:
        return 50  # Default score if FOV can't be calculated
    
    ratio = object_size / fov
    
    if ratio < 0.1:
        # Too small - linear scale 0-50
        return ratio * 500
    elif ratio < 0.3:
        # Getting better - linear scale 50-90
        return 50 + ((ratio - 0.1) / 0.2) * 40
    elif ratio < 0.7:
        # Ideal range - 90-100
        return 90 + ((ratio - 0.3) / 0.4) * 10
    elif ratio < 1.0:
        # Getting too large - 90-70
        return 90 - ((ratio - 0.7) / 0.3) * 20
    elif ratio < 1.5:
        # Too large but still usable - 70-30
        return 70 - ((ratio - 1.0) / 0.5) * 40
    else:
        # Way too large - 30-0
        return max(0, 30 - ((ratio - 1.5) * 20))


def calculate_moon_impact_score(separation: float) -> float:
    """
    Calculate score based on moon separation (0-100).
    
    Greater separation = less light pollution from moon.
    - < 30°: Poor (0-40 points)
    - 30-60°: Moderate (40-70 points)
    - > 60°: Good (70-100 points)
    
    Args:
        separation: Angular separation in degrees
        
    Returns:
        Score from 0-100
    """
    if separation < 30:
        return (separation / 30) * 40
    elif separation < 60:
        return 40 + ((separation - 30) / 30) * 30
    else:
        return 70 + ((separation - 60) / 90) * 30


def calculate_field_of_view(equipment: Dict) -> float:
    """
    Calculate field of view in arcminutes.
    
    FOV = 2 * arctan(sensor_size / (2 * focal_length)) * (180 / π) * 60
    
    Args:
        equipment: Dictionary with focal_length_mm, sensor_width_mm, sensor_height_mm
        
    Returns:
        Field of view in arcminutes (diagonal)
    """
    focal_length = equipment.get('focal_length_mm', 0)
    sensor_width = equipment.get('sensor_width_mm', 0)
    sensor_height = equipment.get('sensor_height_mm', 0)
    
    if focal_length == 0 or sensor_width == 0 or sensor_height == 0:
        return 0
    
    # Calculate diagonal sensor size
    sensor_diagonal = math.sqrt(sensor_width**2 + sensor_height**2)
    
    # Calculate FOV in degrees
    fov_radians = 2 * math.atan(sensor_diagonal / (2 * focal_length))
    fov_degrees = math.degrees(fov_radians)
    
    # Convert to arcminutes
    fov_arcminutes = fov_degrees * 60
    
    return round(fov_arcminutes, 2)


def determine_difficulty(target: Dict, equipment: Dict = None) -> str:
    """
    Determine difficulty level for beginners.
    
    Factors:
    - Magnitude (brightness)
    - Size
    - Type of object
    - Required aperture
    
    Args:
        target: Dictionary with magnitude, size_arcmin, type, min_aperture_mm
        equipment: Optional equipment dictionary with aperture_mm
        
    Returns:
        Difficulty string: 'easy', 'moderate', or 'challenging'
    """
    magnitude = target.get('magnitude', 10)
    size = target.get('size_arcmin', 0)
    obj_type = target.get('type', '')
    min_aperture = target.get('min_aperture_mm', 0)
    
    # Check if user's equipment meets minimum requirements
    if equipment and 'aperture_mm' in equipment:
        user_aperture = equipment['aperture_mm']
        if user_aperture < min_aperture:
            return 'challenging'
    
    # Easy targets: Bright and large
    if magnitude < 6 and size > 30:
        return 'easy'
    
    # Moderate targets: Medium brightness or size
    if magnitude < 9 and size > 10:
        return 'moderate'
    
    # Special cases for object types
    if obj_type == 'open_cluster' and magnitude < 7:
        return 'easy'
    
    if obj_type == 'planetary_nebula' and magnitude > 9:
        return 'challenging'
    
    # Default to challenging for faint or small objects
    return 'challenging'


def get_equipment_match_description(score: float) -> str:
    """
    Get human-readable description of equipment match.
    
    Args:
        score: Equipment match score (0-100)
        
    Returns:
        Description string
    """
    if score >= 90:
        return "excellent"
    elif score >= 70:
        return "good"
    elif score >= 50:
        return "fair"
    else:
        return "poor"


def rank_targets(
    targets: List[Dict],
    location: Dict,
    equipment: Dict,
    observation_time,
    weather: Dict = None
) -> List[Dict]:
    """
    Rank a list of targets by their scores.
    
    This is a helper function that would integrate with visibility calculations.
    
    Args:
        targets: List of target dictionaries
        location: Location dictionary
        equipment: Equipment dictionary
        observation_time: Observation datetime
        weather: Optional weather dictionary
        
    Returns:
        List of targets sorted by score (highest first)
    """
    # This would integrate with visibility.py functions
    # For now, return a placeholder
    # In actual implementation, this would:
    # 1. Calculate visibility for each target
    # 2. Calculate moon separation for each target
    # 3. Score each target
    # 4. Sort by score
    
    return sorted(targets, key=lambda t: t.get('score', 0), reverse=True)


def calculate_imaging_time_recommendation(
    target: Dict,
    equipment: Dict,
    conditions: Dict
) -> Dict:
    """
    Recommend imaging time based on target and conditions.
    
    Args:
        target: Target dictionary with magnitude, type
        equipment: Equipment dictionary with aperture_mm
        conditions: Dictionary with moon_illumination, weather conditions
        
    Returns:
        Dictionary with recommended exposure time and total integration time
    """
    magnitude = target.get('magnitude', 10)
    obj_type = target.get('type', '')
    aperture = equipment.get('aperture_mm', 100)
    
    # Base exposure time (seconds) - brighter objects need less time
    if magnitude < 5:
        base_exposure = 60
    elif magnitude < 8:
        base_exposure = 120
    else:
        base_exposure = 180
    
    # Adjust for aperture (larger aperture = shorter exposure)
    aperture_factor = 100 / aperture
    adjusted_exposure = base_exposure * aperture_factor
    
    # Adjust for moon (bright moon = shorter exposures to avoid saturation)
    moon_illumination = conditions.get('moon_illumination', 0)
    if moon_illumination > 0.5:
        adjusted_exposure *= 0.7
    
    # Recommended number of frames
    if obj_type in ['galaxy', 'nebula']:
        num_frames = 50  # Deep sky objects need more integration
    else:
        num_frames = 30
    
    total_time = (adjusted_exposure * num_frames) / 3600  # Convert to hours
    
    return {
        'exposure_seconds': round(adjusted_exposure, 1),
        'num_frames': num_frames,
        'total_hours': round(total_time, 2),
        'recommendation': f"{num_frames} frames of {round(adjusted_exposure)}s each"
    }

# Made with Bob
