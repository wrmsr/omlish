from .types import Commands


##


class CommandsManager:
    def __init__(
            self,
            *,
            commands: Commands,
    ) -> None:
        super().__init__()

        self._commands = commands
