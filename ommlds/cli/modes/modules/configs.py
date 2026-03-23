from omlish import dataclasses as dc
from omlish import lang


##


@dc.dataclass(frozen=True, kw_only=True)
class ModuleConfig(lang.Abstract):
    pass
