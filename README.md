# chatbot-templates

A production-ready FastAPI-based chatbot server template with LLM integration and RAG (Retrieval-Augmented Generation) capabilities.

## Overview

This repository provides a complete FastAPI server template for building chatbot applications with:
- **LLM Integration**: Support for OpenAI and Anthropic models
- **RAG System**: Context retrieval and augmented generation
- **Multiple Endpoints**: Simple chat and retrieval-enhanced chat
- **Clean Architecture**: Modular design with separation of concerns
- **Production Ready**: Includes retry logic, error handling, logging, and tests

## Features

- **Multi-Provider LLM Support**: Works with OpenAI (GPT-3.5, GPT-4) and Anthropic (Claude)
- **Retry Logic**: Automatic retries with exponential backoff for API calls
- **ChromaDB Integration**: Production-ready vector database for semantic search
- **Document Ingestion**: Automated pipeline for indexing documents into the knowledge base
- **Comprehensive Testing**: Unit tests with mocked LLM clients and retrieval
- **Interactive API Docs**: Automatic OpenAPI documentation at `/docs`
- **Health Checks**: Monitor system status and LLM connectivity

## Installation

1. Clone the repository:
```bash
git clone https://github.com/RazonIn4K/chatbot-templates.git
cd chatbot-templates
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. Ingest documents into the vector database:
```bash
python ingest.py
```

6. Start the server:
```bash
python server.py
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

#### Required: LLM Configuration

```bash
# Choose your provider: 'openai' or 'anthropic'
LLM_PROVIDER=openai

# API Key (set the one for your chosen provider)
OPENAI_API_KEY=your-openai-api-key-here
# ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Model selection
LLM_MODEL=gpt-3.5-turbo  # or gpt-4, claude-3-haiku-20240307, etc.
```

#### Optional: Generation Parameters

```bash
LLM_TEMPERATURE=0.7      # Response creativity (0.0-1.0)
LLM_MAX_TOKENS=500       # Maximum response length
```

#### Optional: ChromaDB Configuration

```bash
CHROMA_PERSIST_DIR=./chroma_db        # Directory for ChromaDB data (default: ./chroma_db)
CHROMA_COLLECTION_NAME=chatbot_docs   # Collection name (default: chatbot_docs)
CHUNK_SIZE=500                        # Size of document chunks (default: 500)
CHUNK_OVERLAP=50                      # Overlap between chunks (default: 50)
```

### Supported Models

**OpenAI:**
- `gpt-3.5-turbo` (default, fast and cost-effective)
- `gpt-4` (more capable, slower)
- `gpt-4-turbo-preview` (latest GPT-4)

**Anthropic:**
- `claude-3-haiku-20240307` (default, fastest)
- `claude-3-sonnet-20240229` (balanced)
- `claude-3-opus-20240229` (most capable)

## Usage

### Starting the Server

Run the FastAPI server:
```bash
python server.py
```

Or use uvicorn directly:
```bash
uvicorn server:app --reload
```

The server will start on `http://localhost:8000`

### API Endpoints

#### GET /

Root endpoint with API information.

#### GET /health

Health check endpoint that verifies LLM connectivity.

**Response:**
```json
{
  "status": "healthy",
  "llm_provider": "openai",
  "llm_model": "gpt-3.5-turbo"
}
```

#### POST /chat

Send a chat message with optional context and get an LLM-generated response.

**Request Body:**
```json
{
  "message": "What is FastAPI?",
  "context": "FastAPI is a modern, fast web framework for building APIs with Python."
}
```

**Response:**
```json
{
  "response": "FastAPI is a modern, fast (high-performance) web framework...",
  "system_prompt": "You are a helpful AI assistant...",
  "context_used": true
}
```

#### POST /chat-with-retrieval

Chat endpoint with automatic context retrieval from vector database (currently uses stub).

**Request Body:**
```json
{
  "message": "What is RAG?"
}
```

**Response:**
```json
{
  "response": "RAG stands for Retrieval-Augmented Generation...",
  "system_prompt": "You are a helpful AI assistant...",
  "context_used": true
}
```

### Testing the API

#### Using curl:

```bash
# Health check
curl http://localhost:8000/health

# Simple chat
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain what a REST API is"}'

# Chat with context
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the benefits?",
    "context": "REST APIs use HTTP methods and are stateless."
  }'

# Chat with retrieval
curl -X POST "http://localhost:8000/chat-with-retrieval" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is semantic search?"}'
```

