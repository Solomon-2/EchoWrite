"""
LangGraph nodes for the content repurposing pipeline

Each node is a function that takes the state and returns an updated state.
"""

import json
from typing import Dict, Any, List
from langchain.prompts import ChatPromptTemplate

from ..config.llm_config import get_llm
from ..services.content_extractor import get_youtube_transcript, scrape_website_text
from ..services.rag_pipeline import rag_pipeline
from .prompts import (
    CONTENT_EXTRACTION_ROUTER_PROMPT,
    INSIGHTS_EXTRACTION_PROMPT,
    BLOG_POST_GENERATION_PROMPT,
    TWITTER_THREAD_GENERATION_PROMPT,
    LINKEDIN_POST_GENERATION_PROMPT,
    RAG_QUERY_THEMES,
    RAG_QUERY_STATISTICS,
    RAG_QUERY_ARGUMENTS,
    RAG_QUERY_AUDIENCE_TONE
)

import json
import asyncio
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate

from ..services.content_extractor import get_youtube_transcript, scrape_webpage_text
from ..services.rag_pipeline import rag_pipeline
from .prompts import (
    CONTENT_EXTRACTION_ROUTER_PROMPT,
    INSIGHTS_EXTRACTION_PROMPT,
    BLOG_POST_GENERATION_PROMPT,
    TWITTER_THREAD_GENERATION_PROMPT,
    LINKEDIN_POST_GENERATION_PROMPT,
    RAG_QUERY_THEMES,
    RAG_QUERY_STATISTICS,
    RAG_QUERY_ARGUMENTS,
    RAG_QUERY_AUDIENCE_TONE
)


def get_llm():
    """Get configured Groq LLM instance"""
    return ChatGroq(
        model="mixtral-8x7b-32768",
        temperature=0.7,
        max_tokens=4000
    )


