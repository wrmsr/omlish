import typing as ta

from ..events.manager import EventsManager
from ...chat.messages import ToolUseResultMessage
from .execution import ToolUseExecutor
from ...tools.types import ToolUse
from ..events.types import ToolUseEvent
from ..events.types import ToolUseResultEvent


##


class EventEmittingToolUseExecutor(ToolUseExecutor):
    def __init__(
            self,
            *,
            wrapped: ToolUseExecutor,
            events: EventsManager,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped
        self._events = events

    async def execute_tool_use(
            self,
            use: ToolUse,
            *ctx_items: ta.Any,
    ) -> ToolUseResultMessage:
        await self._events.emit_event(ToolUseEvent(use))

        out = await self._wrapped.execute_tool_use(use, *ctx_items)

        await self._events.emit_event(ToolUseResultEvent(out))

        return out
