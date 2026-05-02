# 🔌 API Documentation

Complete API reference for the Astrophotography Target Suggestion Engine.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently no authentication required. All endpoints are publicly accessible.

## Response Format

All responses are in JSON format with appropriate HTTP status codes.

### Success Response
```json
{
  "data": { ... },
  "status": "success"
}
```

### Error Response
```json
{
  "detail": "Error message here"
}
```

---

## 📚 Catalogue Endpoints

### Get All Messier Objects

Retrieve the complete Messier catalogue.

**Endpoint:** `GET /catalogue/messier`

**Response:**
```json
{
  "objects": [
    {
      "id": "M31",
      "messier_number": 31,
      "ngc_id": "NGC 224",
      "name": "Andromeda Galaxy",
      "type": "galaxy",
      "ra_hours": 0.712,
      "dec_degrees": 41.269,
      "magnitude": 3.4,
      "size_arcmin": 178.0,
      "constellation": "Andromeda",
      "best_months": ["Sep", "Oct", "Nov", "Dec"],
      "min_aperture_mm": 50,
      "difficulty": "easy",
      "description": "The nearest major galaxy to the Milky Way",
      "imaging_notes": "Wide field recommended...",
      "distance_ly": 2537000
    }
  ],
  "count": 20
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/catalogue/messier
```

### Get Specific Messier Object

Retrieve details for a single object.

**Endpoint:** `GET /catalogue/messier/{object_id}`

**Parameters:**
- `object_id` (path): Messier ID (e.g., "M31", "M42")

**Response:**
```json
{
  "id": "M31",
  "messier_number": 31,
  "name": "Andromeda Galaxy",
  ...
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/catalogue/messier/M31
```

**Error Codes:**
- `404`: Object not found

---

## 🎯 Target Calculation Endpoints

### Calculate Optimal Targets

Get personalized target recommendations based on location, equipment, and preferences.

**Endpoint:** `POST /targets/calculate`

**Request Body:**
```json
{
  "location": {
    "latitude": 51.5074,
    "longitude": -0.1278,
    "timezone": "Europe/London",
    "elevation": 11
  },
  "equipment": {
    "aperture_mm": 200,
    "focal_length_mm": 1000,
    "sensor_width_mm": 23.5,
    "sensor_height_mm": 15.6
  },
  "observation": {
    "date": "2026-05-01",
    "start_time": "21:00:00",
    "duration_hours": 4
  },
  "preferences": {
    "min_altitude": 30,
    "moon_avoidance_deg": 30,
    "include_planets": false
  }
}
```

**Response:**
```json
{
  "targets": [
    {
      "id": "M13",
      "name": "Hercules Globular Cluster",
      "type": "globular_cluster",
      "score": 87.5,
      "visibility": {
        "peak_time": "2026-05-01T23:30:00",
        "peak_altitude": 65.2,
        "duration_hours": 3.5
      },
      "moon_separation": 85.3,
      "weather_score": null,
      "equipment_match": "excellent",
      "magnitude": 5.8,
      "size_arcmin": 20.0,
      "constellation": "Hercules",
      "difficulty": "moderate",
      "description": "Brightest globular cluster..."
    }
  ],
  "moon": {
    "phase": "waxing_gibbous",
    "illumination": 0.73,
    "rise_time": null,
    "set_time": null
  }
}
```

**Validation Rules:**
- `latitude`: -90 to 90
- `longitude`: -180 to 180
- `aperture_mm`: > 0
- `focal_length_mm`: > 0
- `sensor_width_mm`: > 0
- `sensor_height_mm`: > 0
- `duration_hours`: 0 to 12
- `min_altitude`: 0 to 90
- `moon_avoidance_deg`: 0 to 90

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/targets/calculate \
  -H "Content-Type: application/json" \
  -d @request.json
