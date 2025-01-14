# ruff: noqa: UP006 UP007
# @omlish-lite
import hashlib
import os.path
import tempfile
import typing as ta


##


def make_temp_file() -> str:
    file_fd, file = tempfile.mkstemp()
    os.close(file_fd)
    return file


##


def read_yaml_file(yaml_file: str) -> ta.Any:
    yaml = __import__('yaml')

    with open(yaml_file) as f:
        return yaml.safe_load(f)


##


def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()
