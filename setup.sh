#!/bin/bash

# Astrophotography Target Engine - Complete Setup Script
# This script initializes both backend and frontend in one go

set -e  # Exit on any error

echo "🔭 Astrophotography Target Engine - Setup Script"
echo "================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "setup.sh" ]; then
    echo "❌ Error: Please run this script from the astrophotography-engine directory"
    exit 1
fi

# Check for required commands
echo "▶ Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi
echo "✓ Python 3 found: $(python3 --version)"

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi
echo "✓ Node.js found: $(node --version)"

if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi
echo "✓ npm found: $(npm --version)"

echo ""
echo "================================================"
echo "🐍 Setting up Backend"
echo "================================================"
echo ""

cd backend

# Create virtual environment
echo "▶ Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "⚠ Virtual environment already exists, skipping creation"
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "▶ Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install Python dependencies
echo "▶ Installing Python dependencies (this may take a few minutes)..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✓ Python dependencies installed"

# Initialize database
echo "▶ Initializing database..."
if [ -f "app/database/messier.db" ]; then
    echo "⚠ Database already exists, skipping initialization"
else
    python app/database/init_db.py
    echo "✓ Database initialized with 10 Messier objects"
fi

cd ..

echo ""
echo "================================================"
echo "⚛️  Setting up Frontend"
echo "================================================"
echo ""

cd frontend

# Install Node dependencies
echo "▶ Installing Node.js dependencies (this may take a few minutes)..."
npm install
echo "✓ Node.js dependencies installed"

cd ..

echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "To start the application, run:"
echo ""
echo "  ./start.sh     # Start both backend and frontend"
echo ""
echo "Or manually in separate terminals:"
echo ""
echo "  Terminal 1 (Backend):"
echo "    cd backend"
echo "    source venv/bin/activate"
echo "    uvicorn app.main:app --reload"
echo ""
echo "  Terminal 2 (Frontend):"
echo "    cd frontend"
echo "    npm run dev"
echo ""
echo "Then visit: http://localhost:4321"
echo ""

# Made with Bob
