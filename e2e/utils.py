import yaml
import json
import setuptools
from distutils.ccompiler import new_compiler
import subprocess
import datetime
import logging
import logging
import os
import os.path

DEFAULT_LOGGING = logging.DEBUG
DEFAULT_LOG_FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(message)s"

_logger = logging.getLogger(__name__)


def setup_log(log_source, filename):
    for log_base in log_source:
        setup_logging(log_base, filename)


def setup_logging(logger_id, filename):
    logger = logging.getLogger(logger_id)
    logger.setLevel(DEFAULT_LOGGING)
    file_handler = logging.FileHandler(filename)
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def compile_c_code(file_with_c_code):
    compiler = new_compiler()
    filepath = "./tests/"
    filename = file_with_c_code
    cfile = filepath + filename + ".c"
    objectfile = filepath + filename + ".o"
    binaryfile = filepath + filename
    compiler.compile([cfile])
    compiler.link_executable([objectfile], binaryfile)
    return binaryfile


def now_in_isoformat_wo_ms(dateformat):
    now = datetime.datetime.now()
    return str(now.strftime(dateformat))


def compile_c_code(c_file, output):
    filepath = "./e2e/"
    compile_command = f"gcc {filepath}/{c_file} -o {filepath}/{output}"
    result = subprocess.run(
        compile_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if result.returncode == 0:
        _logger.debug(f"Compiled to {output}")
    else:
        _logger.debug(f"Compile error {result.stderr.decode()}")


def load_test_json(filename):
    with open(filename, "r") as f:
        programming_model = json.load(f)
    return programming_model


def loadYaml(infile):
    with open(infile) as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
        return config


def get_files_in_dir(root_dir):
    files = [
        os.path.join(root_dir, f)
        for f in os.listdir(root_dir)
        if os.path.isfile(os.path.join(root_dir, f))
    ]
    return files
