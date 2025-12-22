import enum
import shlex

from omlish import collections as col

from ..ui import UiMessageDisplayer
from .base import Command
from .types import Commands


##


class RunCommandResult(enum.StrEnum):
    SUCCESS = 'success'
    FAILURE = 'failure'


class CommandsManager:
    def __init__(
            self,
            *,
            commands: Commands,
            ui_message_displayer: UiMessageDisplayer,
    ) -> None:
        super().__init__()

        self._commands = commands
        self._ui_message_displayer = ui_message_displayer

        self._commands_by_name = col.make_map((
            (c.name, c) for c in commands
        ), strict=True)

    async def run_command_text(self, text: str) -> RunCommandResult:
        try:
            parts = shlex.split(text)
        except ValueError as e:
            await self._ui_message_displayer.display_ui_message(f'Invalid command syntax: {e}')
            return RunCommandResult.FAILURE

        if not parts:
            return RunCommandResult.FAILURE

        cmd = parts[0].lstrip('/').lower()
        argv = parts[1:]

        command = self._commands_by_name.get(cmd)
        if not command:
            await self._ui_message_displayer.display_ui_message(f'Unknown command: {cmd}')
            return RunCommandResult.FAILURE

        ctx = Command.Context(
            print=self._ui_message_displayer.display_ui_message,
        )

        await command.run(ctx, argv)

        return RunCommandResult.SUCCESS
