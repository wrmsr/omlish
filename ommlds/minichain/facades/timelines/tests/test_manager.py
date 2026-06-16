"""
TimelineManager behavior, exercised through real scripted driver runs (real injector, event bus, ORM, tools) rather
than hand-synthesized event sequences. The convergence check here is the heart: the live item sequence must equal what
replay translation reconstructs from storage.
"""
import typing as ta

import pytest

from omlish import check
from omlish import dataclasses as dc
from omlish import marshal as msh

from ....backends.scripted.scripts import ChatScript
from ....backends.scripted.scripts import ChatScriptTurn
from ....chat.messages import AiMessage
from ....chat.messages import ThinkingMessage
from ....chat.messages import ToolUseMessage
from ....modules.weathertest.inject import bind_weather_test
from ....tools.types import ToolUse
from ..events import TimelineEvent
from ..events import TimelineItemAppendedEvent
from ..events import TimelineItemDeltaEvent
from ..events import TimelineItemUpdatedEvent
from ..items import AiMessageTimelineItem
from ..items import AiStreamTimelineItem
from ..items import ThinkingStreamTimelineItem
from ..items import ThinkingTimelineItem
from ..items import TimelineItem
from ..items import ToolUseTimelineItem
from ..items import ToolUseTimelineItemState
from ..items import UserMessageTimelineItem
from ..translate import timeline_item_id_for_message
from ..translate import timeline_translate_chat
from .harness import timeline_driver_harness


##


def canon_items(items: ta.Iterable[TimelineItem]) -> list[ta.Any]:
    """Marshaled forms modulo revision and live-only fields - the shape the convergence invariant is stated over."""

    out = []
    for it in items:
        it = dc.replace(it, revision=0)
        if isinstance(it, ToolUseTimelineItem):
            it = dc.replace(it, execution=None)
        out.append(msh.marshal(it, TimelineItem))
    return out


def _weather_script() -> ChatScript:
    return ChatScript([
        ChatScriptTurn.of(
            AiMessage('Let me check the weather.'),
            ToolUseMessage(ToolUse(
                id='call_1',
                name='weather',
                args={'location': 'Tokyo'},
            )),
        ),
        ChatScriptTurn.of(
            AiMessage('It is foggy in Tokyo.'),
        ),
    ])


##


@pytest.mark.asyncs('asyncio')
async def test_streaming_prose_and_thinking_lifecycle():
    script = ChatScript([
        ChatScriptTurn.of(
            ThinkingMessage('thinking it over carefully'),
            AiMessage('a considered response to your question'),
        ),
    ])

    async with timeline_driver_harness(script) as h:
        await h.send_user_text('hi there')

        items = h.manager.state.get_items()

        assert [type(it) for it in items] == [
            UserMessageTimelineItem,
            ThinkingTimelineItem,
            AiMessageTimelineItem,
        ]
        assert all(it.finalized for it in items)

        thinking = check.isinstance(items[1], ThinkingTimelineItem)
        assert thinking.message.c == 'thinking it over carefully'

        ai = check.isinstance(items[2], AiMessageTimelineItem)
        assert ai.message.c == 'a considered response to your question'

        # The lifecycle ran through in-flight stream items: appended as stream types, grown by deltas, then
        # *replaced* (same id) by their canonical forms.
        tl_events = [e for e in h.events if isinstance(e, TimelineEvent)]

        thinking_evs = [
            e for e in tl_events
            if (isinstance(e, (TimelineItemAppendedEvent, TimelineItemUpdatedEvent)) and e.item.id == thinking.id)
            or (isinstance(e, TimelineItemDeltaEvent) and e.item_id == thinking.id)
        ]
        assert isinstance(thinking_evs[0], TimelineItemAppendedEvent)
        assert isinstance(thinking_evs[0].item, ThinkingStreamTimelineItem)
        assert all(isinstance(e, TimelineItemDeltaEvent) for e in thinking_evs[1:-1])
        assert isinstance(thinking_evs[-1], TimelineItemUpdatedEvent)
        assert isinstance(thinking_evs[-1].item, ThinkingTimelineItem)
        assert thinking_evs[-1].item.finalized

        ai_evs = [
            e for e in tl_events
            if (isinstance(e, (TimelineItemAppendedEvent, TimelineItemUpdatedEvent)) and e.item.id == ai.id)
            or (isinstance(e, TimelineItemDeltaEvent) and e.item_id == ai.id)
        ]
        assert isinstance(ai_evs[0], TimelineItemAppendedEvent)
        assert isinstance(ai_evs[0].item, AiStreamTimelineItem)
        deltas = [e for e in ai_evs if isinstance(e, TimelineItemDeltaEvent)]
        assert len(deltas) > 1  # chunked
        assert [e.revision for e in deltas] == list(range(1, len(deltas) + 1))
        assert isinstance(ai_evs[-1], TimelineItemUpdatedEvent)
        assert isinstance(ai_evs[-1].item, AiMessageTimelineItem)

        # Watermarks strictly increase across all timeline events.
        wms = [e.watermark for e in tl_events]
        assert wms == sorted(wms)
        assert len(set(wms)) == len(wms)


