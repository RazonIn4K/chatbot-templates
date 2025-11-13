"""
LLM Client for chatbot-templates.
Handles communication with various LLM providers with retry logic and error handling.
"""

import os
import logging
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMClientError(Exception):
    """Base exception for LLM client errors."""
    pass


class LLMClient:
    """
    LLM Client that supports multiple providers (OpenAI, Anthropic, etc.).

    Environment variables:
    - LLM_PROVIDER: Provider name (default: 'openai')
    - OPENAI_API_KEY: API key for OpenAI
    - ANTHROPIC_API_KEY: API key for Anthropic
    - LLM_MODEL: Model name (default: varies by provider)
    - LLM_TEMPERATURE: Temperature for generation (default: 0.7)
    - LLM_MAX_TOKENS: Max tokens for generation (default: 500)
    """

    def __init__(self):
        """Initialize the LLM client with environment configuration."""
        self.provider = os.getenv('LLM_PROVIDER', 'openai').lower()
        self.model = os.getenv('LLM_MODEL')
        self.temperature = float(os.getenv('LLM_TEMPERATURE', '0.7'))
        self.max_tokens = int(os.getenv('LLM_MAX_TOKENS', '500'))

        # Initialize provider-specific client
        if self.provider == 'openai':
            self._init_openai()
        elif self.provider == 'anthropic':
            self._init_anthropic()
        else:
            raise LLMClientError(f"Unsupported provider: {self.provider}")

        logger.info(f"Initialized LLM client with provider: {self.provider}, model: {self.model}")

    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
        except ImportError:
            raise LLMClientError(
                "OpenAI package not installed. Install with: pip install openai"
            )

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise LLMClientError("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI(api_key=api_key)
        if not self.model:
            self.model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')

    def _init_anthropic(self):
        """Initialize Anthropic client."""
        try:
            from anthropic import Anthropic
        except ImportError:
            raise LLMClientError(
                "Anthropic package not installed. Install with: pip install anthropic"
            )

        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise LLMClientError("ANTHROPIC_API_KEY environment variable not set")

        self.client = Anthropic(api_key=api_key)
        if not self.model:
            self.model = os.getenv('LLM_MODEL', 'claude-3-haiku-20240307')

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )
    def generate(
        self,
        system_prompt: str,
        user_message: str,
        context: Optional[str] = None
    ) -> str:
        """
        Generate a response from the LLM.

        Args:
            system_prompt: System prompt to set behavior
            user_message: User's message/question
            context: Optional context to include in the prompt

        Returns:
            Generated response text

        Raises:
            LLMClientError: If generation fails after retries
        """
        try:
            # Build the user message with context if provided
            full_user_message = user_message
            if context:
                full_user_message = f"Context:\n{context}\n\nQuestion: {user_message}"

            logger.info(f"Generating response with {self.provider} ({self.model})")

            if self.provider == 'openai':
                return self._generate_openai(system_prompt, full_user_message)
            elif self.provider == 'anthropic':
                return self._generate_anthropic(system_prompt, full_user_message)
            else:
                raise LLMClientError(f"Provider {self.provider} not implemented")

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise LLMClientError(f"Failed to generate response: {str(e)}") from e

    def _generate_openai(self, system_prompt: str, user_message: str) -> str:
        """Generate response using OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content

    def _generate_anthropic(self, system_prompt: str, user_message: str) -> str:
        """Generate response using Anthropic API."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        return response.content[0].text


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    Get or create the singleton LLM client instance.

    Returns:
        LLMClient instance
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