#### Using Python:

```python
import requests

# Simple chat
response = requests.post(
    "http://localhost:8000/chat",
    json={"message": "What is machine learning?"}
)
print(response.json()["response"])

# Chat with context
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "What are neural networks?",
        "context": "Machine learning is a subset of AI that learns from data."
    }
)
print(response.json())

# Chat with retrieval
response = requests.post(
    "http://localhost:8000/chat-with-retrieval",
    json={"message": "Explain vector databases"}
)
print(response.json()["response"])
```

### Interactive Documentation

Visit `http://localhost:8000/docs` for interactive API documentation powered by Swagger UI.

## Document Ingestion

The template includes a powerful document ingestion pipeline that indexes your documents into ChromaDB for semantic search.

### Quick Start

1. **Add your documents** to the `docs/` folder:
   ```bash
   # Supported formats: .txt, .md, .markdown
   cp your-documents.txt docs/
   ```

2. **Run the ingestion script**:
   ```bash
   python ingest.py
   ```

3. **Verify ingestion**:
   ```bash
   python ingest.py --stats
   ```

### Ingestion Options

The `ingest.py` script supports various options:

```bash
# Basic ingestion
python ingest.py

# Custom docs directory
python ingest.py --docs-dir /path/to/docs

# Custom chunk size and overlap
python ingest.py --chunk-size 1000 --chunk-overlap 100

# Reset collection before ingesting (deletes existing data)
python ingest.py --reset

# Show collection statistics after ingestion
python ingest.py --stats

# Use a different collection name
python ingest.py --collection my_docs

# Combine options
python ingest.py --docs-dir ./my-docs --chunk-size 800 --reset --stats
```

### How It Works

1. **Document Loading**: Reads all `.txt` and `.md` files from the docs folder
2. **Chunking**: Splits documents into overlapping chunks (default: 500 chars with 50 char overlap)
3. **Embedding**: Automatically generates embeddings using ChromaDB's default model
4. **Indexing**: Stores chunks with metadata in ChromaDB for fast semantic search
5. **Persistence**: Data persists to disk in `./chroma_db/` by default

### Chunking Strategy

The ingestion script uses intelligent chunking:
- **Paragraph breaks** are preferred (splits on `\n\n`)
- **Sentence breaks** are used if no paragraph breaks (splits on `. `, `! `, `? `)
- **Hard limit** at chunk_size characters
- **Overlap** maintains context between chunks

### Example Workflow

```bash
# 1. Prepare documents
mkdir -p docs
echo "Your documentation here" > docs/my_guide.txt

# 2. Run ingestion
python ingest.py --reset --stats

# 3. Test retrieval
python server.py &
curl -X POST "http://localhost:8000/chat-with-retrieval" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about the documentation"}'
```

### Metadata

Each chunk is stored with metadata:
- `source`: Original file path
- `filename`: Name of the source file
- `chunk_index`: Position in the document
- `total_chunks`: Total chunks from this document

This metadata enables source attribution and quality monitoring.

## Project Structure

```
chatbot-templates/
├── README.md                      # This file
├── .env.example                   # Example environment variables
├── requirements.txt               # Python dependencies
├── server.py                      # FastAPI server with endpoints
├── llm_client.py                  # LLM client with multi-provider support
├── retriever.py                   # ChromaDB retriever for semantic search
├── ingest.py                      # Document ingestion script
├── prompts/
│   └── rag_system_prompt.txt     # RAG system prompt template
├── docs/                          # Documentation to be indexed
│   ├── fastapi_overview.txt      # Sample: FastAPI documentation
│   ├── rag_explained.txt         # Sample: RAG concepts
│   ├── chatbot_template_guide.txt # Sample: Template usage guide
│   └── python_best_practices.txt  # Sample: Python best practices
├── tests/
│   ├── __init__.py
│   └── test_server.py            # Unit tests for API endpoints
├── chroma_db/                     # ChromaDB data (created after ingestion)
└── .gitignore                    # Git ignore rules
```

## Development

### Running Tests

The project includes comprehensive tests using pytest:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_server.py

# Run specific test class
pytest tests/test_server.py::TestChatEndpoint

# Run with coverage
pytest --cov=. --cov-report=html
```

### Adding New Endpoints

To add new endpoints, edit `server.py` and define new routes:

```python
@app.post("/your-endpoint")
async def your_function(request: YourRequestModel):
    # Your logic here
    return {"result": "your response"}
