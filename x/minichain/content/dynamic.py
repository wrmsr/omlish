from omcore import dataclasses as dc
from omcore import lang

from .standard import StandardContent


##


@dc.dataclass(frozen=True)
class DynamicContent(StandardContent, lang.Abstract):
    pass
