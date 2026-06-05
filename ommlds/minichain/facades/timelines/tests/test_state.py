import uuid

import pytest

from ....chat.messages import AiMessage
from ....chat.messages import UserMessage
from ..events import TimelineItemAppendedEvent
from ..events import TimelineItemDeltaEvent
from ..events import TimelineItemUpdatedEvent
from ..items import AiMessageTimelineItem
from ..items import AiStreamTimelineItem
from ..items import TimelineId
from ..items import TimelineItemId
from ..items import UserMessageTimelineItem
from ..state import TimelineState


def _state() -> TimelineState:
    return TimelineState(timeline_id=TimelineId(uuid.uuid7()))


def _user_item(s: str) -> UserMessageTimelineItem:
    return UserMessageTimelineItem(message=UserMessage(s), finalized=True)


def test_append_positions_and_watermark():
    st = _state()
    assert st.watermark == 0
    assert len(st) == 0

    evs = [st.append_item(_user_item(str(i))) for i in range(3)]

    assert [ev.position for ev in evs] == [0, 1, 2]
    assert [ev.watermark for ev in evs] == [1, 2, 3]
    assert st.watermark == 3
    assert len(st) == 3

    for i, item in enumerate(st.get_items()):
        assert st.get_position(item.id) == i
        assert st.get_item(item.id) is item
        assert st.get_item_at_position(i) is item

    assert st.get_item_at_position(3) is None
    assert st.get_item(TimelineItemId(uuid.uuid7())) is None


def test_duplicate_append_rejected():
    st = _state()
    item = _user_item('hi')
    st.append_item(item)

    with pytest.raises(Exception):  # noqa
        st.append_item(item)


def test_update_advances_revision_and_allows_type_change():
    st = _state()

    mu = uuid.uuid7()
    stream = AiStreamTimelineItem(id=TimelineItemId(mu), message_uuid=mu, content='hel')
    st.append_item(stream)

    # Stale revision rejected.
    with pytest.raises(Exception):  # noqa
        st.update_item(AiStreamTimelineItem(id=stream.id, message_uuid=mu, content='x', revision=0))

    # Live -> canonical replacement: same id, advanced revision, different type.
    canonical = AiMessageTimelineItem(
        id=stream.id,
        revision=1,
        message=AiMessage('hello'),
        finalized=True,
    )
    ev = st.update_item(canonical)

    assert isinstance(ev, TimelineItemUpdatedEvent)
    assert ev.item is canonical
    assert st.get_item(stream.id) is canonical
    assert st.get_position(stream.id) == 0
    assert st.watermark == 2


def test_delta_requires_exact_revision_advance():
    st = _state()

    mu = uuid.uuid7()
    stream = AiStreamTimelineItem(id=TimelineItemId(mu), message_uuid=mu, content='a')
    st.append_item(stream)

    ev = st.apply_item_delta(
        AiStreamTimelineItem(id=stream.id, message_uuid=mu, content='ab', revision=1),
        'b',
    )
    assert isinstance(ev, TimelineItemDeltaEvent)
    assert ev.item_id == stream.id
    assert ev.revision == 1
    assert ev.appended == 'b'

    # Skipping a revision is rejected.
    with pytest.raises(Exception):  # noqa
        st.apply_item_delta(
            AiStreamTimelineItem(id=stream.id, message_uuid=mu, content='abcd', revision=3),
            'cd',
        )


def test_events_carry_timeline_id():
    st = _state()
    ev = st.append_item(_user_item('hi'))

    assert isinstance(ev, TimelineItemAppendedEvent)
    assert ev.timeline_id == st.timeline_id
