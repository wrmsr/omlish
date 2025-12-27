from omlish import dataclasses as dc
from omlish import lang

from .standard import StandardContent
from .types import Content


##


@dc.dataclass(frozen=True)
class SectionContent(StandardContent, lang.Final):
    header: str
    body: Content
