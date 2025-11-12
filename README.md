# chatbot-templates

A FastAPI-based chatbot server template with RAG (Retrieval-Augmented Generation) system prompt support.

## Overview

This repository provides a simple FastAPI server template for chatbot applications. It includes:
- A `/chat` endpoint that processes messages with optional context
- RAG system prompt configuration
- Clean, extensible architecture for chatbot development

## Features

- **FastAPI Server**: Modern, fast web framework for building APIs
- **Context-Aware Responses**: `/chat` endpoint that handles messages with optional context
- **RAG System Prompt**: Configurable system prompt for retrieval-augmented generation
- **Interactive API Documentation**: Automatic OpenAPI docs at `/docs`

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

#### POST /chat
Send a chat message with optional context.

**Request Body:**
```json
{
  "message": "What is the capital of France?",
  "context": "France is a country in Western Europe. Its capital city is Paris."
}
```

**Response:**
```json
{
  "response": "Based on the provided context, I understand your question: 'What is the capital of France?'. The context indicates: France is a country in Western Europe. Its capital city is Paris.",
  "system_prompt": "You are a helpful AI assistant...",
  "context_used": true
}
```

### Testing the API

Using curl:
```bash
# Simple message without context
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'

# Message with context
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is RAG?", "context": "RAG stands for Retrieval-Augmented Generation, a technique that combines retrieval of relevant documents with generation of responses."}'
```

Using Python:
```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "Tell me about this topic",
        "context": "Your relevant context here"
    }
)
print(response.json())
```

### Interactive Documentation

Visit `http://localhost:8000/docs` for interactive API documentation powered by Swagger UI.

## Project Structure

```
chatbot-templates/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── server.py                      # FastAPI server implementation
├── prompts/
│   └── rag_system_prompt.txt     # RAG system prompt template
└── .gitignore                    # Git ignore rules
```

## RAG System Prompt

The RAG system prompt is stored in `prompts/rag_system_prompt.txt`. This prompt defines the behavior of the chatbot when processing context-based queries. You can customize this prompt to fit your specific use case.

## Development

### Adding New Endpoints

To add new endpoints, edit `server.py` and define new routes using FastAPI decorators:

```python
@app.post("/your-endpoint")
async def your_function(request: YourRequestModel):
    # Your logic here
    return {"result": "your response"}
```

### Customizing the System Prompt

Edit `prompts/rag_system_prompt.txt` to customize the chatbot's behavior and response style.

## License

This project is open source and available for use and modification.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.