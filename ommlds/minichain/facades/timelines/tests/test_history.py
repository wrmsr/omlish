import uuid

import pytest

from omlish import orm

from ....chat.messages import UserMessage
from ....chat.metadata import MessageUuid
from ....drivers.orm.impl import OrmImpl
from ....drivers.storage.impl import DriverStorageManagerImpl
from ....drivers.storage.models import storage_mappers
from ....drivers.storage.types import ChatId
from ....drivers.types import DriverId
from ...timelines.history import StorageTimelineHistory
from ...timelines.history import TimelineCursor
from ...timelines.items import TimelineItemId
from ...timelines.items import UserMessageTimelineItem


def _storage_manager() -> DriverStorageManagerImpl:
    return DriverStorageManagerImpl(
        driver_id=DriverId(uuid.uuid7()),
        chat_id=ChatId(uuid.uuid7()),
        orm_=OrmImpl(
            registry=orm.registry(*storage_mappers()),
            store=orm.InMemoryStore(),
        ),
    )


def _message(s: str) -> UserMessage:
    return UserMessage(s).with_metadata(MessageUuid(uuid.uuid7()))


async def _history(*messages: UserMessage) -> StorageTimelineHistory:
    storage = _storage_manager()
    await storage.extend_chat(messages)
    return StorageTimelineHistory(storage=storage)


@pytest.mark.asyncs('asyncio')
async def test_latest_storage_history_window() -> None:
    messages = [_message(str(i)) for i in range(5)]
    history = await _history(*messages)

    win = await history.get_latest(2)

    assert [item.message.c for item in win.items if isinstance(item, UserMessageTimelineItem)] == ['3', '4']
    assert win.has_before
    assert not win.has_after
    assert win.before_cursor == TimelineCursor(win.items[0].id, 4)
    assert win.after_cursor == TimelineCursor(win.items[-1].id, 5)


@pytest.mark.asyncs('asyncio')
async def test_before_storage_history_window() -> None:
    messages = [_message(str(i)) for i in range(6)]
    history = await _history(*messages)

    win = await history.get_before(TimelineCursor(TimelineItemId(uuid.uuid7()), 5), 2)

    assert [item.message.c for item in win.items if isinstance(item, UserMessageTimelineItem)] == ['2', '3']
    assert win.has_before
    assert win.has_after
    assert win.before_cursor == TimelineCursor(win.items[0].id, 3)
    assert win.after_cursor == TimelineCursor(win.items[-1].id, 4)


@pytest.mark.asyncs('asyncio')
async def test_after_storage_history_window() -> None:
    messages = [_message(str(i)) for i in range(6)]
    history = await _history(*messages)

    win = await history.get_after(TimelineCursor(TimelineItemId(uuid.uuid7()), 2), 3)

    assert [item.message.c for item in win.items if isinstance(item, UserMessageTimelineItem)] == ['2', '3', '4']
    assert win.has_before
    assert win.has_after
    assert win.before_cursor == TimelineCursor(win.items[0].id, 3)
    assert win.after_cursor == TimelineCursor(win.items[-1].id, 5)


@pytest.mark.asyncs('asyncio')
async def test_empty_storage_history_window() -> None:
    history = await _history()

    win = await history.get_latest(10)

    assert win.items == ()
    assert not win.has_before
    assert not win.has_after
    assert win.before_cursor is None
    assert win.after_cursor is None
