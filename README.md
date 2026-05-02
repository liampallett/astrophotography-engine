# 🔭 Astrophotography Target Suggestion Engine

A beginner-friendly web application that helps astrophotographers find optimal celestial targets.

## 🚀 Quick Start

### First Time Setup
```bash
./setup.sh
```

### Run the Application
```bash
./start.sh
```

Then visit: **http://localhost:4321**

## 📚 What's Included

- **Backend (FastAPI)**: Python API with astronomy calculations
- **Frontend (Astro)**: Modern web interface with React components
- **Database**: SQLite with complete 110 Messier catalogue objects

## 🎯 Current Features

✅ Browse Messier catalogue objects  
✅ View object details (type, magnitude, size, constellation)  
✅ Difficulty ratings for beginners  
✅ Best viewing months  
✅ Imaging tips  

## 🔧 Manual Commands

### Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm run dev
```

## 📖 Documentation

- **[SETUP_COMPLETE.md](SETUP_COMPLETE.md)** - Detailed setup guide
- **[RUN.md](RUN.md)** - Quick run reference
- **[backend/README.md](backend/README.md)** - Backend documentation

## 🌟 Coming Soon

- Location-based target recommendations
- Equipment compatibility matching
- Real-time visibility calculations
- Interactive sky maps
- Weather integration

## 🛠️ Tech Stack

- **Frontend**: Astro, React, TypeScript, Tailwind CSS
- **Backend**: Python, FastAPI, Astropy, SQLite
- **APIs**: OpenWeatherMap (planned)

---

Built with ❤️ for astrophotography enthusiasts