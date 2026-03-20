from ...chat.messages import ToolUseResultMessage
from ..events.manager import EventsManager
from .events import ToolUseEvent
from .events import ToolUseResultEvent
from .execution import ToolUseExecution
from .execution import ToolUseExecutor


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

    async def execute_tool_use(self, tue: ToolUseExecution) -> ToolUseResultMessage:
        await self._events.emit_event(ToolUseEvent(tue))

        out = await self._wrapped.execute_tool_use(tue)

        await self._events.emit_event(ToolUseResultEvent(tue, out))

        return out
