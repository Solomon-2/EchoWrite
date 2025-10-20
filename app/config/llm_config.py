"""
LLM Configuration for EchoWrite AI
Centralized model and provider settings
"""

import os
from typing import Any, Dict
from langchain_groq import ChatGroq


# Default LLM settings
LLM_SETTINGS = {
    "provider": "groq",
    "model": "openai/gpt-oss-20b",  # Updated to current available model
    "temperature": 0.7,
    "max_tokens": 4000
}

# Provider-specific model mappings
AVAILABLE_MODELS = {
    "groq": [
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant", 
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ]
}


def get_llm(**kwargs) -> Any:
    """
    Get configured LLM instance based on settings
    
    Args:
        **kwargs: Override default settings (model, temperature, max_tokens)
    
    Returns:
        Configured LLM instance
    """
    settings = LLM_SETTINGS.copy()
    settings.update(kwargs)
    
    provider = settings["provider"]
    
    if provider == "groq":
        return ChatGroq(
            model=settings["model"],
            temperature=settings["temperature"],
            max_tokens=settings["max_tokens"]
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def update_model(model: str) -> None:
    """Update the default model"""
    LLM_SETTINGS["model"] = model


def update_provider(provider: str, model: str = None) -> None:
    """Update provider and optionally model"""
    LLM_SETTINGS["provider"] = provider
    if model:
        LLM_SETTINGS["model"] = model


def get_available_models(provider: str = None) -> Dict:
    """Get available models for provider or all providers"""
    if provider:
        return {provider: AVAILABLE_MODELS.get(provider, [])}
    return AVAILABLE_MODELS