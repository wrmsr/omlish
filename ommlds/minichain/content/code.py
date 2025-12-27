from omlish import dataclasses as dc
from omlish import lang

from .standard import StandardContent
from .types import LeafContent


##


@dc.dataclass(frozen=True)
class CodeContent(StandardContent, LeafContent, lang.Final):
    s: str

    _: dc.KW_ONLY

    lang: str | None = None
