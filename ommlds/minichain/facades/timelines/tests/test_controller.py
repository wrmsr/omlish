import uuid

import pytest

from omlish import orm

from ....chat.events import UserMessagesEvent
from ....chat.messages import UserMessage
from ....chat.metadata import MessageUuid
from ....drivers.orm.impl import OrmImpl
from ....drivers.storage.impl import DriverStorageManagerImpl
from ....drivers.storage.models import storage_mappers
from ....drivers.storage.types import ChatId
from ....drivers.types import DriverId
from ....events.manager import EventsManager
from ....events.types import EventCallback
from ....events.types import EventCallbacks
from ...timelines.controller import TimelineController
from ...timelines.controller import TimelineSubscriptionClosedError
from ...timelines.events import TimelineEvent
from ...timelines.events import TimelineItemAppendedEvent
from ...timelines.events import TimelineResetEvent
from ...timelines.history import StorageTimelineHistory
from ...timelines.items import TimelineId
from ...timelines.items import UserMessageTimelineItem
from ...timelines.manager import TimelineManager


def _storage_manager() -> DriverStorageManagerImpl:
    return DriverStorageManagerImpl(
        driver_id=DriverId(uuid.uuid7()),
        chat_id=ChatId(uuid.uuid7()),
        orm_=OrmImpl(
            registry=orm.registry(*storage_mappers()),
            store=orm.InMemoryStore(),
        ),
    )


def _user_message(s: str) -> UserMessage:
    return UserMessage(s).with_metadata(MessageUuid(uuid.uuid7()))


async def _controller(
        *history_messages: UserMessage,
) -> tuple[TimelineController, EventsManager]:
    storage = _storage_manager()
    await storage.extend_chat(history_messages)

    callbacks: list[EventCallback] = []
    events = EventsManager(EventCallbacks(callbacks))

    manager = TimelineManager(
        events=events,
        history=StorageTimelineHistory(storage=storage),
    )
    controller = TimelineController(manager=manager)

    callbacks.extend([
        EventCallback(manager.handle_event),
        EventCallback(controller.handle_event),
    ])

    return controller, events


@pytest.mark.asyncs('asyncio')
async def test_controller_reads_history_and_fans_out_events_to_subscribers() -> None:
    controller, events = await _controller(
        _user_message('old-0'),
        _user_message('old-1'),
        _user_message('old-2'),
    )

    latest = await controller.get_latest(2)

    assert [item.message.c for item in latest.items if isinstance(item, UserMessageTimelineItem)] == ['old-1', 'old-2']
    assert latest.has_before
    assert not latest.has_after
    assert latest.before_cursor is not None
    assert latest.before_cursor.position == 2
    assert latest.after_cursor is not None
    assert latest.after_cursor.position == 3

    async with controller.subscribe() as sub_a, controller.subscribe() as sub_b:
        msg = _user_message('live')
        await events.emit_event(UserMessagesEvent([msg]))

        ev_a = await sub_a.get()
        ev_b = await sub_b.get()

        assert isinstance(ev_a, TimelineItemAppendedEvent)
        assert isinstance(ev_b, TimelineItemAppendedEvent)
        assert ev_a.item == ev_b.item
        assert isinstance(ev_a.item, UserMessageTimelineItem)
        assert ev_a.item.message is msg

        await sub_a.aclose()

        msg2 = _user_message('still-live')
        await events.emit_event(UserMessagesEvent([msg2]))

        with pytest.raises(TimelineSubscriptionClosedError):
            await sub_a.get()

        ev_b2 = await sub_b.get()
        assert isinstance(ev_b2, TimelineItemAppendedEvent)
        assert isinstance(ev_b2.item, UserMessageTimelineItem)
        assert ev_b2.item.message is msg2


@pytest.mark.asyncs('asyncio')
async def test_controller_ignores_other_timeline_events() -> None:
    controller, events = await _controller()

    async with controller.subscribe() as sub:
        await events.emit_event(TimelineResetEvent(timeline_id=TimelineId(uuid.uuid7())))

        assert sub._queue.empty()  # noqa


@pytest.mark.asyncs('asyncio')
async def test_subscription_async_iteration_stops_on_close() -> None:
    controller, events = await _controller()

    sub = controller.subscribe()

    msg = _user_message('live')
    await events.emit_event(UserMessagesEvent([msg]))
    await sub.aclose()

    events_seen: list[TimelineEvent] = []
    async for event in sub:
        events_seen.append(event)

    assert len(events_seen) == 1
    event = events_seen[0]
    assert isinstance(event, TimelineItemAppendedEvent)
    assert isinstance(event.item, UserMessageTimelineItem)
    assert event.item.message is msg
