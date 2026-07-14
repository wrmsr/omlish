from omcore import dataclasses as dc

from .... import minichain as mc
from ...backends.configs import BackendConfig
from .state.configs import StateConfig


##


@dc.dataclass(frozen=True, kw_only=True)
class DriverConfig(mc.drivers.DriverConfig):
    backend: BackendConfig = BackendConfig()
    state: StateConfig = StateConfig()
