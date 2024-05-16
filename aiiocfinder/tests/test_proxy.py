from unittest.mock import patch
from aiiocfinder.tests.basetest import BaseTest
from aiiocfinder.proxy import Proxy
from aiiocfinder.aimalanalysis import AIMalAnalysis
from aiiocfinder.disassembler import Disassambler


class ProxyTest(BaseTest):
    def test_finder(self):
        programming_model = self.load_test_json("aiiocfinder/tests/generic.json")
        with patch("aiiocfinder.aimalanalysis.OpenAIHandler"):
            proxy = Proxy()
            analyst = proxy.setup(
                api_key="api_key",
                model="gpt-1337",
                max_tokens=20,
                temperature=0.2,
                history=programming_model["history"],
            )
            analyst = proxy.analyst
            self.assertIsInstance(analyst, AIMalAnalysis)
            analyst_dup = proxy.analyst
            self.assertIsInstance(analyst_dup, AIMalAnalysis)
            self.assertEqual(analyst, analyst_dup)

    def test_reset(self):
        programming_model = self.load_test_json("aiiocfinder/tests/generic.json")
        with patch("aiiocfinder.aimalanalysis.OpenAIHandler"):
            proxy = Proxy()
            analyst = proxy.setup(
                api_key="api_key",
                model="gpt-1337",
                max_tokens=20,
                temperature=0.2,
                history=programming_model["history"],
            )
            analyst = proxy.analyst
            self.assertIsInstance(analyst, AIMalAnalysis)
            proxy.reset_analyst()
            with self.assertRaises(Exception):
                proxy.analyst

    def test_get_disassambler(self):
        binaryfile = self.compile_c_code("hello_world")
        proxy = Proxy()
        analyst = proxy.get_disassambler(binaryfile)
        self.assertIsInstance(analyst, Disassambler)
