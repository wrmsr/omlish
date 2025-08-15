# ruff: noqa: UP006 UP007 UP045
import hashlib
import typing as ta


##


def read_yaml_file(yaml_file: str) -> ta.Any:
    import yaml  # noqa

    with open(yaml_file) as f:
        return yaml.safe_load(f)


##


def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()
