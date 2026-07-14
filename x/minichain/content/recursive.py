from omcore import dataclasses as dc
from omcore import lang

from .dynamic import DynamicContent


##


@dc.dataclass(frozen=True)
class RecursiveContent(DynamicContent, lang.Abstract):
    pass
