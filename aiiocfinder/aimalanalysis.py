import json
import logging

from aiiocfinder.prompt import Prompt
from aiiocfinder.openai_handler import OpenAIHandler


class AIMalAnalysis:
    def __init__(self, api_key, model, max_tokens, temperature, history):
        self._logger = logging.getLogger(__name__)
        self.openai = OpenAIHandler(api_key, model, max_tokens, temperature)
        self.prompt = Prompt(history)
        self.iocs = []
        self.yara_rules = []

    @property
    def history(self):
        return self.prompt.history

    def add_artifact(self, placeholder, artifact):
        self.prompt.replace_json_placeholders(placeholder, artifact)

    def find_iocs(self):
        if len(self.prompt.artifacts) > 0:
            for artifact in self.prompt.artifacts:
                self.__search_iocs(artifact, self.prompt.tools)
            self.__create_yara_rules()
            self.__summary()
        else:
            self._logger.error("Try to find IOCs with no artifact declared")

    def __search_iocs(self, artifact, tools):
        """
        Search for iocs and
        ask as long as the model thinks
        that there are more iocs to find.
        Model returns different stop reasons (while clause).
        """
        self._logger.debug("Start ioc search")
        self.openai.get_completion_with_tools(messages=self.history, tools=tools)
        while self.openai.finish_reason_is_tool_calls():
            function_name = self.openai.get_function_name_from_tools_call()
            args = self.openai.get_arguments_from_tools_call()
            self.prompt.add_assistant_function_call_to_history(function_name, args)
            self.__append_iocs(args)
            self.prompt.add_user_to_history(artifact["prompt_ioc_reasoning"])
            self.openai.get_completion(messages=self.history)
            self.prompt.add_assistant_to_history(
                self.openai.get_content_from_completion()
            )
            self.prompt.add_user_to_history(artifact["prompt_continue_or_quit"])
            self.openai.get_completion_with_tools(messages=self.history, tools=tools)
        self.prompt.add_assistant_to_history(self.openai.get_content_from_completion())
        self._logger.debug(f"Stop ioc search with iocs: {self.iocs}")

    def __append_iocs(self, args):
        try:
            ioc = json.loads(args)
        except Exception as e:
            self._logger.error(e)
            raise Exception
        self.iocs.append(ioc)

    def __create_yara_rules(self):
        for ioc in self.iocs:
            yara = self.prompt.yara_tools
            self.prompt.add_user_to_history(yara["prompt"] + ioc["ioc"])
            self.openai.get_completion_with_tools(
                messages=self.history, tools=yara["tools"]
            )
            function_name = self.openai.get_function_name_from_tools_call()
            args = self.openai.get_arguments_from_tools_call()
            self.prompt.add_assistant_function_call_to_history(function_name, args)
            self.__append_yara_rules(args)

    def __append_yara_rules(self, args):
        try:
            yara_rule = json.loads(args)["yara_rule"]
        except Exception as e:
            self._logger.error(e)
            raise Exception
        self.yara_rules.append(yara_rule)

    def __summary(self):
        self._logger.debug(f"Start get summary")
        self.prompt.add_user_to_history(self.prompt.summary_prompt())
        self.openai.get_completion(messages=self.history)
        self.summary = self.openai.get_content_from_completion()
        self.prompt.add_assistant_to_history(self.summary)

    def ask_ai(self, question):
        self.prompt.add_user_to_history(question)
        self.openai.get_completion(messages=self.history)
        self.prompt.add_assistant_to_history(self.openai.get_content_from_completion())
