"""
Visibility calculations for celestial objects using Astropy.

This module provides functions to calculate when and how well celestial objects
are visible from a given location on Earth.
"""

from astropy.coordinates import SkyCoord, EarthLocation, AltAz, GeocentricMeanEcliptic, get_sun, get_moon
from astropy.time import Time
import astropy.units as u
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import numpy as np


def calculate_target_visibility(
    target: Dict,
    location: Dict,
    observation_time: datetime,
    duration_hours: float = 4
) -> Dict:
    """
    Calculate visibility window for a celestial target.
    
    Args:
        target: Dictionary with 'ra_hours' and 'dec_degrees' keys
        location: Dictionary with 'latitude', 'longitude', and optional 'elevation' keys
        observation_time: Start time for observation window
        duration_hours: Duration of observation window in hours
        
    Returns:
        Dictionary containing:
        - peak_time: ISO format time of peak altitude
        - peak_altitude: Maximum altitude in degrees
        - peak_azimuth: Azimuth at peak altitude in degrees
        - duration_hours: Hours target is above minimum altitude
        - visibility_data: List of time/altitude/azimuth points
        - is_visible: Boolean indicating if target rises above 30 degrees
    """
    
    # Create observer location
    observer = EarthLocation(
        lat=location['latitude'] * u.deg,
        lon=location['longitude'] * u.deg,
        height=location.get('elevation', 0) * u.m
    )
    
    # Target coordinates
    target_coord = SkyCoord(
        ra=target['ra_hours'] * u.hourangle,
        dec=target['dec_degrees'] * u.deg
    )
    
    # Calculate visibility over time window
    visibility_data = []
    current_time = observation_time
    end_time = current_time + timedelta(hours=duration_hours)
    time_step = timedelta(minutes=15)
    
    altitudes = []
    times = []
    
    while current_time < end_time:
        time_astropy = Time(current_time)
        altaz_frame = AltAz(obstime=time_astropy, location=observer)
        target_altaz = target_coord.transform_to(altaz_frame)
        
        altitude = float(target_altaz.alt.deg)
        azimuth = float(target_altaz.az.deg)
        
        visibility_data.append({
            'time': current_time.isoformat(),
            'altitude': altitude,
            'azimuth': azimuth
        })
        
        altitudes.append(altitude)
        times.append(current_time)
        
        current_time += time_step
    
    # Find peak altitude
    peak_index = np.argmax(altitudes)
    peak_altitude = altitudes[peak_index]
    peak_time = times[peak_index]
    peak_azimuth = visibility_data[peak_index]['azimuth']
    
    # Calculate duration above minimum altitude (30 degrees)
    min_altitude = 30.0
    above_min = [alt >= min_altitude for alt in altitudes]
    duration_above_min = sum(above_min) * 0.25  # 15-minute intervals
    
    return {
        'peak_time': peak_time.isoformat(),
        'peak_altitude': round(peak_altitude, 2),
        'peak_azimuth': round(peak_azimuth, 2),
        'duration_hours': round(duration_above_min, 2),
        'visibility_data': visibility_data,
        'is_visible': peak_altitude >= min_altitude
    }


def calculate_moon_separation(
    target: Dict,
    location: Dict,
    observation_time: datetime
) -> float:
    """
    Calculate angular separation between target and moon.
    
    Args:
        target: Dictionary with 'ra_hours' and 'dec_degrees' keys
        location: Dictionary with 'latitude', 'longitude', and optional 'elevation' keys
        observation_time: Time for calculation
        
    Returns:
        Angular separation in degrees
    """
    
    observer = EarthLocation(
        lat=location['latitude'] * u.deg,
        lon=location['longitude'] * u.deg,
        height=location.get('elevation', 0) * u.m
    )
    
    time_astropy = Time(observation_time)
    
    # Target coordinates
    target_coord = SkyCoord(
        ra=target['ra_hours'] * u.hourangle,
        dec=target['dec_degrees'] * u.deg
    )
    
    # Moon coordinates
    moon_coord = get_moon(time_astropy, location=observer)
    
    # Calculate separation
    separation = target_coord.separation(moon_coord)
    
    return round(float(separation.deg), 2)


def calculate_moon_data(
    location: Dict,
    observation_time: datetime
) -> Dict:
    """
    Calculate moon position, phase, and illumination.
    
    Args:
        location: Dictionary with 'latitude', 'longitude', and optional 'elevation' keys
        observation_time: Time for calculation
        
    Returns:
        Dictionary containing:
        - altitude: Moon altitude in degrees
        - azimuth: Moon azimuth in degrees
        - illumination: Fraction illuminated (0-1)
        - phase: Phase name (new, waxing_crescent, first_quarter, etc.)
        - phase_angle: Phase angle in degrees
    """
    
    observer = EarthLocation(
        lat=location['latitude'] * u.deg,
        lon=location['longitude'] * u.deg,
        height=location.get('elevation', 0) * u.m
    )
    
    time_astropy = Time(observation_time)
    
    # Get moon position
    moon_coord = get_moon(time_astropy, location=observer)
    altaz_frame = AltAz(obstime=time_astropy, location=observer)
    moon_altaz = moon_coord.transform_to(altaz_frame)
    
    # Get sun position for phase calculation
    sun_coord = get_sun(time_astropy)
    
    # Calculate phase angle (angular separation, 0-180°) for illumination
    phase_angle = sun_coord.separation(moon_coord)
    phase_angle_deg = float(phase_angle.deg)

    # Calculate illumination fraction
    # Illumination = (1 + cos(phase_angle)) / 2
    illumination = (1 + np.cos(np.radians(phase_angle_deg))) / 2

    # Compute ecliptic elongation (0-360°) to distinguish waxing vs waning
    ecliptic_frame = GeocentricMeanEcliptic(equinox=time_astropy)
    moon_lon = moon_coord.transform_to(ecliptic_frame).lon
    sun_lon = sun_coord.transform_to(ecliptic_frame).lon
    elongation_deg = float((moon_lon - sun_lon).wrap_at(360 * u.deg).deg)

    # Determine phase name
    phase_name = get_moon_phase_name(elongation_deg)
    
    return {
        'altitude': round(float(moon_altaz.alt.deg), 2),
        'azimuth': round(float(moon_altaz.az.deg), 2),
        'illumination': round(float(illumination), 3),
        'phase': phase_name,
        'phase_angle': round(phase_angle_deg, 2)
    }


