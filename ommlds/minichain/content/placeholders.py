from omlish import dataclasses as dc
from omlish import lang

from .dynamic import DynamicContent


##


class ContentPlaceholder(lang.Marker):
    pass


@dc.dataclass(frozen=True)
class PlaceholderContent(DynamicContent, lang.Final):
    ph: str | type[ContentPlaceholder]
