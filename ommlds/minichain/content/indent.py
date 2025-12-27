from omlish import dataclasses as dc
from omlish import lang

from .standard import StandardContent
from .types import Content


##


@dc.dataclass(frozen=True)
class IndentContent(StandardContent, lang.Final):
    body: Content