@pytest.mark.asyncs('asyncio')
async def test_tool_loop_lifecycle():
    async with timeline_driver_harness(
        _weather_script(),
        enable_tools=True,
        extra_elements=[bind_weather_test()],
    ) as h:
        await h.send_user_text('weather in tokyo?')

        items = h.manager.state.get_items()

        assert [type(it) for it in items] == [
            UserMessageTimelineItem,
            AiMessageTimelineItem,
            ToolUseTimelineItem,
            AiMessageTimelineItem,
        ]

        tool = check.isinstance(items[2], ToolUseTimelineItem)
        assert tool.state is ToolUseTimelineItemState.COMPLETE
        assert tool.finalized
        assert check.not_none(tool.use).name == 'weather'
        assert tool.result is not None
        assert tool.partial_name is None  # cleared by canonical replacement
        assert tool.partial_raw_args is None
        assert tool.execution is not None  # live-only extra

        # One tool item all the way through: STREAMING -> PENDING (canonical) -> RUNNING -> COMPLETE.
        tool_evs = [
            e for e in h.events
            if (isinstance(e, (TimelineItemAppendedEvent, TimelineItemUpdatedEvent)) and e.item.id == tool.id)
        ]
        states = [check.isinstance(e.item, ToolUseTimelineItem).state for e in tool_evs]
        assert states == [
            ToolUseTimelineItemState.STREAMING,
            ToolUseTimelineItemState.PENDING,
            ToolUseTimelineItemState.RUNNING,
            ToolUseTimelineItemState.COMPLETE,
        ]
        assert isinstance(tool_evs[0], TimelineItemAppendedEvent)

        # And the streamed partial args grew through delta events on the same item.
        arg_deltas = [e for e in h.events if isinstance(e, TimelineItemDeltaEvent) and e.item_id == tool.id]
        assert ''.join(check.isinstance(e.appended, str) for e in arg_deltas) == '{"location":"Tokyo"}'

        # The persisted tool use message's uuid is the item's id - identity is stable into replay.
        chat = await h.storage.get_chat()
        tums = [m for m in chat if isinstance(m, ToolUseMessage)]
        assert len(tums) == 1
        assert timeline_item_id_for_message(tums[0]) == tool.id


@pytest.mark.asyncs('asyncio')
async def test_live_replay_convergence():
    scripts = [
        ChatScript([
            ChatScriptTurn.of(
                ThinkingMessage('pondering'),
                AiMessage('the answer is **42**, naturally'),
            ),
        ]),
        _weather_script(),
    ]

    for i, script in enumerate(scripts):
        async with timeline_driver_harness(
            script,
            enable_tools=(i == 1),
            extra_elements=[bind_weather_test()] if i == 1 else [],
        ) as h:
            await h.send_user_text('go')

            live_items = h.manager.state.get_items()
            replayed_items = timeline_translate_chat(await h.storage.get_chat())

            assert canon_items(live_items) == canon_items(replayed_items)


@pytest.mark.asyncs('asyncio')
async def test_non_stream_path():
    script = ChatScript([
        ChatScriptTurn.of(
            AiMessage('a non-streamed response'),
        ),
    ])

    async with timeline_driver_harness(script, stream=False) as h:
        await h.send_user_text('hi')

        items = h.manager.state.get_items()
        assert [type(it) for it in items] == [
            UserMessageTimelineItem,
            AiMessageTimelineItem,
        ]
        assert all(it.finalized for it in items)

        # The talks-down path: no in-flight stream items, no delta events - just canonical appends.
        assert not any(isinstance(e, TimelineItemDeltaEvent) for e in h.events)
        appended = [e for e in h.events if isinstance(e, TimelineItemAppendedEvent)]
        assert all(not isinstance(e.item, AiStreamTimelineItem) for e in appended)

        # And convergence holds here too.
        assert canon_items(items) == canon_items(timeline_translate_chat(await h.storage.get_chat()))


@pytest.mark.asyncs('asyncio')
async def test_stream_error_finalizes_in_flight_item():
    fail_at = 3

    async def gate(pt):
        if pt.emission_index == fail_at:
            raise RuntimeError('scripted stream failure')

    script = ChatScript(
        [ChatScriptTurn.of(AiMessage('this stream will not survive to the end'))],
        gate=gate,
    )

    async with timeline_driver_harness(script) as h:
        with pytest.raises(RuntimeError):
            await h.send_user_text('hi')

        items = h.manager.state.get_items()
        assert [type(it) for it in items] == [
            UserMessageTimelineItem,
            AiStreamTimelineItem,
        ]

        stream = check.isinstance(items[1], AiStreamTimelineItem)
        assert stream.finalized
        assert stream.error is not None
        assert stream.content  # the deltas that made it through

        # Nothing was persisted - the turn never completed.
        assert await h.storage.get_chat() == []


@pytest.mark.asyncs('asyncio')
async def test_message_sequence_across_multiple_actions():
    script = ChatScript([
        ChatScriptTurn.of(AiMessage('first answer')),
        ChatScriptTurn.of(AiMessage('second answer')),
    ])

    async with timeline_driver_harness(script) as h:
        await h.send_user_text('one')
        await h.send_user_text('two')

        items = h.manager.state.get_items()
        assert [type(it) for it in items] == [
            UserMessageTimelineItem,
            AiMessageTimelineItem,
            UserMessageTimelineItem,
            AiMessageTimelineItem,
        ]

        assert canon_items(items) == canon_items(timeline_translate_chat(await h.storage.get_chat()))
