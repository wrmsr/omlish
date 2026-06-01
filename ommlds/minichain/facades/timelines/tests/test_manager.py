import uuid

import pytest

from ....chat.events import AiMessagesEvent
from ....chat.events import UserMessagesEvent
from ....chat.messages import AiMessage
from ....chat.messages import UserMessage
from ....chat.metadata import MessageUuid
from ....chat.stream.events import AiStreamBeginEvent
from ....chat.stream.events import AiStreamDeltaEvent
from ....chat.stream.events import AiStreamEndEvent
from ....chat.stream.types import ContentAiDelta
from ....events.manager import EventsManager
from ....events.types import Event
from ....events.types import EventCallback
from ....events.types import EventCallbacks
from ....tools.execution.events import ToolUseEvent
from ....tools.execution.events import ToolUseResultEvent
from ....tools.types import ToolUse
from ....tools.types import ToolUseResult
from ...timelines.events import TimelineItemAppendedEvent
from ...timelines.events import TimelineItemFinalizedEvent
from ...timelines.events import TimelineItemUpdatedEvent
from ...timelines.events import TimelineResetEvent
from ...timelines.items import AiMessageTimelineItem
from ...timelines.items import AiStreamTimelineItem
from ...timelines.items import TimelineId
from ...timelines.items import ToolUseTimelineItem
from ...timelines.items import ToolUseTimelineItemState
from ...timelines.items import UserMessageTimelineItem
from ...timelines.manager import TimelineManager


def _manager() -> tuple[TimelineManager, list[Event]]:
    seen: list[Event] = []

    async def cb(event: Event) -> None:
        seen.append(event)

    return (
        TimelineManager(events=EventsManager(EventCallbacks([EventCallback(cb)]))),
        seen,
    )


def _user_message(s: str) -> UserMessage:
    return UserMessage(s).with_metadata(MessageUuid(uuid.uuid7()))


def _ai_message(s: str) -> AiMessage:
    return AiMessage(s).with_metadata(MessageUuid(uuid.uuid7()))


@pytest.mark.asyncs('asyncio')
async def test_user_messages_event_appends_user_items() -> None:
    manager, seen = _manager()

    msg = _user_message('hi')
    await manager.handle_event(UserMessagesEvent([msg]))

    assert len(seen) == 1
    ev = seen[0]
    assert isinstance(ev, TimelineItemAppendedEvent)
    assert isinstance(ev.item, UserMessageTimelineItem)
    assert ev.item.message is msg
    assert ev.item.finalized
    assert manager.state.get_items() == (ev.item,)


@pytest.mark.asyncs('asyncio')
async def test_non_streamed_ai_messages_event_appends_ai_items() -> None:
    manager, seen = _manager()

    msg = _ai_message('hello')
    await manager.handle_event(AiMessagesEvent([msg]))

    assert len(seen) == 1
    ev = seen[0]
    assert isinstance(ev, TimelineItemAppendedEvent)
    assert isinstance(ev.item, AiMessageTimelineItem)
    assert ev.item.message is msg
    assert ev.item.finalized
    assert manager.state.get_items() == (ev.item,)


@pytest.mark.asyncs('asyncio')
async def test_streamed_ai_messages_event_does_not_append_final_chat() -> None:
    manager, seen = _manager()

    await manager.handle_event(AiMessagesEvent([_ai_message('hello')], streamed=True))

    assert seen == []
    assert manager.state.get_items() == ()


@pytest.mark.asyncs('asyncio')
async def test_stream_events_create_update_and_finalize_one_item() -> None:
    manager, seen = _manager()

    message_uuid = uuid.uuid7()

    await manager.handle_event(AiStreamBeginEvent(message_uuid=message_uuid))
    await manager.handle_event(AiStreamDeltaEvent(ContentAiDelta('hi'), message_uuid=message_uuid))
    await manager.handle_event(AiStreamDeltaEvent(ContentAiDelta(' there'), message_uuid=message_uuid))
    await manager.handle_event(AiStreamEndEvent(message_uuid=message_uuid))

    assert [type(ev) for ev in seen] == [
        TimelineItemAppendedEvent,
        TimelineItemUpdatedEvent,
        TimelineItemUpdatedEvent,
        TimelineItemFinalizedEvent,
    ]

    item = manager.state.get_items()[0]
    assert isinstance(item, AiStreamTimelineItem)
    assert item.message_uuid == message_uuid
    assert item.content == 'hi there'
    assert item.finalized


@pytest.mark.asyncs('asyncio')
async def test_stream_delta_without_begin_creates_item() -> None:
    manager, seen = _manager()

    message_uuid = uuid.uuid7()

    await manager.handle_event(AiStreamDeltaEvent(ContentAiDelta('hi'), message_uuid=message_uuid))

    assert [type(ev) for ev in seen] == [
        TimelineItemAppendedEvent,
        TimelineItemUpdatedEvent,
    ]

    item = manager.state.get_items()[0]
    assert isinstance(item, AiStreamTimelineItem)
    assert item.message_uuid == message_uuid
    assert item.content == 'hi'


@pytest.mark.asyncs('asyncio')
async def test_timeline_event_is_ignored() -> None:
    manager, seen = _manager()

    await manager.handle_event(TimelineResetEvent(timeline_id=TimelineId(uuid.uuid7())))

    assert seen == []
    assert manager.state.get_items() == ()


@pytest.mark.asyncs('asyncio')
async def test_tool_use_event_appends_running_item() -> None:
    manager, seen = _manager()

    use = ToolUse(
        id='tu-1',
        name='thing',
        args={'x': 1},
    )

    await manager.handle_event(ToolUseEvent(use))

    assert len(seen) == 1
    ev = seen[0]
    assert isinstance(ev, TimelineItemAppendedEvent)
    assert isinstance(ev.item, ToolUseTimelineItem)
    assert ev.item.use is use
    assert ev.item.state is ToolUseTimelineItemState.RUNNING
    assert not ev.item.finalized


@pytest.mark.asyncs('asyncio')
async def test_tool_use_result_event_updates_same_item_to_complete() -> None:
    manager, seen = _manager()

    use = ToolUse(
        id='tu-1',
        name='thing',
        args={'x': 1},
    )
    result = ToolUseResult(
        id='tu-1',
        name='thing',
        c='ok',
    )

    await manager.handle_event(ToolUseEvent(use))
    await manager.handle_event(ToolUseResultEvent(use, result))

    assert [type(ev) for ev in seen] == [
        TimelineItemAppendedEvent,
        TimelineItemUpdatedEvent,
    ]

    item = manager.state.get_items()[0]
    assert isinstance(item, ToolUseTimelineItem)
    assert item.id == seen[0].item.id  # type: ignore[attr-defined]
    assert item.use is use
    assert item.result is result
    assert item.state is ToolUseTimelineItemState.COMPLETE
    assert item.finalized


@pytest.mark.asyncs('asyncio')
async def test_tool_use_result_before_use_appends_finalized_complete_item() -> None:
    manager, seen = _manager()

    use = ToolUse(
        id='tu-1',
        name='thing',
        args={'x': 1},
    )
    result = ToolUseResult(
        id='tu-1',
        name='thing',
        c='ok',
    )

    await manager.handle_event(ToolUseResultEvent(use, result))

    assert len(seen) == 1
    ev = seen[0]
    assert isinstance(ev, TimelineItemAppendedEvent)
    assert isinstance(ev.item, ToolUseTimelineItem)
    assert ev.item.use is use
    assert ev.item.result is result
    assert ev.item.state is ToolUseTimelineItemState.COMPLETE
    assert ev.item.finalized
