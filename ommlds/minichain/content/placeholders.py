from omlish import dataclasses as dc
from omlish import lang

from .dynamic import DynamicContent
from .types import LeafContent


##


class ContentPlaceholder(lang.Marker):
    pass


@dc.dataclass(frozen=True)
class PlaceholderContent(DynamicContent, LeafContent, lang.Final):
    ph: str | type[ContentPlaceholder]
