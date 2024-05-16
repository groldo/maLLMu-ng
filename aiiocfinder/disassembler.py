import io
import re
import logging
from capstone import Cs, CS_ARCH_X86, CS_MODE_64, CsError
from elftools.elf.elffile import ELFFile


class Disassambler:
    def __init__(self, binary):
        self._logger = logging.getLogger(__name__)
        self.assembly = {}
        self.strings = []
        if not isinstance(binary, io.BytesIO):
            binary_bytes = self._openfile(binary)
        else:
            binary_bytes = binary
        self._find_strings(binary_bytes)
        self._disassemble(binary_bytes)
        self._logger.debug(f"Initialized {__name__}")

    @staticmethod
    def _openfile(binary):
        with open(binary, "rb") as f:
            binary_bytes = io.BytesIO(f.read())
        return binary_bytes

    def _disassemble(self, binary_bytes):
        elf = ELFFile(binary_bytes)
        self.assembly = {section.name: [] for section in elf.iter_sections()}
        for dict in self.assembly.keys():
            code = elf.get_section_by_name(dict)
            ops = code.data()
            addr = code["sh_addr"]
            inst_list = []
            try:
                md = Cs(CS_ARCH_X86, CS_MODE_64)
                # iterate over each instruction and print it
                for instruc in md.disasm(ops, addr):
                    instruc_str = (
                        f"0x{instruc.address:x}:\t{instruc.mnemonic}\t{instruc.op_str}"
                    )
                    inst_list.append(instruc_str)
            except CsError as e:
                self._logger.error("Capstone Error: %s" % e)
            self.assembly[dict] = inst_list
            self._logger.debug(
                f"Disassambled {len(inst_list)} instructions from section {dict}"
            )

    def get_section(self, section_name):
        return self.assembly[section_name]

    def _find_strings(self, binary_bytes, min_length=4):
        pattern = rb"[\x20-\x7E]{" + str(min_length).encode() + rb",}"
        strings = re.findall(pattern, binary_bytes.read())
        self.strings = [s.decode("utf-8") for s in strings]

    @property
    def text_section(self):
        return self.assembly[".text"]

    @property
    def sections(self):
        return self.assembly.keys()
