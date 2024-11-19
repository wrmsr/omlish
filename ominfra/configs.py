# ruff: noqa: UP006 UP007
# @omlish-lite
import json
import typing as ta

from omdev.toml.parser import toml_loads
from omlish.lite.marshal import unmarshal_obj


T = ta.TypeVar('T')


def read_config_file(
        path: str,
        cls: ta.Type[T],
        *,
        prepare: ta.Optional[ta.Callable[[ta.Mapping[str, ta.Any]], ta.Mapping[str, ta.Any]]] = None,
) -> T:
    with open(path) as cf:
        if path.endswith('.toml'):
            config_dct = toml_loads(cf.read())
        else:
            config_dct = json.loads(cf.read())

    if prepare is not None:
        config_dct = prepare(config_dct)  # type: ignore

    return unmarshal_obj(config_dct, cls)
