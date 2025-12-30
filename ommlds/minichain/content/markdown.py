from omlish import dataclasses as dc
from omlish import lang

from .standard import StandardContent
from .types import LeafContent


##


@dc.dataclass(frozen=True)
class MarkdownContent(StandardContent, LeafContent, lang.Final):
    s: str
