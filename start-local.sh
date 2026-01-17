#!/bin/bash

echo "🚀 Quick Start - Running Locally (Without Docker)"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi
echo "✅ Python found: $(python3 --version)"

# Check Node
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi
echo "✅ Node.js found: $(node --version)"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL client not found. You'll need PostgreSQL running."
    echo "   Install: sudo apt-get install postgresql postgresql-contrib"
fi

echo ""
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies (this will take a few minutes)
echo "Installing Python dependencies (this may take 5-10 minutes)..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Created .env from template. Please add your OPENAI_API_KEY!"
fi

# Create upload directory
mkdir -p ../data/uploads

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "🔧 Setting up frontend..."
cd ../frontend

# Install frontend dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "==========================================\n"
echo "📋 MANUAL STEPS REQUIRED:"
echo ""
echo "1. Start PostgreSQL database (if not running):"
echo "   sudo systemctl start postgresql"
echo "   OR use Docker: docker run -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15"
echo ""
echo "2. Create database:"
echo "   sudo -u postgres psql -c 'CREATE DATABASE patient_summarizer;'"
echo ""
echo "3. Start the backend (in terminal 1):"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo ""
echo "4. Start the frontend (in terminal 2):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "5. Open browser:"
echo "   http://localhost:5173"
echo ""
echo "==========================================\n"
