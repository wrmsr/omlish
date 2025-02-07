# ruff: noqa: UP006 UP007
import hashlib
import typing as ta


##


def read_yaml_file(yaml_file: str) -> ta.Any:
    yaml = __import__('yaml')

    with open(yaml_file) as f:
        return yaml.safe_load(f)


##


def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()
