import logging
import yaml
from yaml.loader import SafeLoader


class Config:
    def __init__(self, config_file):
        self._logger = logging.getLogger(__name__)
        self._config = self.loadYaml(config_file)
        self._logger.debug(f"Initialized {__name__}")

    def loadYaml(self, infile):
        with open(infile) as f:
            config = yaml.load(f, Loader=SafeLoader)
            self._logger.debug(f"Load config file {infile}")
            return config

    @property
    def openaiAccessToken(self):
        return self._config["openai"]["access-token"]
