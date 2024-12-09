# ruff: noqa: UP006 UP007
import dataclasses as dc

from omlish.lite.logs import log

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
    async def execute(self, cmd: DeployCommand) -> DeployCommand.Output:
        log.info('Deploying!')

        return DeployCommand.Output()
