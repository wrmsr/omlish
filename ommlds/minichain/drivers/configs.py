from omlish import dataclasses as dc

from .ai.configs import AiConfig
from .orm.configs import OrmConfig
from .session.configs import SessionConfig
from .state.configs import StateConfig
from .tools.configs import ToolsConfig
from .user.configs import UserConfig


##


@dc.dataclass(frozen=True, kw_only=True)
class DriverConfig:
    ai: AiConfig = AiConfig()
    orm: OrmConfig = OrmConfig()
    session: SessionConfig = SessionConfig()
    state: StateConfig = StateConfig()
    tools: ToolsConfig = ToolsConfig()
    user: UserConfig = UserConfig()
