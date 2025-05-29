import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


Token: ta.TypeAlias = int


@dc.dataclass(frozen=True)
class Tokens(lang.Final):
    l: ta.Sequence[Token]
