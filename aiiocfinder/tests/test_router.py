from unittest import TestCase
from unittest.mock import patch, MagicMock, call
from fastapi.testclient import TestClient

from aiiocfinder.tests.basetest import BaseTest
from main import app


class TestapiTest(BaseTest):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.client = TestClient(app)

    def call_upload_api(self):
        self.compile_c_code("hello_world")
        myfile = "./aiiocfinder/tests/hello_world"
        files = {"file": open(myfile, "rb")}
        r = self.client.post("/disassamble", files=files)
        return r

    def test_setup_return_200(self):
        programming_model = self.load_test_json("aiiocfinder/tests/elffile.json")
        response = self.client.post("/setup", json=programming_model)
        self.assertEqual(response.status_code, 200)

    def test_setup_return_success(self):
        programming_model = self.load_test_json("aiiocfinder/tests/elffile.json")
        response = self.client.post("/setup", json=programming_model)
        self.assertIn("success", response.json()["status"])

    def test_disassamble_return_200(self):
        r = self.call_upload_api()
        self.assertEqual(r.status_code, 200)

    def test_disassamble_return_strings(self):
        r = self.call_upload_api()
        self.assertIn("Hello, World!", r.json()["strings"])

    def test_disassamble_return_assembly(self):
        r = self.call_upload_api()
        self.assertIn("xor", " ".join(r.json()["assembly"][".text"]))

    def test_artifact_returns_200(self):
        with patch("aiiocfinder.router.Router.proxy"):
            data = [{"type": "code", "artifact": "import json"}]
            response = self.client.post("/artifact", json=data)
            assert response.status_code == 200

    def test_artifact_calls_add_artifact_with_multiple_artifacts(self):
        with patch("aiiocfinder.router.Router.proxy") as proxy:
            proxy.analyst.add_artifact = MagicMock()
            data = [
                {"type": "code", "artifact": "import json"},
                {"type": "strings", "artifact": "this is a string"},
            ]
            response = self.client.post("/artifact", json=data)
            self.assertEqual(proxy.analyst.add_artifact.call_count, 2)
            proxy.analyst.add_artifact.assert_has_calls(
                [call("code", "import json"), call("strings", "this is a string")]
            )
            assert response.status_code == 200

    def test_artifact_wrong_post_return_422(self):
        """missing post parameter returns 422"""
        with patch("aiiocfinder.router.Router.proxy"):
            response = self.client.post("/artifact")
            assert response.status_code == 422

    def test_analyze_returns_200(self):
        with patch("aiiocfinder.router.Router.proxy"):
            response = self.client.get("/analyze")
            assert response.status_code == 200

    def test_yara_returns_200(self):
        with patch("aiiocfinder.router.Router.proxy"):
            response = self.client.get("/yara")
            assert response.status_code == 200

    def test_history_rules_returns_200(self):
        with patch("aiiocfinder.router.Router.proxy"):
            response = self.client.get("/history")
            assert response.status_code == 200

    def test_summary_returns_200(self):
        with patch("aiiocfinder.router.Router.proxy"):
            response = self.client.get("/summary")
            assert response.status_code == 200

    def test_iocs_returns_200(self):
        with patch("aiiocfinder.router.Router.proxy"):
            response = self.client.get("/iocs")
            assert response.status_code == 200

    def test_completion_returns_200(self):
        with patch("aiiocfinder.router.Router.proxy"):
            data = {"message": "test"}
            response = self.client.post("/completion", params=data)
            assert response.status_code == 200

    def test_completion_returns_422(self):
        with patch("aiiocfinder.router.Router.proxy"):
            data = {"language": "elffile", "strings": "test"}
            response = self.client.post("/completion", params=data)
            assert response.status_code == 422

    def test_reset_returns_200(self):
        with patch("aiiocfinder.router.Router.proxy"):
            response = self.client.get("/reset")
            assert response.status_code == 200
