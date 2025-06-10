import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .content import Content
from .simple import SimpleExtendedContent


##


@dc.dataclass(frozen=True)
class ListContent(SimpleExtendedContent, lang.Final):
    l: ta.Sequence[Content]
