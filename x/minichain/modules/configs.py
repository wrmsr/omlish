from omcore import dataclasses as dc
from omcore import lang


##


@dc.dataclass(frozen=True, kw_only=True)
class ModuleConfig(lang.Abstract):
    pass
