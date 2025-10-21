# EchoWrite AI - Single Container Deployment 🚀

Deploy both FastAPI backend and Streamlit frontend in one simple container!

## 🎯 Quick Start (3 steps!)

### Step 1: Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Groq API key:
# GROQ_API_KEY=your_actual_groq_api_key_here
```

### Step 2: Deploy with one command
**Windows:**
```cmd
deploy.bat
```

**Linux/Mac:**
```bash
./deploy.sh
```

**Or manually:**
```bash
docker-compose up --build -d
```

### Step 3: Access your app
- **🌐 Frontend**: http://localhost:8501 (Main app interface)
- **🔗 Backend API**: http://localhost:8000 (API endpoints)
- **📚 API Docs**: http://localhost:8000/docs (Swagger documentation)

## 📋 What's Running

The single container runs both services using supervisor:
- **FastAPI backend** (uvicorn) on port 8000
- **Streamlit frontend** on port 8501
- **ChromaDB data** persisted in `./data/chromadb`

## 🛠️ Management Commands

```bash
# View logs (both services)
docker-compose logs -f

# Stop the application
docker-compose down

# Restart
docker-compose restart

# Rebuild and restart
docker-compose up --build -d

# View resource usage
docker stats echowrite_app
```

## 🔧 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | ✅ Yes | - | Your Groq API key |
| `JWT_SECRET` | ❌ No | Auto-generated | JWT signing secret |

## 📁 Project Structure

```
EchoWrite/
├── Dockerfile              # Single container definition
├── docker-compose.yml      # Service orchestration
├── deploy.bat             # Windows deploy script
├── deploy.sh              # Linux/Mac deploy script
├── .env.example           # Environment template
├── docker/
│   ├── supervisord.conf   # Process management
│   └── start.sh          # Container startup
├── app/                   # FastAPI backend
│   └── main.py           # API server
├── frontend/             # Streamlit frontend
│   └── app.py           # Web interface
└── data/
    └── chromadb/        # Persisted vector database
```

## 🐛 Troubleshooting

### Check if services are running:
```bash
# Health check both services
curl http://localhost:8000/health
curl http://localhost:8501/_stcore/health

# Or check container status
docker-compose ps
```

### View detailed logs:
```bash
# All logs
docker-compose logs

# Specific service logs
docker-compose exec echowrite_app tail -f /var/log/backend.log
docker-compose exec echowrite_app tail -f /var/log/frontend.log
```

### Access container shell:
```bash
docker-compose exec echowrite_app bash
```

### Common Issues:

1. **Port already in use**: Change ports in `docker-compose.yml`
2. **API key error**: Check your `.env` file has correct `GROQ_API_KEY`
3. **Permission issues**: Ensure `./data` directory is writable

## 🌍 Production Deployment

For production servers:

1. **Change JWT_SECRET** in `.env`:
   ```
   JWT_SECRET=your_super_secure_random_key_here
   ```

2. **Use a reverse proxy** (nginx example):
   ```nginx
   # Frontend
   location / {
       proxy_pass http://localhost:8501;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
   }
   
   # Backend API
   location /api {
       proxy_pass http://localhost:8000;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
   }
   ```

3. **Enable HTTPS** with Let's Encrypt or your SSL certificate

4. **Backup ChromaDB data** regularly:
   ```bash
   tar -czf chromadb-backup-$(date +%Y%m%d).tar.gz ./data/chromadb
   ```

## 💡 Why Single Container?

✅ **Simpler deployment** - One container to manage  
✅ **Lower resource usage** - Shared Python environment  
✅ **Easier networking** - Services communicate via localhost  
✅ **Perfect for small/medium deployments**  
✅ **Great for development and testing**  

## 🔄 Development Mode

For development with auto-reload:

```yaml
# Add to docker-compose.yml
volumes:
  - ./app:/app/app          # Backend code
  - ./frontend:/app/frontend # Frontend code
```

Then rebuild: `docker-compose up --build`

---

**🎉 That's it! Your EchoWrite AI is ready to transform content at http://localhost:8501**