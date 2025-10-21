FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install streamlit and required packages
RUN pip install --no-cache-dir \
    streamlit==1.50.0 \
    requests==2.32.5 \
    python-dotenv==1.1.1

# Copy frontend code
COPY app.py .

# Create streamlit config
RUN mkdir -p ~/.streamlit
RUN echo '[server]\nheadless = true\nport = 8501\naddress = "0.0.0.0"' > ~/.streamlit/config.toml

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run streamlit
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]