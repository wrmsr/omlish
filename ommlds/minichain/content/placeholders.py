import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .recursive import RecursiveContent


##


class ContentPlaceholder(lang.Marker, lang.Abstract):
    pass


PlaceholderContentKey: ta.TypeAlias = str | type[ContentPlaceholder]


@dc.dataclass(frozen=True)
class PlaceholderContent(RecursiveContent, lang.Final):
    k: PlaceholderContentKey
