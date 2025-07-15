import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .simple import SimpleExtendedContent
from .types import Content


##


@dc.dataclass(frozen=True)
class ListContent(SimpleExtendedContent, lang.Final):
    l: ta.Sequence[Content]
