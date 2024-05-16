import os
import json
import unittest
import setuptools
from distutils.ccompiler import new_compiler


class BaseTest(unittest.TestCase):
    def compile_c_code(self, file_with_c_code):
        compiler = new_compiler()
        filepath = "./aiiocfinder/tests/"
        filename = file_with_c_code
        cfile = filepath + filename + ".c"
        objectfile = filepath + filename + ".o"
        binaryfile = filepath + filename
        compiler.compile([cfile])
        compiler.link_executable([objectfile], binaryfile)
        self.remove_artifacts(objectfile)
        return binaryfile

    def remove_artifacts(self, path_to_file):
        os.remove(path_to_file)

    def assert_system_message(self, system, hist_item):
        self.assertIn("system", hist_item["role"])
        self.assertIn(system, hist_item["content"])

    def assert_user_message(self, user, hist_item):
        self.assertIn("user", hist_item["role"])
        self.assertIn(user, hist_item["content"])

    def load_test_json(self, filename):
        with open(filename, "r") as f:
            programming_model = json.load(f)
        return programming_model
