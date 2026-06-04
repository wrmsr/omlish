import asyncio
import typing as ta

from omlish import check

from ...events.types import Event
from .events import TimelineEvent
from .history import TimelineCursor
from .history import TimelineWindow
from .items import TimelineId
from .manager import TimelineManager


##


class TimelineSubscriptionClosedError(Exception):
    pass


class TimelineSubscription:
    def __init__(
            self,
            controller: TimelineController,
            queue: asyncio.Queue[TimelineEvent | None],
    ) -> None:
        super().__init__()

        self._controller = controller
        self._queue = queue
        self._closed = False

    @property
    def closed(self) -> bool:
        return self._closed

    async def __aenter__(self) -> ta.Self:
        return self

    async def __aexit__(self, et, e, tb) -> None:
        await self.aclose()

    async def deliver_event(self, event: TimelineEvent) -> None:
        if self._closed:
            return

        await self._queue.put(event)

    async def _close_from_controller(self) -> None:
        if self._closed:
            return

        self._closed = True

        await self._queue.put(None)

    async def aclose(self) -> None:
        await self._controller._unsubscribe(self)  # noqa

    async def get(self) -> TimelineEvent:
        event = await self._queue.get()
        if event is None:
            raise TimelineSubscriptionClosedError

        return event

    def __aiter__(self) -> ta.AsyncIterator[TimelineEvent]:
        async def inner() -> ta.AsyncIterator[TimelineEvent]:
            while True:
                try:
                    yield await self.get()
                except TimelineSubscriptionClosedError:
                    break

        return inner()


##


class TimelineController:
    def __init__(
            self,
            *,
            manager: TimelineManager,
            event_queue_size: int = 256,
    ) -> None:
        super().__init__()

        check.arg(event_queue_size >= 0)

        self._manager = manager
        self._event_queue_size = event_queue_size

        self._subscriptions: set[TimelineSubscription] = set()

    @property
    def manager(self) -> TimelineManager:
        return self._manager

    @property
    def timeline_id(self) -> TimelineId:
        return self._manager.timeline_id

    async def get_latest(self, limit: int) -> TimelineWindow:
        return await self._manager.view.get_latest(limit)

    async def get_before(self, cursor: TimelineCursor, limit: int) -> TimelineWindow:
        return await self._manager.view.get_before(cursor, limit)

    async def get_after(self, cursor: TimelineCursor, limit: int) -> TimelineWindow:
        return await self._manager.view.get_after(cursor, limit)

    def subscribe(self) -> TimelineSubscription:
        sub = TimelineSubscription(
            self,
            asyncio.Queue(maxsize=self._event_queue_size),
        )

        self._subscriptions.add(sub)

        return sub

    async def _unsubscribe(self, sub: TimelineSubscription) -> None:
        self._subscriptions.discard(sub)
        await sub._close_from_controller()  # noqa

    async def handle_event(self, event: Event) -> None:
        if not isinstance(event, TimelineEvent):
            return

        if event.timeline_id != self.timeline_id:
            return

        for sub in tuple(self._subscriptions):
            await sub.deliver_event(event)
