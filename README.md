# chatbot-templates

A production-ready FastAPI-based chatbot server template with LLM integration and RAG (Retrieval-Augmented Generation) capabilities.

**This repo is part of my Upwork portfolio for GPT research agents with Notion integration, FAQ chatbots, and RAG-powered knowledge assistants.**

---

## 🚀 Quick Demo

### Loom Demo

▶️ **Watch the 4-minute overview:**  
[GPT + Notion Research Agent](INSERT_LINK_HERE)

**What you’ll see:**

- FastAPI backend with RAG support
- Live query demo with context retrieval
- How I wire this into Notion for status updates

**Prerequisites:**

- Python 3.8+
- OpenAI or Anthropic API key (or use mock mode for testing)

**Run the demo:**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment (copy example, add your API key)
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=your_key_here

# 3. Start the server
uvicorn server:app --reload

# 4. In another terminal, test the support bot endpoint
curl -X POST http://localhost:8000/support-bot/query \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo","message":"How do I deploy this chatbot?"}'
```

**Expected Output:**

```json
{
  "user_id": "demo",
  "answer": "Deploy by running docker run -p 8000:8000 --env-file .env ...",
  "sources": ["getting_started.md"],
  "retrieved_context": "Source: getting_started.md...",
  "fallback_used": false
}
```

**What this proves:**

- FastAPI server runs with RAG-powered FAQ bot
- Retrieves relevant context from knowledge base
- Returns structured responses with source citations
- Perfect for GPT research agent jobs where clients need Notion integration + status updates

**Alternative demo (no API key needed):**

```bash
# Run tests to see functionality without API calls
pytest tests/test_server.py -v
```

**Next Steps:**

- See `docs/loom_script.md` for client demo walkthrough
- See `examples/simple_faq_rag/` for ingestion examples
- See `docs/upwork/UPWORK_GPT_NOTION_AGENT.md` for Upwork summary

---

## Overview

This repository provides a complete FastAPI server template for building chatbot applications with:

- **LLM Integration**: Support for OpenAI and Anthropic models
- **RAG System**: Context retrieval and augmented generation
- **Multiple Endpoints**: Simple chat and retrieval-enhanced chat
- **Clean Architecture**: Modular design with separation of concerns
- **Production Ready**: Includes retry logic, error handling, logging, and tests

## Quickstart for Upwork Clients

1. **Clone + install**
   ```bash
   git clone https://github.com/RazonIn4K/chatbot-templates.git
   cd chatbot-templates
   pip install -r requirements.txt
   ```
2. **Configure environment**
   ```bash
   cp .env.example .env
   # drop your OpenAI/Claude keys + optional support bot settings into .env
   ```
3. **Launch the API**
   ```bash
   uvicorn server:app --reload
   ```
4. **Hit the turnkey support bot**
   ```bash
   http POST :8000/support-bot/query user_id=demo message="How do I deploy this?"
   ```
5. **Swap providers instantly** – set `LLM_PROVIDER=anthropic` + `ANTHROPIC_API_KEY=...` in `.env` and restart.

Share this exact block with prospects during screen shares so they can reproduce your demo in minutes.

👉 Need a no-code website embed? See [`docs/website_faq_chatbot.md`](docs/website_faq_chatbot.md) for the "Website FAQ Chatbot" walkthrough and copy/paste widget snippet.
👉 Pitching on Upwork? Grab the pre-written offer outline in [`docs/upwork_offering.md`](docs/upwork_offering.md).
👉 Managing several customers? Follow the playbook in [`docs/multi_tenant_runbook.md`](docs/multi_tenant_runbook.md).

## Architecture at a Glance

```
Markdown docs (docs/, docs/faq) ── ingest.py / examples/simple_faq_rag/ingest_faq.py
                                        │
                                        ▼
                             ChromaDB vector store
                                        │
                                        ▼
retriever.py ──► support_bot.py ──► FastAPI server (server.py) ──► Clients/UI
                ▲                     │
                │                     ▼
                └────────── llm_client.py (OpenAI/Anthropic)
```

See `docs/architecture.md` for a deeper dive into the modules and RAG flow.

## Features

- **Multi-Provider LLM Support**: Works with OpenAI (GPT-3.5, GPT-4) and Anthropic (Claude)
- **Retry Logic**: Automatic retries with exponential backoff for API calls
- **ChromaDB Integration**: Production-ready vector database for semantic search
- **Document Ingestion**: Automated pipeline for indexing documents into the knowledge base
- **Turnkey Support Bot**: `/support-bot/query` endpoint backed by docs/faq with configurable fallback messaging
- **Example RAG Pipeline**: `examples/simple_faq_rag/` scripts showcase ingestion + CLI querying
- **Multi-Tenant Ready**: Route `tenant_id`s to different knowledge bases + prompts from a single deployment
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

## One-Click Deploy (Docker)

Build once, then share the single `docker run` command with clients:

```bash
docker build -t ghcr.io/razonin4k/chatbot-templates:latest .
docker run -it --rm -p 8000:8000 --env-file .env ghcr.io/razonin4k/chatbot-templates:latest
```

If you push the image to GHCR (or any registry), Upwork clients only need the second command to spin up a fully configured demo container.

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

#### Optional: Support Bot Overrides

```bash
SUPPORT_BOT_COLLECTION=support_faq              # Change the collection backing /support-bot/query
SUPPORT_BOT_TOP_K=3                             # Number of FAQ chunks to load into the prompt
SUPPORT_BOT_FALLBACK="Thanks! A specialist will follow up."  # Friendly fallback text
# SUPPORT_BOT_SYSTEM_PROMPT="Custom system prompt text"      # Optional style override
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

