#!/usr/bin/env python3
"""
Document ingestion script for chatbot-templates.
Indexes documents from the docs/ folder into ChromaDB for RAG retrieval.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Tuple
import argparse

from retriever import get_collection, reset_collection, get_collection_stats

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_documents_from_directory(directory: str = "docs") -> List[Tuple[str, str]]:
    """
    Load all text documents from a directory.

    Args:
        directory: Path to the directory containing documents

    Returns:
        List of tuples (file_path, content)
    """
    docs_path = Path(directory)

    if not docs_path.exists():
        logger.error(f"Directory not found: {directory}")
        return []

    documents = []
    supported_extensions = {'.txt', '.md', '.markdown'}

    for file_path in docs_path.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                if content.strip():  # Only add non-empty documents
                    documents.append((str(file_path), content))
                    logger.info(f"Loaded: {file_path.name} ({len(content)} chars)")
                else:
                    logger.warning(f"Skipped empty file: {file_path}")

            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")

    logger.info(f"Loaded {len(documents)} documents from {directory}")
    return documents


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Text to chunk
        chunk_size: Maximum size of each chunk in characters
        chunk_overlap: Number of characters to overlap between chunks

    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to break at a sentence or paragraph boundary
        if end < len(text):
            # Look for paragraph break
            paragraph_break = text.rfind('\n\n', start, end)
            if paragraph_break != -1 and paragraph_break > start:
                end = paragraph_break
            else:
                # Look for sentence break
                sentence_break = max(
                    text.rfind('. ', start, end),
                    text.rfind('! ', start, end),
                    text.rfind('? ', start, end)
                )
                if sentence_break != -1 and sentence_break > start:
                    end = sentence_break + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move to next chunk with overlap
        start = end - chunk_overlap if end < len(text) else end

    return chunks


def ingest_documents(
    documents: List[Tuple[str, str]],
    collection_name: str = None,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    reset: bool = False
) -> Dict[str, int]:
    """
    Ingest documents into ChromaDB.

    Args:
        documents: List of (file_path, content) tuples
        collection_name: Name of the collection to use
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        reset: Whether to reset the collection before ingesting

    Returns:
        Dictionary with ingestion statistics
    """
    if not documents:
        logger.warning("No documents to ingest")
        return {"total_documents": 0, "total_chunks": 0}

    # Get chunk size from environment if available
    chunk_size = int(os.getenv('CHUNK_SIZE', chunk_size))
    chunk_overlap = int(os.getenv('CHUNK_OVERLAP', chunk_overlap))

    logger.info(f"Chunk settings: size={chunk_size}, overlap={chunk_overlap}")

    # Reset collection if requested
    if reset:
        logger.info("Resetting collection...")
        reset_collection(collection_name)

    # Get collection
    collection = get_collection(collection_name)

    # Prepare data for ingestion
    all_ids = []
    all_documents = []
    all_metadatas = []

    for file_path, content in documents:
        # Chunk the document
        chunks = chunk_text(content, chunk_size, chunk_overlap)

        logger.info(f"Processing {Path(file_path).name}: {len(chunks)} chunks")

        for i, chunk in enumerate(chunks):
            # Create unique ID
            chunk_id = f"{Path(file_path).stem}_chunk_{i}"

            # Create metadata
            metadata = {
                "source": file_path,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "filename": Path(file_path).name
            }

            all_ids.append(chunk_id)
            all_documents.append(chunk)
            all_metadatas.append(metadata)

    # Ingest in batches for efficiency
    batch_size = 100
    total_chunks = len(all_documents)

    logger.info(f"Ingesting {total_chunks} chunks in batches of {batch_size}...")

    for i in range(0, total_chunks, batch_size):
        batch_end = min(i + batch_size, total_chunks)

        try:
            collection.add(
                ids=all_ids[i:batch_end],
                documents=all_documents[i:batch_end],
                metadatas=all_metadatas[i:batch_end]
            )
            logger.info(f"Ingested batch {i//batch_size + 1}: {batch_end}/{total_chunks} chunks")

        except Exception as e:
            logger.error(f"Error ingesting batch {i//batch_size + 1}: {e}")
            raise

    logger.info(f"✓ Successfully ingested {len(documents)} documents ({total_chunks} chunks)")

    return {
        "total_documents": len(documents),
        "total_chunks": total_chunks
    }


def main():
    """Main function to run the ingestion script."""
    parser = argparse.ArgumentParser(
        description="Ingest documents into ChromaDB for RAG retrieval"
    )
    parser.add_argument(
        '--docs-dir',
        type=str,
        default='docs',
        help='Directory containing documents to ingest (default: docs)'
    )
    parser.add_argument(
        '--collection',
        type=str,
        default=None,
        help='ChromaDB collection name (default: from env or chatbot_docs)'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=500,
        help='Size of text chunks in characters (default: 500)'
    )
    parser.add_argument(
        '--chunk-overlap',
        type=int,
        default=50,
        help='Overlap between chunks in characters (default: 50)'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset collection before ingesting (deletes existing data)'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show collection statistics after ingestion'
    )

    args = parser.parse_args()

    try:
        logger.info("=" * 60)
        logger.info("Document Ingestion Script")
        logger.info("=" * 60)

        # Load documents
        logger.info(f"Loading documents from: {args.docs_dir}")
        documents = load_documents_from_directory(args.docs_dir)

        if not documents:
            logger.error("No documents found to ingest!")
            sys.exit(1)

        # Ingest documents
        stats = ingest_documents(
            documents=documents,
            collection_name=args.collection,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            reset=args.reset
        )

        # Print statistics
        logger.info("=" * 60)
        logger.info("Ingestion Summary")
        logger.info("=" * 60)
        logger.info(f"Documents processed: {stats['total_documents']}")
        logger.info(f"Total chunks created: {stats['total_chunks']}")

        if args.stats:
            logger.info("=" * 60)
            logger.info("Collection Statistics")
            logger.info("=" * 60)
            collection_stats = get_collection_stats(args.collection)
            for key, value in collection_stats.items():
                logger.info(f"{key}: {value}")

        logger.info("=" * 60)
        logger.info("✓ Ingestion complete!")
        logger.info("=" * 60)

    except KeyboardInterrupt:
        logger.info("\n\nIngestion interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
