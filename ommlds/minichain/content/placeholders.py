import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .content import LeafContent
from .dynamic import DynamicContent


##


class ContentPlaceholder(lang.Marker, lang.Abstract):
    pass


PlaceholderContentKey: ta.TypeAlias = str | type[ContentPlaceholder]


@dc.dataclass(frozen=True)
class PlaceholderContent(DynamicContent, LeafContent, lang.Final):
    k: PlaceholderContentKey
