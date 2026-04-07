from omlish import dataclasses as dc

from ..... import minichain as mc
from ....backends.configs import BackendConfig
from .state.configs import StateConfig


##


DEFAULT_BACKEND = 'openai'


##


@dc.dataclass(frozen=True, kw_only=True)
class DriverConfig(mc.drivers.DriverConfig):
    state: StateConfig = StateConfig()

    backend: BackendConfig = BackendConfig()

    print_ai_responses: bool = False
    print_tool_use: bool = False
