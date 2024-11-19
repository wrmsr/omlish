# ruff: noqa: UP006 UP007
# @omlish-lite
import json
import typing as ta

from omdev.toml.parser import toml_loads
from omlish.lite.check import check_isinstance
from omlish.lite.check import check_not_isinstance
from omlish.lite.marshal import unmarshal_obj


T = ta.TypeVar('T')

ConfigMapping = ta.Mapping[str, ta.Any]


def read_config_file(
        path: str,
        cls: ta.Type[T],
        *,
        prepare: ta.Optional[ta.Callable[[ConfigMapping], ConfigMapping]] = None,
) -> T:
    with open(path) as cf:
        if path.endswith('.toml'):
            config_dct = toml_loads(cf.read())
        else:
            config_dct = json.loads(cf.read())

    if prepare is not None:
        config_dct = prepare(config_dct)  # type: ignore

    return unmarshal_obj(config_dct, cls)


def build_config_named_children(
        o: ta.Union[
            ta.Sequence[ConfigMapping],
            ta.Mapping[str, ConfigMapping],
            None,
        ],
        *,
        name_key: str = 'name',
) -> ta.Optional[ta.Sequence[ConfigMapping]]:
    if o is None:
        return None

    lst: ta.List[ConfigMapping] = []
    if isinstance(o, ta.Mapping):
        for k, v in o.items():
            check_isinstance(v, ta.Mapping)
            if name_key in v:
                n = v[name_key]
                if k != n:
                    raise KeyError(f'Given names do not match: {n} != {k}')
                lst.append(v)
            else:
                lst.append({name_key: k, **v})

    else:
        check_not_isinstance(o, str)
        lst.extend(o)

    seen = set()
    for d in lst:
        n = d['name']
        if n in d:
            raise KeyError(f'Duplicate name: {n}')
        seen.add(n)

    return lst
