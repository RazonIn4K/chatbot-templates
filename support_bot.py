"""Support bot service layer coordinating the simple FAQ RAG flow."""

from __future__ import annotations

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from llm_client import get_llm_client
from retriever import retrieve_relevant_documents
from analytics import record_support_interaction


BASE_SUPPORT_CONFIG = {
    'collection': os.getenv('SUPPORT_BOT_COLLECTION', 'support_faq'),
    'top_k': int(os.getenv('SUPPORT_BOT_TOP_K', '3')),
    'fallback': os.getenv(
        'SUPPORT_BOT_FALLBACK',
        "Thanks for your question! A support specialist will follow up shortly."
    ),
    'system_prompt': os.getenv(
        'SUPPORT_BOT_SYSTEM_PROMPT',
        (
            "You are SupportBot, a concise customer support assistant. Use the provided "
            "FAQ context to craft answers grounded in the docs. Quote filenames when "
            "useful and keep responses under 200 words. If the context is empty, fall "
            "back to the provided fallback message."
        )
    ),
}

TENANT_CONFIG_PATH = Path(os.getenv('SUPPORT_TENANT_CONFIG_PATH', 'config/support_tenants.json'))


def _load_tenant_overrides() -> Dict[str, Dict[str, object]]:
    if not TENANT_CONFIG_PATH.exists():
        return {}

    try:
        data = json.loads(TENANT_CONFIG_PATH.read_text())
        overrides: Dict[str, Dict[str, object]] = {}
        if isinstance(data, list):
            for entry in data:
                tenant_id = entry.get('tenant_id')
                if tenant_id:
                    overrides[tenant_id] = entry
        elif isinstance(data, dict):
            # Allow dict keyed by tenant_id as alternative format
            for tenant_id, entry in data.items():
                entry['tenant_id'] = tenant_id
                overrides[tenant_id] = entry
        return overrides
    except Exception:
        return {}


TENANT_OVERRIDES = _load_tenant_overrides()


def _resolve_config(tenant_id: Optional[str]) -> Dict[str, object]:
    """Merge base config with any tenant-specific overrides."""

    config = BASE_SUPPORT_CONFIG.copy()
    if tenant_id:
        tenant_cfg = TENANT_OVERRIDES.get(tenant_id)
        if tenant_cfg:
            config['collection'] = tenant_cfg.get('collection', config['collection'])
            config['top_k'] = int(tenant_cfg.get('top_k', config['top_k']))
            config['fallback'] = tenant_cfg.get('fallback', config['fallback'])
            config['system_prompt'] = tenant_cfg.get('system_prompt', config['system_prompt'])
    config['tenant_id'] = tenant_id or 'default'
    return config


def _format_context(docs: List[Dict[str, object]]) -> Tuple[str, List[str]]:
    """Build a readable context block plus list of source names."""

    context_blocks: List[str] = []
    sources: List[str] = []

    for doc in docs:
        metadata = doc.get('metadata') or {}
        source_name = metadata.get('filename') or metadata.get('source') or 'faq'
        sources.append(source_name)
        content = doc.get('content', '') or ''
        context_blocks.append(f"Source: {source_name}\n\n{content.strip()}")

    return "\n\n---\n\n".join(context_blocks), sources


def run_support_bot_flow(
    user_id: str,
    message: str,
    tenant_id: Optional[str] = None
) -> Dict[str, object]:
    """Execute the FAQ-backed support bot flow and return response metadata for a tenant."""

    config = _resolve_config(tenant_id)
    start_time = time.perf_counter()

    docs = retrieve_relevant_documents(
        query=message,
        top_k=config['top_k'],
        collection_name=config['collection']
    )

    context_text = ""
    sources: List[str] = []
    fallback_used = False

    if docs:
        context_text, sources = _format_context(docs)

        llm_client = get_llm_client()
        answer = llm_client.generate(
            system_prompt=config['system_prompt'],
            user_message=(
                f"User ID: {user_id}\n"
                f"Tenant: {config['tenant_id']}\n"
                f"Question: {message}\n"
                "Provide a concise, friendly support response."
            ),
            context=context_text
        )
    else:
        answer = config['fallback']
        fallback_used = True

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    record_support_interaction(
        message=message,
        fallback_used=fallback_used,
        tenant_id=config['tenant_id'],
        response_time_ms=elapsed_ms
    )

    return {
        "user_id": user_id,
        "answer": answer,
        "fallback_used": fallback_used,
        "sources": sources,
        "retrieved_context": context_text or None,
        "tenant_id": config['tenant_id']
    }
