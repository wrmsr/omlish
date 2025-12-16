from omlish import dataclasses as dc

from ....backends.configs import BackendConfig
from .chat.ai.configs import AiConfig
from .chat.state.configs import StateConfig
from .chat.user.configs import UserConfig
from .tools.configs import ToolsConfig


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
