# Makefile for chatbot-templates

.PHONY: help demo test-demo

help:
	@echo "Commands:"
	@echo "  make demo        - Start the FastAPI server in development mode."
	@echo "  make test-demo   - Run the automated tests."

demo:
	@echo "Starting FastAPI server..."
	uvicorn server:app --reload

test-demo:
	@echo "Running tests..."
	pytest
