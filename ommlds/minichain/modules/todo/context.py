import typing as ta

from omlish import dataclasses as dc

from ...tools.execution.context import tool_context
from .types import TodoItem


##


def _try_int(s: str | None) -> int | None:
    if s is None:
        return None
    try:
        return int(s)
    except ValueError:
        return None


class TodoContext:
    def __init__(
            self,
            items: ta.Sequence[TodoItem] | None = None,
    ) -> None:
        super().__init__()

        self._items = items
        self._next_id: int = 1

    def get_items(self) -> ta.Sequence[TodoItem] | None:
        return self._items

    def set_items(self, items: ta.Sequence[TodoItem] | None) -> ta.Sequence[TodoItem] | None:
        if items and any(item.id is None for item in items):
            max_id = max([
                *[ii for item in items if (ii := _try_int(item.id)) is not None],
                self._next_id - 1,
            ])
            new_items: list[TodoItem] = []
            for item in items:
                if item.id is None:
                    item = dc.replace(item, id=str(max_id + 1))
                    max_id += 1
                new_items.append(item)
            items = new_items
            self._next_id = max_id + 1

        self._items = list(items) if items is not None else None
        return items


def tool_todo_context() -> TodoContext:
    return tool_context()[TodoContext]
