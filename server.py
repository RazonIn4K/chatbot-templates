"""
FastAPI demo server for chatbot-templates
This server provides a /chat endpoint that echoes context-based answers using RAG system prompt.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from typing import Optional

app = FastAPI(title="Chatbot Templates Demo", version="1.0.0")

# Load RAG system prompt
PROMPTS_DIR = Path(__file__).parent / "prompts"
RAG_PROMPT_FILE = PROMPTS_DIR / "rag_system_prompt.txt"

def load_system_prompt() -> str:
    """Load the RAG system prompt from file."""
    try:
        with open(RAG_PROMPT_FILE, 'r') as f:
            return f.read()
    except FileNotFoundError:
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


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Chatbot Templates Demo API",
        "version": "1.0.0",
        "endpoints": {
            "/chat": "POST - Send a chat message with optional context",
            "/docs": "GET - Interactive API documentation"
        }
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint that echoes a context-based answer.
    
    The response is formulated based on:
    - The system prompt loaded from prompts/rag_system_prompt.txt
    - The user's message
    - Optional context provided in the request
    """
    if not request.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Build the context-based response
    context_used = request.context is not None and len(request.context.strip()) > 0
    
    if context_used:
        # Echo a context-aware response
        response_text = (
            f"Based on the provided context, I understand your question: '{request.message}'. "
            f"The context indicates: {request.context[:200]}..."
            if len(request.context) > 200 else
            f"Based on the provided context, I understand your question: '{request.message}'. "
            f"The context indicates: {request.context}"
        )
    else:
        # Echo without context
        response_text = (
            f"I received your message: '{request.message}'. "
            f"However, no context was provided. To give you a better answer, "
            f"please provide relevant context in your request."
        )
    
    return ChatResponse(
        response=response_text,
        system_prompt=SYSTEM_PROMPT,
        context_used=context_used
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
