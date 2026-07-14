"""
The frontend-facing surface of a timeline: snapshot paging plus live subscription, with a race-free way to start.

THE ATTACH RECIPE (load-bearing; see the package README): `Timeline.attach` captures the state watermark and registers
the subscription *synchronously* - no awaits - and only then fetches the initial window (whose history implementation
snapshots live state synchronously on entry, per the history coherence invariant). The result: the returned window
reflects the watermark exactly, and the subscription delivers precisely the events with watermark > it - no gaps, no
duplicates, even when attaching mid-stream. Storage reads may interleave with new events during the fetch; region
filtering (epoch + live-id dedupe) keeps them out of the window.

Subscriptions buffer without bound and deliver synchronously from event dispatch - subscribers are assumed to be good
citizens (in-process consumers that drain promptly); backpressure/lag policy is an explicitly punted future concern.
Events flow through the process-wide `EventsManager` (so e.g. the JSONL event logger sees timeline events too);
`Timeline.handle_event` is just another bus callback, filtering by timeline id and fanning out to subscriptions.
"""
import asyncio
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from ...events.types import Event
from .events import TimelineEvent
from .history import TimelineCursor
from .history import TimelineHistory
from .history import TimelineWindow
from .items import TimelineId
from .manager import TimelineManager


##


class TimelineSubscriptionClosedError(Exception):
    pass


class TimelineSubscription:
    """
    An async-iterable feed of one timeline's events, in order. Iteration ends (and `get` raises
    `TimelineSubscriptionClosedError`) once closed; closing is idempotent and detaches it from its `Timeline`.
    """

    def __init__(self) -> None:
        super().__init__()

        self._queue: asyncio.Queue[TimelineEvent | None] = asyncio.Queue()
        self._closed = False
        self._on_close: ta.Callable[[TimelineSubscription], None] | None = None

    @property
    def closed(self) -> bool:
        return self._closed

    def _deliver(self, event: TimelineEvent) -> None:
        if self._closed:
            return

        self._queue.put_nowait(event)

    async def aclose(self) -> None:
        if self._closed:
            return

        self._closed = True
        self._queue.put_nowait(None)

        if (oc := self._on_close) is not None:
            self._on_close = None
            oc(self)

    async def __aenter__(self) -> ta.Self:
        return self

    async def __aexit__(self, et, e, tb) -> None:
        await self.aclose()

    async def get(self) -> TimelineEvent:
        event = await self._queue.get()
        if event is None:
            # Propagate the sentinel for any concurrent/subsequent getters.
            self._queue.put_nowait(None)
            raise TimelineSubscriptionClosedError

        return event

    def drain_pending(self) -> list[TimelineEvent]:
        """All currently-buffered events, without waiting - for poll-style consumers (and tests)."""

        out: list[TimelineEvent] = []

        while True:
            try:
                event = self._queue.get_nowait()
            except asyncio.QueueEmpty:
                break

            if event is None:
                self._queue.put_nowait(None)
                break

            out.append(event)

        return out

    def __aiter__(self) -> ta.AsyncIterator[TimelineEvent]:
        return self

    async def __anext__(self) -> TimelineEvent:
        try:
            return await self.get()
        except TimelineSubscriptionClosedError:
            raise StopAsyncIteration from None


##


@dc.dataclass(frozen=True)
class TimelineAttachment(lang.Final):
    """An initial window, the watermark it reflects, and the events strictly after that watermark."""

    window: TimelineWindow
    watermark: int
    subscription: TimelineSubscription

    async def __aenter__(self) -> ta.Self:
        return self

    async def __aexit__(self, et, e, tb) -> None:
        await self.subscription.aclose()


##


class Timeline:
    """One conversation's timeline, as a frontend consumes it: attach for now-and-onward, page back for the past."""

    def __init__(
            self,
            *,
            manager: TimelineManager,
            history: TimelineHistory,
    ) -> None:
        super().__init__()

        self._manager = manager
        self._history = history

        self._subscriptions: set[TimelineSubscription] = set()

    @property
    def timeline_id(self) -> TimelineId:
        return self._manager.timeline_id

    @property
    def watermark(self) -> int:
        return self._manager.state.watermark

    #

    async def handle_event(self, event: Event) -> None:
        if not isinstance(event, TimelineEvent):
            return

        if event.timeline_id != self.timeline_id:
            return

        for sub in tuple(self._subscriptions):
            sub._deliver(event)  # noqa

    #

    def subscribe(self) -> TimelineSubscription:
        sub = TimelineSubscription()
        sub._on_close = self._subscriptions.discard  # noqa

        self._subscriptions.add(sub)

        return sub

    async def attach(self, limit: int) -> TimelineAttachment:
        check.arg(limit >= 0)

        # The attach recipe - synchronous section: watermark, then subscription. No awaits until the history fetch,
        # whose implementations snapshot live state synchronously on entry.
        watermark = self._manager.state.watermark
        sub = self.subscribe()

        try:
            window = await self._history.get_latest(limit)

        except BaseException:  # noqa
            await sub.aclose()
            raise

        return TimelineAttachment(
            window=window,
            watermark=watermark,
            subscription=sub,
        )

    #

    async def get_latest(self, limit: int) -> TimelineWindow:
        """A bare snapshot window - use `attach` when you also want the events after it."""

        return await self._history.get_latest(limit)

    async def get_before(self, cursor: TimelineCursor, limit: int) -> TimelineWindow:
        return await self._history.get_before(cursor, limit)

    async def get_after(self, cursor: TimelineCursor, limit: int) -> TimelineWindow:
        return await self._history.get_after(cursor, limit)
