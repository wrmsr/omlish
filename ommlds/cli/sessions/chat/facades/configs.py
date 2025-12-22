from omlish import dataclasses as dc

from .commands.configs import CommandsConfig


##


@dc.dataclass(frozen=True, kw_only=True)
class FacadeConfig:
    commands: CommandsConfig = CommandsConfig()
