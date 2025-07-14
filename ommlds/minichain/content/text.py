from omlish import dataclasses as dc
from omlish import lang

from .simple import SimpleSingleExtendedContent


##


@dc.dataclass(frozen=True)
class TextContent(SimpleSingleExtendedContent, lang.Final):
    s: str
