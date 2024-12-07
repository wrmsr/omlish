# ruff: noqa: UP006 UP007
import dataclasses as dc

from ..commands.base import Command
from ..commands.base import CommandExecutor


##


@dc.dataclass(frozen=True)
class DeployCommand(Command['DeployCommand.Output']):
    @dc.dataclass(frozen=True)
    class Output(Command.Output):
        pass


##


class DeployCommandExecutor(CommandExecutor[DeployCommand, DeployCommand.Output]):
    def execute(self, cmd: DeployCommand) -> DeployCommand.Output:
        return DeployCommand.Output()
