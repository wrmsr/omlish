import abc
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from ...drivers.storage.manager import DriverStorageManager
from ...drivers.storage.types import ChatPage
from .items import TimelineItem
from .items import TimelineItemId
from .messages import timeline_item_from_message
from .state import TimelineState


##


@dc.dataclass(frozen=True)
class TimelineCursor:
    item_id: TimelineItemId
    position: int


@dc.dataclass(frozen=True, kw_only=True)
class TimelineWindow:
    items: ta.Sequence[TimelineItem]

    has_before: bool = False
    has_after: bool = False

    before_cursor: TimelineCursor | None = None
    after_cursor: TimelineCursor | None = None


##


class TimelineHistory(lang.Abstract):
    @abc.abstractmethod
    async def get_latest(self, limit: int) -> TimelineWindow:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_before(self, cursor: TimelineCursor, limit: int) -> TimelineWindow:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_after(self, cursor: TimelineCursor, limit: int) -> TimelineWindow:
        raise NotImplementedError


#


class StateTimelineHistory(TimelineHistory):
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

        position = self._resolve_cursor(cursor)
        stop = position
        start = max(stop - limit, 0)

        return self._make_window(
            start=start,
            stop=stop,
        )

    async def get_after(self, cursor: TimelineCursor, limit: int) -> TimelineWindow:
        check.arg(limit >= 0)

        position = self._resolve_cursor(cursor)
        start = position + 1
        stop = min(start + limit, len(self._state))

        return self._make_window(
            start=start,
            stop=stop,
        )

    def _resolve_cursor(self, cursor: TimelineCursor) -> int:
        if (item := self._state.get_item_by_ordinal(cursor.position)) is not None and item.id == cursor.item_id:
            return cursor.position

        return check.not_none(self._state.get_item_ordinal(cursor.item_id))


#


class StorageTimelineHistory(TimelineHistory):
    def __init__(
            self,
            *,
            storage: DriverStorageManager,
    ) -> None:
        super().__init__()

        self._storage = storage

    @staticmethod
    def _page_to_window(page: ChatPage) -> TimelineWindow:
        items = tuple(
            timeline_item_from_message(message)
            for message in page.messages
        )

        before_cursor: TimelineCursor | None = None
        after_cursor: TimelineCursor | None = None

        if items:
            if page.before_seq is not None:
                before_cursor = TimelineCursor(items[0].id, page.before_seq)

            if page.after_seq is not None:
                after_cursor = TimelineCursor(items[-1].id, page.after_seq)

        return TimelineWindow(
            items=items,
            has_before=page.has_before,
            has_after=page.has_after,
            before_cursor=before_cursor,
            after_cursor=after_cursor,
        )

    async def get_latest(self, limit: int) -> TimelineWindow:
        return self._page_to_window(await self._storage.get_latest_chat_page(limit))

    async def get_before(self, cursor: TimelineCursor, limit: int) -> TimelineWindow:
        return self._page_to_window(await self._storage.get_chat_page_before(cursor.position, limit))

    async def get_after(self, cursor: TimelineCursor, limit: int) -> TimelineWindow:
        return self._page_to_window(await self._storage.get_chat_page_after(cursor.position, limit))
