# Getting Started FAQ

## How do I launch the support bot locally?
- Create a virtualenv with Python 3.11+
- Install dependencies with `pip install -r requirements.txt`
- Run `uvicorn server:app --reload`

## What should I do if the bot cannot answer a question?
If the knowledge base does not include a relevant answer, the SupportBot returns a friendly fallback message and routes the request to a human specialist.
