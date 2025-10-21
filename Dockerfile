# Single container running both FastAPI backend and Streamlit frontend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
COPY app/requirements.txt app_requirements.txt

# Install dependencies (combine both requirements files)
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r app_requirements.txt

# Copy application code
COPY app/ ./app/
COPY frontend/ ./frontend/
COPY data/ ./data/

# Create data directory for ChromaDB persistence
RUN mkdir -p /app/data/chromadb

# Copy supervisor configuration
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create startup script
COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

# Expose ports for both services
EXPOSE 8000 8501

# Health check for both services
HEALTHCHECK --interval=30s --timeout=15s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health && curl -f http://localhost:8501/_stcore/health || exit 1

# Run startup script
CMD ["/start.sh"]