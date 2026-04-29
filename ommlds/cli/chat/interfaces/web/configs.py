from omlish import dataclasses as dc

from ..configs import InterfaceConfig


##


DEFAULT_PORT = 8087


@dc.dataclass(frozen=True, kw_only=True)
class WebInterfaceConfig(InterfaceConfig):
    port: int = DEFAULT_PORT
