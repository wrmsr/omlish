from omlish import dataclasses as dc

from .backends.configs import BackendConfig
from .chat.ai.configs import AiConfig
from .chat.state.configs import StateConfig
from .chat.user.configs import UserConfig
from .rendering.configs import RenderingConfig
from .tools.configs import ToolsConfig


##


@dc.dataclass(frozen=True, kw_only=True)
class ChatConfig:
    backend: BackendConfig = BackendConfig()
    ai: AiConfig = AiConfig()
    state: StateConfig = StateConfig()
    user: UserConfig = UserConfig()
    rendering: RenderingConfig = RenderingConfig()
    tools: ToolsConfig = ToolsConfig()
