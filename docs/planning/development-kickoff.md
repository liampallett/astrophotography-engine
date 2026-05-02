# 🚀 Development Kickoff Guide

This guide provides step-by-step instructions to kick off development of the Astrophotography Target Suggestion Engine.

## Prerequisites Checklist

- ✅ Node.js installed (v18+ recommended)
- ✅ Python installed (v3.9+ recommended)
- ✅ Git installed
- ✅ Code editor (VS Code recommended)
- ⬜ OpenWeatherMap API key (get from https://openweathermap.org/api)

---

## Phase 1: Project Foundation 🏗️

### Step 1: Create Project Structure

```bash
# Create main project directory
mkdir astrophotography-engine
cd astrophotography-engine

# Create subdirectories
mkdir frontend backend docs

# Initialize git repository
git init
echo "node_modules/" > .gitignore
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
echo "*.db" >> .gitignore
```

**Expected Result:** Directory structure created with git initialized

---

### Step 2: Initialize Astro Frontend

```bash
cd frontend

# Create Astro project
npm create astro@latest . -- --template minimal --typescript strict --install

# Install dependencies
npm install

# Install Tailwind CSS
npm install -D tailwindcss @astrojs/tailwind
npx tailwindcss init

# Install visualization libraries
npm install chart.js react-chartjs-2
npm install leaflet react-leaflet
npm install @types/leaflet

# Install React for interactive components
npm install react react-dom
npm install @astrojs/react

# Verify installation
npm run dev
```

**Configuration Files to Create:**

1. **`astro.config.mjs`** - Add Tailwind and React integrations:
```javascript
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import react from '@astrojs/react';

export default defineConfig({
  integrations: [tailwind(), react()],
  server: {
    port: 4321
  }
});
```

2. **`tailwind.config.cjs`** - Configure Tailwind:
```javascript
module.exports = {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

3. **`src/styles/global.css`** - Add Tailwind directives:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**Expected Result:** Astro dev server running on http://localhost:4321

---

### Step 3: Initialize Python FastAPI Backend

```bash
cd ../backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Create requirements.txt
cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
astropy==5.3.4
skyfield==1.46
geopy==2.4.0
requests==2.31.0
pydantic==2.5.0
python-multipart==0.0.6
python-dotenv==1.0.0
EOF

# Install dependencies
pip install -r requirements.txt

# Create basic directory structure
mkdir -p app/api app/core app/models app/database app/services
touch app/__init__.py
touch app/api/__init__.py
touch app/core/__init__.py
touch app/models/__init__.py
touch app/database/__init__.py
touch app/services/__init__.py
```

**Create Basic FastAPI App:**

**`app/main.py`**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Astrophotography Target API",
    description="API for calculating optimal astrophotography targets",
    version="1.0.0"
)

# CORS configuration for Astro frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4321"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "Astrophotography Target API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

**Test the backend:**
```bash
uvicorn app.main:app --reload --port 8000
```

**Expected Result:** FastAPI server running on http://localhost:8000 with interactive docs at http://localhost:8000/docs

---

## Phase 2: Database Setup 🗄️

### Step 4: Create Messier Catalogue Database

**Create database initialization script:**

**`app/database/init_db.py`**:
```python
import sqlite3
import json
from pathlib import Path

def create_messier_database():
    """Create and populate the Messier Catalogue database"""
    
    db_path = Path(__file__).parent / "messier.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messier_objects (
            id TEXT PRIMARY KEY,
            messier_number INTEGER,
            ngc_id TEXT,
            name TEXT,
            type TEXT,
            ra_hours REAL,
            dec_degrees REAL,
            magnitude REAL,
            size_arcmin REAL,
            constellation TEXT,
            best_months TEXT,
            min_aperture_mm INTEGER,
            difficulty TEXT,
            description TEXT,
            imaging_notes TEXT,
            distance_ly REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Sample data for top 10 beginner-friendly objects
    sample_objects = [
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
            "best_months": json.dumps(["Sep", "Oct", "Nov", "Dec"]),
            "min_aperture_mm": 50,
            "difficulty": "easy",
            "description": "The nearest major galaxy to the Milky Way, visible to the naked eye",
            "imaging_notes": "Wide field recommended. Long exposures reveal spiral structure.",
            "distance_ly": 2537000
        },
        {
            "id": "M42",
            "messier_number": 42,
            "ngc_id": "NGC 1976",
            "name": "Orion Nebula",
            "type": "nebula",
            "ra_hours": 5.583,
            "dec_degrees": -5.391,
            "magnitude": 4.0,
            "size_arcmin": 65.0,
            "constellation": "Orion",
            "best_months": json.dumps(["Dec", "Jan", "Feb", "Mar"]),
            "min_aperture_mm": 50,
            "difficulty": "easy",
            "description": "Stunning emission nebula in Orion's sword, great for beginners",
            "imaging_notes": "Very bright. Watch for overexposure in core. Beautiful colors.",
            "distance_ly": 1344
        },
        {
            "id": "M45",
            "messier_number": 45,
            "ngc_id": None,
            "name": "Pleiades",
            "type": "open_cluster",
            "ra_hours": 3.783,
            "dec_degrees": 24.117,
            "magnitude": 1.6,
            "size_arcmin": 110.0,
            "constellation": "Taurus",
            "best_months": json.dumps(["Nov", "Dec", "Jan", "Feb"]),
            "min_aperture_mm": 30,
            "difficulty": "easy",
            "description": "Beautiful open star cluster, also known as the Seven Sisters",
            "imaging_notes": "Wide field essential. Blue reflection nebulae visible with long exposures.",
            "distance_ly": 444
        },
        {
            "id": "M13",
            "messier_number": 13,
            "ngc_id": "NGC 6205",
            "name": "Hercules Globular Cluster",
            "type": "globular_cluster",
            "ra_hours": 16.694,
            "dec_degrees": 36.461,
            "magnitude": 5.8,
            "size_arcmin": 20.0,
            "constellation": "Hercules",
            "best_months": json.dumps(["May", "Jun", "Jul", "Aug"]),
            "min_aperture_mm": 100,
            "difficulty": "moderate",
            "description": "Brightest globular cluster in northern hemisphere",
            "imaging_notes": "Dense core requires careful exposure. Resolve individual stars.",
            "distance_ly": 25100
        },
        {
            "id": "M27",
            "messier_number": 27,
            "ngc_id": "NGC 6853",
            "name": "Dumbbell Nebula",
            "type": "planetary_nebula",
            "ra_hours": 19.992,
            "dec_degrees": 22.721,
            "magnitude": 7.5,
            "size_arcmin": 8.0,
            "constellation": "Vulpecula",
            "best_months": json.dumps(["Jul", "Aug", "Sep", "Oct"]),
            "min_aperture_mm": 100,
            "difficulty": "moderate",
            "description": "Bright planetary nebula with distinctive dumbbell shape",
            "imaging_notes": "OIII and H-alpha filters enhance detail. Good narrowband target.",
            "distance_ly": 1360
        }
    ]
    
    # Insert sample data
    for obj in sample_objects:
        cursor.execute("""
            INSERT OR REPLACE INTO messier_objects 
            (id, messier_number, ngc_id, name, type, ra_hours, dec_degrees, 
             magnitude, size_arcmin, constellation, best_months, min_aperture_mm, 
             difficulty, description, imaging_notes, distance_ly)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            obj["id"], obj["messier_number"], obj["ngc_id"], obj["name"],
            obj["type"], obj["ra_hours"], obj["dec_degrees"], obj["magnitude"],
            obj["size_arcmin"], obj["constellation"], obj["best_months"],
            obj["min_aperture_mm"], obj["difficulty"], obj["description"],
            obj["imaging_notes"], obj["distance_ly"]
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database created at {db_path}")
    print(f"✅ Inserted {len(sample_objects)} sample Messier objects")

if __name__ == "__main__":
    create_messier_database()
```

**Run the database initialization:**
```bash
cd app/database
python init_db.py
```

**Expected Result:** `messier.db` file created with 5 sample objects

---

## Phase 3: Backend API Development 🔧

### Step 5: Set Up API Structure

**Create Pydantic models for request/response:**

**`app/models/request.py`**:
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time

class LocationModel(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: str = Field(..., example="Europe/London")
    elevation: Optional[float] = Field(0, ge=0)

class EquipmentModel(BaseModel):
    aperture_mm: float = Field(..., gt=0, example=200)
    focal_length_mm: float = Field(..., gt=0, example=1000)
    sensor_width_mm: float = Field(..., gt=0, example=23.5)
    sensor_height_mm: float = Field(..., gt=0, example=15.6)

class ObservationModel(BaseModel):
    date: date
    start_time: time
    duration_hours: float = Field(..., gt=0, le=12, example=4)

class PreferencesModel(BaseModel):
    min_altitude: float = Field(30, ge=0, le=90)
    moon_avoidance_deg: float = Field(30, ge=0, le=90)
    include_planets: bool = Field(True)

class TargetCalculationRequest(BaseModel):
    location: LocationModel
    equipment: EquipmentModel
    observation: ObservationModel
    preferences: PreferencesModel
```

**`app/models/response.py`**:
```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import time

class VisibilityModel(BaseModel):
    peak_time: str
    peak_altitude: float
    duration_hours: float

class TargetModel(BaseModel):
    id: str
    name: str
    type: str
    score: float
    visibility: VisibilityModel
    moon_separation: float
    weather_score: Optional[float] = None
    equipment_match: str
    magnitude: float
    size_arcmin: float
    constellation: str
    difficulty: str
    description: str

class MoonDataModel(BaseModel):
    phase: str
    illumination: float
    rise_time: Optional[str]
    set_time: Optional[str]

class TargetCalculationResponse(BaseModel):
    targets: List[TargetModel]
    moon: MoonDataModel
```

**Create catalogue router:**

**`app/api/catalogue.py`**:
```python
from fastapi import APIRouter, HTTPException
import sqlite3
import json
from pathlib import Path

router = APIRouter()

def get_db_connection():
    db_path = Path(__file__).parent.parent / "database" / "messier.db"
    return sqlite3.connect(db_path)

@router.get("/messier")
def get_messier_catalogue():
    """Get all Messier objects from the catalogue"""
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM messier_objects ORDER BY messier_number")
        rows = cursor.fetchall()
        
        objects = []
        for row in rows:
            obj = dict(row)
            obj['best_months'] = json.loads(obj['best_months'])
            objects.append(obj)
        
        conn.close()
        
        return {"objects": objects, "count": len(objects)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/messier/{object_id}")
def get_messier_object(object_id: str):
    """Get a specific Messier object by ID"""
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM messier_objects WHERE id = ?", (object_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail=f"Object {object_id} not found")
        
        obj = dict(row)
        obj['best_months'] = json.loads(obj['best_months'])
        
        conn.close()
        
        return obj
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Update main.py to include the router:**

**`app/main.py`** (updated):
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import catalogue

app = FastAPI(
    title="Astrophotography Target API",
    description="API for calculating optimal astrophotography targets",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4321"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(catalogue.router, prefix="/api/v1/catalogue", tags=["catalogue"])

@app.get("/")
def read_root():
    return {
        "message": "Astrophotography Target API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

**Test the API:**
```bash
# Start the server
uvicorn app.main:app --reload

# Test endpoints (in another terminal)
curl http://localhost:8000/api/v1/catalogue/messier
curl http://localhost:8000/api/v1/catalogue/messier/M31
```

**Expected Result:** API returns Messier catalogue data in JSON format

---

## Phase 4: Frontend Development 🎨

### Step 8: Build Astro Components

**Create base layout:**

**`frontend/src/layouts/Layout.astro`**:
```astro
---
interface Props {
  title: string;
}

const { title } = Astro.props;
---

<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <title>{title}</title>
  </head>
  <body class="bg-gray-900 text-white min-h-screen">
    <nav class="bg-gray-800 border-b border-gray-700">
      <div class="container mx-auto px-4 py-4">
        <h1 class="text-2xl font-bold">🔭 Astrophotography Target Finder</h1>
      </div>
    </nav>
    <main class="container mx-auto px-4 py-8">
      <slot />
    </main>
    <footer class="bg-gray-800 border-t border-gray-700 mt-12">
      <div class="container mx-auto px-4 py-6 text-center text-gray-400">
        <p>Built with Astro & FastAPI | Powered by Astropy</p>
      </div>
    </footer>
  </body>
</html>

<style is:global>
  @import '../styles/global.css';
</style>
```

**Create API client:**

**`frontend/src/lib/api.ts`**:
```typescript
const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface MessierObject {
  id: string;
  name: string;
  type: string;
  magnitude: number;
  size_arcmin: number;
  constellation: string;
  difficulty: string;
  description: string;
}

export async function getMessierCatalogue(): Promise<MessierObject[]> {
  const response = await fetch(`${API_BASE_URL}/catalogue/messier`);
  if (!response.ok) {
    throw new Error('Failed to fetch Messier catalogue');
  }
  const data = await response.json();
  return data.objects;
}

export async function getMessierObject(id: string): Promise<MessierObject> {
  const response = await fetch(`${API_BASE_URL}/catalogue/messier/${id}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch object ${id}`);
  }
  return response.json();
}
```

**Create home page:**

**`frontend/src/pages/index.astro`**:
```astro
---
import Layout from '../layouts/Layout.astro';
import { getMessierCatalogue } from '../lib/api';

let objects = [];
let error = null;

try {
  objects = await getMessierCatalogue();
} catch (e) {
  error = e.message;
}
---

<Layout title="Astrophotography Target Finder">
  <div class="max-w-4xl mx-auto">
    <div class="text-center mb-12">
      <h1 class="text-4xl font-bold mb-4">Find Your Perfect Astrophotography Target</h1>
      <p class="text-xl text-gray-400">
        Discover what to image tonight based on your location and equipment
      </p>
    </div>

    {error && (
      <div class="bg-red-900 border border-red-700 text-red-100 px-4 py-3 rounded mb-6">
        <p><strong>Error:</strong> {error}</p>
        <p class="text-sm mt-2">Make sure the backend server is running on http://localhost:8000</p>
      </div>
    )}

    <div class="bg-gray-800 rounded-lg p-6 mb-8">
      <h2 class="text-2xl font-bold mb-4">Messier Catalogue</h2>
      <p class="text-gray-400 mb-6">
        Browse {objects.length} deep sky objects perfect for astrophotography
      </p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        {objects.map((obj) => (
          <div class="bg-gray-700 rounded-lg p-4 hover:bg-gray-600 transition">
            <div class="flex justify-between items-start mb-2">
              <h3 class="text-lg font-bold">{obj.id} - {obj.name}</h3>
              <span class={`px-2 py-1 rounded text-xs ${
                obj.difficulty === 'easy' ? 'bg-green-600' :
                obj.difficulty === 'moderate' ? 'bg-yellow-600' :
                'bg-red-600'
              }`}>
                {obj.difficulty}
              </span>
            </div>
            <p class="text-sm text-gray-300 mb-2">{obj.description}</p>
            <div class="flex gap-4 text-sm text-gray-400">
              <span>Type: {obj.type}</span>
              <span>Mag: {obj.magnitude}</span>
              <span>Size: {obj.size_arcmin}'</span>
            </div>
          </div>
        ))}
      </div>
    </div>

    <div class="bg-blue-900 border border-blue-700 rounded-lg p-6">
      <h3 class="text-xl font-bold mb-2">🚀 Coming Soon</h3>
      <ul class="list-disc list-inside text-gray-300 space-y-1">
        <li>Location-based target recommendations</li>
        <li>Equipment compatibility matching</li>
        <li>Real-time visibility calculations</li>
        <li>Interactive sky maps</li>
        <li>Weather integration</li>
      </ul>
    </div>
  </div>
</Layout>
```

**Test the frontend:**
```bash
cd frontend
npm run dev
```

Visit http://localhost:4321 to see the catalogue displayed.

**Expected Result:** Frontend displays Messier objects from the backend API

---

## Quick Start Commands 🏃

### Start Both Servers

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Verify Everything Works

1. ✅ Backend API: http://localhost:8000/docs
2. ✅ Frontend: http://localhost:4321
3. ✅ Catalogue endpoint: http://localhost:8000/api/v1/catalogue/messier
4. ✅ Frontend displays objects from backend

---

## Next Development Phases 📋

### Phase 5: Core Astronomy Services (Steps 6-7)
- Implement visibility calculations with Astropy
- Add moon position and phase calculations
- Create target ranking algorithm
- Build location geocoding service

### Phase 6: Advanced Features (Steps 9-11)
- Weather API integration
- Interactive sky map component
- Equipment field-of-view calculator
- Target recommendation engine

### Phase 7: Polish & Deploy (Steps 12-14)
- End-to-end testing
- API documentation
- Deployment configuration
- User guide

---

## Troubleshooting 🔧

### Backend Issues

**Import errors:**
```bash
pip install --upgrade -r requirements.txt
```

**Database not found:**
```bash
cd app/database
python init_db.py
```

### Frontend Issues

**Module not found:**
```bash
npm install
```

**CORS errors:**
- Check backend CORS settings in `app/main.py`
- Ensure frontend URL matches allowed origins

**API connection failed:**
- Verify backend is running on port 8000
- Check API_BASE_URL in `frontend/src/lib/api.ts`

---

## Environment Variables 🔐

Create `.env` files for sensitive data:

**`backend/.env`**:
```
OPENWEATHER_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./app/database/messier.db
CORS_ORIGINS=http://localhost:4321
```

**`frontend/.env`**:
```
PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## Success Criteria ✅

You've successfully kicked off development when:

1. ✅ Both frontend and backend servers run without errors
2. ✅ Frontend displays Messier objects from the backend API
3. ✅ API documentation is accessible at http://localhost:8000/docs
4. ✅ Database contains sample Messier objects
5. ✅ CORS is properly configured for local development

---

## Resources 📚

- [Astro Documentation](https://docs.astro.build)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Astropy Documentation](https://docs.astropy.org)
- [Messier Catalogue Reference](https://en.wikipedia.org/wiki/Messier_object)

---

**Ready to start coding? Follow the steps above and you'll have a working foundation in under an hour! 🚀**