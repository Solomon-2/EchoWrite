"""
FastAPI application for EchoWrite AI content repurposing service
"""

import os
import json
import threading
import hashlib
import secrets
from datetime import datetime, timedelta
import requests
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
import jwt
import sqlite3
from typing import Optional

from schemas import (
    RepurposeRequest, RepurposeResponse, HealthResponse, ContentInsights, GeneratedContent,
    RegisterRequest, LoginRequest, AuthResponse
)
from ai_core.graph import run_content_repurposing_pipeline

# Load environment variables
load_dotenv()

# Verify Groq API key is present
if not os.getenv("GROQ_API_KEY"):
    raise RuntimeError("GROQ_API_KEY environment variable is not set")

# N8N webhook configuration
N8N_WEBHOOK_URL = "https://nderitu-wahome.app.n8n.cloud/webhook-test/4d7ff303-fe36-4de4-936c-5c7070afd380"

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24 * 7  # 1 week

# Password hashing configuration
HASH_ITERATIONS = 100000  # PBKDF2 iterations for security
security = HTTPBearer()

# Simple in-memory user storage (replace with database in production)
users_db = {}

# User management functions
def hash_password(password: str) -> str:
    """Hash password using PBKDF2 with SHA-256"""
    # Generate a random salt
    salt = secrets.token_bytes(32)  # 32 bytes = 256 bits
    
    # Hash the password with PBKDF2
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        HASH_ITERATIONS
    )
    
    # Return salt + hash encoded as hex
    return salt.hex() + ':' + password_hash.hex()

def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verify password against stored hash"""
    try:
        # Split the stored hash into salt and hash
        salt_hex, hash_hex = stored_hash.split(':')
        salt = bytes.fromhex(salt_hex)
        stored_password_hash = bytes.fromhex(hash_hex)
        
        # Hash the provided password with the same salt
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt,
            HASH_ITERATIONS
        )
        
        # Compare hashes
        return password_hash == stored_password_hash
    except (ValueError, AttributeError):
        return False

def create_access_token(user_id: str, is_demo: bool = False) -> str:
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode = {
        "user_id": user_id,
        "is_demo": is_demo,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {
            "user_id": user_id,
            "is_demo": payload.get("is_demo", False)
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def send_to_webhook(response_data, final_state, user_id: str = None):
    """Send response data to n8n webhook in the background (fire and forget)"""
    try:
        # Create webhook payload with flattened content structure
        webhook_payload = {
            "success": response_data.get("success"),
            "url": response_data.get("url"),
            "user_id": user_id,
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


# Authentication endpoints
@app.post("/auth/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register a new user"""
    # Check if user already exists
    if request.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email already exists
    for user_data in users_db.values():
        if user_data.get("email") == request.email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create new user
    hashed_password = hash_password(request.password)
    user_id = f"user_{len(users_db) + 1}"
    
    users_db[request.username] = {
        "user_id": user_id,
        "email": request.email,
        "password_hash": hashed_password,
        "created_at": datetime.utcnow().isoformat(),
        "is_demo": False
    }
    
    # Generate token
    token = create_access_token(user_id, is_demo=False)
    
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user_id=user_id,
        is_demo=False,
        expires_in=ACCESS_TOKEN_EXPIRE_HOURS * 3600
    )


@app.post("/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login user"""
    # Find user by username or email
    user_data = None
    username_key = None
    
    for username, data in users_db.items():
        if username == request.username or data.get("email") == request.username:
            user_data = data
            username_key = username
            break
    
    if not user_data or not verify_password(request.password, user_data["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Generate token
    token = create_access_token(user_data["user_id"], is_demo=user_data.get("is_demo", False))
    
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user_id=user_data["user_id"],
        is_demo=user_data.get("is_demo", False),
        expires_in=ACCESS_TOKEN_EXPIRE_HOURS * 3600
    )


@app.post("/auth/demo", response_model=AuthResponse)
async def demo_login():
    """Get demo account access"""
    demo_user_id = f"demo_{datetime.utcnow().timestamp()}"
    
    # Generate demo token
    token = create_access_token(demo_user_id, is_demo=True)
    
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user_id=demo_user_id,
        is_demo=True,
        expires_in=ACCESS_TOKEN_EXPIRE_HOURS * 3600
    )


@app.post("/repurpose", response_model=RepurposeResponse)
async def repurpose_content(request: RepurposeRequest, auth_data: dict = Depends(verify_token)):
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
        user_id = auth_data["user_id"]
        
        # Run the content repurposing pipeline
        final_state = run_content_repurposing_pipeline(url, user_id)
        
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
        threading.Thread(target=send_to_webhook, args=(response_data, final_state, user_id), daemon=True).start()
        
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
