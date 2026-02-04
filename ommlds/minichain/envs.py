import typing as ta

from omlish import collections as col
from omlish import lang


##


EnvKey = ta.NewType('EnvKey', str)


class Env(
    # col.FrozenDict[str, ta.Any],
    # RequestContextItem,
    ta.Mapping[str, ta.Any],
    lang.Final,
):
    def __init__(self, *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__(*args, **kwargs)

        self._dct: ta.Mapping[str, ta.Any] = col.frozendict(*args, **kwargs)

    def __getitem__(self, key, /):
        return self._dct[key]

    def __len__(self):
        return len(self._dct)

    def __iter__(self):
        return iter(self._dct)
