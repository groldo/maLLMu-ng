import logging

from aiiocfinder.disassembler import Disassambler
from aiiocfinder.aimalanalysis import AIMalAnalysis


class Proxy:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self.disassambler = None
        self._analyst = None
        self._logger.debug(f"Initialized {__name__}")

    def setup(self, api_key, model, max_tokens, temperature, history):
        self._logger.debug("Created new analyst")
        self._analyst = AIMalAnalysis(
            api_key=api_key,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            history=history,
        )

    @property
    def analyst(self):
        if self._analyst:
            self._logger.debug("Returned existing analyst")
            return self._analyst
        raise Exception("No analyst was setup")

    def reset_analyst(self):
        self._analyst = None
        self._logger.debug("Reset analyst")

    def get_disassambler(self, file_object):
        if not self.disassambler:
            self.disassambler = Disassambler(file_object)
        return self.disassambler
