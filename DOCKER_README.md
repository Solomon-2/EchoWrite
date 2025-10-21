# EchoWrite AI - Docker Setup Guide

This guide explains how to run EchoWrite AI using Docker containers.

## Architecture

The application consists of two services:
- **Backend**: FastAPI application (`app/main.py`) running on uvicorn
- **Frontend**: Streamlit web interface (`frontend/app.py`)

## Prerequisites

1. **Docker & Docker Compose**: Install from [docker.com](https://docs.docker.com/get-docker/)
2. **Groq API Key**: Sign up at [console.groq.com](https://console.groq.com/) to get your API key

## Quick Start

1. **Clone and navigate to the project**:
   ```bash
   git clone <your-repo-url>
   cd EchoWrite
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file and add your Groq API key:
   ```
   GROQ_API_KEY=your_actual_groq_api_key_here
   JWT_SECRET=your_super_secret_jwt_key_change_in_production
   ```

3. **Build and start the services**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - **Frontend**: http://localhost:8501 (Streamlit interface)
   - **Backend API**: http://localhost:8080 (FastAPI docs at http://localhost:8080/docs)

## Docker Commands

### Development Mode (with auto-restart)
```bash
# Build and start services
docker-compose up --build

# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Production Mode
```bash
# Build and start in production
docker-compose -f docker-compose.yml up --build -d

# Scale services if needed
docker-compose up --scale backend=2
```

### Management Commands
```bash
# Stop services
docker-compose down

# Stop and remove volumes (will delete ChromaDB data)
docker-compose down -v

# Restart specific service
docker-compose restart backend

# Rebuild specific service
docker-compose build backend
docker-compose up -d backend
```

## Service Details

### Backend Service
- **Container**: `echowrite_backend`
- **Port**: 8080 (mapped from container port 8000)
- **Health Check**: `/health` endpoint
- **Data Persistence**: ChromaDB data stored in `./data/chromadb`

### Frontend Service  
- **Container**: `echowrite_frontend`
- **Port**: 8501
- **Depends on**: Backend service (waits for health check)
- **Configuration**: Connects to backend via internal Docker network

## Data Persistence

ChromaDB data is persisted using Docker volumes:
- Host directory: `./data/chromadb`
- Container directories: `/app/data/chromadb` and `/app/app/data/chromadb`

**Important**: Don't delete the `./data/chromadb` directory if you want to keep your vector database data.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | Yes | - | Your Groq API key for AI functionality |
| `JWT_SECRET` | No | Auto-generated | Secret key for JWT token signing |
| `BACKEND_BASE_URL` | No | Auto-configured | Backend URL for frontend (auto-set in Docker) |

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Check what's using the port
   netstat -tulpn | grep :8501
   
   # Change ports in docker-compose.yml if needed
   ports:
     - "8502:8501"  # Use different host port
   ```

2. **Permission issues with data directory**:
   ```bash
   # Fix permissions
   sudo chown -R $USER:$USER ./data/chromadb
   chmod -R 755 ./data/chromadb
   ```

3. **API key not working**:
   - Verify your Groq API key is correct in `.env`
   - Check backend logs: `docker-compose logs backend`

4. **Services not connecting**:
   ```bash
   # Check network connectivity
   docker-compose exec frontend ping backend
   
   # Check if backend is responding
   docker-compose exec frontend curl http://backend:8000/health
   ```

### Debugging

1. **Access container shell**:
   ```bash
   # Backend container
   docker-compose exec backend bash
   
   # Frontend container  
   docker-compose exec frontend bash
   ```

2. **Check logs in detail**:
   ```bash
   # All services with timestamps
   docker-compose logs -f -t
   
   # Specific service with tail
   docker-compose logs --tail=100 backend
   ```

3. **Test API directly**:
   ```bash
   # Health check
   curl http://localhost:8080/health
   
   # Get rate limit status (requires auth)
   curl -H "Authorization: Bearer <your-token>" http://localhost:8080/rate-limit/status
   ```

## Development Setup

For development with code auto-reload:

1. **Create development override**:
   ```yaml
   # docker-compose.override.yml
   version: '3.8'
   services:
     backend:
       volumes:
         - ./app:/app/app
       command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
     
     frontend:
       volumes:
         - ./frontend:/app/frontend
   ```

2. **Start development mode**:
   ```bash
   docker-compose up --build
   ```

## Security Notes

- Change the `JWT_SECRET` in production
- Don't expose the backend port (8080) directly in production
- Use a reverse proxy (nginx) for production deployments
- Keep your `.env` file secure and never commit it to version control

## Production Deployment

For production, consider:

1. **Use a reverse proxy** (nginx, traefik)
2. **Enable HTTPS/SSL**
3. **Set resource limits** in docker-compose.yml
4. **Use Docker secrets** for sensitive data
5. **Set up monitoring** and logging
6. **Regular backups** of ChromaDB data

Example production additions to docker-compose.yml:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```