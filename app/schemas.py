"""
Pydantic schemas for FastAPI request/response models
"""

from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any


class RepurposeRequest(BaseModel):
    """Request model for the content repurposing endpoint"""
    url: HttpUrl = Field(..., description="URL to repurpose (YouTube video or webpage)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.youtube.com/watch?v=example"
            }
        }


class ContentInsights(BaseModel):
    """Model for extracted content insights"""
    main_themes: List[str] = Field(..., description="Core themes of the content")
    key_statistics: List[str] = Field(default=[], description="Important statistics mentioned")
    main_arguments: List[str] = Field(..., description="Primary arguments or points")
    target_audience: str = Field(..., description="Intended audience for the content")
    content_type: str = Field(..., description="Type of original content")
    tone: str = Field(..., description="Overall tone of the content")


class GeneratedContent(BaseModel):
    """Model for generated content output"""
    blog_post: str = Field(..., description="Generated blog post (800-1200 words)")
    twitter_thread: List[str] = Field(..., description="Twitter thread (5-8 tweets)")
    linkedin_post: str = Field(..., description="LinkedIn post (150-300 words)")


class RepurposeResponse(BaseModel):
    """Response model for the content repurposing endpoint"""
    success: bool = Field(..., description="Whether the operation was successful")
    url: str = Field(..., description="Original URL that was processed")
    extraction_method: Optional[str] = Field(None, description="Method used for content extraction")
    word_count: Optional[int] = Field(None, description="Word count of extracted content")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    
    # Content analysis
    insights: Optional[ContentInsights] = Field(None, description="Extracted insights from content")
    
    # Generated content
    content: Optional[GeneratedContent] = Field(None, description="Generated content suite")
    
    # Error handling
    errors: List[str] = Field(default=[], description="Any errors that occurred during processing")
    current_step: str = Field(..., description="Current or final step in the pipeline")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "url": "https://www.youtube.com/watch?v=example",
                "extraction_method": "youtube",
                "word_count": 1500,
                "processing_time": 45.2,
                "insights": {
                    "main_themes": ["AI development", "automation", "productivity"],
                    "key_statistics": ["50% increase in efficiency", "10x faster processing"],
                    "main_arguments": ["AI improves productivity", "Automation reduces errors"],
                    "target_audience": "developers and tech professionals",
                    "content_type": "educational",
                    "tone": "informative and encouraging"
                },
                "content": {
                    "blog_post": "# How AI is Transforming Development...",
                    "twitter_thread": [
                        "🧵 Thread: How AI is changing software development",
                        "1/ Traditional coding workflows are evolving...",
                        "2/ AI tools now help with code generation..."
                    ],
                    "linkedin_post": "The future of software development is here..."
                },
                "errors": [],
                "current_step": "completed"
            }
        }


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")