#### POST /support-bot/query

FAQ-backed endpoint that looks inside `docs/faq`, retrieves the most relevant snippets, and falls back to a friendly auto-reply when nothing matches.

**Request Body:**

```json
{
  "user_id": "demo-client",
  "tenant_id": "studio",
  "message": "How do I deploy the chatbot?"
}
```

**Response:**

```json
{
  "user_id": "demo-client",
  "answer": "Deploy by running docker run -p 8000:8000 --env-file .env ...",
  "sources": ["getting_started.md"],
  "retrieved_context": "Source: getting_started.md...",
  "fallback_used": false,
  "tenant_id": "studio"
}
```

If no document matches, `answer` becomes the configurable `SUPPORT_BOT_FALLBACK` string and `fallback_used` flips to `true`.

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

## Simple FAQ RAG Example

The `examples/simple_faq_rag/` folder provides a copy‑and‑paste pipeline tailor-made for screen shares:

```bash
# 1. Ingest only docs/faq (creates the support_faq collection by default)
python examples/simple_faq_rag/ingest_faq.py --reset

# 2. Query the same collection from the CLI without hitting the API
python examples/simple_faq_rag/query_faq.py "How are projects billed?"

# 3. Call the live endpoint
http POST :8000/support-bot/query user_id=upwork-demo message="How do I launch locally?"
```

Use this trio to demonstrate ingestion, retrieval, and the API surface area inside a single meeting.

## Website FAQ Chatbot (Embed Example)

Marketing teams often ask how to surface the support bot without code changes. Point them to [`docs/website_faq_chatbot.md`](docs/website_faq_chatbot.md) which covers:

- Deploying the FastAPI container behind HTTPS.
- A self-contained HTML/JS widget calling `POST /support-bot/query`.
- Tips for branding, per-session `user_id` hashing, and analytics review.

## Support Bot Analytics & Review

Every `/support-bot/query` call updates `SUPPORT_ANALYTICS_FILE` (default `analytics/support_metrics.json`) with anonymized totals, fallback count, and intent buckets. Share this snippet so clients can audit usage:

```bash
python - <<'PY'
import json
from analytics import compute_fallback_rate, compute_average_response_time_ms

with open("analytics/support_metrics.json") as f:
    metrics = json.load(f)

print("Total queries:", metrics["total_queries"])
print("Fallbacks:", metrics["fallback_count"])
print("Fallback rate:", f"{compute_fallback_rate(metrics)*100:.1f}%")
print("Avg response time:", f"{compute_average_response_time_ms(metrics):.1f} ms")
print("Intents:")
for intent, count in sorted(metrics["intent_counts"].items(), key=lambda x: x[1], reverse=True):
    print(f" - {intent}: {count}")
PY
```

Reset metrics between demos by deleting the JSON file or pointing `SUPPORT_ANALYTICS_FILE` to another path.
Per-tenant summaries live under `metrics["tenant_breakdown"]` so you can highlight which business unit uses the bot most.

### SLA Snapshot CLI

Need a sales-ready “support quality” dashboard? Run the helper script:

```bash
python scripts/analyze_support_metrics.py --metrics-file analytics/support_metrics.json
```

It prints per-tenant fallback rates and average response times, which you can screenshot for kickoff decks or weekly updates.

## Multi-Tenant FAQ Bots

Host multiple customer-facing bots on one FastAPI process by adding tenant overrides.

1. Define tenant configs in `config/support_tenants.json` (or set `SUPPORT_TENANT_CONFIG_PATH`):
   ```json
   [
     {
       "tenant_id": "studio",
       "collection": "studio_faq",
       "top_k": 4,
       "fallback": "Studio support will follow up soon.",
       "system_prompt": "You are StudioBot..."
     },
     {
       "tenant_id": "retail",
       "collection": "retail_faq",
       "fallback": "Retail team reply coming soon."
     }
   ]
   ```
2. Ingest each tenant's docs into its own Chroma collection (e.g., `studio_faq`, `retail_faq`).
3. Pass `tenant_id` in the request body or widget call:
   ```bash
   http POST :8000/support-bot/query \
     user_id=studio-demo \
     tenant_id=studio \
     message="How do I share mockups?"
   http POST :8000/support-bot/query \
     user_id=retail-demo \
     tenant_id=retail \
     message="When do I change store hours?"
   ```

