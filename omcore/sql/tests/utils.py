import typing as ta

import pytest


T = ta.TypeVar('T')


SqlBackend: ta.TypeAlias = ta.Literal[
    'mysql',
    'postgres',
]


##


def mark_sql_backend(backend: SqlBackend) -> ta.Callable[[T], T]:
    def inner(obj):
        pytest.mark.xdist_group(backend)(obj)
        return obj

    return inner
