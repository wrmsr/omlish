from omlish import dataclasses as dc
from omlish import lang

from .content import ExtendedContent


##


@dc.dataclass(frozen=True)
class Placeholder(ExtendedContent, lang.Final):
    k: str
