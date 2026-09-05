"""Tests for model configuration, fallback, and safe error handling."""

import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.chat_lightweight import ChatEngine, ChatServiceUnavailableError


class FakeProviderError(RuntimeError):
    def __init__(self, message, status_code=404):
        super().__init__(message)
        self.status_code = status_code


class FakeCompletions:
    def __init__(self, failing_models=None):
        if isinstance(failing_models, dict):
            self.failing_models = failing_models
        else:
            self.failing_models = {
                model: 404 for model in (failing_models or [])
            }
        self.calls = []

    def create(self, **kwargs):
        model = kwargs["model"]
        self.calls.append(model)
        if model in self.failing_models:
            raise FakeProviderError(
                f"private provider detail for {model}",
                status_code=self.failing_models[model],
            )

        message = SimpleNamespace(content=f"response from {model}")
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def make_engine(failing_models=None):
    completions = FakeCompletions(failing_models)
    engine = ChatEngine.__new__(ChatEngine)
    engine.rag_pipeline = None
    engine.models = ["primary-model", "fallback-model"]
    engine.model = engine.models[0]
    engine.client = SimpleNamespace(
        chat=SimpleNamespace(completions=completions)
    )
    return engine, completions


class ModelConfigurationTests(unittest.TestCase):
    def test_supported_production_models_are_the_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(
                ChatEngine._configured_models(),
                ["openai/gpt-oss-120b", "openai/gpt-oss-20b"],
            )

    def test_environment_models_are_trimmed_and_deduplicated(self):
        env = {
            "GROQ_MODEL": " primary-model ",
            "GROQ_FALLBACK_MODELS": "fallback-model, primary-model, second-fallback",
        }
        with patch.dict(os.environ, env, clear=False):
            self.assertEqual(
                ChatEngine._configured_models(),
                ["primary-model", "fallback-model", "second-fallback"],
            )

    def test_fallback_is_used_and_remembered(self):
        engine, completions = make_engine({"primary-model"})

        response = engine._create_completion([{"role": "user", "content": "Hi"}])

        self.assertEqual(response.choices[0].message.content, "response from fallback-model")
        self.assertEqual(completions.calls, ["primary-model", "fallback-model"])
        self.assertEqual(engine.model, "fallback-model")

    def test_all_provider_errors_become_service_unavailable(self):
        engine, _ = make_engine({"primary-model", "fallback-model"})

        with self.assertRaises(ChatServiceUnavailableError) as raised:
            engine._create_completion([{"role": "user", "content": "Hi"}])

        self.assertNotIn("private provider detail", str(raised.exception))

    def test_authentication_error_does_not_retry_another_model(self):
        engine, completions = make_engine({"primary-model": 401})

        with self.assertRaises(ChatServiceUnavailableError):
            engine._create_completion([{"role": "user", "content": "Hi"}])

        self.assertEqual(completions.calls, ["primary-model"])

    def test_transient_fallback_does_not_replace_primary_model(self):
        engine, completions = make_engine({"primary-model": 429})

        response = engine._create_completion([{"role": "user", "content": "Hi"}])

        self.assertEqual(response.choices[0].message.content, "response from fallback-model")
        self.assertEqual(completions.calls, ["primary-model", "fallback-model"])
        self.assertEqual(engine.model, "primary-model")


class ResponseTests(unittest.IsolatedAsyncioTestCase):
    async def test_response_uses_working_fallback(self):
        engine, _ = make_engine({"primary-model"})

        response, sources = await engine.get_response("Tell me about the thesis")

        self.assertEqual(response, "response from fallback-model")
        self.assertEqual(sources, [])

    async def test_provider_details_are_not_returned_as_chat_text(self):
        engine, _ = make_engine({"primary-model", "fallback-model"})

        with self.assertRaises(ChatServiceUnavailableError):
            await engine.get_response("Tell me about the thesis")


if __name__ == "__main__":
    unittest.main()
