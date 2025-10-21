"""
LangGraph State and Workflow Definition for EchoWrite AI

This module defines the state schema and assembles the AI workflow graph.
"""

from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from .nodes import extract_content, populate_rag, extract_insights, generate_content_suite


class ContentState(TypedDict):
    """
    State object that tracks content through the entire repurposing pipeline.
    Acts as a job ticket that gets passed between all nodes.
    """
    # Input
    url: str
    user_id: Optional[str]  # User ID for tracking and analytics
    
    # Content extraction
    extracted_text: Optional[str]
    extraction_method: Optional[str]  # 'youtube' or 'website'
    
    # RAG pipeline
    chunks: Optional[List[str]]
    vector_store_id: Optional[str]
    
    # Content analysis
    key_insights: Optional[Dict[str, Any]]
    
    # Generated content
    blog_post: Optional[str]
    twitter_thread: Optional[List[str]]
    linkedin_post: Optional[str]
    
    # Error handling
    errors: List[str]
    current_step: str
    
    # Metadata
    processing_time: Optional[float]
    word_count: Optional[int]


def create_content_repurposing_graph() -> StateGraph:
    """
    Creates and returns the LangGraph workflow for content repurposing.
    
    Returns:
        StateGraph: Configured workflow graph
    """
    # Initialize the state graph
    workflow = StateGraph(ContentState)
    
    # Add nodes to the graph
    workflow.add_node("extract_content", extract_content)
    workflow.add_node("populate_rag", populate_rag)
    workflow.add_node("extract_insights", extract_insights)
    workflow.add_node("generate_content_suite", generate_content_suite)
    
    # Define the workflow edges (sequential pipeline)
    workflow.add_edge("extract_content", "populate_rag")
    workflow.add_edge("populate_rag", "extract_insights")
    workflow.add_edge("extract_insights", "generate_content_suite")
    
    # Set entry point
    workflow.set_entry_point("extract_content")
    
    # Set finish point (connect last node to END)
    workflow.add_edge("generate_content_suite", END)
    
    return workflow


def run_content_repurposing_pipeline(url: str, user_id: str = None) -> ContentState:
    """
    Executes the complete content repurposing pipeline for a given URL.
    
    Args:
        url (str): The URL to process (YouTube video or webpage)
        user_id (str, optional): User ID for tracking and analytics
        
    Returns:
        ContentState: Final state with all generated content
    """
    import time
    
    # Initialize state
    initial_state = ContentState(
        url=url,
        user_id=user_id,
        extracted_text=None,
        extraction_method=None,
        chunks=None,
        vector_store_id=None,
        key_insights=None,
        blog_post=None,
        twitter_thread=None,
        linkedin_post=None,
        errors=[],
        current_step="starting",
        processing_time=None,
        word_count=None
    )
    
    # Create and compile the graph
    workflow = create_content_repurposing_graph()
    compiled_workflow = workflow.compile()
    
    start_time = time.time()
    
    try:
        # Execute the workflow
        final_state = compiled_workflow.invoke(initial_state)
        
        # Add processing metadata
        final_state["processing_time"] = time.time() - start_time
        final_state["current_step"] = "completed"
        
        return final_state
        
    except Exception as e:
        # Handle any errors that occur during processing
        error_state = initial_state.copy()
        error_state["errors"].append(f"Pipeline execution failed: {str(e)}")
        error_state["current_step"] = "failed"
        error_state["processing_time"] = time.time() - start_time
        
        return error_state
