# ruff: noqa: UP006 UP007
import dataclasses as dc

from omlish.lite.logs import log

from ..commands.base import Command
from ..commands.base import CommandExecutor
from .apps import DeployAppManager
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
    _apps: DeployAppManager

    async def execute(self, cmd: DeployCommand) -> DeployCommand.Output:
        log.info('Deploying! %r', cmd.spec)

        await self._apps.prepare_app(cmd.spec)

        return DeployCommand.Output()
