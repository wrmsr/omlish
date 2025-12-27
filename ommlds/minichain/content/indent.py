from omlish import dataclasses as dc
from omlish import lang

from .types import Content
from .standard import StandardContent


##


@dc.dataclass(frozen=True)
class IndentContent(StandardContent, lang.Final):
    body: Content
