"""
Lightweight chat engine using the Groq API directly.

The primary and fallback models are configurable so a provider-side model
retirement does not require another code change.
"""

import logging
import os
from typing import AsyncGenerator, List, Tuple

from groq import Groq
from pydantic import BaseModel

from .prompts import get_rag_prompt


logger = logging.getLogger(__name__)

DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
DEFAULT_FALLBACK_MODELS = "openai/gpt-oss-20b"
FALLBACK_STATUS_CODES = {403, 404, 408, 429, 500, 502, 503, 504}
PERSISTENT_MODEL_STATUS_CODES = {403, 404}


class ChatServiceUnavailableError(RuntimeError):
    """Raised when none of the configured chat models can serve a request."""


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatEngine:
    """Memory-efficient chat engine suitable for Render's free tier."""

    def __init__(self, rag_pipeline=None):
        self.rag_pipeline = rag_pipeline
        self.client = self._initialize_client()
        self.models = self._configured_models()
        self.model = self.models[0]
        print(f"Using Groq LLM ({self.model})")

    @staticmethod
    def _initialize_client():
        """Initialize the Groq client."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        return Groq(api_key=api_key)

    @staticmethod
    def _configured_models() -> List[str]:
        """Return a de-duplicated primary/fallback model list."""
        primary = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL).strip()
        fallback_value = os.getenv(
            "GROQ_FALLBACK_MODELS", DEFAULT_FALLBACK_MODELS
        )
        candidates = [primary]
        candidates.extend(model.strip() for model in fallback_value.split(","))

        models = []
        for model in candidates:
            if model and model not in models:
                models.append(model)

        return models or [DEFAULT_GROQ_MODEL]

    def _candidate_models(self) -> List[str]:
        """Try the last working model first, then the configured alternatives."""
        return [self.model] + [model for model in self.models if model != self.model]

    @staticmethod
    def _status_code(error):
        """Return an integer provider status code when one is available."""
        status_code = getattr(error, "status_code", None)
        try:
            return int(status_code)
        except (TypeError, ValueError):
            return None

    def _create_completion(self, messages: List[dict], stream: bool = False):
        """Create a completion and fall back if a model cannot serve it."""
        last_error = None
        persist_next_model = False
        for model in self._candidate_models():
            try:
                request_options = {
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_completion_tokens": 1024,
                    "stream": stream,
                }
                if model.startswith("openai/gpt-oss-"):
                    request_options["reasoning_effort"] = "low"

                response = self.client.chat.completions.create(**request_options)
                if model != self.model and persist_next_model:
                    logger.warning("Switched Groq chat model to %s", model)
                    self.model = model
                return response
            except Exception as exc:
                last_error = exc
                status_code = self._status_code(exc)
                logger.warning(
                    "Groq model %s failed (status=%s, type=%s)",
                    model,
                    status_code if status_code is not None else "unknown",
                    type(exc).__name__,
                )
                if status_code not in FALLBACK_STATUS_CODES:
                    break
                persist_next_model = status_code in PERSISTENT_MODEL_STATUS_CODES

        raise ChatServiceUnavailableError(
            "No configured chat model is currently available."
        ) from last_error

    @staticmethod
    def _convert_history(history: List[ChatMessage]) -> List[dict]:
        """Convert chat history to Groq message format."""
        return [
            {"role": message.role, "content": message.content}
            for message in history
        ]

    async def get_response(
        self,
        message: str,
        conversation_history: List[ChatMessage] = None,
    ) -> Tuple[str, List[str]]:
        """Return response text and source-document names for a user message."""
        sources = []
        context = ""

        if self.rag_pipeline:
            context = await self.rag_pipeline.get_context(message)
            sources = self.rag_pipeline.get_all_sources()

        messages = [{"role": "system", "content": get_rag_prompt(context)}]
        if conversation_history:
            messages.extend(self._convert_history(conversation_history))
        messages.append({"role": "user", "content": message})

        response = self._create_completion(messages)
        return response.choices[0].message.content, sources

    async def get_response_stream(
        self,
        message: str,
        conversation_history: List[ChatMessage] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream response chunks for a user message."""
        context = ""
        if self.rag_pipeline:
            context = await self.rag_pipeline.get_context(message)

        messages = [{"role": "system", "content": get_rag_prompt(context)}]
        if conversation_history:
            messages.extend(self._convert_history(conversation_history))
        messages.append({"role": "user", "content": message})

        try:
            stream = self._create_completion(messages, stream=True)
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except ChatServiceUnavailableError:
            raise
        except Exception as exc:
            logger.warning(
                "Groq response stream failed (type=%s)", type(exc).__name__
            )
            raise ChatServiceUnavailableError(
                "The chat response stream is temporarily unavailable."
            ) from exc
