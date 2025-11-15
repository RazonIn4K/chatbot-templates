"""
FastAPI server for chatbot-templates with LLM integration.
This server provides chat endpoints with RAG capabilities.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from typing import List, Optional
import logging

from llm_client import get_llm_client, LLMClientError
from retriever import retrieve_relevant_context
from support_bot import run_support_bot_flow

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Chatbot Templates API", version="2.0.0")

# Load RAG system prompt
PROMPTS_DIR = Path(__file__).parent / "prompts"
RAG_PROMPT_FILE = PROMPTS_DIR / "rag_system_prompt.txt"


def load_system_prompt() -> str:
    """Load the RAG system prompt from file."""
    try:
        with open(RAG_PROMPT_FILE, 'r') as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"System prompt file not found: {RAG_PROMPT_FILE}")
        return "You are a helpful AI assistant."


SYSTEM_PROMPT = load_system_prompt()


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    context: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    system_prompt: str
    context_used: bool


class SupportBotRequest(BaseModel):
    """Request payload for the support bot endpoint."""
    user_id: str
    message: str
    tenant_id: Optional[str] = None


class SupportBotResponse(BaseModel):
    """Response payload for the support bot endpoint."""
    user_id: str
    answer: str
    fallback_used: bool
    sources: List[str]
    retrieved_context: Optional[str] = None
    tenant_id: str


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Chatbot Templates API",
        "version": "2.0.0",
        "endpoints": {
            "/chat": "POST - Send a chat message with optional context (uses LLM)",
            "/chat-with-retrieval": "POST - Chat with automatic context retrieval from vector DB",
            "/support-bot/query": "POST - FAQ-backed support assistant for Upwork demos",
            "/health": "GET - Health check endpoint",
            "/docs": "GET - Interactive API documentation"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        # Check if LLM client can be initialized
        client = get_llm_client()
        return {
            "status": "healthy",
            "llm_provider": client.provider,
            "llm_model": client.model
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint that generates responses using an LLM.

    The response is generated based on:
    - The system prompt loaded from prompts/rag_system_prompt.txt
    - The user's message
    - Optional context provided in the request

    Args:
        request: ChatRequest with message and optional context

    Returns:
        ChatResponse with the generated response, system prompt, and context flag

    Raises:
        HTTPException: If message is empty or LLM generation fails
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    context_used = request.context is not None and len(request.context.strip()) > 0

    try:
        # Get LLM client
        llm_client = get_llm_client()

        # Generate response using the LLM
        logger.info(f"Generating response for message: {request.message[:50]}...")
        response_text = llm_client.generate(
            system_prompt=SYSTEM_PROMPT,
            user_message=request.message,
            context=request.context if context_used else None
        )

        logger.info("Response generated successfully")

        return ChatResponse(
            response=response_text,
            system_prompt=SYSTEM_PROMPT,
            context_used=context_used
        )

    except LLMClientError as e:
        logger.error(f"LLM client error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate response: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in /chat: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/chat-with-retrieval", response_model=ChatResponse)
async def chat_with_retrieval(request: ChatRequest):
    """
    Chat endpoint with automatic context retrieval.

    This endpoint:
    1. Takes the user's message
    2. Retrieves relevant context from the vector database (currently a stub)
    3. Generates a response using the LLM with the retrieved context

    Args:
        request: ChatRequest with message (context field is ignored)

    Returns:
        ChatResponse with the generated response, system prompt, and context flag

    Raises:
        HTTPException: If message is empty or processing fails
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        # Retrieve relevant context
        logger.info(f"Retrieving context for message: {request.message[:50]}...")
        retrieved_context = retrieve_relevant_context(
            query=request.message,
            top_k=3
        )

        # Get LLM client
        llm_client = get_llm_client()

        # Generate response with retrieved context
        logger.info("Generating response with retrieved context...")
        response_text = llm_client.generate(
            system_prompt=SYSTEM_PROMPT,
            user_message=request.message,
            context=retrieved_context
        )

        logger.info("Response generated successfully")

        return ChatResponse(
            response=response_text,
            system_prompt=SYSTEM_PROMPT,
            context_used=True
        )

    except LLMClientError as e:
        logger.error(f"LLM client error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate response: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in /chat-with-retrieval: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/support-bot/query", response_model=SupportBotResponse)
async def support_bot_query(request: SupportBotRequest):
    """FAQ-backed support assistant with tenant-aware RAG over docs/faq collections."""

    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    if not request.user_id or not request.user_id.strip():
        raise HTTPException(status_code=400, detail="user_id is required")

    try:
        result = run_support_bot_flow(
            user_id=request.user_id.strip(),
            message=request.message.strip(),
            tenant_id=request.tenant_id.strip() if request.tenant_id else None
        )
        return SupportBotResponse(**result)
    except LLMClientError as exc:
        logger.error(f"LLM client error in support bot: {exc}")
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Unexpected error in /support-bot/query: {exc}")
        raise HTTPException(status_code=500, detail="Internal server error") from exc


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
