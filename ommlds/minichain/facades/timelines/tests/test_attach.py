"""
The attach-coherence suite: the watermark/attach contract under adversarial timing, choreographed deterministically
via the scripted backend's gate (no sleeps). The property under test, every time:

    projection(attach.window) + attach.subscription events == live state. Exactly. No gaps, no duplicates.

...regardless of when the attach happens: before anything, mid-prose-stream, mid-tool-args-stream, between turns of a
tool loop, or after everything. Plus: paging during streaming, and multiple subscribers attached at different moments
all converging on identical views.
"""
import asyncio
import uuid

import pytest

from omlish import check

from ....backends.scripted.scripts import ChatScript
from ....backends.scripted.scripts import ChatScriptTurn
from ....chat.messages import AiMessage
from ....chat.messages import ThinkingMessage
from ....chat.messages import ToolUseMessage
from ....drivers.storage.types import ChatId
from ....modules.weathertest.inject import bind_weather_test
from ....tools.types import ToolUse
from ..items import AiStreamTimelineItem
from ..items import ToolUseTimelineItem
from ..items import ToolUseTimelineItemState
from ..items import UserMessageTimelineItem
from ..projection import TimelineProjection
from ..timeline import TimelineAttachment
from .harness import PausingGate
from .harness import timeline_driver_harness


##


async def _project_to_completion(att: TimelineAttachment, h) -> TimelineProjection:
    """Applies the attachment's window and all buffered events - state must already be quiescent."""

    proj = TimelineProjection()
    proj.initialize(att.window)

    for ev in att.subscription.drain_pending():
        assert ev.watermark > att.watermark
        proj.apply_event(ev)

    return proj


def _assert_projection_equals_state(proj: TimelineProjection, h) -> None:
    assert list(proj.items) == list(h.manager.state.get_items())


##


@pytest.mark.asyncs('asyncio')
async def test_attach_mid_prose_stream():
    gate = PausingGate(lambda pt: pt.invocation_index == 0 and pt.emission_index == 4)

    script = ChatScript(
        [ChatScriptTurn.of(AiMessage('a response of considerable length, streamed in many small chunks'))],
        gate=gate,
    )

    async with timeline_driver_harness(script) as h:
        task = asyncio.create_task(h.send_user_text('hi'))
        await gate.wait_paused()

        # Parked mid-stream: 4 emissions have fully flowed. Attach now.
        att = await h.timeline.attach(50)
        async with att:
            assert [type(it) for it in att.window.items] == [UserMessageTimelineItem, AiStreamTimelineItem]
            stream = check.isinstance(att.window.items[1], AiStreamTimelineItem)
            assert not stream.finalized
            assert stream.content  # mid-accumulation

            gate.resume()
            await task

            proj = await _project_to_completion(att, h)
            _assert_projection_equals_state(proj, h)

            # The in-flight item finished through deltas + replacement applied on top of the mid-stream snapshot.
            assert proj.items[1].finalized
            assert proj.items[1].message.c == 'a response of considerable length, streamed in many small chunks'  # type: ignore[attr-defined]  # noqa


@pytest.mark.asyncs('asyncio')
async def test_attach_mid_tool_args_stream():
    gate = PausingGate(
        # Pause while the tool call's args are streaming in: past the prose (5 chars / chunk_size 8 -> 1 emission),
        # past the partial head, into the raw-args chunks.
        lambda pt: pt.invocation_index == 0 and pt.emission_index == 4,
    )

    script = ChatScript(
        [
            ChatScriptTurn.of(
                AiMessage('hmm..'),
                ToolUseMessage(ToolUse(id='call_1', name='weather', args={'location': 'Tokyo'})),
            ),
            ChatScriptTurn.of(AiMessage('foggy!')),
        ],
        gate=gate,
    )

    async with timeline_driver_harness(
        script,
        enable_tools=True,
        extra_elements=[bind_weather_test()],
    ) as h:
        task = asyncio.create_task(h.send_user_text('weather?'))
        await gate.wait_paused()

        att = await h.timeline.attach(50)
        async with att:
            tool = check.isinstance(att.window.items[-1], ToolUseTimelineItem)
            assert tool.state is ToolUseTimelineItemState.STREAMING
            assert tool.partial_name == 'weather'

            gate.resume()
            await task

            proj = await _project_to_completion(att, h)
            _assert_projection_equals_state(proj, h)

            final_tool = check.isinstance(proj.get_item(tool.id), ToolUseTimelineItem)
            assert final_tool.state is ToolUseTimelineItemState.COMPLETE
            assert final_tool.finalized
            assert final_tool.result is not None


