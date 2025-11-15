"""Mini FastAPI app exposing an internal knowledge assistant endpoint."""

from __future__ import annotations

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llm_client import get_llm_client
from retriever import retrieve_relevant_context

INTERNAL_COLLECTION = os.getenv('INTERNAL_COLLECTION_NAME', 'internal_handbook')
INTERNAL_TOP_K = int(os.getenv('INTERNAL_TOP_K', '3'))
INTERNAL_SYSTEM_PROMPT = os.getenv(
    'INTERNAL_SYSTEM_PROMPT',
    'You are InternalAssistant, answering employee handbook questions succinctly.'
)

app = FastAPI(title="Internal Knowledge Assistant")


class InternalRequest(BaseModel):
    question: str


class InternalResponse(BaseModel):
    answer: str
    context_used: str


@app.post("/internal-assistant/query", response_model=InternalResponse)
async def internal_query(payload: InternalRequest) -> InternalResponse:
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    context = retrieve_relevant_context(
        query=payload.question,
        top_k=INTERNAL_TOP_K,
        collection_name=INTERNAL_COLLECTION
    )

    llm = get_llm_client()
    answer = llm.generate(
        system_prompt=INTERNAL_SYSTEM_PROMPT,
        user_message=payload.question,
        context=context
    )

    return InternalResponse(answer=answer, context_used=context)


__all__ = ["app"]
