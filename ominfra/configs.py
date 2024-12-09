# ruff: noqa: UP006 UP007
# @omlish-lite
import json
import os.path
import typing as ta

from omdev.toml.parser import toml_loads
from omlish.lite.check import check_isinstance
from omlish.lite.check import check_not_isinstance
from omlish.lite.marshal import unmarshal_obj


T = ta.TypeVar('T')

ConfigMapping = ta.Mapping[str, ta.Any]


def parse_config_file(
        name: str,
        f: ta.TextIO,
) -> ConfigMapping:
    if name.endswith('.toml'):
        return toml_loads(f.read())

    elif any(name.endswith(e) for e in ('.yml', '.yaml')):
        yaml = __import__('yaml')
        return yaml.safe_load(f)

    elif name.endswith('.ini'):
        import configparser
        cp = configparser.ConfigParser()
        cp.read_file(f)
        config_dct: ta.Dict[str, ta.Any] = {}
        for sec in cp.sections():
            cd = config_dct
            for k in sec.split('.'):
                cd = cd.setdefault(k, {})
            cd.update(cp.items(sec))
        return config_dct

    else:
        return json.loads(f.read())


def read_config_file(
        path: str,
        cls: ta.Type[T],
        *,
        prepare: ta.Optional[ta.Callable[[ConfigMapping], ConfigMapping]] = None,
) -> T:
    with open(path) as cf:
        config_dct = parse_config_file(os.path.basename(path), cf)

    if prepare is not None:
        config_dct = prepare(config_dct)

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
