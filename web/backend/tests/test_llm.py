"""LLM endpoint and provider error handling tests."""

from __future__ import annotations

import unittest

import httpx

from app.services.llm import _completion_url, _error_detail


class LlmEndpointTests(unittest.TestCase):
    def test_deepseek_legacy_v1_url_is_normalized(self):
        self.assertEqual(
            _completion_url("deepseek", "https://api.deepseek.com/v1"),
            "https://api.deepseek.com/chat/completions",
        )

    def test_openai_v1_url_is_preserved(self):
        self.assertEqual(
            _completion_url("openai", "https://api.openai.com/v1"),
            "https://api.openai.com/v1/chat/completions",
        )

    def test_full_completion_url_is_not_duplicated(self):
        endpoint = "https://gateway.example.test/v1/chat/completions"
        self.assertEqual(_completion_url("custom", endpoint), endpoint)

    def test_provider_error_message_is_kept(self):
        response = httpx.Response(
            404,
            json={"error": {"message": "model not found", "code": "model_not_found"}},
        )
        self.assertEqual(_error_detail(response), "model not found")


if __name__ == "__main__":
    unittest.main()