def extract_content(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Content extraction router node.
    Analyzes URL and chooses appropriate extraction tool.
    """
    state["current_step"] = "extracting_content"
    
    try:
        url = state["url"]
        
        # Create agent with access to extraction tools
        llm = get_llm()
        tools = [get_youtube_transcript, scrape_website_text]
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a content extraction router. Choose and use the appropriate tool to extract content from the given URL."),
            ("human", CONTENT_EXTRACTION_ROUTER_PROMPT.format(url=url)),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        # Create agent
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        # Execute extraction
        result = agent_executor.invoke({"url": url})
        
        # Extract the content from the result
        extracted_text = result["output"]
        
        # Determine extraction method based on URL
        if "youtube.com" in url.lower() or "youtu.be" in url.lower():
            extraction_method = "youtube"
        else:
            extraction_method = "website"
        
        state["extracted_text"] = extracted_text
        state["extraction_method"] = extraction_method
        state["word_count"] = len(extracted_text.split()) if extracted_text else 0
        
    except Exception as e:
        state["errors"].append(f"Content extraction failed: {str(e)}")
        state["extracted_text"] = None
    
    return state

import json
import asyncio
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate

from ..services.content_extractor import get_youtube_transcript, scrape_webpage_text
from ..services.rag_pipeline import rag_pipeline
from .prompts import (
    CONTENT_EXTRACTION_ROUTER_PROMPT,
    INSIGHTS_EXTRACTION_PROMPT,
    BLOG_POST_GENERATION_PROMPT,
    TWITTER_THREAD_GENERATION_PROMPT,
    LINKEDIN_POST_GENERATION_PROMPT,
    RAG_QUERY_THEMES,
    RAG_QUERY_STATISTICS,
    RAG_QUERY_ARGUMENTS,
    RAG_QUERY_AUDIENCE_TONE
)


def get_llm():
    """Get configured Groq LLM instance"""
    return ChatGroq(
        model="mixtral-8x7b-32768",
        temperature=0.7,
        max_tokens=4000
    )


def extract_content(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Content extraction router node.
    Analyzes URL and chooses appropriate extraction tool.
    """
    state["current_step"] = "extracting_content"
    
    try:
        url = state["url"]
        
        # Simple URL-based routing
        if "youtube.com" in url.lower() or "youtu.be" in url.lower():
            # Use YouTube transcript tool
            extracted_text = get_youtube_transcript(url)
            extraction_method = "youtube"
        else:
            # Use web scraping tool
            extracted_text = scrape_webpage_text(url)
            extraction_method = "website"
        
        # Check if extraction was successful
        if extracted_text and not extracted_text.startswith("Error:"):
            state["extracted_text"] = extracted_text
            state["extraction_method"] = extraction_method
            state["word_count"] = len(extracted_text.split()) if extracted_text else 0
        else:
            state["errors"].append(f"Content extraction failed: {extracted_text}")
            state["extracted_text"] = None
        
    except Exception as e:
        state["errors"].append(f"Content extraction failed: {str(e)}")
        state["extracted_text"] = None
    
    return state


def populate_rag(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    RAG population node.
    Creates vector embeddings and stores content in ChromaDB.
    """
    state["current_step"] = "populating_rag"
    
    try:
        extracted_text = state.get("extracted_text")
        url = state.get("url")
        
        if not extracted_text:
            raise ValueError("No extracted text available for RAG processing")
        
        # Create RAG collection
        collection_id = rag_pipeline.create_collection(extracted_text, url)
        
        # Get chunks for state tracking
        chunks = rag_pipeline.chunk_text(extracted_text)
        
        state["vector_store_id"] = collection_id
        state["chunks"] = chunks
        
    except Exception as e:
        state["errors"].append(f"RAG pipeline creation failed: {str(e)}")
        state["vector_store_id"] = None
        state["chunks"] = None
    
    return state


def extract_insights(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Insights extraction node.
    Analyzes content using RAG to extract key insights.
    """
    state["current_step"] = "extracting_insights"
    
    try:
        collection_id = state.get("vector_store_id")
        
        if not collection_id:
            raise ValueError("No vector store available for insights extraction")
        
        llm = get_llm()
        
        # Query RAG for different types of insights
        themes_results = rag_pipeline.query_content(collection_id, RAG_QUERY_THEMES, n_results=3)
        stats_results = rag_pipeline.query_content(collection_id, RAG_QUERY_STATISTICS, n_results=3)
        arguments_results = rag_pipeline.query_content(collection_id, RAG_QUERY_ARGUMENTS, n_results=3)
        audience_results = rag_pipeline.query_content(collection_id, RAG_QUERY_AUDIENCE_TONE, n_results=2)
        
        # Combine relevant content for analysis
        relevant_content = []
        for result_set in [themes_results, stats_results, arguments_results, audience_results]:
            for result in result_set:
                relevant_content.append(result["content"])
        
        combined_content = "\n\n".join(relevant_content[:10])  # Limit to avoid token overflow
        
        # Create insights extraction prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert content analyst. Extract key insights in JSON format."),
            ("human", INSIGHTS_EXTRACTION_PROMPT.format(content=combined_content))
        ])
        
        # Generate insights
        chain = prompt | llm
        insights_response = chain.invoke({"content": combined_content})
        
        # Parse insights (attempt to extract JSON structure)
        insights_text = insights_response.content
        
        # Create structured insights object
        insights = {
            "main_themes": [],
            "key_statistics": [],
            "main_arguments": [],
            "target_audience": "general audience",
            "content_type": "informational",
            "tone": "neutral"
        }
        
        # Simple parsing logic (could be enhanced with better JSON extraction)
        lines = insights_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if "main themes" in line.lower():
                current_section = "main_themes"
            elif "key statistics" in line.lower():
                current_section = "key_statistics"
            elif "main arguments" in line.lower():
                current_section = "main_arguments"
            elif "target audience" in line.lower():
                current_section = "target_audience"
            elif "content type" in line.lower():
                current_section = "content_type"
            elif "tone" in line.lower():
                current_section = "tone"
            elif line.startswith("-") or line.startswith("*") or line.startswith("•"):
                if current_section in ["main_themes", "key_statistics", "main_arguments"]:
                    clean_item = line.lstrip("-*•").strip()
                    if clean_item:
                        insights[current_section].append(clean_item)
            elif ":" in line and current_section in ["target_audience", "content_type", "tone"]:
                value = line.split(":", 1)[1].strip()
                if value:
                    insights[current_section] = value
        
        state["key_insights"] = insights
        
    except Exception as e:
        state["errors"].append(f"Insights extraction failed: {str(e)}")
        state["key_insights"] = None
    
    return state


