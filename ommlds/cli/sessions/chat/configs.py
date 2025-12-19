from omlish import dataclasses as dc

from ...rendering.configs import RenderingConfig
from .drivers.configs import DriverConfig
from .facades.configs import FacadeConfig
from .interfaces.bare.configs import BareInterfaceConfig
from .interfaces.configs import InterfaceConfig


##


@dc.dataclass(frozen=True, kw_only=True)
class ChatConfig:
    driver: DriverConfig = DriverConfig()
    facade: FacadeConfig = FacadeConfig()
    interface: InterfaceConfig = BareInterfaceConfig()
    rendering: RenderingConfig = RenderingConfig()
