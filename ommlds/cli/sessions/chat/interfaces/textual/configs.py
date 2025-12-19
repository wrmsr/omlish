from omlish import dataclasses as dc

from ..configs import InterfaceConfig


##


@dc.dataclass(frozen=True, kw_only=True)
class TextualInterfaceConfig(InterfaceConfig):
    pass
