import uuid

import pytest

from ....chat.messages import UserMessage
from ...timelines.items import TimelineId
from ...timelines.items import TimelineItemId
from ...timelines.items import UserMessageTimelineItem
from ...timelines.state import TimelineState
from ...timelines.views import TimelineCursor
from ...timelines.views import TimelineView


def _item(s: str) -> UserMessageTimelineItem:
    return UserMessageTimelineItem(
        id=TimelineItemId(uuid.uuid7()),
        message=UserMessage(s),
    )


def _state(*items: UserMessageTimelineItem) -> TimelineState:
    return TimelineState(
        timeline_id=TimelineId(uuid.uuid7()),
        items=items,
    )


@pytest.mark.asyncs('asyncio')
async def test_get_latest() -> None:
    items = [_item(str(i)) for i in range(5)]
    view = TimelineView(state=_state(*items))

    win = await view.get_latest(2)

    assert win.items == tuple(items[-2:])
    assert win.has_before
    assert not win.has_after
    assert win.before_cursor == TimelineCursor(items[3].id, 3)
    assert win.after_cursor == TimelineCursor(items[4].id, 4)


@pytest.mark.asyncs('asyncio')
async def test_get_latest_with_large_limit() -> None:
    items = [_item(str(i)) for i in range(3)]
    view = TimelineView(state=_state(*items))

    win = await view.get_latest(10)

    assert win.items == tuple(items)
    assert not win.has_before
    assert not win.has_after
    assert win.before_cursor == TimelineCursor(items[0].id, 0)
    assert win.after_cursor == TimelineCursor(items[2].id, 2)


@pytest.mark.asyncs('asyncio')
async def test_get_latest_empty() -> None:
    view = TimelineView(state=_state())

    win = await view.get_latest(10)

    assert win.items == ()
    assert not win.has_before
    assert not win.has_after
    assert win.before_cursor is None
    assert win.after_cursor is None


@pytest.mark.asyncs('asyncio')
async def test_get_before() -> None:
    items = [_item(str(i)) for i in range(6)]
    view = TimelineView(state=_state(*items))

    win = await view.get_before(TimelineCursor(items[4].id, 4), 2)

    assert win.items == tuple(items[2:4])
    assert win.has_before
    assert win.has_after
    assert win.before_cursor == TimelineCursor(items[2].id, 2)
    assert win.after_cursor == TimelineCursor(items[3].id, 3)


@pytest.mark.asyncs('asyncio')
async def test_get_after() -> None:
    items = [_item(str(i)) for i in range(6)]
    view = TimelineView(state=_state(*items))

    win = await view.get_after(TimelineCursor(items[1].id, 1), 3)

    assert win.items == tuple(items[2:5])
    assert win.has_before
    assert win.has_after
    assert win.before_cursor == TimelineCursor(items[2].id, 2)
    assert win.after_cursor == TimelineCursor(items[4].id, 4)


@pytest.mark.asyncs('asyncio')
async def test_cursor_fallback_when_ordinal_is_stale() -> None:
    items = [_item(str(i)) for i in range(5)]
    view = TimelineView(state=_state(*items))

    win = await view.get_after(TimelineCursor(items[1].id, 99), 2)

    assert win.items == tuple(items[2:4])
    assert win.before_cursor == TimelineCursor(items[2].id, 2)
    assert win.after_cursor == TimelineCursor(items[3].id, 3)
