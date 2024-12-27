# ruff: noqa: UP006 UP007
# @omlish-lite
"""
usecase: supervisor process groups
"""
import typing as ta

from ...lite.check import check
from ..types import ConfigMap


##


def build_config_named_children(
        o: ta.Union[
            ta.Sequence[ConfigMap],
            ta.Mapping[str, ConfigMap],
            None,
        ],
        *,
        name_key: str = 'name',
) -> ta.Optional[ta.Sequence[ConfigMap]]:
    if o is None:
        return None

    lst: ta.List[ConfigMap] = []
    if isinstance(o, ta.Mapping):
        for k, v in o.items():
            check.isinstance(v, ta.Mapping)
            if name_key in v:
                n = v[name_key]
                if k != n:
                    raise KeyError(f'Given names do not match: {n} != {k}')
                lst.append(v)
            else:
                lst.append({name_key: k, **v})

    else:
        check.not_isinstance(o, str)
        lst.extend(o)

    seen = set()
    for d in lst:
        n = d['name']
        if n in d:
            raise KeyError(f'Duplicate name: {n}')
        seen.add(n)

    return lst
