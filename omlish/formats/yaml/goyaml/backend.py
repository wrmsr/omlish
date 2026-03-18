# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import typing as ta

from ....lite.json import json_dumps_pretty
from ..backends import YamlBackend
from .decoding import yaml_decode


##


class GoyamlYamlBackend(YamlBackend):
    def is_available(self) -> bool:
        return True

    def loads(self, s: str) -> ta.Any:
        return yaml_decode(s)

    def dumps(self, o: ta.Any) -> str:
        return json_dumps_pretty(o)
