# ruff: noqa: TC003 UP006 UP007
import dataclasses as dc
import time

from .base import Command
from .base import CommandExecutor


##


@dc.dataclass(frozen=True)
class PingCommand(Command['PingCommand.Output']):
    time: float = dc.field(default_factory=time.time)

    @dc.dataclass(frozen=True)
    class Output(Command.Output):
        time: float


class PingCommandExecutor(CommandExecutor[PingCommand, PingCommand.Output]):
    async def execute(self, cmd: PingCommand) -> PingCommand.Output:
        return PingCommand.Output(cmd.time)
