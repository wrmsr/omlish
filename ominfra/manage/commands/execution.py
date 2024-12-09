# ruff: noqa: UP006 UP007
import typing as ta

from .base import Command
from .base import CommandExecutor


CommandExecutorMap = ta.NewType('CommandExecutorMap', ta.Mapping[ta.Type[Command], CommandExecutor])


class LocalCommandExecutor(CommandExecutor):
    def __init__(
            self,
            *,
            command_executors: CommandExecutorMap,
    ) -> None:
        super().__init__()

        self._command_executors = command_executors

    async def execute(self, cmd: Command) -> Command.Output:
        ce: CommandExecutor = self._command_executors[type(cmd)]
        return await ce.execute(cmd)
