# EchoWrite AI - Setup and Usage Guide

## 🎯 Overview

EchoWrite AI is a sophisticated content repurposing system that transforms any URL (YouTube video or webpage) into multiple content formats using AI agents orchestrated with LangGraph.

**Output Formats:**
- 📰 Blog Post (800-1200 words)
- 🐦 Twitter Thread (5-8 tweets)
- 💼 LinkedIn Post (150-300 words)

## 🏗️ Architecture

The system uses a multi-agent pipeline with LangGraph:

1. **Content Extraction Router** - Intelligently chooses YouTube or web scraping
2. **RAG Pipeline** - Creates vector embeddings using ChromaDB
3. **Insights Analyst** - Extracts key themes, statistics, and arguments
4. **Content Generation Suite** - Three parallel agents create different formats

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run the API Server

```bash
# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
python -m app.main
```

### 4. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Main Endpoint**: `POST http://localhost:8000/repurpose`

## 📡 API Usage

### Request Format

```json
{
  "url": "https://www.youtube.com/watch?v=example"
}
```

### Response Format

```json
{
  "success": true,
  "url": "https://www.youtube.com/watch?v=example",
  "extraction_method": "youtube",
  "word_count": 1500,
  "processing_time": 45.2,
  "insights": {
    "main_themes": ["AI development", "automation"],
    "key_statistics": ["50% increase", "10x faster"],
    "main_arguments": ["AI improves productivity"],
    "target_audience": "developers",
    "content_type": "educational",
    "tone": "informative"
  },
  "content": {
    "blog_post": "# How AI is Transforming...",
    "twitter_thread": [
      "🧵 Thread: AI in development",
      "1/ Traditional workflows are evolving..."
    ],
    "linkedin_post": "The future of development is here..."
  },
  "errors": [],
  "current_step": "completed"
}
```

## 🧪 Testing

Run the end-to-end test:

```bash
python test_system.py
```

## 📁 Project Structure

```
EchoWrite/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── schemas.py           # Pydantic models
│   ├── ai_core/
│   │   ├── graph.py         # LangGraph workflow
│   │   ├── nodes.py         # Pipeline nodes
│   │   └── prompts.py       # AI agent prompts
│   └── services/
│       ├── content_extractor.py  # Extraction tools
│       └── rag_pipeline.py       # ChromaDB integration
├── data/                    # ChromaDB storage
├── requirements.txt
├── test_system.py
└── .env                     # Environment variables
```

## 🔧 Configuration

### Supported URLs

- **YouTube**: `youtube.com`, `youtu.be`, `m.youtube.com`
- **Websites**: Any public webpage with readable content

### Content Lengths

- **Blog Post**: 800-1200 words
- **Twitter Thread**: 5-8 tweets (~280 chars each)
- **LinkedIn Post**: 150-300 words

## 🛠️ Development

### Adding New Content Formats

1. Update `ContentState` in `graph.py`
2. Add new prompt in `prompts.py`
3. Extend `generate_content_suite` node in `nodes.py`
4. Update response schemas in `schemas.py`

### Customizing AI Behavior

Edit prompts in `app/ai_core/prompts.py` to change:
- Content tone and style
- Output structure
- Analysis depth

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Install dependencies with `pip install -r requirements.txt`
2. **API Key Error**: Ensure `GROQ_API_KEY` is set in `.env`
3. **ChromaDB Issues**: Check that `data/` directory is writable
4. **URL Extraction Fails**: Verify URL is publicly accessible

### Error Responses

The API returns detailed error information in the `errors` array:

```json
{
  "success": false,
  "errors": ["Content extraction failed: Invalid URL"],
  "current_step": "extracting_content"
}
```

## 🚀 Production Deployment

### Environment Variables

```env
GROQ_API_KEY=your_production_key
LOG_LEVEL=INFO
CORS_ORIGINS=https://yourdomain.com
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📊 Performance

- **Typical Processing Time**: 30-60 seconds
- **Memory Usage**: ~500MB with ChromaDB
- **Concurrent Requests**: Limited by Groq API rate limits

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is available under the MIT License.