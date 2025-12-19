from omlish import dataclasses as dc

from ...rendering.configs import RenderingConfig
from .drivers.configs import DriverConfig
from .facades.configs import FacadeConfig
from .interfaces.configs import InterfaceConfig


##


DEFAULT_BACKEND = 'openai'


##


@dc.dataclass(frozen=True, kw_only=True)
class ChatConfig:
    driver: DriverConfig = DriverConfig()
    facade: FacadeConfig = FacadeConfig()
    interface: InterfaceConfig = InterfaceConfig()
    rendering: RenderingConfig = RenderingConfig()
