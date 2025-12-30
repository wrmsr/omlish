from omlish import dataclasses as dc
from omlish import lang

from .standard import StandardContent


##


@dc.dataclass(frozen=True)
class CodeContent(StandardContent, lang.Abstract):
    s: str

    _: dc.KW_ONLY

    lang: str | None = None


@dc.dataclass(frozen=True)
class InlineCodeContent(CodeContent, lang.Final):
    pass


@dc.dataclass(frozen=True)
class BlockCodeContent(CodeContent, lang.Final):
    pass
