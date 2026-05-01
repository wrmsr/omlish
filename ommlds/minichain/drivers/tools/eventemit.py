from ...chat.messages import ToolUseResultMessage
from ...events.types import EventCallback
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
            on_event: EventCallback,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped
        self._on_event = on_event

    async def execute_tool_use(self, tue: ToolUseExecution) -> ToolUseResultMessage:
        await self._on_event(ToolUseEvent(tue))

        out = await self._wrapped.execute_tool_use(tue)

        await self._on_event(ToolUseResultEvent(tue, out))

        return out
