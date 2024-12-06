from .base import Command
from .base import CommandExecutor
from .base import CommandExecutorRegistrations
from .base import CommandRegistrations


class CommandExecutionService(CommandExecutor):
    def __init__(
            self,
            *,
            command_registrations: CommandRegistrations,
            command_executor_registrations: CommandExecutorRegistrations,
    ) -> None:
        super().__init__()

        self._command_registrations = command_registrations
        self._command_executor_registrations = command_executor_registrations

    def execute(self, i: Command) -> Command.Output:
        raise NotImplementedError
