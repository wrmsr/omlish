# ruff: noqa: UP006 UP007
import dataclasses as dc

from omlish.lite.logs import log

from ..commands.base import Command
from ..commands.base import CommandExecutor


##


@dc.dataclass(frozen=True)
class CheckSystemPackageCommand(Command['CheckSystemPackageCommand.Output']):
    @dc.dataclass(frozen=True)
    class Output(Command.Output):
        pass


class CheckSystemPackageCommandExecutor(CommandExecutor[CheckSystemPackageCommand, CheckSystemPackageCommand.Output]):
    async def execute(self, cmd: CheckSystemPackageCommand) -> CheckSystemPackageCommand.Output:
        log.info('Checking system package!')

        return CheckSystemPackageCommand.Output()
