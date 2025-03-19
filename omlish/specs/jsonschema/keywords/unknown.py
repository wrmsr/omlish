import typing as ta

from .... import dataclasses as dc
from .... import lang
from .base import Keyword


##


@dc.dataclass(frozen=True)
class UnknownKeyword(Keyword, lang.Final):
    tag: str  # type: ignore[misc]
    value: ta.Any
