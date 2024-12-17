# ruff: noqa: UP006 UP007
import dataclasses as dc

from omlish.lite.logs import log

from ..commands.base import Command
from ..commands.base import CommandExecutor
from .deploy import DeployManager
from .specs import DeploySpec


##


@dc.dataclass(frozen=True)
class DeployCommand(Command['DeployCommand.Output']):
    spec: DeploySpec

    @dc.dataclass(frozen=True)
    class Output(Command.Output):
        pass


@dc.dataclass(frozen=True)
class DeployCommandExecutor(CommandExecutor[DeployCommand, DeployCommand.Output]):
    _deploy: DeployManager

    async def execute(self, cmd: DeployCommand) -> DeployCommand.Output:
        log.info('Deploying! %r', cmd.spec)

        await self._deploy.run_deploy(cmd.spec)

        return DeployCommand.Output()
