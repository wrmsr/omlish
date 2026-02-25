# ruff: noqa: UP006 UP007 UP045
import hashlib
import typing as ta

from omlish.formats.yaml.goyaml.decoding import yaml_decode


##


def read_yaml_file(yaml_file: str) -> ta.Any:
    with open(yaml_file) as f:
        return yaml_decode(f.read())


##


def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()
