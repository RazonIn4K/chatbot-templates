"""
Retriever module for chatbot-templates using ChromaDB.
Provides context retrieval functionality for RAG (Retrieval-Augmented Generation).
"""

import os
import logging
from typing import List, Dict, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global ChromaDB client and collection
_chroma_client = None
_collection = None


def get_chroma_client():
    """
    Get or create the ChromaDB client.

    Returns:
        ChromaDB client instance
    """
    global _chroma_client

    if _chroma_client is None:
        try:
            import chromadb
            from chromadb.config import Settings

            # Get persist directory from environment or use default
            persist_dir = os.getenv('CHROMA_PERSIST_DIR', './chroma_db')

            # Create client with persistence
            _chroma_client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info(f"ChromaDB client initialized with persist_dir: {persist_dir}")

        except ImportError:
            logger.error("ChromaDB not installed. Install with: pip install chromadb")
            raise ImportError(
                "ChromaDB not installed. Install with: pip install chromadb"
            )

    return _chroma_client


def get_collection(collection_name: Optional[str] = None):
    """
    Get or create a ChromaDB collection.

    Args:
        collection_name: Name of the collection (default from env or 'chatbot_docs')

    Returns:
        ChromaDB collection instance
    """
    global _collection

    if collection_name is None:
        collection_name = os.getenv('CHROMA_COLLECTION_NAME', 'chatbot_docs')

    # Return existing collection if same name
    if _collection is not None and _collection.name == collection_name:
        return _collection

    try:
        client = get_chroma_client()

        # Get or create collection with default embedding function
        _collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        count = _collection.count()
        logger.info(f"Collection '{collection_name}' loaded with {count} documents")

        return _collection

    except Exception as e:
        logger.error(f"Error getting collection: {str(e)}")
        raise


def retrieve_relevant_context(
    query: str,
    top_k: int = 3,
    min_score: float = 0.0,
    collection_name: Optional[str] = None
) -> str:
    """
    Retrieve relevant context for a given query using ChromaDB.

    Args:
        query: The user's query to find relevant context for
        top_k: Number of documents to retrieve (default: 3)
        min_score: Minimum similarity score to include (default: 0.0)
        collection_name: Optional collection name to use

    Returns:
        Concatenated relevant context as a string

    Example:
        >>> context = retrieve_relevant_context("What is FastAPI?", top_k=3)
        >>> print(context)
        FastAPI is a modern, fast web framework for building APIs...
    """
    try:
        collection = get_collection(collection_name)

        # Check if collection is empty
        if collection.count() == 0:
            logger.warning("Collection is empty. Run ingest.py to add documents.")
            return (
                "[No documents in database] Please run the ingestion script to add "
                "documents to the knowledge base."
            )

        logger.info(f"Retrieving context for query: '{query[:50]}...' (top_k={top_k})")

        # Query the collection
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )

        # Extract documents and distances
        documents = results['documents'][0] if results['documents'] else []
        distances = results['distances'][0] if results['distances'] else []
        metadatas = results['metadatas'][0] if results['metadatas'] else []

        if not documents:
            logger.warning("No documents found for query")
            return "[No relevant documents found]"

        # Filter by minimum score (convert distance to similarity)
        # ChromaDB uses cosine distance, so similarity = 1 - distance
        filtered_docs = []
        for doc, dist, metadata in zip(documents, distances, metadatas):
            similarity = 1 - dist
            if similarity >= min_score:
                logger.info(f"Retrieved doc (similarity={similarity:.3f}): {metadata.get('source', 'unknown')}")
                filtered_docs.append(doc)

        if not filtered_docs:
            logger.warning(f"No documents met minimum score threshold: {min_score}")
            return "[No documents met the similarity threshold]"

        # Concatenate documents with separators
        context = "\n\n---\n\n".join(filtered_docs)

        logger.info(f"Retrieved {len(filtered_docs)} documents")
        return context

    except Exception as e:
        logger.error(f"Error retrieving context: {str(e)}")
        # Return error message instead of raising to prevent server crashes
        return f"[Error retrieving context: {str(e)}]"


def retrieve_relevant_documents(
    query: str,
    top_k: int = 3,
    min_score: float = 0.0,
    collection_name: Optional[str] = None
) -> List[Dict[str, any]]:
    """
    Retrieve relevant documents with metadata.

    This returns structured document data rather than concatenated text.
    Useful when you need access to metadata, scores, or individual documents.

    Args:
        query: The user's query
        top_k: Number of documents to retrieve
        min_score: Minimum similarity score threshold
        collection_name: Optional collection name to use

    Returns:
        List of documents with metadata and scores

    Example:
        >>> docs = retrieve_relevant_documents("What is RAG?")
        >>> for doc in docs:
        ...     print(f"{doc['source']}: {doc['score']:.2f}")
        ...     print(doc['content'][:100])
    """
    try:
        collection = get_collection(collection_name)

        if collection.count() == 0:
            logger.warning("Collection is empty")
            return []

        logger.info(f"Retrieving documents for query: '{query[:50]}...'")

        # Query the collection
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )

        # Extract and structure results
        documents = results['documents'][0] if results['documents'] else []
        distances = results['distances'][0] if results['distances'] else []
        metadatas = results['metadatas'][0] if results['metadatas'] else []
        ids = results['ids'][0] if results['ids'] else []

        # Build structured response
        structured_docs = []
        for doc_id, doc, dist, metadata in zip(ids, documents, distances, metadatas):
            similarity = 1 - dist
            if similarity >= min_score:
                structured_docs.append({
                    "id": doc_id,
                    "content": doc,
                    "score": similarity,
                    "metadata": metadata or {}
                })

        logger.info(f"Retrieved {len(structured_docs)} documents")
        return structured_docs

    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        return []


def reset_collection(collection_name: Optional[str] = None):
    """
    Reset (delete and recreate) a collection.

    Args:
        collection_name: Name of the collection to reset

    Warning:
        This will delete all documents in the collection!
    """
    global _collection

    if collection_name is None:
        collection_name = os.getenv('CHROMA_COLLECTION_NAME', 'chatbot_docs')

    try:
        client = get_chroma_client()

        # Delete existing collection
        try:
            client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
        except Exception:
            logger.info(f"Collection {collection_name} does not exist, creating new")

        # Create new collection
        _collection = client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        logger.info(f"Created new collection: {collection_name}")
        return _collection

    except Exception as e:
        logger.error(f"Error resetting collection: {str(e)}")
        raise


def get_collection_stats(collection_name: Optional[str] = None) -> Dict[str, any]:
    """
    Get statistics about a collection.

    Args:
        collection_name: Name of the collection

    Returns:
        Dictionary with collection statistics
    """
    try:
        collection = get_collection(collection_name)

        stats = {
            "name": collection.name,
            "count": collection.count(),
            "metadata": collection.metadata
        }

        # Get a peek at the collection
        if stats["count"] > 0:
            peek = collection.peek(limit=1)
            if peek and peek.get('metadatas') and peek['metadatas'][0]:
                stats["sample_metadata"] = peek['metadatas'][0]

        return stats

    except Exception as e:
        logger.error(f"Error getting collection stats: {str(e)}")
        return {"error": str(e)}
