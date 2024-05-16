from aiiocfinder.tests.basetest import BaseTest
from aiiocfinder.prompt import Prompt


class BasePrompt(BaseTest):
    def _scenario_one_artifact_provided(self, filename):
        programming_model = self.load_test_json(filename)
        code = "python -c 'import socket'"
        prompt = Prompt(programming_model["history"])
        prompt.replace_json_placeholders("code", code)
        self.assertEqual(len(prompt.artifacts), 1)
        return prompt
