from omlish import dataclasses as dc

from ....backends.configs import BackendConfig
from .ai.configs import AiConfig
from .state.configs import StateConfig
from .tools.configs import ToolsConfig
from .user.configs import UserConfig


##


DEFAULT_BACKEND = 'openai'


##


@dc.dataclass(frozen=True, kw_only=True)
class DriverConfig:
    backend: BackendConfig = BackendConfig()
    ai: AiConfig = AiConfig()
    state: StateConfig = StateConfig()
    user: UserConfig = UserConfig()
    tools: ToolsConfig = ToolsConfig()