@pytest.mark.asyncs('asyncio')
async def test_attach_between_tool_loop_turns():
    gate = PausingGate(lambda pt: pt.invocation_index == 1 and pt.emission_index == 0)

    script = ChatScript(
        [
            ChatScriptTurn.of(ToolUseMessage(ToolUse(id='call_1', name='weather', args={'location': 'Osaka'}))),
            ChatScriptTurn.of(AiMessage('the weather has been checked')),
        ],
        gate=gate,
    )

    async with timeline_driver_harness(
        script,
        enable_tools=True,
        extra_elements=[bind_weather_test()],
    ) as h:
        task = asyncio.create_task(h.send_user_text('go'))
        await gate.wait_paused()

        # Parked before the second LLM segment: the tool has run to COMPLETE.
        att = await h.timeline.attach(50)
        async with att:
            tool = check.isinstance(att.window.items[-1], ToolUseTimelineItem)
            assert tool.state is ToolUseTimelineItemState.COMPLETE

            gate.resume()
            await task

            proj = await _project_to_completion(att, h)
            _assert_projection_equals_state(proj, h)


@pytest.mark.asyncs('asyncio')
async def test_subscribers_attached_at_different_moments_converge():
    gate = PausingGate(lambda pt: pt.emission_index == 2)

    script = ChatScript(
        [ChatScriptTurn.of(
            ThinkingMessage('let me think'),
            AiMessage('considered and thorough'),
        )],
        gate=gate,
    )

    async with timeline_driver_harness(script) as h:
        # Subscriber A: before anything.
        att_a = await h.timeline.attach(50)

        task = asyncio.create_task(h.send_user_text('hi'))
        await gate.wait_paused()

        # Subscriber B: mid-stream.
        att_b = await h.timeline.attach(50)

        gate.resume()
        await task

        # Subscriber C: after completion.
        att_c = await h.timeline.attach(50)

        async with att_a, att_b, att_c:
            projs = []
            for att in (att_a, att_b, att_c):
                proj = await _project_to_completion(att, h)
                _assert_projection_equals_state(proj, h)
                projs.append(proj)

            assert list(projs[0].items) == list(projs[1].items) == list(projs[2].items)


@pytest.mark.asyncs('asyncio')
async def test_paging_back_while_streaming(tmp_path):
    """Lazy scrollback during an active stream: pages stay coherent, the in-flight tail keeps flowing."""

    db = str(tmp_path / 'chat.db')
    chat_id = ChatId(uuid.uuid7())

    prior_script = ChatScript([
        ChatScriptTurn.of(AiMessage(f'old answer {i}'))
        for i in range(3)
    ])
    async with timeline_driver_harness(prior_script, chat_id=chat_id, db_file_path=db) as h:
        for i in range(3):
            await h.send_user_text(f'old question {i}')

    gate = PausingGate(lambda pt: pt.emission_index == 3)
    script = ChatScript(
        [ChatScriptTurn.of(AiMessage('the new streaming answer, long enough to chunk'))],
        gate=gate,
    )

    async with timeline_driver_harness(script, chat_id=chat_id, db_file_path=db) as h:
        task = asyncio.create_task(h.send_user_text('new question'))
        await gate.wait_paused()

        # Attach with a small window mid-stream, then page back across the seam into storage - twice.
        att = await h.timeline.attach(2)
        async with att:
            proj = TimelineProjection()
            proj.initialize(att.window)
            assert isinstance(proj.items[-1], AiStreamTimelineItem)  # the in-flight tail
            assert att.window.has_before

            w1 = await h.timeline.get_before(check.not_none(att.window.before_cursor), 3)
            proj.prepend_window(w1)

            w2 = await h.timeline.get_before(check.not_none(w1.before_cursor), 100)
            proj.prepend_window(w2)
            assert not w2.has_before

            gate.resume()
            await task

            for ev in att.subscription.drain_pending():
                proj.apply_event(ev)

            # The projection now holds the *entire* conversation - storage prefix and the completed live turn - in
            # order, with the live suffix exactly equal to live state.
            texts = [getattr(it, 'message', None) and it.message.c for it in proj.items]  # type: ignore[attr-defined]
            assert texts == [
                'old question 0', 'old answer 0',
                'old question 1', 'old answer 1',
                'old question 2', 'old answer 2',
                'new question', 'the new streaming answer, long enough to chunk',
            ]

            live = list(h.manager.state.get_items())
            assert list(proj.items)[-len(live):] == live


@pytest.mark.asyncs('asyncio')
async def test_attach_quiescent_sees_no_events():
    script = ChatScript([ChatScriptTurn.of(AiMessage('done and dusted'))])

    async with timeline_driver_harness(script) as h:
        await h.send_user_text('hi')

        att = await h.timeline.attach(50)
        async with att:
            assert att.subscription.drain_pending() == []
            proj = TimelineProjection()
            proj.initialize(att.window)
            _assert_projection_equals_state(proj, h)
