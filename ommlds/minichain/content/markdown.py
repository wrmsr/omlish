from omlish import dataclasses as dc
from omlish import lang

from .content import LeafContent
from .standard import StandardContent


##


@dc.dataclass(frozen=True)
class MarkdownContent(StandardContent, LeafContent, lang.Final):
    s: str
