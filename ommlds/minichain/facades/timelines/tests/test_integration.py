import uuid

import pytest

from omlish import orm

from ....chat.events import UserMessagesEvent
from ....chat.messages import AiMessage
from ....chat.messages import UserMessage
from ....chat.metadata import MessageUuid
from ....chat.stream.events import AiStreamBeginEvent
from ....chat.stream.events import AiStreamDeltaEvent
from ....chat.stream.events import AiStreamEndEvent
from ....chat.stream.types import ContentAiDelta
from ....drivers.orm.impl import OrmImpl
from ....drivers.storage.impl import DriverStorageManagerImpl
from ....drivers.storage.models import storage_mappers
from ....drivers.storage.types import ChatId
from ....drivers.types import DriverId
from ....events.manager import EventsManager
from ....events.types import Event
from ....events.types import EventCallback
from ....events.types import EventCallbacks
from ....tools.execution.events import ToolUseEvent
from ....tools.execution.events import ToolUseResultEvent
from ....tools.types import ToolUse
from ....tools.types import ToolUseResult
from ...timelines.events import TimelineEvent
from ...timelines.events import TimelineItemAppendedEvent
from ...timelines.events import TimelineItemFinalizedEvent
from ...timelines.events import TimelineItemUpdatedEvent
from ...timelines.history import StorageTimelineHistory
from ...timelines.items import AiMessageTimelineItem
from ...timelines.items import AiStreamTimelineItem
from ...timelines.items import ToolUseTimelineItem
from ...timelines.items import ToolUseTimelineItemState
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


def _ai_message(s: str) -> AiMessage:
    return AiMessage(s).with_metadata(MessageUuid(uuid.uuid7()))


@pytest.mark.asyncs('asyncio')
async def test_timeline_manager_with_storage_history_and_event_bus() -> None:
    storage = _storage_manager()
    await storage.extend_chat([
        _user_message('old-0'),
        _ai_message('old-1'),
        _user_message('old-2'),
    ])

    callbacks: list[EventCallback] = []
    events = EventsManager(EventCallbacks(callbacks))

    timeline_events: list[TimelineEvent] = []

    async def capture_timeline_events(event: Event) -> None:
        if isinstance(event, TimelineEvent):
            timeline_events.append(event)

    manager = TimelineManager(
        events=events,
        history=StorageTimelineHistory(storage=storage),
    )

    callbacks.extend([
        EventCallback(manager.handle_event),
        EventCallback(capture_timeline_events),
    ])

    initial = await manager.view.get_latest(10)

    assert [type(item) for item in initial.items] == [
        UserMessageTimelineItem,
        AiMessageTimelineItem,
        UserMessageTimelineItem,
    ]
    assert [item.message.c for item in initial.items] == ['old-0', 'old-1', 'old-2']  # type: ignore[attr-defined]
    assert not initial.has_before
    assert not initial.has_after
    assert initial.before_cursor is not None
    assert initial.before_cursor.position == 1
    assert initial.after_cursor is not None
    assert initial.after_cursor.position == 3

    new_user_message = _user_message('live-user')
    await events.emit_event(UserMessagesEvent([new_user_message]))

    assert len(timeline_events) == 1
    user_event = timeline_events.pop()
    assert isinstance(user_event, TimelineItemAppendedEvent)
    assert isinstance(user_event.item, UserMessageTimelineItem)
    assert user_event.item.message is new_user_message

    stream_message_uuid = uuid.uuid7()
    await events.emit_event(AiStreamBeginEvent(message_uuid=stream_message_uuid))
    await events.emit_event(AiStreamDeltaEvent(ContentAiDelta('hi'), message_uuid=stream_message_uuid))
    await events.emit_event(AiStreamDeltaEvent(ContentAiDelta(' there'), message_uuid=stream_message_uuid))
    await events.emit_event(AiStreamEndEvent(message_uuid=stream_message_uuid))

    assert [type(event) for event in timeline_events] == [
        TimelineItemAppendedEvent,
        TimelineItemUpdatedEvent,
        TimelineItemUpdatedEvent,
        TimelineItemFinalizedEvent,
    ]
    timeline_events.clear()

    stream_item = manager.state.get_items()[-1]
    assert isinstance(stream_item, AiStreamTimelineItem)
    assert stream_item.content == 'hi there'
    assert stream_item.finalized

    tool_use = ToolUse(
        id='tool-1',
        name='thing',
        args={'x': 1},
    )
    tool_result = ToolUseResult(
        id='tool-1',
        name='thing',
        c='ok',
    )

    await events.emit_event(ToolUseEvent(tool_use))
    await events.emit_event(ToolUseResultEvent(tool_use, tool_result))

    assert [type(event) for event in timeline_events] == [
        TimelineItemAppendedEvent,
        TimelineItemUpdatedEvent,
    ]

    tool_item = manager.state.get_items()[-1]
    assert isinstance(tool_item, ToolUseTimelineItem)
    assert tool_item.state is ToolUseTimelineItemState.COMPLETE
    assert tool_item.result is tool_result
    assert tool_item.finalized
