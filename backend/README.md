# Astrophotography Target API - Backend

FastAPI backend for calculating optimal astrophotography targets.

## Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
python app/database/init_db.py
```

This creates `app/database/messier.db` with 10 sample Messier objects.

## Running the Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /` - API information
- `GET /health` - Health check

### Catalogue
- `GET /api/v1/catalogue/messier` - Get all Messier objects
- `GET /api/v1/catalogue/messier/{id}` - Get specific object (e.g., M31)

## Testing the API

### Using curl

```bash
# Get all objects
curl http://localhost:8000/api/v1/catalogue/messier

# Get specific object
curl http://localhost:8000/api/v1/catalogue/messier/M31
```

### Using the browser

Visit http://localhost:8000/docs for interactive API documentation.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   └── catalogue.py     # Catalogue endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py       # Request schemas
│   │   └── response.py      # Response schemas
│   ├── database/
│   │   ├── __init__.py
│   │   ├── init_db.py       # Database initialization
│   │   └── messier.db       # SQLite database
│   ├── core/
│   │   └── __init__.py
│   └── services/
│       └── __init__.py
├── requirements.txt
└── README.md
```

## Development

The server runs with auto-reload enabled, so changes to Python files will automatically restart the server.

## Next Steps

- [ ] Implement visibility calculations (Astropy)
- [ ] Add moon position and phase calculations
- [ ] Create target ranking algorithm
- [ ] Add location geocoding service
- [ ] Integrate weather API