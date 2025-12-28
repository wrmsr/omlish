import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .dynamic import DynamicContent
from .types import LeafContent


##


class ContentPlaceholder(lang.Marker, lang.Abstract):
    pass


PlaceholderContentKey: ta.TypeAlias = str | type[ContentPlaceholder]


@dc.dataclass(frozen=True)
class PlaceholderContent(DynamicContent, LeafContent, lang.Final):
    k: PlaceholderContentKey
