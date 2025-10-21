# EchoWrite AI: Intelligent Content Repurposing Engine

![EchoWrite AI](https://img.shields.io/badge/EchoWrite%20AI-Content%20Repurposing-blue?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-121212?style=flat&logo=chainlink&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)

EchoWrite AI is an intelligent content repurposing platform that transforms YouTube videos and web articles into multiple content formats including blog posts, Twitter threads, and LinkedIn posts. Built with FastAPI, LangGraph, and Streamlit, it features advanced AI pipelines, user authentication, rate limiting, and webhook integration.

## 🌟 Features

- **Multi-Format Content Generation**: Transform URLs into blog posts, Twitter threads, and LinkedIn posts
- **Dual Content Sources**: Supports both YouTube videos (via transcription) and web articles
- **AI-Powered Pipeline**: LangGraph workflow with content extraction, RAG, insights, and generation
- **User Authentication**: JWT-based auth with registration, login, and demo modes
- **Rate Limiting**: Tier-based rate limiting for demo and registered users
- **Webhook Integration**: Real-time data forwarding to n8n workflows
- **Modern UI**: Clean Streamlit frontend with authentication and session management
- **Configurable LLMs**: Centralized model configuration with multiple provider support

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   FastAPI        │    │  LangGraph      │
│   Frontend      │◄──►│   Backend        │◄──►│  AI Pipeline    │
│                 │    │                  │    │                 │
│ • Auth UI       │    │ • JWT Auth       │    │ • Content       │
│ • Content Form  │    │ • Rate Limiting  │    │   Extraction    │
│ • Results Tabs  │    │ • API Endpoints  │    │ • RAG Pipeline  │
└─────────────────┘    └──────────────────┘    │ • Content Gen   │
                                │               └─────────────────┘
                                │               
                       ┌────────▼────────┐    
                       │   n8n Webhook   │    
                       │   Integration   │    
                       └─────────────────┘    
```

## 📁 Project Structure

```
EchoWrite/
├── app/                          # Backend application
│   ├── main.py                   # FastAPI application entry point
│   ├── schemas.py                # Pydantic models and validation schemas
│   ├── rate_limiter.py           # Rate limiting implementation
│   ├── ai_core/                  # LangGraph AI pipeline
│   │   ├── graph.py              # State management and workflow
│   │   ├── nodes.py              # Individual pipeline nodes
│   │   └── prompts.py            # AI agent prompts
│   ├── services/                 # Core services
│   │   ├── content_extractor.py  # YouTube/web content extraction
│   │   └── rag_pipeline.py       # ChromaDB RAG implementation
│   └── config/                   # Configuration management
│       └── llm_config.py         # LLM provider and model settings
├── frontend/                     # Streamlit frontend
│   └── app.py                    # Complete Streamlit application
├── n8n/                          # Automation workflows
│   └── workflow.json             # n8n workflow definitions
├── tests/                        # Test suite
├── requirements.txt              # Python dependencies
└── README.md                     # This documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- GROQ API Key
- Whisper API URL (for YouTube transcription)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd EchoWrite
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment configuration**
Create a `.env` file with:
```env
GROQ_API_KEY=your_groq_api_key_here
WHISPER_API_URL=your_whisper_api_endpoint
JWT_SECRET=your_jwt_secret_key_here
```

5. **Start the backend**
```bash
cd app
uvicorn main:app --port 8080 --reload
```

6. **Start the frontend** (in new terminal)
```bash
cd frontend
streamlit run app.py
```

7. **Access the application**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8080
- API Documentation: http://localhost:8080/docs

## 🧠 AI Pipeline Deep Dive

### LangGraph Workflow (`app/ai_core/graph.py`)

The content repurposing pipeline is built using LangGraph, providing a stateful, multi-agent workflow:

#### State Management
```python
class ContentState(TypedDict):
    url: str                          # Input URL
    user_id: Optional[str]            # User tracking
    extracted_text: Optional[str]     # Raw content
    extraction_method: Optional[str]  # youtube/website
    chunks: Optional[List[str]]       # Text chunks for RAG
    vector_store_id: Optional[str]    # ChromaDB collection ID
    key_insights: Optional[Dict]      # Extracted insights
    blog_post: Optional[str]          # Generated blog post
    twitter_thread: Optional[List]    # Generated Twitter thread
    linkedin_post: Optional[str]      # Generated LinkedIn post
    errors: List[str]                 # Error tracking
    current_step: str                 # Pipeline progress
    processing_time: Optional[float]  # Performance metrics
    word_count: Optional[int]         # Content metrics
```

#### Pipeline Nodes (`app/ai_core/nodes.py`)

1. **Content Extraction Node**
   - Routes URLs to appropriate extraction method
   - YouTube: Whisper API transcription
   - Websites: BeautifulSoup web scraping
   - Error handling and validation

2. **RAG Population Node**
   - Text chunking with smart splitting
   - ChromaDB vector storage
   - Embedding generation

3. **Insights Extraction Node**
   - AI-powered content analysis
   - Theme identification
   - Statistics and arguments extraction
   - Audience and tone analysis

4. **Content Generation Node**
   - Multi-format content creation
   - Blog posts (800-1200 words)
   - Twitter threads (5-8 tweets)
   - LinkedIn posts (150-300 words)

### AI Prompts (`app/ai_core/prompts.py`)

Specialized prompts for each AI agent:
- **Content Router**: URL analysis and tool selection
- **Insights Extractor**: Structured content analysis
- **Blog Generator**: Long-form content creation
- **Twitter Generator**: Thread format optimization
- **LinkedIn Generator**: Professional platform adaptation

## 🔧 Content Extraction Services

### YouTube Transcription (`app/services/content_extractor.py`)
```python
@tool(args_schema=YoutubeURLInput)
def get_youtube_transcript(youtube_url: str) -> str:
    # Whisper API integration for video transcription
```

### Web Scraping (`app/services/content_extractor.py`)
```python
@tool(args_schema=WebpageURLInput)
def scrape_webpage_text(webpage_url: str) -> str:
    # BeautifulSoup-based content extraction
```

## 🗄️ RAG Pipeline (`app/services/rag_pipeline.py`)

### ChromaDB Integration
- **Vector Storage**: Persistent ChromaDB collections
- **Smart Chunking**: Paragraph and sentence-aware splitting
- **Embedding**: Default ChromaDB embedding model
- **Retrieval**: Context-aware content queries

### RAG Workflow
1. Content chunking with overlap
2. Vector embedding generation
3. Storage in ChromaDB collection
4. Contextual retrieval for insights
5. Enhanced content generation

## 🔐 Authentication System

### JWT Implementation (`app/main.py`)

#### User Management
- **Registration**: Username, email, password with validation
- **Login**: JWT token generation with expiration
- **Demo Mode**: Temporary access with restrictions
- **Password Security**: PBKDF2 with SHA-256 hashing

#### Authentication Endpoints
```python
POST /auth/register  # User registration
POST /auth/login     # User authentication  
POST /auth/demo      # Demo access
```

#### Security Features
- **Token Expiration**: 1-week default validity
- **Password Hashing**: PBKDF2 with 100,000 iterations
- **User Isolation**: Per-user rate limiting and tracking
- **Session Management**: Frontend token persistence

### Frontend Authentication (`frontend/app.py`)

#### User Experience
- **Login/Register Tabs**: Clean authentication interface
- **Session Persistence**: Automatic token management
- **Demo Access**: One-click temporary access
- **Token Expiry**: Automatic logout and re-authentication

## 🚦 Rate Limiting System

### Implementation (`app/rate_limiter.py`)

#### Rate Limit Configuration
```python
RATE_LIMITS = {
    "demo": {
        "requests_per_hour": 3,
        "requests_per_day": 5,
    },
    "registered": {
        "requests_per_hour": 15,
        "requests_per_day": 100,
    }
}
```

#### Features
- **User-Based Limiting**: JWT user_id tracking
- **Tier-Based Limits**: Different limits for user types
- **Memory Management**: Automatic cleanup of old records
- **Thread Safety**: Concurrent request handling
- **Usage Statistics**: Real-time limit monitoring

#### Rate Limit API
```python
GET /rate-limit/status  # Check current usage
```

### Frontend Integration
- **Usage Display**: Real-time limit information
- **Error Handling**: Clear rate limit messages
- **Tier Indication**: Demo vs registered user status

## 🔧 LLM Configuration (`app/config/llm_config.py`)

### Centralized Model Management
```python
LLM_SETTINGS = {
    "provider": "groq",
    "model": "llama-3.1-70b-versatile",
    "temperature": 0.7,
    "max_tokens": 4000
}
```

### Dynamic Configuration
- **Runtime Model Switching**: Change models without restart
- **Provider Support**: Groq with multiple models
- **Parameter Overrides**: Task-specific temperature/tokens
- **Available Models**: Programmatic model discovery

### Usage Examples
See [`LLM_CONFIG_USAGE.md`](LLM_CONFIG_USAGE.md) for detailed examples.

## 🔗 Webhook Integration

### n8n Automation (`app/main.py`)

#### Webhook Payload
```json
{
  "success": true,
  "url": "https://example.com/video",
  "user_id": "user_123",
  "blog_post": "Generated content...",
  "twitter_thread": ["Tweet 1", "Tweet 2"],
  "linkedin_post": "Professional content...",
  "extraction_method": "youtube",
  "word_count": 1500,
  "processing_time": 45.2,
  "current_step": "completed"
}
```

#### Integration Features
- **Fire-and-Forget**: Non-blocking webhook calls
- **Error Resilience**: Silent failure handling
- **Complete Data**: Full processing results
- **User Tracking**: User identification for analytics

## 📡 API Reference

### Authentication Endpoints

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com", 
  "password": "secure_password"
}
```

#### Login User
```http
POST /auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password"
}
```

#### Demo Access
```http
POST /auth/demo
```

### Content Processing

#### Repurpose Content
```http
POST /repurpose
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "url": "https://youtube.com/watch?v=example"
}
```

#### Rate Limit Status
```http
GET /rate-limit/status
Authorization: Bearer <jwt_token>
```

## 🧪 Testing

### Test Structure
```
tests/
├── test_tool.py           # Service integration tests
├── test_extractor_agent.py # Content extraction tests  
├── test_graph.py          # LangGraph pipeline tests
└── test_system.py         # End-to-end system tests
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_graph.py

