# 🚀 Quick Run Guide

## First Time Setup

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
```

## Running the Application

### Start Backend (Terminal 1)
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```
✅ Backend running at http://localhost:8000

### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```
✅ Frontend running at http://localhost:4321

## Quick Test

Open http://localhost:4321 in your browser - you should see 10 Messier objects!

## API Documentation

Visit http://localhost:8000/docs for interactive API documentation.