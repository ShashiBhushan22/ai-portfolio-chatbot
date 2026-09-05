"""API-level tests for readiness and sanitized outage responses."""

import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import main
from app.chat_lightweight import ChatServiceUnavailableError


class UnavailableChatEngine:
    model = "unavailable-test-model"

    async def get_response(self, message, conversation_history=None):
        raise ChatServiceUnavailableError("private provider detail")

    async def get_response_stream(self, message, conversation_history=None):
        if False:
            yield ""
        raise ChatServiceUnavailableError("private provider detail")


class ApiTests(unittest.TestCase):
    def test_health_and_sanitized_outage_responses(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-only"}, clear=False):
            with TestClient(main.app) as client:
                health = client.get("/health")
                self.assertEqual(health.status_code, 200)
                self.assertTrue(health.json()["ready"])
                self.assertEqual(
                    health.json()["model"], "openai/gpt-oss-120b"
                )

                with patch.object(main, "chat_engine", UnavailableChatEngine()):
                    response = client.post(
                        "/chat", json={"message": "Tell me about the thesis"}
                    )
                    self.assertEqual(response.status_code, 503)
                    self.assertNotIn("private provider detail", response.text)

                    stream_response = client.post(
                        "/chat/stream",
                        json={"message": "Tell me about the thesis"},
                    )
                    self.assertEqual(stream_response.status_code, 200)
                    self.assertIn("temporarily unavailable", stream_response.text)
                    self.assertNotIn("private provider detail", stream_response.text)


if __name__ == "__main__":
    unittest.main()
