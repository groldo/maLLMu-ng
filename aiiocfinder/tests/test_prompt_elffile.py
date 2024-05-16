from aiiocfinder.tests.baseprompt import BasePrompt
from aiiocfinder.prompt import Prompt


class PromptElffileTest(BasePrompt):
    def test_system_message_in_history(self):
        system_message = "These artifacts are from an elffile."
        programming_model = self.load_test_json("aiiocfinder/tests/elffile.json")
        prompt = Prompt(programming_model["history"])
        self.assert_system_message(system_message, prompt.history[0])

    def test_empty_artifacts(self):
        programming_model = self.load_test_json("aiiocfinder/tests/elffile.json")
        prompt = Prompt(programming_model["history"])
        self.assertEqual(len(prompt.artifacts), 0)

    def test_code_preamble(self):
        code_preamble = "This is the .text section from an elffile"
        prompt = self._scenario_one_artifact_provided("aiiocfinder/tests/elffile.json")
        self.assert_user_message(code_preamble, prompt.history[1])

    def test_code_in_history(self):
        code = "python -c 'import socket'"
        prompt = self._scenario_one_artifact_provided("aiiocfinder/tests/elffile.json")
        self.assert_user_message(code, prompt.history[1])

    def test_one_artifacts_in_history(self):
        prompt = self._scenario_one_artifact_provided("aiiocfinder/tests/elffile.json")
        self.assertEqual(len(prompt.artifacts), 1)

    def test_function_call_in_history(self):
        prompt = self._scenario_one_artifact_provided("aiiocfinder/tests/elffile.json")
        self.assertEqual(
            "auto", prompt._programming_model[1]["tools"][0]["function_call"]
        )

    def test_two_artifacts_in_history(self):
        prompt = self.__scenario_two_artifact_provided("aiiocfinder/tests/elffile.json")
        self.assertEqual(len(prompt.artifacts), 2)

    def test_strings_prequel(self):
        code_sequal = "These are the strings found in the elffile"
        prompt = self.__scenario_two_artifact_provided("aiiocfinder/tests/elffile.json")
        self.assert_user_message(code_sequal, prompt.history[2])

    def test_strings_in_history(self):
        strings = "these are extracted strings"
        prompt = self.__scenario_two_artifact_provided(
            "aiiocfinder/tests/elffile.json", strings
        )
        self.assert_user_message(strings, prompt.history[2])
        self.assertIn(strings, prompt.artifacts[1]["prompt_artifact"])

    def test_strings_sequel(self):
        code_sequal = "Do you find any IOCs?"
        prompt = self.__scenario_two_artifact_provided("aiiocfinder/tests/elffile.json")
        self.assert_user_message(code_sequal, prompt.history[2])

    def __scenario_two_artifact_provided(
        self, filename, strings="these are extracted strings"
    ):
        programming_model = self.load_test_json(filename)
        code = "python -c 'import socket'"
        prompt = Prompt(programming_model["history"])
        prompt.replace_json_placeholders("code", code)
        prompt.replace_json_placeholders("strings", strings)
        self.assertEqual(len(prompt.artifacts), 2)
        return prompt
