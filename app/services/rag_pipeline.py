"""
RAG Pipeline Service using ChromaDB

Handles text chunking, embedding generation, and vector storage for content retrieval.
"""

import chromadb
from chromadb.config import Settings
import uuid
from typing import List, Dict, Any, Optional
import re
import os


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline using ChromaDB for vector storage.
    Uses ChromaDB's default embedding model to avoid heavy ML dependencies.
    """
    
    def __init__(self, persist_directory: str = "./data/chromadb"):
        """
        Initialize the RAG pipeline with ChromaDB.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory
        
        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks for better retrieval.
        
        Args:
            text: Input text to chunk
            chunk_size: Target size for each chunk
            overlap: Overlap between consecutive chunks
            
        Returns:
            List of text chunks
        """
        if not text or len(text) < chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Find the end of the chunk
            end = start + chunk_size
            
            # If we're not at the end of the text, try to break at a sentence or word boundary
            if end < len(text):
                # Look for sentence endings
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
                else:
                    # Look for word boundaries
                    word_end = text.rfind(' ', start, end)
                    if word_end > start + chunk_size // 2:
                        end = word_end
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - overlap
            if start >= len(text):
                break
                
        return chunks
    
    def create_collection(self, content_text: str, url: str) -> str:
        """
        Create a new ChromaDB collection for the content.
        
        Args:
            content_text: The full content text to process
            url: Source URL for metadata
            
        Returns:
            Collection ID for future retrieval
        """
        # Generate unique collection ID
        collection_id = f"content_{uuid.uuid4().hex[:8]}"
        
        # Clean and prepare the text
        cleaned_text = self._clean_text(content_text)
        
        # Chunk the text
        chunks = self.chunk_text(cleaned_text)
        
        if not chunks:
            raise ValueError("No content chunks generated from input text")
        
        # Create collection
        collection = self.client.create_collection(
            name=collection_id,
            metadata={"source_url": url, "total_chunks": len(chunks)}
        )
        
        # Prepare documents and metadata
        documents = chunks
        metadatas = [
            {
                "chunk_index": i,
                "source_url": url,
                "chunk_length": len(chunk)
            }
            for i, chunk in enumerate(chunks)
        ]
        ids = [f"{collection_id}_chunk_{i}" for i in range(len(chunks))]
        
        # Add documents to collection (ChromaDB will generate embeddings automatically)
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        return collection_id
    
    def query_content(self, collection_id: str, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query the RAG knowledge base for relevant content.
        
        Args:
            collection_id: ID of the collection to query
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant content chunks with metadata
        """
        try:
            collection = self.client.get_collection(collection_id)
        except Exception:
            raise ValueError(f"Collection {collection_id} not found")
        
        # Query the collection
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, document in enumerate(results['documents'][0]):
                result = {
                    "content": document,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else None
                }
                formatted_results.append(result)
        
        return formatted_results
    
    def get_content_summary(self, collection_id: str) -> Dict[str, Any]:
        """
        Get summary information about a collection.
        
        Args:
            collection_id: ID of the collection
            
        Returns:
            Summary information
        """
        try:
            collection = self.client.get_collection(collection_id)
            collection_info = collection.get()
            
            return {
                "collection_id": collection_id,
                "total_chunks": len(collection_info['documents']) if collection_info['documents'] else 0,
                "metadata": collection.metadata
            }
        except Exception:
            return {"error": f"Collection {collection_id} not found"}
    
    def cleanup_collection(self, collection_id: str) -> bool:
        """
        Delete a collection to free up space.
        
        Args:
            collection_id: ID of the collection to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_collection(collection_id)
            return True
        except Exception:
            return False
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text for better processing.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere with chunking
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/\@\#\$\%\^\&\*\+\=\<\>\~\`]', ' ', text)
        
        # Clean up multiple spaces again
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()


# Global instance for use across the application
rag_pipeline = RAGPipeline()
