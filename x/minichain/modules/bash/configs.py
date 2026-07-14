from omlish import dataclasses as dc

from ..configs import ModuleConfig


##


@dc.dataclass(frozen=True, kw_only=True)
class BashConfig(ModuleConfig):
    pass
