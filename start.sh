#!/bin/bash

echo "🚀 Starting Smart Patient Case Summarizer..."
echo ""

# Check if .env exists
if [ ! -f backend/.env ]; then
    echo "⚠️  Creating backend/.env from template..."
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env"
    echo "⚠️  IMPORTANT: Edit backend/.env and add your OPENAI_API_KEY"
    echo ""
fi

# Create data directories
mkdir -p data/uploads data/postgres

echo "📦 Starting Docker containers..."
docker compose up --build -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 5

echo ""
echo "✅ Smart Patient Case Summarizer is running!"
echo ""
echo "📍 Access points:"
echo "   Frontend:    http://localhost:5173"
echo "   Backend API: http://localhost:8000"
echo "   API Docs:    http://localhost:8000/docs"
echo ""
echo "📝 Next steps:"
echo "   1. Make sure you've set your OPENAI_API_KEY in backend/.env"
echo "   2. Open http://localhost:5173 in your browser"
echo "   3. Create an account to get started"
echo ""
echo "🛑 To stop: docker compose down"
echo "📋 View logs: docker compose logs -f"
