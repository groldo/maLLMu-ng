from aiiocfinder.disassembler import Disassambler
from aiiocfinder.tests.basetest import BaseTest
from io import BytesIO


class DisassamblerTest(BaseTest):
    def test_find_strings_with_file(self):
        binaryfile = self.compile_c_code("hello_world")
        dis = Disassambler(binaryfile)
        ret = dis.text_section
        self.assertIn("rax", "".join(ret))
        self.assertIn("mov", "".join(ret))

    def test_find_strings_with_bytes(self):
        binaryfile = self.compile_c_code("hello_world")
        with open(binaryfile, "rb") as f:
            test = f.read()
        f = BytesIO(test)
        dis = Disassambler(f)
        ret = dis.text_section
        self.assertIn("rax", "".join(ret))
        self.assertIn("mov", "".join(ret))

    def test_sections_contains_text(self):
        binaryfile = self.compile_c_code("hello_world")
        dis = Disassambler(binaryfile)
        ret = dis.sections
        self.assertIn(".text", "".join(ret))
        self.assertIn(".plt.got", "".join(ret))

    def test_get_section_contains_code(self):
        binaryfile = self.compile_c_code("hello_world")
        dis = Disassambler(binaryfile)
        ret = dis.get_section(".text")
        self.assertIn("rax", "".join(ret))
        self.assertIn("mov", "".join(ret))

    def test_find_strings_with_code(self):
        binaryfile = self.compile_c_code("hello_world")
        with open(binaryfile, "rb") as f:
            test = f.read()
        f = BytesIO(test)
        dis = Disassambler(f)
        ret = dis.strings
        self.assertIn("Hello, World!", "".join(ret))
