import typing as ta

from omlish import check
from omlish import dataclasses as dc

from .items import TimelineItem
from .items import TimelineItemId
from .state import TimelineState


##


@dc.dataclass(frozen=True)
class TimelineCursor:
    item_id: TimelineItemId
    ordinal: int


@dc.dataclass(frozen=True, kw_only=True)
class TimelineWindow:
    items: tuple[TimelineItem, ...]

    has_before: bool = False
    has_after: bool = False

    before_cursor: TimelineCursor | None = None
    after_cursor: TimelineCursor | None = None


class TimelineView:
    def __init__(
            self,
            *,
            state: TimelineState,
    ) -> None:
        super().__init__()

        self._state = state

    def _make_window(
            self,
            *,
            start: int,
            stop: int,
    ) -> TimelineWindow:
        all_items = self._state.get_items()

        start = max(start, 0)
        stop = min(stop, len(all_items))
        check.arg(start <= stop)

        items = tuple(all_items[start:stop])

        before_cursor: TimelineCursor | None = None
        after_cursor: TimelineCursor | None = None

        if items:
            before_cursor = TimelineCursor(items[0].id, start)
            after_cursor = TimelineCursor(items[-1].id, stop - 1)

        return TimelineWindow(
            items=items,
            has_before=start > 0,
            has_after=stop < len(all_items),
            before_cursor=before_cursor,
            after_cursor=after_cursor,
        )

    async def get_latest(self, limit: int) -> TimelineWindow:
        check.arg(limit >= 0)

        stop = len(self._state)
        start = max(stop - limit, 0)

        return self._make_window(
            start=start,
            stop=stop,
        )

    async def get_before(self, cursor: TimelineCursor, limit: int) -> TimelineWindow:
        check.arg(limit >= 0)

        ordinal = self._resolve_cursor(cursor)
        stop = ordinal
        start = max(stop - limit, 0)

        return self._make_window(
            start=start,
            stop=stop,
        )

    async def get_after(self, cursor: TimelineCursor, limit: int) -> TimelineWindow:
        check.arg(limit >= 0)

        ordinal = self._resolve_cursor(cursor)
        start = ordinal + 1
        stop = min(start + limit, len(self._state))

        return self._make_window(
            start=start,
            stop=stop,
        )

    def _resolve_cursor(self, cursor: TimelineCursor) -> int:
        if (item := self._state.get_item_by_ordinal(cursor.ordinal)) is not None and item.id == cursor.item_id:
            return cursor.ordinal

        return check.not_none(self._state.get_item_ordinal(cursor.item_id))

    async def get_items(self) -> ta.Sequence[TimelineItem]:
        return self._state.get_items()
