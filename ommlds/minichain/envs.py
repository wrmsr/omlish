import typing as ta

from omlish import collections as col
from omlish import lang


##


EnvKey = ta.NewType('EnvKey', str)


class Env(
    col.FrozenDict[str, ta.Any],
    # RequestContextItem,
    lang.Final,
):
    pass
