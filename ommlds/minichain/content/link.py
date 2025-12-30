from omlish import dataclasses as dc
from omlish import lang

from .standard import StandardContent


##


@dc.dataclass(frozen=True)
class LinkContent(StandardContent, lang.Final):
    url: str
    title: str | None = None
