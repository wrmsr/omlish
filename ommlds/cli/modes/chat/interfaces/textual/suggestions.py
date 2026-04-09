import itertools
import typing as ta

from omlish import dataclasses as dc

from ...... import minichain as mc


##


@dc.dataclass(frozen=True)
class SuggestionItem:
    label: str
    description: str | None = None

    _: dc.KW_ONLY

    selected: bool = False


class SuggestionsManager:
    @dc.dataclass(frozen=True)
    class Config:
        max_items: int = 10

    def __init__(
            self,
            config: Config = Config(),
            *,
            commands_manager: mc.facades.CommandsManager,
    ) -> None:
        super().__init__()

        self._config = config
        self._commands_manager = commands_manager

        self._suggestions: list[SuggestionItem] | None = None
        self._selected_index: int | None = None

    @property
    def is_cycling(self) -> bool:
        return self._selected_index is not None

    def end_cycling(self) -> None:
        self._selected_index = None

    def clear_suggestions(self) -> None:
        self._suggestions = None
        self._selected_index = None

    def get_suggestions(self) -> ta.Sequence[SuggestionItem] | None:
        return self._suggestions

    def select_next(self) -> SuggestionItem | None:
        if not self._suggestions:
            return None

        if self._selected_index is None:
            self._selected_index = 0
        else:
            self._selected_index = (self._selected_index + 1) % len(self._suggestions)

        self._suggestions = [
            dc.replace(si, selected=(i == self._selected_index))
            for i, si in enumerate(self._suggestions)
        ]

        return self._suggestions[self._selected_index]

    def update_suggestions(self, prefix: str = '') -> ta.Sequence[SuggestionItem]:
        self._selected_index = None

        if prefix.startswith('/'):
            pfx_cmds = list(itertools.islice((
                cmd
                for cmd in sorted(self._commands_manager.get_commands().values(), key=lambda cmd: cmd.name)
                if cmd.name.startswith(prefix[1:])
            ), self._config.max_items))

            self._suggestions = [
                SuggestionItem(f'/{cmd.name}', cmd.description)
                for cmd in pfx_cmds
            ]

        else:
            self._suggestions = []

        return self._suggestions
