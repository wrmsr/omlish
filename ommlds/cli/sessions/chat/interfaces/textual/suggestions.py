import typing as ta

from omlish import dataclasses as dc

from ...facades.commands.manager import CommandsManager


##


@dc.dataclass(frozen=True)
class SuggestionItem:
    label: str
    description: str | None = None

    _: dc.KW_ONLY

    selected: bool = False


class SuggestionsManager:
    def __init__(
            self,
            *,
            commands_manager: CommandsManager,
    ) -> None:
        super().__init__()

        self._commands_manager = commands_manager

    def get_suggestions(self) -> ta.Sequence[SuggestionItem]:
        return [
            SuggestionItem(f'/{cmd.name}', cmd.description, selected=not i)
            for i, cmd in enumerate(sorted(self._commands_manager.get_commands().values(), key=lambda cmd: cmd.name))
        ]
