from omlish import dataclasses as dc

from ...rendering.configs import RenderingConfig
from .agents.configs import AgentConfig
from .interfaces.configs import InterfaceConfig


##


DEFAULT_BACKEND = 'openai'


##


@dc.dataclass(frozen=True, kw_only=True)
class ChatConfig:
    agent: AgentConfig = AgentConfig()
    interface: InterfaceConfig = InterfaceConfig()
    rendering: RenderingConfig = RenderingConfig()
