"""
Sets up logging for maLLMu.
Creates a file log and a console log.
"""

import sys
import logging
import uvicorn

DEFAULT_LOGGING = logging.DEBUG
DEFAULT_LOG_FILE = "mallmu.log"
DEFAULT_LOG_FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(message)s"

logger = logging.getLogger(__name__)

log_sources = [
    "aiiocfinder.aimalanalysis",
    "aiiocfinder.config",
    "aiiocfinder.disassembler",
    "aiiocfinder.openai_handler",
    "aiiocfinder.prompt",
    "aiiocfinder.proxy",
    "aiiocfinder.router",
]


def setup():
    for source in log_sources:
        setup_file_logging(source)
    console_logging()


def setup_file_logging(logger_id):
    logger = logging.getLogger(logger_id)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(DEFAULT_LOGGING)
    file_handler = logging.FileHandler(DEFAULT_LOG_FILE)
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.debug(f"Log setup for {logger_id}")


def console_logging():
    console_formatter = uvicorn.logging.ColourizedFormatter(
        "{levelprefix:<8} @ {name} : {message}", style="{", use_colors=True
    )
    logger = logging.getLogger("uvicorn")
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(console_formatter)
    logger.addHandler(handler)
