# ruff: noqa: UP006 UP007
import dataclasses as dc

from omdev.interp.default import get_default_interp_resolver
from omdev.interp.types import InterpOpts
from omdev.interp.types import InterpSpecifier
from omlish.lite.check import check

from ..commands.base import Command
from ..commands.base import CommandExecutor


##


@dc.dataclass(frozen=True)
class InterpCommand(Command['InterpCommand.Output']):
    spec: str
    install: bool = False

    @dc.dataclass(frozen=True)
    class Output(Command.Output):
        exe: str
        version: str
        opts: InterpOpts


class InterpCommandExecutor(CommandExecutor[InterpCommand, InterpCommand.Output]):
    async def execute(self, cmd: InterpCommand) -> InterpCommand.Output:
        i = InterpSpecifier.parse(check.not_none(cmd.spec))
        o = check.not_none(await get_default_interp_resolver().resolve(i, install=cmd.install))
        return InterpCommand.Output(
            exe=o.exe,
            version=str(o.version.version),
            opts=o.version.opts,
        )
