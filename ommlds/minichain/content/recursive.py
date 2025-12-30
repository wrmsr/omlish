from omlish import dataclasses as dc
from omlish import lang

from .dynamic import DynamicContent


##


@dc.dataclass(frozen=True)
class RecursiveContent(DynamicContent, lang.Abstract):
    pass
