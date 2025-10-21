#!/bin/bash
set -e

# Set environment variables with defaults
export GROQ_API_KEY=${GROQ_API_KEY}
export JWT_SECRET=${JWT_SECRET:-"your-secret-key-change-in-production"}
export BACKEND_BASE_URL=${BACKEND_BASE_URL:-"http://localhost:8000"}

echo "Starting EchoWrite services..."
echo "Backend will be available at: http://localhost:8000"
echo "Frontend will be available at: http://localhost:8501"

# Ensure data directory exists and has proper permissions
mkdir -p /app/data/chromadb /app/app/data/chromadb
chmod -R 755 /app/data

# Start supervisord to manage both services
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf