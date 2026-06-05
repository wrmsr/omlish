"""
Window/cursor/paging behavior: live state history, storage replay history (including tool-pairing extension at page
edges), and the composite's storage⊎live seam - the resume-then-watch machinery.
"""
import uuid

import pytest

from omlish import check
from omlish import orm

from ....backends.scripted.scripts import ChatScript
from ....backends.scripted.scripts import ChatScriptTurn
from ....chat.messages import AiMessage
from ....chat.messages import Message
from ....chat.messages import ToolUseMessage
from ....chat.messages import ToolUseResultMessage
from ....chat.metadata import MessageUuid
from ....drivers.orm.impl import OrmImpl
from ....drivers.storage.impl import DriverStorageManagerImpl
from ....drivers.storage.models import storage_mappers
from ....drivers.storage.types import ChatId
from ....drivers.types import DriverId
from ....tools.types import ToolUse
from ....tools.types import ToolUseResult
from ..history import LIVE_TIMELINE_CURSOR_REALM
from ..history import STORAGE_TIMELINE_CURSOR_REALM
from ..history import StateTimelineHistory
from ..history import StorageTimelineHistory
from ..items import AiMessageTimelineItem
from ..items import TimelineId
from ..items import ToolUseTimelineItem
from ..items import ToolUseTimelineItemState
from ..items import UserMessageTimelineItem
from ..state import TimelineState
from ..translate import translate_message
from .harness import timeline_driver_harness
from .harness import user_message


##


def _with_uuid(m: Message) -> Message:
    return m.with_metadata(MessageUuid(uuid.uuid7()))


def _new_storage(store: orm.InMemoryStore | None = None, chat_id: ChatId | None = None) -> DriverStorageManagerImpl:
    return DriverStorageManagerImpl(
        driver_id=DriverId(uuid.uuid7()),
        chat_id=chat_id if chat_id is not None else ChatId(uuid.uuid7()),
        orm_=OrmImpl(
            registry=orm.registry(*storage_mappers()),
            store=store if store is not None else orm.InMemoryStore(),
        ),
    )


##


@pytest.mark.asyncs('asyncio')
async def test_state_history_windows_and_cursors():
    state = TimelineState(timeline_id=TimelineId(uuid.uuid7()))
    hist = StateTimelineHistory(state=state)

    for i in range(7):
        state.append_item(translate_message(user_message(str(i))))

    latest = await hist.get_latest(3)
    assert [it.message.c for it in latest.items] == ['4', '5', '6']  # type: ignore[attr-defined]
    assert latest.has_before
    assert not latest.has_after

    before = await hist.get_before(check.not_none(latest.before_cursor), 3)
    assert [it.message.c for it in before.items] == ['1', '2', '3']  # type: ignore[attr-defined]
    assert before.has_before
    assert before.has_after

    first = await hist.get_before(check.not_none(before.before_cursor), 3)
    assert [it.message.c for it in first.items] == ['0']  # type: ignore[attr-defined]
    assert not first.has_before

    # And forward again from the middle window's end.
    after = await hist.get_after(check.not_none(before.after_cursor), 2)
    assert [it.message.c for it in after.items] == ['4', '5']  # type: ignore[attr-defined]
    assert after.has_after


@pytest.mark.asyncs('asyncio')
async def test_storage_history_basic_paging():
    storage = _new_storage()
    await storage.extend_chat([user_message(str(i)) for i in range(10)])

    hist = StorageTimelineHistory(storage=storage)

    latest = await hist.get_latest(4)
    assert [it.message.c for it in latest.items] == ['6', '7', '8', '9']  # type: ignore[attr-defined]
    assert latest.has_before
    assert not latest.has_after
    assert check.not_none(latest.before_cursor).realm == STORAGE_TIMELINE_CURSOR_REALM

    before = await hist.get_before(check.not_none(latest.before_cursor), 4)
    assert [it.message.c for it in before.items] == ['2', '3', '4', '5']  # type: ignore[attr-defined]
    assert before.has_before
    assert before.has_after

    after = await hist.get_after(check.not_none(before.after_cursor), 4)
    assert [it.message.c for it in after.items] == ['6', '7', '8', '9']  # type: ignore[attr-defined]
    assert not after.has_after


@pytest.mark.asyncs('asyncio')
async def test_storage_history_tool_pairing_extension():
    """A page that opens on a tool result extends backward (bounded over-widening) until pairing closes."""

    storage = _new_storage()

    tu = ToolUse(id='call_1', name='thing', args={'x': 1})
    await storage.extend_chat([
        *[user_message(f'filler-{i}') for i in range(20)],  # seqs 1-20
        user_message('q'),  # seq 21
        _with_uuid(ToolUseMessage(tu)),  # seq 22
        _with_uuid(ToolUseResultMessage(ToolUseResult(id='call_1', name='thing', c='ok'))),  # seq 23
        _with_uuid(AiMessage('done')),  # seq 24
    ])

    hist = StorageTimelineHistory(storage=storage)

    # A 2-row latest page would open exactly on the result row - extension pulls earlier rows in until the leading
    # item is no longer an orphan result. Windows may over-widen; they may not split pairs.
    latest = await hist.get_latest(2)

    tools = [it for it in latest.items if isinstance(it, ToolUseTimelineItem)]
    assert len(tools) == 1
    tool = tools[0]
    assert tool.state is ToolUseTimelineItemState.COMPLETE
    assert check.not_none(tool.use).id == 'call_1'
    assert tool.result is not None
    assert tool.finalized

    assert isinstance(latest.items[-1], AiMessageTimelineItem)
    assert latest.has_before
    assert not latest.has_after

    # Paging back continues cleanly from the (widened) window's leading edge, with no overlap.
    before = await hist.get_before(check.not_none(latest.before_cursor), 100)
    assert all(isinstance(it, UserMessageTimelineItem) for it in before.items)
    assert not before.has_before
    assert (
        [it.message.c for it in before.items] +  # type: ignore[attr-defined]
        [it.message.c for it in latest.items if isinstance(it, UserMessageTimelineItem)]
    ) == [*[f'filler-{i}' for i in range(20)], 'q']


@pytest.mark.asyncs('asyncio')
async def test_composite_seam_resume_then_live(tmp_path):
    """Prior-session storage + live turns: one seamless paging surface. Real sqlite, real resume."""

    db = str(tmp_path / 'chat.db')
    chat_id = ChatId(uuid.uuid7())

    # A prior session's persisted conversation - driven by a real driver run.
    prior_script = ChatScript([
        ChatScriptTurn.of(AiMessage('old-a-1')),
        ChatScriptTurn.of(AiMessage('old-a-2')),
    ])
    async with timeline_driver_harness(prior_script, chat_id=chat_id, db_file_path=db) as h:
        await h.send_user_text('old-q-1')
        await h.send_user_text('old-q-2')

    script = ChatScript([
        ChatScriptTurn.of(AiMessage('live answer one')),
        ChatScriptTurn.of(AiMessage('live answer two')),
    ])

    async with timeline_driver_harness(script, chat_id=chat_id, db_file_path=db) as h:
        await h.send_user_text('live-q-1')
        await h.send_user_text('live-q-2')

        # 4 live items; ask for 6 -> 2 storage items + 4 live.
        latest = await h.timeline.get_latest(6)

        texts = [
            it.message.c  # type: ignore[attr-defined]
            for it in latest.items
        ]
        assert texts == ['old-q-2', 'old-a-2', 'live-q-1', 'live answer one', 'live-q-2', 'live answer two']
        assert latest.has_before
        assert not latest.has_after
        assert check.not_none(latest.before_cursor).realm == STORAGE_TIMELINE_CURSOR_REALM
        assert check.not_none(latest.after_cursor).realm == LIVE_TIMELINE_CURSOR_REALM

        # No duplicate ids across the seam - the session's persisted rows are excluded from the storage region.
        ids = [it.id for it in latest.items]
        assert len(set(ids)) == len(ids)

        # Page back across the rest of storage.
        before = await h.timeline.get_before(check.not_none(latest.before_cursor), 10)
        assert [it.message.c for it in before.items] == ['old-q-1', 'old-a-1']  # type: ignore[attr-defined]
        assert not before.has_before
        assert before.has_after

        # And forward again from deep history, across the seam into live.
        after = await h.timeline.get_after(check.not_none(before.after_cursor), 4)
        texts = [it.message.c for it in after.items]  # type: ignore[attr-defined]
        assert texts == ['old-q-2', 'old-a-2', 'live-q-1', 'live answer one']
        assert after.has_after

        # Forward again within live, to the present.
        live_after = await h.timeline.get_after(check.not_none(after.after_cursor), 10)
        assert [it.message.c for it in live_after.items] == ['live-q-2', 'live answer two']  # type: ignore[attr-defined]  # noqa
        assert not live_after.has_after

        # And before-paging from a live cursor crosses back into storage when live underflows.
        spanning = await h.timeline.get_before(check.not_none(live_after.before_cursor), 10)
        texts = [it.message.c for it in spanning.items]  # type: ignore[attr-defined]
        assert texts == ['old-q-1', 'old-a-1', 'old-q-2', 'old-a-2', 'live-q-1', 'live answer one']
        assert not spanning.has_before
        assert spanning.has_after


@pytest.mark.asyncs('asyncio')
async def test_composite_pure_live_no_storage():
    script = ChatScript([ChatScriptTurn.of(AiMessage('hello'))])

    async with timeline_driver_harness(script) as h:
        await h.send_user_text('hi')

        att = await h.timeline.attach(10)
        async with att:
            assert [type(it) for it in att.window.items] == [UserMessageTimelineItem, AiMessageTimelineItem]
            assert not att.window.has_before
            assert not att.window.has_after
            assert att.watermark == h.manager.state.watermark


@pytest.mark.asyncs('asyncio')
async def test_composite_pure_storage_resume_before_first_action(tmp_path):
    """Attaching to a freshly resumed (no live activity yet) chat serves pure storage."""

    db = str(tmp_path / 'chat.db')
    chat_id = ChatId(uuid.uuid7())

    prior_script = ChatScript([
        ChatScriptTurn.of(AiMessage(f'old-a-{i}'))
        for i in range(3)
    ])
    async with timeline_driver_harness(prior_script, chat_id=chat_id, db_file_path=db) as h:
        for i in range(3):
            await h.send_user_text(f'old-q-{i}')

    script = ChatScript([ChatScriptTurn.of(AiMessage('unused'))])

    async with timeline_driver_harness(script, chat_id=chat_id, db_file_path=db) as h:
        att = await h.timeline.attach(3)
        async with att:
            assert [it.message.c for it in att.window.items] == ['old-a-1', 'old-q-2', 'old-a-2']  # type: ignore[attr-defined]  # noqa
            assert att.window.has_before
            assert att.watermark == 0
