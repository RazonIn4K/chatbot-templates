# Architecture

This template is intentionally compact so you can showcase projects quickly while still following a clear separation of concerns.

## High-Level Flow

```
Markdown Docs (docs/, docs/faq)
        │
        │  ingest.py / examples/simple_faq_rag/ingest_faq.py (chunk + embed)
        ▼
 ChromaDB Vector Store ── retriever.py ──► support_bot.py / server.py
        ▲                                 │
        │                                 │
        └────────────── llm_client.py ◄───┘
```

1. **Ingestion layer (`ingest.py`, `examples/simple_faq_rag/ingest_faq.py`)**
   - Loads Markdown/TXT files, chunks them, and writes to ChromaDB collections.
   - Uses environment variables (`CHROMA_*`, `CHUNK_*`) for repeatable runs.

2. **Retrieval layer (`retriever.py`)**
   - Singleton client wrapper around ChromaDB with helpers for raw context strings (`retrieve_relevant_context`) and structured docs (`retrieve_relevant_documents`).
   - Provides utilities to reset and inspect collections when demoing.

3. **LLM layer (`llm_client.py`)**
   - Abstracts OpenAI/Anthropic with retry logic, configurable model/temperature/max tokens, and lazy initialization.

4. **API layer (`server.py`)**
   - Exposes `/chat`, `/chat-with-retrieval`, `/support-bot/query`, and `/health`.
   - Handles validation, error mapping, and logging while delegating heavy lifting to service modules.

5. **Support service (`support_bot.py`)**
   - Formats FAQ documents into attribution-friendly context blocks and prepares user prompts.
   - Falls back to the configurable message when no FAQ match is found.
   - Emits anonymized usage stats via `analytics.py` so you can track volume and fallback rate without storing PII.

## Typical Demo Flow

1. Drop Markdown FAQs into `docs/faq`.
2. Run `python examples/simple_faq_rag/ingest_faq.py --reset` to create or refresh the `support_faq` collection.
3. Launch the API (`uvicorn server:app --reload`).
4. Use `http --json POST :8000/support-bot/query user_id=demo message="How do I deploy?"` during a screen share.  The endpoint performs:
   - Retrieval via `retrieve_relevant_documents` (top_k configurable).
   - LLM generation via `llm_client` when context exists.
   - Graceful fallback when knowledge is missing.

## Extending

- Swap vector DBs by replacing `retriever.py` while keeping the service + API layers intact.
- Add more bots by following the `support_bot.py` pattern (service module + endpoint + example ingestion script).
- Attach background ingestion workers by invoking `ingest_documents` from Celery/RQ.

With this structure you can walk clients through a demo that covers ingestion, retrieval, LLM orchestration, and deployment in minutes.