# Run with coverage
python -m pytest tests/ --cov=app
```

## 🔧 Configuration

### Environment Variables
```env
# Required
GROQ_API_KEY=your_groq_api_key
WHISPER_API_URL=your_whisper_endpoint

# Optional  
JWT_SECRET=your_jwt_secret
ECHO_BACKEND_URL=http://127.0.0.1:8080  # Frontend backend URL
ECHO_N8N_WEBHOOK=your_n8n_webhook_url   # n8n integration
```

### LLM Configuration
Modify `app/config/llm_config.py` to:
- Change default models
- Add new providers
- Adjust generation parameters
- Configure model availability

### Rate Limits
Modify `app/rate_limiter.py` to:
- Adjust user tier limits
- Change cleanup intervals
- Add new limit types
- Modify enforcement logic

## 🚀 Deployment

### Production Considerations

1. **Database Migration**: Replace in-memory storage with PostgreSQL/MongoDB
2. **Redis Integration**: Use Redis for rate limiting persistence
3. **Security Hardening**: 
   - Strong JWT secrets
   - HTTPS enforcement
   - CORS configuration
   - Input validation

4. **Monitoring**: Add logging, metrics, and health checks
5. **Scaling**: Docker containerization and load balancing

### Docker Deployment
```dockerfile
# Example Dockerfile structure
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app/
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the test files for usage examples

## 🔮 Roadmap

- [ ] PostgreSQL database integration
- [ ] Redis-based rate limiting
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Additional content formats (Instagram, TikTok)
- [ ] Enterprise authentication (LDAP, SSO)
- [ ] Advanced webhook customization
- [ ] Performance monitoring and alerting

---

Built with ❤️ using FastAPI, LangChain, and Streamlit AI - Setup and Usage Guide

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