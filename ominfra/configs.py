# ruff: noqa: UP006
# @omlish-lite
import json
import typing as ta

from omdev.toml.parser import toml_loads
from omlish.lite.marshal import unmarshal_obj


T = ta.TypeVar('T')


def read_config_file(path: str, cls: ta.Type[T]) -> T:
    with open(path) as cf:
        if path.endswith('.toml'):
            config_dct = toml_loads(cf.read())
        else:
            config_dct = json.loads(cf.read())
    return unmarshal_obj(config_dct, cls)
