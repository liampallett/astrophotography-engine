# 🔭 Astrophotography Target Suggestion Engine

A beginner-friendly web application that helps astrophotographers find optimal celestial targets based on their location, equipment, and current sky conditions.

## 🌟 Features

- **Smart Target Recommendations** - Get personalized suggestions from the Messier Catalogue
- **Location-Based Calculations** - Visibility predictions for your specific location
- **Equipment Matching** - Find targets that fit your telescope and camera setup
- **Real-Time Sky Conditions** - Weather and moon phase integration
- **Interactive Sky Maps** - Visualize target positions in the night sky
- **Beginner-Friendly** - Clear difficulty ratings and imaging tips

## 🛠️ Technology Stack

### Frontend
- **Astro** - Modern static site generator
- **TypeScript** - Type-safe development
- **React** - Interactive components
- **Tailwind CSS** - Utility-first styling
- **Chart.js & Leaflet** - Data visualizations

### Backend
- **Python FastAPI** - High-performance API framework
- **Astropy** - Professional astronomy calculations
- **Skyfield** - Precise ephemeris calculations
- **SQLite** - Messier Catalogue database
- **OpenWeatherMap API** - Weather data integration

## 📁 Project Structure

```
astrophotography-engine/
├── frontend/              # Astro frontend application
├── backend/               # Python FastAPI backend
├── docs/                  # Documentation
├── ASTROPHOTOGRAPHY_ENGINE_PLAN.md    # Detailed project plan
├── DEVELOPMENT_KICKOFF.md             # Comprehensive setup guide
├── QUICK_START.md                     # Quick reference guide
└── README.md                          # This file
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- Git

### One-Command Setup

```bash
cd astrophotography-engine
./setup.sh
```

This will:
- Create Python virtual environment
- Install all backend dependencies
- Initialize the database with complete 110 Messier objects
- Install all frontend dependencies

### Running the Application

**One-Command Start:**
```bash
cd astrophotography-engine
./start.sh
```

This starts both backend and frontend servers automatically!

**Or manually in separate terminals:**

Terminal 1 - Backend:
```bash
cd astrophotography-engine/backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

Terminal 2 - Frontend:
```bash
cd astrophotography-engine/frontend
npm run dev
```

**Access the application:**
- Frontend: http://localhost:4321
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📚 Documentation

- **[Project Plan](ASTROPHOTOGRAPHY_ENGINE_PLAN.md)** - Complete technical specification
- **[Development Kickoff](DEVELOPMENT_KICKOFF.md)** - Detailed setup and implementation guide
- **[Quick Start](QUICK_START.md)** - Fast reference for getting started

## 🎯 Development Roadmap

### Phase 1: Foundation ✅
- [x] Project planning and architecture
- [ ] Project structure setup
- [ ] Frontend initialization (Astro + TypeScript)
- [ ] Backend initialization (FastAPI + Python)

### Phase 2: Database & API
- [ ] Messier Catalogue database
- [ ] Catalogue API endpoints
- [ ] Location services
- [ ] Moon calculations

### Phase 3: Core Features
- [ ] Visibility calculations (Astropy)
- [ ] Target ranking algorithm
- [ ] Equipment matching
- [ ] Weather integration

### Phase 4: Frontend UI
- [ ] Location input component
- [ ] Equipment form
- [ ] Target cards
- [ ] Results page
- [ ] Interactive sky map

### Phase 5: Polish & Deploy
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Documentation
- [ ] Deployment configuration

## 🔧 API Endpoints

### Catalogue
- `GET /api/v1/catalogue/messier` - Get all Messier objects
- `GET /api/v1/catalogue/messier/{id}` - Get specific object

### Targets (Coming Soon)
- `POST /api/v1/targets/calculate` - Calculate optimal targets
- `GET /api/v1/moon` - Get moon data
- `GET /api/v1/weather` - Get weather conditions
- `GET /api/v1/location/geocode` - Geocode address

## 🌙 Complete Messier Catalogue

The system includes the complete Messier Catalogue with all 110 deep sky objects:

- **40 Galaxies** - Including M31 (Andromeda), M51 (Whirlpool), M81/M82 pair
- **29 Globular Clusters** - Including M13 (Hercules), M22, M15
- **26 Open Clusters** - Including M45 (Pleiades), M44 (Beehive), M7
- **7 Emission/Reflection Nebulae** - Including M42 (Orion), M8 (Lagoon), M17 (Omega)
- **4 Planetary Nebulae** - Including M27 (Dumbbell), M57 (Ring)
- **4 Special Objects** - Supernova remnants, star clouds, and more

Each object includes:
- Accurate coordinates and physical data
- Difficulty ratings (Easy, Moderate, Challenging)
- Best viewing months
- Imaging tips and techniques
- Equipment recommendations

## 🤝 Contributing

This is a learning project built during the IBM Bob Hackathon. Contributions and suggestions are welcome!

## 📝 License

MIT License - Feel free to use this project for learning and development.

## 🙏 Acknowledgments

- **Messier Catalogue** - Charles Messier's catalog of deep sky objects
- **Astropy** - Community-developed astronomy tools
- **FastAPI** - Modern Python web framework
- **Astro** - Next-generation web framework

## 📧 Contact

Built with ❤️ for astrophotography enthusiasts

---

**Ready to find your next imaging target? Let's get started! 🚀**