Each tenant inherits the base `.env` config unless overridden, and analytics log per-tenant breakdowns automatically.

### B2B SaaS Support Preset

- Seeded sample FAQs live in `docs/faq/b2b_saas_*` and the tenant config already contains `tenant_id: b2b_saas` → `collection: b2b_saas_faq`.
- Ingest them before demos:
  ```bash
  python examples/simple_faq_rag/ingest_faq.py --docs-dir docs/faq --collection b2b_saas_faq --reset
  ```
- During demos, call the support bot with `tenant_id=b2b_saas` to showcase SaaS-specific language:
  ```bash
  http POST :8000/support-bot/query tenant_id=b2b_saas user_id=demo message="What is your onboarding timeline?"
  ```
- Replace the sample Markdown files with the prospect's docs and rerun the ingest script to personalize the experience in minutes.

## Internal Knowledge Assistant Example

`examples/internal_knowledge_assistant/` mirrors what enterprise teams ask for: a lightweight ingestion script + CLI and HTTP demos that point at `docs/internal/`. To try it:

```bash
# 1. Ingest the sample handbook
python examples/internal_knowledge_assistant/ingest_internal.py --reset

# 2. Ask questions from the terminal
python examples/internal_knowledge_assistant/cli_query.py "How do we request PTO?"

# 3. Spin up an internal-only HTTP endpoint
uvicorn examples.internal_knowledge_assistant.serve_internal:app --reload
```

Drop your own Markdown files into `docs/internal/` (or pass `--docs-dir`) and rerun the ingest script—no other code changes required.

## Project Structure

```
chatbot-templates/
├── README.md                      # This file
├── .env.example                   # Example environment variables
├── requirements.txt               # Python dependencies
├── server.py                      # FastAPI server with endpoints
├── support_bot.py                 # FAQ-specific RAG service powering /support-bot/query
├── llm_client.py                  # LLM client with multi-provider support
├── retriever.py                   # ChromaDB retriever for semantic search
├── ingest.py                      # Document ingestion script
├── Dockerfile                     # Container image for one-click demos
├── prompts/
│   └── rag_system_prompt.txt     # RAG system prompt template
├── docs/                          # Documentation to be indexed
│   ├── fastapi_overview.txt      # Sample: FastAPI documentation
│   ├── rag_explained.txt         # Sample: RAG concepts
│   ├── chatbot_template_guide.txt # Sample: Template usage guide
│   ├── python_best_practices.txt  # Sample: Python best practices
│   └── faq/                      # Dedicated FAQ snippets for the support bot
│       ├── billing.md
│       └── getting_started.md
│       ├── b2b_saas_onboarding.md
│       └── b2b_saas_success.md
│   ├── internal/                 # Sample internal docs for internal assistant demo
│   │   └── handbook.md
│   ├── multi_tenant_runbook.md   # Runbook for onboarding/updating tenants
│   └── website_faq_chatbot.md    # Widget instructions
├── scripts/
│   └── analyze_support_metrics.py # CLI for SLA-style analytics summaries
│   └── internal/                 # Sample internal docs for internal assistant demo
│       └── handbook.md
├── examples/
│   └── simple_faq_rag/           # Minimal ingestion/query scripts for demos
│       ├── ingest_faq.py
│       └── query_faq.py
│   └── internal_knowledge_assistant/
│       ├── ingest_internal.py    # Chunks docs/internal into 'internal_handbook'
│       ├── cli_query.py          # CLI assistant hitting the internal collection
│       └── serve_internal.py     # Mini FastAPI endpoint for internal enablement
├── tests/
│   ├── __init__.py
│   └── test_server.py            # Unit tests for API endpoints
├── chroma_db/                     # ChromaDB data (created after ingestion)
└── .gitignore                    # Git ignore rules

## Security & Privacy

- **PII minimization**: Only send the necessary text to `/support-bot/query` and prefer hashed `user_id` values for analytics. Strip emails/phone numbers in the widget before forwarding.
- **Secrets management**: Keep API keys in `.env` locally but move them to platform-specific secret stores (Render/Heroku/Fly) in production. Never bake them into Docker images or client-side JS.
- **TLS + network boundaries**: Terminate HTTPS in front of the FastAPI container and restrict ingress to trusted origins. Enable CORS rules that list approved domains only.
- **Logging hygiene**: The analytics logger stores aggregates only—no raw questions or IDs—to stay GDPR/CCPA friendly. If deeper debugging is needed, log to a secure sink (e.g., Datadog) with encryption at rest and retention limits.
- **Access control**: Protect admin endpoints or ingestion jobs with auth headers or a VPN. Rotate LLM API keys regularly and monitor usage via provider dashboards.
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