```

### Customizing the System Prompt

Edit `prompts/rag_system_prompt.txt` to customize the chatbot's behavior and response style.

### Working with ChromaDB

The template uses **ChromaDB** as the vector database, which is already integrated and ready to use:

#### Key Features:
- **Persistent storage**: Data is saved to disk in `./chroma_db/`
- **Automatic embeddings**: Uses ChromaDB's default embedding model
- **Cosine similarity**: Optimized for semantic search
- **Local-first**: No external services required
- **Scalable**: Works for development and production

#### Managing Collections:

```python
from retriever import get_collection_stats, reset_collection

# Get collection statistics
stats = get_collection_stats()
print(f"Documents: {stats['count']}")

# Reset collection (deletes all data)
reset_collection()
```

#### Customizing Retrieval:

Edit `server.py` to adjust retrieval parameters:

```python
# In chat_with_retrieval endpoint
retrieved_context = retrieve_relevant_context(
    query=request.message,
    top_k=5,           # Retrieve more documents
    min_score=0.7      # Filter by similarity threshold
)
```

#### Alternative Vector Databases:

While ChromaDB is integrated, you can switch to other databases:
- **Pinecone**: Managed cloud service, great for production
- **Weaviate**: GraphQL-based, powerful filtering
- **Qdrant**: High-performance, Rust-based

See the original `retriever.py` stub (git history) for integration guides.

## Architecture

### LLM Client (`llm_client.py`)

- **Multi-provider support**: OpenAI and Anthropic
- **Singleton pattern**: Efficient resource usage
- **Retry logic**: Exponential backoff with tenacity
- **Error handling**: Custom exceptions and logging
- **Environment-based config**: Easy deployment

### Server (`server.py`)

- **FastAPI framework**: Modern async Python web framework
- **Type validation**: Pydantic models for requests/responses
- **Error handling**: Comprehensive HTTP error responses
- **Logging**: Structured logging for debugging
- **Health checks**: Monitor system status

### Retriever (`retriever.py`)

- **ChromaDB integration**: Production-ready vector database
- **Semantic search**: Cosine similarity with automatic embeddings
- **Flexible interface**: Returns text or structured documents
- **Collection management**: Statistics, reset, and configuration options
- **Persistence**: Local storage with configurable directory

## Next Steps

Here are suggested enhancements to build on this template:

1. **Integrate a Vector Database**
   - Choose Pinecone, Chroma, Weaviate, or Qdrant
   - Replace stub in `retriever.py`
   - Prepare and upload your knowledge base

2. **Add Streaming Responses**
   - Implement Server-Sent Events (SSE)
   - Stream tokens as they're generated
   - Improve perceived performance

3. **Implement Conversation History**
   - Add session management
   - Store conversation context
   - Enable multi-turn dialogues

4. **Add Authentication**
   - Implement API key authentication
   - Add rate limiting
   - Track usage per user

5. **Enhance Error Handling**
   - Add circuit breakers
   - Implement fallback responses
   - Better retry strategies

6. **Add Observability**
   - Integrate with monitoring tools (Prometheus, Datadog)
   - Add structured logging (JSON logs)
   - Track latency and error rates

7. **Document Management**
   - Add endpoints for uploading documents
   - Implement chunking and embedding pipeline
   - Support multiple document formats

8. **Advanced RAG Features**
   - Implement re-ranking
   - Add hybrid search (keyword + semantic)
   - Support metadata filtering

## License

This project is open source and available for use and modification.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## Troubleshooting

### "OPENAI_API_KEY environment variable not set"

Make sure you've created a `.env` file with your API key:
```bash
cp .env.example .env
# Edit .env with your actual API key
```

### "Module not found" errors

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Tests failing

Make sure you're running tests from the project root:
```bash
cd chatbot-templates
pytest
```

### Health check returns "unhealthy"

- Verify your API key is correct
- Check your internet connection
- Ensure you have API credits/quota remaining
- Verify the LLM_PROVIDER matches your API key type

## Support

For issues and questions:
- Open an issue on GitHub
- Check the `/docs` endpoint for API documentation
- Review the inline code documentation

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [OpenAI](https://openai.com/) - GPT models
- [Anthropic](https://anthropic.com/) - Claude models
- [Tenacity](https://tenacity.readthedocs.io/) - Retry logic
