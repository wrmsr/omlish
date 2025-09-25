import typing as ta

from ...tools.execution.context import tool_context
from .types import TodoItem


##


class TodoToolContext:
    def __init__(
            self,
            items: ta.Sequence[TodoItem] | None = None,
    ) -> None:
        super().__init__()

        self._items = items

    def get_items(self) -> ta.Sequence[TodoItem] | None:
        return self._items

    def set_items(self, items: ta.Sequence[TodoItem] | None) -> None:
        self._items = list(items) if items is not None else None


def todo_tool_context() -> TodoToolContext:
    return tool_context()[TodoToolContext]
