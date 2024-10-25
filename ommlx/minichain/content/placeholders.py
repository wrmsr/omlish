import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .content import ExtendedContent


##


EnvKey = ta.NewType('EnvKey', str)


# class Env(col.FrozenDict[str, str], RequestContextItem, lang.Final):
#     pass


##


@dc.dataclass(frozen=True)
class Placeholder(ExtendedContent, lang.Final):
    k: EnvKey
