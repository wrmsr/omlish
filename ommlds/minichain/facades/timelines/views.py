from .history import TimelineCursor
from .history import TimelineHistory
from .history import TimelineWindow


##


class TimelineView:
    def __init__(
            self,
            *,
            history: TimelineHistory,
    ) -> None:
        super().__init__()

        self._history = history

    async def get_latest(self, limit: int) -> TimelineWindow:
        return await self._history.get_latest(limit)

    async def get_before(self, cursor: TimelineCursor, limit: int) -> TimelineWindow:
        return await self._history.get_before(cursor, limit)

    async def get_after(self, cursor: TimelineCursor, limit: int) -> TimelineWindow:
        return await self._history.get_after(cursor, limit)
