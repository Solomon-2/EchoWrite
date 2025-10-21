"""
FastAPI application for EchoWrite AI content repurposing service
"""

import os
import json
import threading
from datetime import datetime
import requests
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from schemas import RepurposeRequest, RepurposeResponse, HealthResponse, ContentInsights, GeneratedContent
from ai_core.graph import run_content_repurposing_pipeline

# Load environment variables
load_dotenv()

# Verify Groq API key is present
if not os.getenv("GROQ_API_KEY"):
    raise RuntimeError("GROQ_API_KEY environment variable is not set")

# N8N webhook configuration
N8N_WEBHOOK_URL = "https://nderitu-wahome.app.n8n.cloud/webhook-test/4d7ff303-fe36-4de4-936c-5c7070afd380"


def send_to_webhook(response_data, final_state):
    """Send response data to n8n webhook in the background (fire and forget)"""
    try:
        # Create webhook payload with flattened content structure
        webhook_payload = {
            "success": response_data.get("success"),
            "url": response_data.get("url"),
            "blog_post": final_state.get("blog_post", ""),
            "twitter_thread": final_state.get("twitter_thread", []),
            "linkedin_post": final_state.get("linkedin_post", ""),
            "extraction_method": response_data.get("extraction_method"),
            "word_count": response_data.get("word_count"),
            "processing_time": response_data.get("processing_time"),
            "current_step": response_data.get("current_step")
        }
        
        headers = {"Content-Type": "application/json"}
        requests.post(N8N_WEBHOOK_URL, headers=headers, data=json.dumps(webhook_payload), timeout=5)
    except Exception:
        # Silently ignore webhook errors
        pass

# Initialize FastAPI app
app = FastAPI(
    title="EchoWrite AI",
    description="Intelligent content repurposing service that transforms URLs into multiple content formats",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with basic service information"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


@app.post("/repurpose", response_model=RepurposeResponse)
async def repurpose_content(request: RepurposeRequest):
    """
    Main endpoint to repurpose content from a URL into multiple formats.
    
    Takes a URL (YouTube video or webpage) and returns:
    - Blog post (800-1200 words)
    - Twitter thread (5-8 tweets)
    - LinkedIn post (150-300 words)
    """
    try:
        # Convert Pydantic URL to string
        url = str(request.url)
        
        # Run the content repurposing pipeline
        final_state = run_content_repurposing_pipeline(url)
        
        # Check if pipeline succeeded
        success = final_state.get("current_step") == "completed" and not final_state.get("errors")
        
        # Prepare response data
        response_data = {
            "success": success,
            "url": url,
            "extraction_method": final_state.get("extraction_method"),
            "word_count": final_state.get("word_count"),
            "processing_time": final_state.get("processing_time"),
            "errors": final_state.get("errors", []),
            "current_step": final_state.get("current_step", "unknown")
        }
        
        # Add insights if available
        if final_state.get("key_insights"):
            insights_data = final_state["key_insights"]
            response_data["insights"] = ContentInsights(
                main_themes=insights_data.get("main_themes", []),
                key_statistics=insights_data.get("key_statistics", []),
                main_arguments=insights_data.get("main_arguments", []),
                target_audience=insights_data.get("target_audience", "general audience"),
                content_type=insights_data.get("content_type", "informational"),
                tone=insights_data.get("tone", "neutral")
            )
        
        # Add generated content if available
        if final_state.get("blog_post") or final_state.get("twitter_thread") or final_state.get("linkedin_post"):
            response_data["content"] = GeneratedContent(
                blog_post=final_state.get("blog_post", ""),
                twitter_thread=final_state.get("twitter_thread", []),
                linkedin_post=final_state.get("linkedin_post", "")
            )
        
        # Send to webhook in background (fire and forget)
        threading.Thread(target=send_to_webhook, args=(response_data, final_state), daemon=True).start()
        
        return RepurposeResponse(**response_data)
        
    except Exception as e:
        # Handle any unexpected errors
        error_message = f"Unexpected error during content repurposing: {str(e)}"
        
        return RepurposeResponse(
            success=False,
            url=str(request.url),
            extraction_method=None,
            word_count=None,
            processing_time=None,
            insights=None,
            content=None,
            errors=[error_message],
            current_step="failed"
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler for unexpected errors"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error occurred",
            "status_code": 500
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
