import uuid

import pytest

from omlish import dataclasses as dc

from ....chat.messages import UserMessage
from ...timelines.events import TimelineItemAppendedEvent
from ...timelines.events import TimelineItemFinalizedEvent
from ...timelines.events import TimelineItemUpdatedEvent
from ...timelines.items import TimelineId
from ...timelines.items import TimelineItemId
from ...timelines.items import UserMessageTimelineItem
from ...timelines.state import TimelineState


def _item(s: str) -> UserMessageTimelineItem:
    return UserMessageTimelineItem(
        id=TimelineItemId(uuid.uuid7()),
        message=UserMessage(s),
    )


def test_append_preserves_order() -> None:
    state = TimelineState(timeline_id=TimelineId(uuid.uuid7()))

    a = _item('a')
    b = _item('b')

    ev_a = state.append_item(a)
    ev_b = state.append_item(b)

    assert isinstance(ev_a, TimelineItemAppendedEvent)
    assert ev_a.item is a
    assert isinstance(ev_b, TimelineItemAppendedEvent)
    assert ev_b.item is b

    assert state.get_items() == (a, b)
    assert state.get_item(a.id) is a
    assert state.get_item(b.id) is b
    assert state.get_item_ordinal(a.id) == 0
    assert state.get_item_ordinal(b.id) == 1


def test_update_requires_increasing_revision() -> None:
    state = TimelineState(timeline_id=TimelineId(uuid.uuid7()))

    item = _item('a')
    state.append_item(item)

    with pytest.raises(Exception):  # noqa: B017, PT011
        state.update_item(item)

    updated = dc.replace(item, revision=item.revision + 1)
    ev = state.update_item(updated)

    assert isinstance(ev, TimelineItemUpdatedEvent)
    assert ev.item is updated
    assert state.get_items() == (updated,)
    assert state.get_item(item.id) is updated


def test_finalize_carries_full_updated_item() -> None:
    state = TimelineState(timeline_id=TimelineId(uuid.uuid7()))

    item = _item('a')
    state.append_item(item)

    ev = state.finalize_item(item.id)

    assert isinstance(ev, TimelineItemFinalizedEvent)
    assert ev.item.id == item.id
    assert ev.item.revision == item.revision + 1
    assert ev.item.finalized
    assert ev.item == state.get_item(item.id)


def test_finalize_already_finalized_item_is_stable() -> None:
    state = TimelineState(timeline_id=TimelineId(uuid.uuid7()))

    item = dc.replace(_item('a'), finalized=True)
    state.append_item(item)

    ev = state.finalize_item(item.id)

    assert isinstance(ev, TimelineItemFinalizedEvent)
    assert ev.item is item
    assert state.get_item(item.id) is item
