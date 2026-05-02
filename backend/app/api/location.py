"""
Location services API endpoints.

Provides geocoding, timezone detection, and location-based utilities.
"""

from fastapi import APIRouter, HTTPException, Query
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from typing import Optional
import pytz
from timezonefinder import TimezoneFinder

router = APIRouter()

# Initialize geocoder
geolocator = Nominatim(user_agent="astrophotography-target-finder")
tf = TimezoneFinder()


@router.get("/geocode")
def geocode_address(
    address: str = Query(..., description="Address or place name to geocode"),
    language: str = Query("en", description="Language for results")
):
    """
    Convert an address or place name to coordinates.
    
    Examples:
    - "London, UK"
    - "New York City"
    - "Tokyo, Japan"
    - "51.5074, -0.1278" (coordinates also work)
    
    Returns:
    - latitude: Latitude in degrees
    - longitude: Longitude in degrees
    - timezone: IANA timezone identifier
    - elevation: Estimated elevation in meters (approximate)
    - display_name: Full formatted address
    - country: Country name
    """
    try:
        # Try to geocode the address
        location = geolocator.geocode(address, language=language, timeout=10)
        
        if not location:
            raise HTTPException(
                status_code=404,
                detail=f"Could not find location for address: {address}"
            )
        
        latitude = location.latitude
        longitude = location.longitude
        
        # Get timezone
        timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
        if not timezone_str:
            timezone_str = "UTC"
        
        # Extract country from address components
        address_parts = location.address.split(", ")
        country = address_parts[-1] if address_parts else "Unknown"
        
        # Estimate elevation (this is approximate - for better accuracy, use elevation API)
        # For now, we'll return 0 and note it should be updated by user if needed
        elevation = 0
        
        return {
            "latitude": round(latitude, 6),
            "longitude": round(longitude, 6),
            "timezone": timezone_str,
            "elevation": elevation,
            "display_name": location.address,
            "country": country,
            "raw": {
                "lat": latitude,
                "lon": longitude,
                "boundingbox": location.raw.get("boundingbox", [])
            }
        }
        
    except GeocoderTimedOut:
        raise HTTPException(
            status_code=504,
            detail="Geocoding service timed out. Please try again."
        )
    except GeocoderServiceError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Geocoding service error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error geocoding address: {str(e)}"
        )


@router.get("/reverse")
def reverse_geocode(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in degrees"),
    language: str = Query("en", description="Language for results")
):
    """
    Convert coordinates to an address.
    
    Returns:
    - display_name: Full formatted address
    - city: City name (if available)
    - country: Country name
    - timezone: IANA timezone identifier
    """
    try:
        # Reverse geocode
        location = geolocator.reverse(
            f"{latitude}, {longitude}",
            language=language,
            timeout=10
        )
        
        if not location:
            raise HTTPException(
                status_code=404,
                detail=f"Could not find address for coordinates: {latitude}, {longitude}"
            )
        
        # Get timezone
        timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
        if not timezone_str:
            timezone_str = "UTC"
        
        # Extract address components
        address = location.raw.get("address", {})
        city = (
            address.get("city") or
            address.get("town") or
            address.get("village") or
            address.get("hamlet") or
            "Unknown"
        )
        country = address.get("country", "Unknown")
        
        return {
            "display_name": location.address,
            "city": city,
            "country": country,
            "timezone": timezone_str,
            "latitude": latitude,
            "longitude": longitude,
            "address_components": address
        }
        
    except GeocoderTimedOut:
        raise HTTPException(
            status_code=504,
            detail="Geocoding service timed out. Please try again."
        )
    except GeocoderServiceError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Geocoding service error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reverse geocoding: {str(e)}"
        )


@router.get("/timezone")
def get_timezone(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in degrees")
):
    """
    Get timezone information for coordinates.
    
    Returns:
    - timezone: IANA timezone identifier
    - utc_offset: Current UTC offset in hours
    - dst_active: Whether daylight saving time is currently active
    """
    try:
        # Get timezone
        timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
        
        if not timezone_str:
            return {
                "timezone": "UTC",
                "utc_offset": 0,
                "dst_active": False
            }
        
        # Get timezone object
        tz = pytz.timezone(timezone_str)
        
        # Get current offset
        from datetime import datetime
        now = datetime.now(tz)
        utc_offset = now.utcoffset().total_seconds() / 3600
        
        # Check if DST is active
        dst_active = bool(now.dst())
        
        return {
            "timezone": timezone_str,
            "utc_offset": utc_offset,
            "dst_active": dst_active
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting timezone: {str(e)}"
        )


@router.get("/validate")
def validate_coordinates(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in degrees")
):
    """
    Validate coordinates and return basic information.
    
    Returns:
    - valid: Whether coordinates are valid
    - latitude: Validated latitude
    - longitude: Validated longitude
    - hemisphere: N/S and E/W
    """
    try:
        # Determine hemispheres
        lat_hemisphere = "N" if latitude >= 0 else "S"
        lon_hemisphere = "E" if longitude >= 0 else "W"
        
        return {
            "valid": True,
            "latitude": latitude,
            "longitude": longitude,
            "hemisphere": f"{lat_hemisphere}/{lon_hemisphere}",
            "latitude_dms": decimal_to_dms(latitude, is_latitude=True),
            "longitude_dms": decimal_to_dms(longitude, is_latitude=False)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid coordinates: {str(e)}"
        )


def decimal_to_dms(decimal: float, is_latitude: bool = True) -> str:
    """
    Convert decimal degrees to degrees, minutes, seconds format.
    
    Args:
        decimal: Decimal degrees
        is_latitude: True for latitude, False for longitude
        
    Returns:
        DMS string (e.g., "51°30'26.4\"N")
    """
    direction = ""
    if is_latitude:
        direction = "N" if decimal >= 0 else "S"
    else:
        direction = "E" if decimal >= 0 else "W"
    
    decimal = abs(decimal)
    degrees = int(decimal)
    minutes_decimal = (decimal - degrees) * 60
    minutes = int(minutes_decimal)
    seconds = (minutes_decimal - minutes) * 60
    
    return f"{degrees}°{minutes}'{seconds:.1f}\"{direction}"

# Made with Bob
