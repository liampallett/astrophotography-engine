from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import catalogue, targets, moon, location

app = FastAPI(
    title="Astrophotography Target API",
    description="API for calculating optimal astrophotography targets based on location, equipment, and sky conditions",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for Astro frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4321", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(catalogue.router, prefix="/api/v1/catalogue", tags=["catalogue"])
app.include_router(targets.router, prefix="/api/v1/targets", tags=["targets"])
app.include_router(moon.router, prefix="/api/v1/moon", tags=["moon"])
app.include_router(location.router, prefix="/api/v1/location", tags=["location"])

@app.get("/")
def read_root():
    return {
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

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "catalogue": "operational",
            "targets": "operational",
            "moon": "operational",
            "location": "operational"
        }
    }

# Made with Bob - Phase 3 Complete
