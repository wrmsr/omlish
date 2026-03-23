from omlish import dataclasses as dc

from ...interfaces.bare.printing.configs import PrintingConfig
from ..configs import ModeConfig
from .drivers.configs import DriverConfig
from .facades.configs import FacadeConfig
from .interfaces.bare.configs import BareInterfaceConfig
from .interfaces.configs import InterfaceConfig


##


@dc.dataclass(frozen=True, kw_only=True)
class ChatConfig(ModeConfig):
    driver: DriverConfig = DriverConfig()
    facade: FacadeConfig = FacadeConfig()
    interface: InterfaceConfig = BareInterfaceConfig()
    printing: PrintingConfig = PrintingConfig()
