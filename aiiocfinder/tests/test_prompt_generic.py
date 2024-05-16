from aiiocfinder.tests.baseprompt import BasePrompt
from aiiocfinder.prompt import Prompt


class PromptGenericTest(BasePrompt):
    def test_if_system_message_in_history(self):
        system_message = "You are a malware analyst."
        programming_model = self.load_test_json("aiiocfinder/tests/generic.json")
        prompt = Prompt(programming_model["history"])
        self.assert_system_message(system_message, prompt.history[0])

    def test_empty_artifacts(self):
        programming_model = self.load_test_json("aiiocfinder/tests/generic.json")
        prompt = Prompt(programming_model["history"])
        self.assertEqual(len(prompt.artifacts), 0)

    def test_one_artifacts(self):
        prompt = self._scenario_one_artifact_provided("aiiocfinder/tests/generic.json")
        self.assertEqual(len(prompt.artifacts), 1)

    def test_code_preamble(self):
        code_preamble = "This is malicious code:"
        prompt = self._scenario_one_artifact_provided("aiiocfinder/tests/generic.json")
        self.assert_user_message(code_preamble, prompt.history[1])

    def test_code_sequel(self):
        code_sequal = "Do you find any IOCs?"
        prompt = self._scenario_one_artifact_provided("aiiocfinder/tests/generic.json")
        self.assert_user_message(code_sequal, prompt.history[1])

    def test_if_provided_code_in_history(self):
        code = "python -c 'import socket'"
        prompt = self._scenario_one_artifact_provided("aiiocfinder/tests/generic.json")
        self.assert_user_message(code, prompt.history[1])

    def test_if_function_call_in_history(self):
        prompt = self._scenario_one_artifact_provided("aiiocfinder/tests/generic.json")
        self.assertEqual(
            "get_ioc", prompt._programming_model[1]["tools"][0]["function"]["name"]
        )

    def test_tools(self):
        prompt = self._scenario_one_artifact_provided("aiiocfinder/tests/generic.json")
        tools = prompt.tools
        print(tools)
        self.assertEqual("get_ioc", tools[0]["function"]["name"])

    def test_if_yara_function_call_in_history(self):
        prompt = self._scenario_one_artifact_provided("aiiocfinder/tests/generic.json")
        self.assertEqual(
            "get_yara_rules",
            prompt._programming_model[2]["tools"][0]["function"]["name"],
        )

    def test_get_yara_rules(self):
        prompt = self._scenario_one_artifact_provided("aiiocfinder/tests/generic.json")
        tools = prompt.yara_tools
        self.assertEqual("get_yara_rules", tools["tools"][0]["function"]["name"])
