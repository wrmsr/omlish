from omlish import dataclasses as dc
from omlish import lang

from .simple import SimpleExtendedContent


##


@dc.dataclass(frozen=True)
class TextContent(SimpleExtendedContent, lang.Final):
    s: str
