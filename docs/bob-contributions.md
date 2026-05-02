# IBM Bob's Contributions to the Astrophotography Engine

IBM Bob was the AI pair-programmer throughout this hackathon project. Every source file carries a `# Made with Bob` or `// Made with Bob` signature. This document catalogues Bob's specific technical contributions across the codebase.

---

## Project Planning

Bob produced the full technical specification before a single line of code was written — system architecture, database schema, REST API design, component hierarchy, scoring algorithm design, and a phased development roadmap. These artefacts live in `docs/planning/project-plan.md` and `docs/planning/development-kickoff.md`.

---

## Backend

### `backend/app/main.py`
- FastAPI application skeleton with CORS middleware configured for the Astro dev server
- Health check endpoint and root info endpoint
- Router registration for all sub-APIs

### `backend/app/database/init_db.py`
- SQLite schema creation script
- Seeded the complete **110-object Messier Catalogue** with accurate coordinates (RA/Dec), visual magnitudes, angular sizes, best viewing months, minimum aperture recommendations, difficulty ratings, descriptions, imaging tips, and distances in light-years

### `backend/app/models/request.py` and `backend/app/models/response.py`
- All Pydantic request and response models: `LocationModel`, `EquipmentModel` (with `f_number` → `aperture_mm` derived property), `ObservationModel`, `PreferencesModel`, `TargetCalculationRequest`
- Response models: `VisibilityModel`, `TargetModel`, `MoonDataModel` (with optional `altitude`/`azimuth` for sky map use), `TargetCalculationResponse`, `MessierObjectResponse`

### `backend/app/services/visibility.py`
Implements all Astropy-based astronomy calculations:

- **`calculate_target_visibility`** — samples altitude/azimuth at 15-minute intervals across the observation window, finds the peak, and counts hours above 30°
- **`calculate_moon_separation`** — angular separation between a target and the moon using `SkyCoord.separation()`
- **`calculate_moon_data`** — moon altitude, azimuth, illumination, and phase; uses **ecliptic elongation (0–360°)** via `GeocentricMeanEcliptic` to correctly distinguish waxing from waning phases (a naive `separation()` call only gives 0–180° and cannot tell the difference)
- **`get_moon_phase_name`** — maps elongation to all 8 named phases with correct 45° boundaries
- **`calculate_sun_position`** — sun altitude/azimuth and twilight classification (civil, nautical, astronomical, night); used to reject daytime observation requests

### `backend/app/services/ranking.py`
Multi-factor scoring algorithm (0–100) with weighted components:

| Factor | Weight | Logic |
|--------|--------|-------|
| Altitude | 40% | Piecewise linear: <30° → 0–30 pts, 30–60° → 30–80 pts, >60° → 80–100 pts |
| Brightness | 25% | Inverse of magnitude; mag < 5 scores 90–100, mag > 10 scores 0–30 |
| FOV match | 15% | Object/FOV size ratio; ideal at 30–70% of frame |
| Moon separation | 10% | <30° → 0–40 pts, 30–60° → 40–70 pts, >60° → 70–100 pts |
| Weather | 10% | `100 - cloud_cover`; weights redistributed proportionally when no weather data is available |

Also implements:
- **`calculate_field_of_view`** — diagonal FOV in arcminutes from sensor dimensions and focal length
- **`calculate_size_match_score`** — object/FOV ratio scoring used separately for equipment match labels
- **`determine_difficulty`** — classifies targets easy/moderate/challenging by magnitude, angular size, and user aperture vs. `min_aperture_mm`
- **`calculate_imaging_time_recommendation`** — suggested sub-exposure length and frame count based on magnitude, aperture, and moon illumination

### `backend/app/api/targets.py`
The main `/targets/calculate` endpoint orchestrating the full pipeline:
1. Parse and validate request
2. Reject non-nighttime observation times
3. Fetch all Messier objects from SQLite
4. For each object: compute visibility, check altitude/moon avoidance preferences, score, classify difficulty, compute equipment match
5. Sort by score, return top 10
Also provides `/targets/tonight` (quick endpoint with sensible defaults) and `/targets/visibility/{id}` (detailed per-object breakdown).

### `backend/app/api/catalogue.py`
`GET /catalogue/messier` and `GET /catalogue/messier/{id}` with proper `try/finally` connection handling.

### `backend/app/api/location.py` and `backend/app/api/moon.py`
Location geocoding/reverse-geocoding/timezone and standalone moon phase/position endpoints.

---

## Frontend

### `frontend/src/lib/api.ts`
Complete TypeScript API client (`// Made with Bob - Phase 4`):
- All type interfaces matching the backend Pydantic models
- `calculateTargets`, `getMessierCatalogue`, `getMessierObject`, `getMoonInfo`, `getMoonPhase`, `geocodeAddress`, `reverseGeocode`, `getTimezone`, `getTonightTargets`, `getTargetVisibility`, `checkApiHealth`
- Utility formatters: `formatMoonPhase` (all 8 phases), `formatDifficulty`, `formatEquipmentMatch`

### `frontend/src/components/SkyMap.tsx`
Interactive sky map built on Chart.js scatter chart (`// Made with Bob`):

- **Coordinate system** — polar projection: `radius = 90 − altitude`, `x = sin(az) × radius`, `y = cos(az) × radius`; zenith at origin, horizon at radius 90, North up
- **Reference rings** — `circleAt(altitude)` generates 361-point circles at 0°, 30°, and 60° altitude
- **Time simulation** — altitude falls off `~10°/hr` from peak; azimuth drifts `15°/hr` (Earth's rotation); time slider covers ±6 hours
- **Astro island data bridge** — `window.__SKYMAP_DATA__` + `CustomEvent('skymap-data-ready')` pattern decouples the Astro `<script>` from the React island; component resets slider on new data arrival
- **Chart.js integration** — correct registration of `ScatterController`, `LinearScale`, `PointElement`, `LineElement`; `maintainAspectRatio: false` with padding-bottom: 100% container trick to give the canvas real pixel dimensions at init time
- Compass direction overlays (N/S/E/W), difficulty colour coding, tooltip filter suppressing reference-circle labels, visible-targets list sorted by altitude

---

## Documentation

Bob authored all 11 documents now living in `/docs`:

- `docs/planning/project-plan.md` — original technical specification
- `docs/planning/development-kickoff.md` — phase-by-phase implementation guide
- `docs/planning/quick-start-guide.md` — 5-minute setup reference
- `docs/planning/hackathon-overview.md` — project overview and roadmap
- `docs/planning/catalogue-expansion.md` — notes on the 20 → 110 object expansion
- `docs/api/api-reference.md` — complete REST API reference
- `docs/user-guide.md` — end-user guide for the web application
- `docs/setup.md` — first-time environment setup
- `docs/run.md` — quick server start reference
- `docs/backend-setup.md` — backend-specific setup instructions
- `docs/frontend/skymap-integration.md` and `skymap-quick-start.md` — SkyMap component guides

---

## Summary

| Area | Files authored or co-authored |
|------|-------------------------------|
| Backend services | `visibility.py`, `ranking.py` |
| Backend API | `targets.py`, `catalogue.py`, `location.py`, `moon.py`, `main.py` |
| Backend models | `request.py`, `response.py` |
| Backend database | `init_db.py` + 110 Messier objects |
| Frontend components | `SkyMap.tsx` |
| Frontend API client | `api.ts` |
| Documentation | 11 docs in `/docs` |

All source files are signed `Made with Bob`.
