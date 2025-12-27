from omlish import dataclasses as dc
from omlish import lang

from .standard import StandardContent
from .types import Content


##


@dc.dataclass(frozen=True)
class CodeContent(StandardContent, lang.Final):
    body: Content

    _: dc.KW_ONLY

    lang: str | None = None
