import unittest
from unittest.mock import patch, MagicMock, call

from aiiocfinder.openai_handler import OpenAIHandler


class OpenAIHandlerTest(unittest.TestCase):
    def test_finish_reason_is_function_call(self):
        handler = OpenAIHandler(
            "test_api_key", "test_model", "test_token", "test_temperature"
        )
        handler.response = MagicMock()
        handler.client = MagicMock()
        handler.response.choices[0].finish_reason = "tool_calls"
        self.assertTrue(handler.finish_reason_is_tool_calls())

    def test_finish_reason_is_not_function_call(self):
        handler = OpenAIHandler(
            "test_api_key", "test_model", "test_token", "test_temperature"
        )
        handler.response = MagicMock()
        handler.client = MagicMock()
        handler.response.choices[0].finish_reason = "length"
        self.assertFalse(handler.finish_reason_is_tool_calls())

    def test_get_completion(self):
        with patch("aiiocfinder.openai_handler.OpenAI") as openai:
            handler = OpenAIHandler(
                "test_api_key", "test_model", "test_token", "test_temperature"
            )
            self.assertEqual(openai.call_count, 1)
            openai.assert_has_calls([call(api_key="test_api_key")])
            handler.get_completion("message")
            self.assertEqual(handler.client.chat.completions.create.call_count, 1)
            handler.client.chat.completions.create.assert_has_calls([
                call(
                    model="test_model",
                    messages="message",
                    max_tokens="test_token",
                    temperature="test_temperature",
                )
            ])
