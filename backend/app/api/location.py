"""
Location services API endpoints.

Provides geocoding, timezone detection, and location-based utilities.
"""

from fastapi import APIRouter, HTTPException, Query
from geopy.geocoders import ArcGIS
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from typing import Optional
import pytz
from timezonefinder import TimezoneFinder
import time
import logging
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Rate limiting for ArcGIS (more generous than Nominatim)
_last_request_time = 0
_min_request_interval = 0.1  # seconds (ArcGIS allows higher rate)

def rate_limit():
    """Ensure we don't exceed ArcGIS rate limits."""
    global _last_request_time
    current_time = time.time()
    time_since_last = current_time - _last_request_time
    
    if time_since_last < _min_request_interval:
        sleep_time = _min_request_interval - time_since_last
        logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
        time.sleep(sleep_time)
    
    _last_request_time = time.time()

# Initialize ArcGIS geocoder
# No user-agent or API key required for basic usage
geolocator = ArcGIS(timeout=10)
tf = TimezoneFinder()

def retry_on_error(max_retries=3, backoff_factor=2):
    """Decorator to retry geocoding operations with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    if attempt > 0:
                        wait_time = backoff_factor ** attempt
                        logger.info(f"Retry attempt {attempt + 1}/{max_retries}, waiting {wait_time}s")
                        time.sleep(wait_time)
                    
                    return func(*args, **kwargs)
                    
                except GeocoderTimedOut as e:
                    last_exception = e
                    logger.warning(f"Geocoder timeout on attempt {attempt + 1}: {str(e)}")
                    continue
                    
                except GeocoderServiceError as e:
                    last_exception = e
                    logger.error(f"Geocoder service error on attempt {attempt + 1}: {str(e)}")
                    # Don't retry on 403 errors after first attempt
                    if "403" in str(e):
                        break
                    continue
                    
                except Exception as e:
                    last_exception = e
                    logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                    break
            
            # If we get here, all retries failed
            raise last_exception
        
        return wrapper
    return decorator


@router.get("/geocode")
@retry_on_error(max_retries=3, backoff_factor=2)
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
        logger.info(f"Geocoding address: {address}")
        
        # Apply rate limiting before making request
        rate_limit()
        
        # Try to geocode the address
        # Note: ArcGIS doesn't support language parameter in the same way
        location = geolocator.geocode(
            address,
            timeout=10
        )
        
        if not location:
            logger.warning(f"No location found for address: {address}")
            raise HTTPException(
                status_code=404,
                detail=f"Could not find location for address: {address}"
            )
        
        logger.info(f"Successfully geocoded: {address} -> {location.latitude}, {location.longitude}")
        
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
        
    except GeocoderTimedOut as e:
        logger.error(f"Geocoder timeout for address '{address}': {str(e)}")
        raise HTTPException(
            status_code=504,
            detail="Geocoding service timed out. Please try again."
        )
    except GeocoderServiceError as e:
        logger.error(f"Geocoder service error for address '{address}': {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Geocoding service error: {str(e)}. This may be due to rate limiting. Please wait a moment and try again."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error geocoding address '{address}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error geocoding address: {str(e)}"
        )


@router.get("/reverse")
@retry_on_error(max_retries=3, backoff_factor=2)
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
        logger.info(f"Reverse geocoding: {latitude}, {longitude}")
        
        # Apply rate limiting before making request
        rate_limit()
        
        # Reverse geocode
        # ArcGIS expects coordinates as tuple or string
        location = geolocator.reverse(
            f"{latitude}, {longitude}",
            timeout=10
        )
        
        if not location:
            logger.warning(f"No address found for coordinates: {latitude}, {longitude}")
            raise HTTPException(
                status_code=404,
                detail=f"Could not find address for coordinates: {latitude}, {longitude}"
            )
        
        logger.info(f"Successfully reverse geocoded: {latitude}, {longitude} -> {location.address}")
        
        # Get timezone
        timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
        if not timezone_str:
            timezone_str = "UTC"
        
        # Extract address components from ArcGIS response
        # ArcGIS has a different structure than Nominatim
        raw_address = location.raw.get("address", {})
        city = (
            raw_address.get("City") or
            raw_address.get("Subregion") or
            raw_address.get("Region") or
            "Unknown"
        )
        country = raw_address.get("CountryCode", "Unknown")
        
        return {
            "display_name": location.address,
            "city": city,
            "country": country,
            "timezone": timezone_str,
            "latitude": latitude,
            "longitude": longitude,
            "address_components": raw_address
        }
        
    except GeocoderTimedOut as e:
        logger.error(f"Geocoder timeout for coordinates {latitude}, {longitude}: {str(e)}")
        raise HTTPException(
            status_code=504,
            detail="Geocoding service timed out. Please try again."
        )
    except GeocoderServiceError as e:
        logger.error(f"Geocoder service error for coordinates {latitude}, {longitude}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Geocoding service error: {str(e)}. This may be due to rate limiting. Please wait a moment and try again."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error reverse geocoding {latitude}, {longitude}: {str(e)}", exc_info=True)
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
        offset = now.utcoffset()
        utc_offset = offset.total_seconds() / 3600 if offset else 0
        
        # Check if DST is active
        dst = now.dst()
        dst_active = bool(dst) if dst else False
        
        return {
            "timezone": timezone_str,
            "utc_offset": utc_offset,
            "dst_active": dst_active
        }
        
    except Exception as e:
        logger.error(f"Error getting timezone for {latitude}, {longitude}: {str(e)}", exc_info=True)
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
