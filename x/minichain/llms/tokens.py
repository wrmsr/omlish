import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##
# FIXME: clashes with mc.tokens lol


Token: ta.TypeAlias = int


@dc.dataclass(frozen=True)
class Tokens(lang.Final):
    l: ta.Sequence[Token]


##


@dc.dataclass(frozen=True)
class TokenUsage(lang.Final):
    input: int
    output: int
    total: int
