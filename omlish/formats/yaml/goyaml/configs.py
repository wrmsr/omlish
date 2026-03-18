import typing as ta

from ....configs.formats import DEFAULT_YAML_CONFIG_BACKEND
from ....configs.formats import PyyamlYamlConfigBackend
from ....configs.formats import YamlConfigBackend
from ....lite.json import json_dumps_pretty
from .decoding import yaml_decode


##


class GoyamlYamlConfigBackend(YamlConfigBackend):
    def loads(self, s: str) -> ta.Any:
        return yaml_decode(s)

    def dumps(self, o: ta.Any) -> str:
        return json_dumps_pretty()

    @classmethod
    def set_as_default(cls) -> None:
        DEFAULT_YAML_CONFIG_BACKEND.INSTANCE = cls()


class PyyamlOrGoyamlYamlConfigBackend(GoyamlYamlConfigBackend):
    def loads(self, s: str) -> ta.Any:
        try:
            return PyyamlYamlConfigBackend().loads(s)
        except ImportError:
            return super().loads(s)

    def dumps(self, o: ta.Any) -> str:
        try:
            return PyyamlYamlConfigBackend().dumps(o)
        except ImportError:
            return super().dumps(o)