def generate_content_suite(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Content generation node.
    Generates blog post, Twitter thread, and LinkedIn post in parallel.
    """
    state["current_step"] = "generating_content"
    
    try:
        insights = state.get("key_insights")
        collection_id = state.get("vector_store_id")
        
        if not insights or not collection_id:
            raise ValueError("Missing insights or vector store for content generation")
        
        # Get relevant content context from RAG
        context_results = rag_pipeline.query_content(collection_id, "main content summary", n_results=5)
        context = "\n\n".join([r["content"] for r in context_results])
        
        insights_str = json.dumps(insights, indent=2)
        
        # Generate all three content types
        llm = get_llm()
        
        # Blog post
        blog_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert blog writer. Create engaging, well-structured long-form content."),
            ("human", BLOG_POST_GENERATION_PROMPT.format(insights=insights_str, context=context))
        ])
        blog_chain = blog_prompt | llm
        blog_result = blog_chain.invoke({"insights": insights_str, "context": context})
        
        # Twitter thread
        twitter_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a social media expert. Create viral Twitter threads."),
            ("human", TWITTER_THREAD_GENERATION_PROMPT.format(insights=insights_str, context=context))
        ])
        twitter_chain = twitter_prompt | llm
        twitter_result = twitter_chain.invoke({"insights": insights_str, "context": context})
        
        # LinkedIn post
        linkedin_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a professional content creator. Create engaging LinkedIn posts."),
            ("human", LINKEDIN_POST_GENERATION_PROMPT.format(insights=insights_str, context=context))
        ])
        linkedin_chain = linkedin_prompt | llm
        linkedin_result = linkedin_chain.invoke({"insights": insights_str, "context": context})
        
        # Parse Twitter thread into individual tweets
        twitter_content = twitter_result.content
        twitter_lines = [line.strip() for line in twitter_content.split('\n') if line.strip()]
        twitter_thread = []
        
        for line in twitter_lines:
            # Look for numbered tweets or thread format
            if any(starter in line.lower() for starter in ['1/', '2/', '3/', '4/', '5/', '6/', '7/', '8/', 'thread:', '🧵']):
                twitter_thread.append(line)
            elif len(line) > 20 and len(line) <= 280:  # Reasonable tweet length
                twitter_thread.append(line)
        
        # Ensure we have at least 5 tweets, max 8
        if len(twitter_thread) < 5:
            # Split content into more tweets if needed
            remaining_content = twitter_result.content
            while len(twitter_thread) < 5 and remaining_content:
                if len(remaining_content) > 280:
                    split_point = remaining_content.rfind(' ', 0, 280)
                    if split_point == -1:
                        split_point = 280
                    tweet = remaining_content[:split_point].strip()
                    remaining_content = remaining_content[split_point:].strip()
                else:
                    tweet = remaining_content.strip()
                    remaining_content = ""
                
                if tweet and tweet not in twitter_thread:
                    twitter_thread.append(tweet)
        
        twitter_thread = twitter_thread[:8]  # Max 8 tweets
        
        state["blog_post"] = blog_result.content
        state["twitter_thread"] = twitter_thread
        state["linkedin_post"] = linkedin_result.content
        
    except Exception as e:
        state["errors"].append(f"Content generation failed: {str(e)}")
        state["blog_post"] = None
        state["twitter_thread"] = None
        state["linkedin_post"] = None
    
    return state