def get_moon_phase_name(elongation: float) -> str:
    """
    Convert ecliptic elongation (0-360°) to phase name.

    Elongation is the moon's ecliptic longitude minus the sun's, wrapped to
    0-360°.  0° = new moon, 180° = full moon; 0-180° = waxing, 180-360° = waning.

    Args:
        elongation: Moon elongation in degrees (0-360)

    Returns:
        Phase name string
    """
    if elongation < 22.5 or elongation >= 337.5:
        return "new"
    elif elongation < 67.5:
        return "waxing_crescent"
    elif elongation < 112.5:
        return "first_quarter"
    elif elongation < 157.5:
        return "waxing_gibbous"
    elif elongation < 202.5:
        return "full"
    elif elongation < 247.5:
        return "waning_gibbous"
    elif elongation < 292.5:
        return "last_quarter"
    else:
        return "waning_crescent"


def calculate_sun_position(
    location: Dict,
    observation_time: datetime
) -> Dict:
    """
    Calculate sun position for twilight calculations.
    
    Args:
        location: Dictionary with 'latitude', 'longitude', and optional 'elevation' keys
        observation_time: Time for calculation
        
    Returns:
        Dictionary containing:
        - altitude: Sun altitude in degrees
        - azimuth: Sun azimuth in degrees
        - is_night: Boolean indicating if it's astronomical night (sun < -18°)
        - twilight_type: Type of twilight (day, civil, nautical, astronomical, night)
    """
    
    observer = EarthLocation(
        lat=location['latitude'] * u.deg,
        lon=location['longitude'] * u.deg,
        height=location.get('elevation', 0) * u.m
    )
    
    time_astropy = Time(observation_time)
    
    # Get sun position
    sun_coord = get_sun(time_astropy)
    altaz_frame = AltAz(obstime=time_astropy, location=observer)
    sun_altaz = sun_coord.transform_to(altaz_frame)
    
    sun_altitude = float(sun_altaz.alt.deg)
    
    # Determine twilight type
    if sun_altitude > 0:
        twilight_type = "day"
    elif sun_altitude > -6:
        twilight_type = "civil_twilight"
    elif sun_altitude > -12:
        twilight_type = "nautical_twilight"
    elif sun_altitude > -18:
        twilight_type = "astronomical_twilight"
    else:
        twilight_type = "night"
    
    return {
        'altitude': round(sun_altitude, 2),
        'azimuth': round(float(sun_altaz.az.deg), 2),
        'is_night': sun_altitude < -18,
        'twilight_type': twilight_type
    }


def find_optimal_observation_window(
    target: Dict,
    location: Dict,
    date: datetime,
    min_altitude: float = 30.0
) -> Optional[Tuple[datetime, datetime]]:
    """
    Find the optimal observation window for a target on a given night.
    
    Args:
        target: Dictionary with 'ra_hours' and 'dec_degrees' keys
        location: Dictionary with 'latitude', 'longitude', and optional 'elevation' keys
        date: Date to check (time will be set to sunset)
        min_altitude: Minimum altitude in degrees for observation
        
    Returns:
        Tuple of (start_time, end_time) for optimal window, or None if not visible
    """
    
    # Check visibility throughout the night (sunset to sunrise, roughly 18:00 to 06:00)
    start_time = date.replace(hour=18, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=12)
    
    observer = EarthLocation(
        lat=location['latitude'] * u.deg,
        lon=location['longitude'] * u.deg,
        height=location.get('elevation', 0) * u.m
    )
    
    target_coord = SkyCoord(
        ra=target['ra_hours'] * u.hourangle,
        dec=target['dec_degrees'] * u.deg
    )
    
    # Find continuous window above minimum altitude during astronomical night
    current_time = start_time
    window_start = None
    best_window = None
    max_duration = 0
    
    while current_time < end_time:
        time_astropy = Time(current_time)
        
        # Check if it's astronomical night
        sun_data = calculate_sun_position(location, current_time)
        
        if sun_data['is_night']:
            # Check target altitude
            altaz_frame = AltAz(obstime=time_astropy, location=observer)
            target_altaz = target_coord.transform_to(altaz_frame)
            altitude = float(target_altaz.alt.deg)
            
            if altitude >= min_altitude:
                if window_start is None:
                    window_start = current_time
            else:
                if window_start is not None:
                    duration = (current_time - window_start).total_seconds() / 3600
                    if duration > max_duration:
                        max_duration = duration
                        best_window = (window_start, current_time)
                    window_start = None
        else:
            if window_start is not None:
                duration = (current_time - window_start).total_seconds() / 3600
                if duration > max_duration:
                    max_duration = duration
                    best_window = (window_start, current_time)
                window_start = None
        
        current_time += timedelta(minutes=15)
    
    # Check if window extends to end time
    if window_start is not None:
        duration = (end_time - window_start).total_seconds() / 3600
        if duration > max_duration:
            best_window = (window_start, end_time)
    
    return best_window

# Made with Bob
