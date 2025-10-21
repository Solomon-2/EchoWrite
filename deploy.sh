#!/bin/bash
set -e

echo "EchoWrite AI - Quick Deploy Script"
echo "=================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ ERROR: Docker is not installed"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ ERROR: Docker Compose is not installed"
    echo "Please install Docker Compose"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit the .env file and add your GROQ_API_KEY"
    echo "Then run this script again."
    echo ""
    exit 1
fi

# Check if GROQ_API_KEY is set properly
if grep -q "GROQ_API_KEY=your_groq_api_key_here" .env; then
    echo ""
    echo "⚠️  WARNING: Please update your GROQ_API_KEY in the .env file"
    echo "Current value appears to be the default placeholder."
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "🐳 Building and starting EchoWrite..."
docker-compose up --build -d

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ EchoWrite is starting up!"
    echo ""
    echo "🌐 Frontend (Streamlit): http://localhost:8501"
    echo "🔗 Backend API: http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: docker-compose down"
    echo ""
else
    echo ""
    echo "❌ Failed to start EchoWrite"
    echo "Check the error messages above."
    echo ""
    exit 1
fi