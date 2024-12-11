# ruff: noqa: UP006 UP007
import dataclasses as dc
import typing as ta

from omlish.lite.check import check
from omlish.lite.logs import log

from ..commands.base import Command
from ..commands.base import CommandExecutor
from .packages import SystemPackage
from .packages import SystemPackageManager


##


@dc.dataclass(frozen=True)
class CheckSystemPackageCommand(Command['CheckSystemPackageCommand.Output']):
    pkgs: ta.Sequence[str] = ()

    def __post_init__(self) -> None:
        check.not_isinstance(self.pkgs, str)

    @dc.dataclass(frozen=True)
    class Output(Command.Output):
        pkgs: ta.Sequence[SystemPackage]


class CheckSystemPackageCommandExecutor(CommandExecutor[CheckSystemPackageCommand, CheckSystemPackageCommand.Output]):
    def __init__(
            self,
            *,
            mgr: SystemPackageManager,
    ) -> None:
        super().__init__()

        self._mgr = mgr

    async def execute(self, cmd: CheckSystemPackageCommand) -> CheckSystemPackageCommand.Output:
        log.info('Checking system package!')

        ret = await self._mgr.query(*cmd.pkgs)

        return CheckSystemPackageCommand.Output(list(ret.values()))
