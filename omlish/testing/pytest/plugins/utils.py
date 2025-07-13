import typing as ta

import pytest


T = ta.TypeVar('T')


##


def find_plugin(pm: pytest.PytestPluginManager, ty: type[T]) -> T | None:
    lst = [p for p in pm.get_plugins() if isinstance(p, ty)]
    if not lst:
        return None
    [ret] = lst
    return ret
