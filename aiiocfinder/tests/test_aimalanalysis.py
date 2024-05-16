from unittest.mock import patch, MagicMock

from aiiocfinder.tests.basetest import BaseTest
from aiiocfinder.aimalanalysis import AIMalAnalysis


class AIMalAnalysisTest(BaseTest):
    def test_history_contains_summary(self):
        completions = [
            "Completion after ioc",
            "Completion after loop",
            "This is the summary",
        ]
        with patch(
            "aiiocfinder.aimalanalysis.OpenAIHandler",
            return_value=self.__get_mock_for_scenario_one_ioc(completions=completions),
        ):
            iocfinder = self.__scenario_one_ioc_with_generic_prompt()
        self.assertIn(completions[2], iocfinder.summary)
        self.assert_user_message("summary", iocfinder.history[9])
        self.assert_assistant_message(completions[2], iocfinder.history[10])

    def test_with_complete_history(self):
        completions = [
            "Completion after ioc",
            "Completion after loop",
            "This is the summary",
        ]
        with patch(
            "aiiocfinder.aimalanalysis.OpenAIHandler",
            return_value=self.__get_mock_for_scenario_one_ioc(completions=completions),
        ):
            iocfinder = self.__scenario_one_ioc_with_generic_prompt()
        hist = iocfinder.history
        self.assert_assistant_message(completions[0], hist[4])
        self.assert_user_message("Do you find more iocs?", hist[5])
        self.assert_assistant_message(completions[1], hist[6])

    def test_iocs_returns_iocs(self):
        completions = [
            "Completion after ioc",
            "Completion after loop",
            "This is the summary",
        ]
        with patch(
            "aiiocfinder.aimalanalysis.OpenAIHandler",
            return_value=self.__get_mock_for_scenario_one_ioc(completions=completions),
        ):
            iocfinder = self.__scenario_one_ioc_with_generic_prompt()
        print(iocfinder.history)
        print(iocfinder.iocs)
        self.assertEqual(len(iocfinder.iocs), 1)

    def test_summary_bug_double_assistant(self):
        """
        Test bugfix for double assistant output for summary
        """
        completions = [
            "Completion after ioc",
            "Completion after loop",
            "This is the summary",
        ]
        with patch(
            "aiiocfinder.aimalanalysis.OpenAIHandler",
            return_value=self.__get_mock_for_scenario_one_ioc(completions=completions),
        ):
            iocfinder = self.__scenario_one_ioc_with_generic_prompt()
        self.assertNotEqual("assistant", iocfinder.history[7]["role"])

    def test_two_artifacts_in_history(self):
        completions = [
            "Completion after ioc with code",
            "Completion after loop with",
            "Completion after loop with strings without ioc",
            "This is the summary",
        ]
        with patch(
            "aiiocfinder.aimalanalysis.OpenAIHandler",
            return_value=self.__get_mock_for_scenario_one_ioc(
                completions=completions, finish_reasons=[True, False, False]
            ),
        ):
            iocfinder = self.__scenario_one_ioc_two_artifacts_with_elffile_prompt()
        self.assertEqual(len(iocfinder.prompt.artifacts), 2)

    def test_create_yara_rules_for_elffile(self):
        completions = [
            "Completion after ioc with code",
            "Completion after loop with",
            "Completion after loop with strings without ioc",
            "This is the summary",
        ]
        with patch(
            "aiiocfinder.aimalanalysis.OpenAIHandler",
            return_value=self.__get_mock_for_scenario_one_ioc(
                completions=completions, finish_reasons=[True, False, False]
            ),
        ):
            iocfinder = self.__scenario_one_ioc_two_artifacts_with_elffile_prompt()
        self.assertEqual(len(iocfinder.yara_rules), 1)

    def test_create_yara_rules_for_generic(self):
        completions = [
            "Completion after ioc",
            "Completion after loop",
            "This is the summary",
        ]
        with patch(
            "aiiocfinder.aimalanalysis.OpenAIHandler",
            return_value=self.__get_mock_for_scenario_one_ioc(completions=completions),
        ):
            iocfinder = self.__scenario_one_ioc_with_generic_prompt()
        self.assertEqual(len(iocfinder.yara_rules), 1)

    def assert_assistant_message(self, assistant, hist_item):
        self.assertIn("assistant", hist_item["role"])
        self.assertIn(assistant, hist_item["content"])

    def __scenario_one_ioc_with_generic_prompt(self):
        code = "empty code"
        programming_model = self.load_test_json("aiiocfinder/tests/generic.json")
        iocfinder = AIMalAnalysis(
            api_key="api_key",
            model="gpt-1337",
            max_tokens=20,
            temperature=0.2,
            history=programming_model["history"],
        )
        iocfinder.add_artifact("code", code)
        iocfinder.find_iocs()
        self.assertEqual(len(iocfinder.prompt.artifacts), 1)
        self.assert_user_message(code, iocfinder.history[1])
        return iocfinder

    def __scenario_one_ioc_two_artifacts_with_elffile_prompt(self):
        programming_model = self.load_test_json("aiiocfinder/tests/elffile.json")
        iocfinder = AIMalAnalysis(
            api_key="api_key",
            model="gpt-1337",
            max_tokens=20,
            temperature=0.2,
            history=programming_model["history"],
        )
        iocfinder.add_artifact("code", "empty code")
        iocfinder.add_artifact("strings", "empty strings")
        iocfinder.find_iocs()
        return iocfinder

    def __get_mock_for_scenario_one_ioc(
        self, completions, finish_reasons=[True, False]
    ):
        """
        Scenario: One IOC (test_value) was found
        There is one ioc found and should contain the provided test_value
        """
        call_args = [
            '{\n "ioc": "socket", "line": "\\\\npython -c \'import socket\'\\\\n"\n}',
            '{\n "yara_rule": "my yara rule"\n}',
        ]
        mock = MagicMock()
        mock.finish_reason_is_tool_calls = MagicMock(side_effect=finish_reasons)
        mock.get_arguments_from_tools_call = MagicMock(side_effect=call_args)
        mock.get_content_from_completion = MagicMock(side_effect=completions)
        return mock
