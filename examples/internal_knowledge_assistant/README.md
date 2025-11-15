# Internal Knowledge Assistant Example

This example reuses the core ingestion + retrieval utilities to build an employee handbook assistant.

## Quickstart
1. **Ingest internal docs**
   ```bash
   python examples/internal_knowledge_assistant/ingest_internal.py --reset
   ```
   Drop your own Markdown files into `docs/internal/` or pass `--docs-dir` to point at an existing Confluence export.

2. **Query from the CLI**
   ```bash
   python examples/internal_knowledge_assistant/cli_query.py "Where is the PTO policy?"
   ```

3. **Launch the internal HTTP endpoint**
   ```bash
   uvicorn examples.internal_knowledge_assistant.serve_internal:app --reload
   # POST http://127.0.0.1:8000/internal-assistant/query {"question": "How do we deploy?"}
   ```

## Swapping in Your Docs
- Replace the sample Markdown files under `docs/internal/` with your content or call the scripts with `--docs-dir /path/to/docs`.
- Update environment overrides (`INTERNAL_COLLECTION_NAME`, `INTERNAL_SYSTEM_PROMPT`) to match each knowledge base.
- Because the example reuses the shared `llm_client` + `retriever`, no code changes are needed beyond rerunning the ingest script.
