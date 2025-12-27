from omlish import dataclasses as dc
from omlish import lang

from .standard import StandardContent


##


@dc.dataclass(frozen=True)
class TextContent(StandardContent, lang.Final):
    s: str
