from omcore import dataclasses as dc

from ... import minichain as mc
from ..configs import EntrypointConfig
from ..interfaces.bare.printing.configs import PrintingConfig
from .drivers.configs import DriverConfig
from .interfaces.bare.configs import BareInterfaceConfig
from .interfaces.configs import InterfaceConfig


##


@dc.dataclass(frozen=True, kw_only=True)
class ChatConfig(EntrypointConfig):
    driver: DriverConfig = DriverConfig()
    facade: mc.facades.FacadeConfig = mc.facades.FacadeConfig()
    interface: InterfaceConfig = BareInterfaceConfig()
    printing: PrintingConfig = PrintingConfig()
