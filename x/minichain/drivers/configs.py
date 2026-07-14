from omcore import dataclasses as dc

from .ai.configs import AiConfig
from .orm.configs import OrmConfig
from .session.configs import SessionConfig
from .storage.configs import StorageConfig
from .tools.configs import ToolsConfig
from .user.configs import UserConfig


##


@dc.dataclass(frozen=True, kw_only=True)
class DriverConfig:
    ai: AiConfig = AiConfig()
    orm: OrmConfig = OrmConfig()
    session: SessionConfig = SessionConfig()
    storage: StorageConfig = StorageConfig()
    tools: ToolsConfig = ToolsConfig()
    user: UserConfig = UserConfig()
