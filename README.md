# 🔭 Astrophotography Target Suggestion Engine

A beginner-friendly web application that calculates the best Messier Catalogue objects to photograph based on your location, equipment, and sky conditions — powered by professional astronomy calculations via Astropy.

## Quick Start

### First-time setup
```bash
./setup.sh
```

### Run both servers
```bash
./start.sh
```

Then open **http://localhost:4321**

Or start servers manually:

```bash
# Terminal 1 — backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2 — frontend
cd frontend
npm run dev
```

---

## Features

### Target Recommendations
- Enter your location (address search or manual coordinates), equipment, and observation window
- Receives a ranked list of up to 10 targets from the complete 110-object Messier Catalogue
- Daylight guard — requests are rejected if the observation time falls outside astronomical night (sun above −18°)
- Configurable minimum altitude and moon avoidance preferences

### Scoring Algorithm
Each target receives a 0–100 score weighted across five factors:

| Factor | Weight | Basis |
|--------|--------|-------|
| Visibility | 40% | Peak altitude above horizon |
| Brightness | 25% | Visual magnitude (lower = brighter = better) |
| Equipment match | 15% | Object size vs. calculated field of view |
| Moon separation | 10% | Angular distance from moon |
| Weather | 10% | Cloud cover (redistributed when unavailable) |

### Sky Map
- Interactive polar projection — zenith at centre, horizon at edge, North up
- Each target plotted at its real altitude/azimuth position
- Time slider (±6 hours) shows targets drifting across the sky as Earth rotates
- Colour-coded by difficulty: green (easy), yellow (moderate), red (challenging)
- Moon position shown when above the horizon
- Tooltip with altitude, azimuth, and difficulty on hover

### Equipment Support
- Accepts aperture in mm **or** f-number (aperture derived as `focal_length / f_number`)
- Field of view calculated from sensor dimensions and focal length
- Equipment match label (excellent / good / fair / poor) based on how well the object fills the frame

### Moon & Sky Conditions
- Moon phase using ecliptic elongation (0–360°) — correctly distinguishes all 8 phases including waxing vs. waning
- Moon altitude, azimuth, and illumination fraction at observation time
- Sun altitude and twilight classification (civil, nautical, astronomical, night)

### Location Services
- Address/city geocoding to coordinates and timezone
- Reverse geocoding (coordinates → place name)
- Timezone lookup

### Messier Catalogue
- All 110 objects with accurate coordinates, visual magnitude, angular size, constellation, best viewing months, minimum aperture, difficulty rating, description, imaging notes, and distance

---

## Tech Stack

**Frontend**
- Astro 6.2.1 with TypeScript
- React 19 (islands architecture — interactive components only)
- Tailwind CSS
- Chart.js 4.5.1 + react-chartjs-2 5.3.1 (sky map)

**Backend**
- Python 3.9+ / FastAPI 2.0.0
- Astropy 5.3.4 (visibility, moon, and sun calculations)
- SQLite (Messier Catalogue database)
- Pydantic v2 (request/response validation)

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/targets/calculate` | Calculate ranked targets for a session |
| `GET` | `/api/v1/targets/tonight` | Quick recommendations with default settings |
| `GET` | `/api/v1/targets/visibility/{id}` | Detailed visibility breakdown for one object |
| `GET` | `/api/v1/catalogue/messier` | Full Messier Catalogue |
| `GET` | `/api/v1/catalogue/messier/{id}` | Single Messier object |
| `GET` | `/api/v1/moon` | Moon position, phase, and illumination |
| `GET` | `/api/v1/moon/phase` | Moon phase without location |
| `GET` | `/api/v1/location/geocode` | Address → coordinates |
| `GET` | `/api/v1/location/reverse` | Coordinates → address |
| `GET` | `/api/v1/location/timezone` | Timezone for coordinates |
| `GET` | `/health` | Service health check |

Interactive API documentation: **http://localhost:8000/docs**

---

## Project Structure

```
astrophotography-engine/
├── backend/
│   └── app/
│       ├── api/              # Route handlers (targets, catalogue, moon, location)
│       ├── database/         # SQLite DB + init script
│       ├── models/           # Pydantic request/response models
│       └── services/         # Astronomy logic (visibility.py, ranking.py)
├── frontend/
│   └── src/
│       ├── components/       # LocationInput, EquipmentForm, ObservationSelector, SkyMap
│       ├── layouts/          # Base page layout
│       ├── lib/              # TypeScript API client
│       └── pages/            # index.astro
├── docs/                     # All project documentation
├── setup.sh                  # One-command environment setup
└── start.sh                  # One-command server start
```

---

## Documentation

All docs are in [`/docs`](docs/README.md):

- [Quick Start Guide](docs/planning/quick-start-guide.md)
- [Run Guide](docs/run.md)
- [Setup Guide](docs/setup.md)
- [User Guide](docs/user-guide.md)
- [API Reference](docs/api/api-reference.md)
- [SkyMap Integration](docs/frontend/skymap-integration.md)
- [Bob Contributions](docs/bob-contributions.md)

---

## Roadmap

- [ ] Weather integration — live cloud cover and atmospheric seeing from OpenWeatherMap
- [ ] Planet tracking — extend recommendations beyond the Messier Catalogue
- [ ] Imaging plan export — generate a session plan with recommended exposure times

---

Built with ❤️ for astrophotography enthusiasts · Made with Bob
