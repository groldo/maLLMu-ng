import logging
from openai import OpenAI


class OpenAIHandler:
    """
    OpenAIHandler is wrapper around the openai API implementation
    with some conveniance functions.
    There is no history,
    so keeping track of consecutive/history calls has to be done somewhere else.
    The handler only remembers the last completion call it has made in self.response
    There are some conveniance functions to get only a subset of the response.
    """

    def __init__(self, api_key, model, max_tokens, temperature):
        self._logger = logging.getLogger(__name__)
        self.client = OpenAI(api_key=api_key)
        self.response = None
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._logger.debug(f"Initialized {__name__}")

    def finish_reason_is_tool_calls(self) -> bool:
        """
        Check if there was function call made by the AI
        Return true if so.
        """
        return "tool_calls" in self.response.choices[0].finish_reason

    def get_tools_call_from_completion(self) -> str:
        """
        Returns a string in json format
        """
        return self.response.choices[0].message

    def get_arguments_from_tools_call(self) -> str:
        """
        Returns a string in json format
        """
        return self.get_tools_call_from_completion().tool_calls[0].function.arguments

    def get_function_name_from_tools_call(self):
        """
        Returns the name of the called function
        """
        return self.get_tools_call_from_completion().tool_calls[0].function.name

    def get_content_from_completion(self):
        return self.response.choices[0].message.content

    def get_completion(self, messages):
        self.response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        self._logger.debug(self.response)
        self._logger.debug(" ".join(self.get_content_from_completion().split()))
        return self.get_content_from_completion()

    def get_completion_with_tools(self, messages, tools):
        try:
            self.response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            self._logger.debug(self.response)
            self._logger.debug(self.get_tools_call_from_completion())
            return self.response
        except Exception as e:
            self._logger.error(e)
            self._logger.error(
                f"failed with model: {self.model}; max_tokens: {self.max_tokens};"
                f" temperature: {self.temperature}"
            )