```

**Error Codes:**
- `400`: Invalid input or observation during daylight
- `404`: No suitable targets found
- `500`: Calculation error

### Get Tonight's Targets (Quick)

Simplified endpoint for quick recommendations with minimal input.

**Endpoint:** `GET /targets/tonight`

**Query Parameters:**
- `latitude` (required): Observer latitude
- `longitude` (required): Observer longitude
- `aperture_mm` (optional, default: 200): Telescope aperture
- `focal_length_mm` (optional, default: 1000): Focal length
- `sensor_width_mm` (optional, default: 23.5): Sensor width
- `sensor_height_mm` (optional, default: 15.6): Sensor height
- `elevation` (optional, default: 0): Elevation in meters

**Response:** Same as `/targets/calculate`

**Example:**
```bash
curl "http://localhost:8000/api/v1/targets/tonight?latitude=51.5&longitude=-0.1&aperture_mm=200"
```

### Get Target Visibility

Get detailed visibility information for a specific object.

**Endpoint:** `GET /targets/visibility/{object_id}`

**Path Parameters:**
- `object_id`: Messier ID (e.g., "M31")

**Query Parameters:**
- `latitude` (required): Observer latitude
- `longitude` (required): Observer longitude
- `date` (required): Date in YYYY-MM-DD format
- `time` (optional, default: "21:00:00"): Time in HH:MM:SS format
- `duration_hours` (optional, default: 4): Duration in hours
- `elevation` (optional, default: 0): Elevation in meters

**Response:**
```json
{
  "object": {
    "id": "M31",
    "name": "Andromeda Galaxy",
    "type": "galaxy",
    "magnitude": 3.4,
    "size_arcmin": 178.0
  },
  "visibility": {
    "peak_time": "2026-05-01T23:30:00",
    "peak_altitude": 65.2,
    "peak_azimuth": 180.5,
    "duration_hours": 5.5,
    "visibility_data": [
      {
        "time": "2026-05-01T21:00:00",
        "altitude": 45.2,
        "azimuth": 120.3
      }
    ],
    "is_visible": true
  },
  "moon": {
    "altitude": 30.5,
    "azimuth": 200.1,
    "illumination": 0.73,
    "phase": "waxing_gibbous",
    "phase_angle": 120.5,
    "separation_from_target": 85.3
  },
  "sun": {
    "altitude": -25.3,
    "azimuth": 280.1,
    "is_night": true,
    "twilight_type": "night"
  },
  "observation_time": "2026-05-01T21:00:00",
  "location": {
    "latitude": 51.5074,
    "longitude": -0.1278,
    "elevation": 0
  }
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/targets/visibility/M31?latitude=51.5&longitude=-0.1&date=2026-05-01"
```

---

## 🌙 Moon Endpoints

### Get Moon Information

Get moon position, phase, and illumination for a specific location and time.

**Endpoint:** `GET /moon`

**Query Parameters:**
- `latitude` (required): Observer latitude (-90 to 90)
- `longitude` (required): Observer longitude (-180 to 180)
- `date` (optional): Date in YYYY-MM-DD format (defaults to now)
- `time` (optional): Time in HH:MM:SS format (defaults to now)
- `elevation` (optional, default: 0): Elevation in meters

**Response:**
```json
{
  "altitude": 45.2,
  "azimuth": 180.5,
  "illumination": 0.73,
  "phase": "waxing_gibbous",
  "phase_angle": 120.5,
  "observation_time": "2026-05-01T21:00:00",
  "location": {
    "latitude": 51.5074,
    "longitude": -0.1278,
    "elevation": 0
  }
}
```

**Moon Phases:**
- `new`: New moon (0-22.5°)
- `waxing_crescent`: Waxing crescent (22.5-67.5°)
- `first_quarter`: First quarter (67.5-112.5°)
- `waxing_gibbous`: Waxing gibbous (112.5-157.5°)
- `full`: Full moon (157.5-180°)

**Example:**
```bash
curl "http://localhost:8000/api/v1/moon?latitude=51.5&longitude=-0.1&date=2026-05-01&time=21:00:00"
```

### Get Moon Phase (Simplified)

Get moon phase without location (phase is same everywhere on Earth).

**Endpoint:** `GET /moon/phase`

**Query Parameters:**
- `date` (optional): Date in YYYY-MM-DD format (defaults to today)

**Response:**
```json
{
  "phase": "waxing_gibbous",
  "illumination": 0.73,
  "phase_angle": 120.5,
  "date": "2026-05-01"
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/moon/phase?date=2026-05-01"
```

---

## 📍 Location Endpoints

### Geocode Address

Convert an address or place name to coordinates.

**Endpoint:** `GET /location/geocode`

**Query Parameters:**
- `address` (required): Address or place name
- `language` (optional, default: "en"): Language for results

**Response:**
```json
{
  "latitude": 51.507351,
  "longitude": -0.127758,
  "timezone": "Europe/London",
  "elevation": 0,
  "display_name": "London, Greater London, England, United Kingdom",
  "country": "United Kingdom",
  "raw": {
    "lat": 51.507351,
    "lon": -0.127758,
    "boundingbox": ["51.28", "51.69", "-0.51", "0.33"]
  }
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/location/geocode?address=London,UK"
```

**Error Codes:**
- `404`: Location not found
- `504`: Geocoding service timeout
- `503`: Geocoding service error

### Reverse Geocode

Convert coordinates to an address.

**Endpoint:** `GET /location/reverse`

**Query Parameters:**
- `latitude` (required): Latitude (-90 to 90)
- `longitude` (required): Longitude (-180 to 180)
- `language` (optional, default: "en"): Language for results

**Response:**
```json
{
  "display_name": "Westminster, London, Greater London, England, SW1A 2DX, United Kingdom",
  "city": "London",
  "country": "United Kingdom",
  "timezone": "Europe/London",
  "latitude": 51.5074,
  "longitude": -0.1278,
  "address_components": {
    "city": "London",
    "country": "United Kingdom",
    "postcode": "SW1A 2DX"
  }
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/location/reverse?latitude=51.5074&longitude=-0.1278"
```

### Get Timezone

Get timezone information for coordinates.

**Endpoint:** `GET /location/timezone`

**Query Parameters:**
- `latitude` (required): Latitude (-90 to 90)
- `longitude` (required): Longitude (-180 to 180)

**Response:**
```json
{
  "timezone": "Europe/London",
  "utc_offset": 1.0,
  "dst_active": true
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/location/timezone?latitude=51.5074&longitude=-0.1278"
```

### Validate Coordinates

Validate coordinates and get hemisphere information.

**Endpoint:** `GET /location/validate`

**Query Parameters:**
- `latitude` (required): Latitude (-90 to 90)
- `longitude` (required): Longitude (-180 to 180)

**Response:**
```json
{
  "valid": true,
  "latitude": 51.5074,
  "longitude": -0.1278,
  "hemisphere": "N/W",
  "latitude_dms": "51°30'26.6\"N",
  "longitude_dms": "0°7'40.1\"W"
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/location/validate?latitude=51.5074&longitude=-0.1278"
```

---

## 🏥 Health & Status Endpoints

### Health Check

Check if the API is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "services": {
    "catalogue": "operational",
    "targets": "operational",
    "moon": "operational",
    "location": "operational"
  }
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

### Root Endpoint

Get API information and available endpoints.

**Endpoint:** `GET /`

**Response:**
```json
{
  "message": "Astrophotography Target API",
  "version": "2.0.0",
  "status": "running",
  "endpoints": {
    "docs": "/docs",
    "catalogue": "/api/v1/catalogue/messier",
    "targets": "/api/v1/targets/calculate",
    "moon": "/api/v1/moon",
    "location": "/api/v1/location/geocode"
  }
}
```

---

## 📊 Rate Limiting

Currently no rate limiting implemented. Use responsibly.

## 🔒 CORS

CORS is enabled for:
- `http://localhost:4321` (Astro dev server)
- `http://localhost:3000` (Alternative dev port)

## 🐛 Error Handling

### HTTP Status Codes

- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found
- `500`: Internal Server Error
- `503`: Service Unavailable
- `504`: Gateway Timeout

### Error Response Format

```json
{
  "detail": "Descriptive error message"
}
```

## 📝 Notes

- All times are in ISO 8601 format
- Coordinates use decimal degrees
- Angles in degrees (0-360 for azimuth, -90 to 90 for altitude)
- Distances in light years
- Sizes in arcminutes
- Magnitudes follow astronomical convention (lower = brighter)

## 🔗 Interactive Documentation

Visit http://localhost:8000/docs for interactive Swagger UI documentation where you can test all endpoints directly.

---

**API Version:** 2.0.0  
**Last Updated:** 2026-05-01