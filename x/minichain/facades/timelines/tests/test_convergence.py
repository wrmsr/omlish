"""
The broader convergence suite (beyond test_manager's core cases): parallel tool calls, multi-turn tool loops across
multiple user actions, and recovery after a failed stream. The invariant throughout: for every *completed* turn, live
state ≡ replay translation of storage (modulo revision and live-only fields). Failed turns persist nothing and are
live-only by design.
"""
import pytest

from omcore import check

from ....backends.scripted.scripts import ChatScript
from ....backends.scripted.scripts import ChatScriptTurn
from ....chat.messages import AiMessage
from ....chat.messages import ToolUseMessage
from ....modules.weathertest.inject import bind_weather_test
from ....tools.types import ToolUse
from ..items import AiMessageTimelineItem
from ..items import AiStreamTimelineItem
from ..items import ToolUseTimelineItem
from ..items import ToolUseTimelineItemState
from ..items import UserMessageTimelineItem
from ..translate import timeline_translate_chat
from .harness import timeline_driver_harness
from .test_manager import canon_items


##


@pytest.mark.asyncs('asyncio')
async def test_parallel_tool_calls_converge():
    script = ChatScript([
        ChatScriptTurn.of(
            AiMessage('I will check both cities.'),
            ToolUseMessage(ToolUse(id='call_a', name='weather', args={'location': 'Tokyo'})),
            ToolUseMessage(ToolUse(id='call_b', name='weather', args={'location': 'Osaka'})),
            indexed_tool_uses=True,
        ),
        ChatScriptTurn.of(AiMessage('Both foggy. Classic.')),
    ])

    async with timeline_driver_harness(
        script,
        enable_tools=True,
        extra_elements=[bind_weather_test()],
    ) as h:
        await h.send_user_text('tokyo and osaka?')

        items = h.manager.state.get_items()

        tools = [it for it in items if isinstance(it, ToolUseTimelineItem)]
        assert len(tools) == 2
        assert {check.not_none(t.use).id for t in tools} == {'call_a', 'call_b'}
        assert all(t.state is ToolUseTimelineItemState.COMPLETE for t in tools)
        assert all(t.result is not None for t in tools)

        assert canon_items(items) == canon_items(timeline_translate_chat(await h.storage.get_chat()))


@pytest.mark.asyncs('asyncio')
async def test_multi_action_tool_loops_converge():
    script = ChatScript([
        ChatScriptTurn.of(ToolUseMessage(ToolUse(id='c1', name='weather', args={'location': 'A'}))),
        ChatScriptTurn.of(AiMessage('first done')),
        ChatScriptTurn.of(ToolUseMessage(ToolUse(id='c2', name='weather', args={'location': 'B'}))),
        ChatScriptTurn.of(AiMessage('second done')),
    ])

    async with timeline_driver_harness(
        script,
        enable_tools=True,
        extra_elements=[bind_weather_test()],
    ) as h:
        await h.send_user_text('first')
        await h.send_user_text('second')

        items = h.manager.state.get_items()

        assert [type(it) for it in items] == [
            UserMessageTimelineItem,
            ToolUseTimelineItem,
            AiMessageTimelineItem,
            UserMessageTimelineItem,
            ToolUseTimelineItem,
            AiMessageTimelineItem,
        ]

        assert canon_items(items) == canon_items(timeline_translate_chat(await h.storage.get_chat()))


@pytest.mark.asyncs('asyncio')
async def test_recovery_after_failed_stream():
    """A failed turn leaves its errored in-flight item live-only; the next turn proceeds cleanly."""

    fail_once = {'done': False}

    async def gate(pt):
        if pt.invocation_index == 0 and pt.emission_index == 2 and not fail_once['done']:
            fail_once['done'] = True
            raise RuntimeError('scripted mid-stream failure')

    script = ChatScript(
        [
            ChatScriptTurn.of(AiMessage('this answer dies midway')),
            ChatScriptTurn.of(AiMessage('this answer survives')),
        ],
        gate=gate,
    )

    async with timeline_driver_harness(script) as h:
        with pytest.raises(RuntimeError):
            await h.send_user_text('one')

        await h.send_user_text('two')

        items = h.manager.state.get_items()
        assert [type(it) for it in items] == [
            UserMessageTimelineItem,
            AiStreamTimelineItem,  # errored, finalized, live-only
            UserMessageTimelineItem,
            AiMessageTimelineItem,
        ]

        errored = check.isinstance(items[1], AiStreamTimelineItem)
        assert errored.finalized
        assert errored.error is not None

        # Storage holds only the completed turn (the failed turn persisted nothing, its user message included);
        # replay equals live minus the entire failed turn.
        replayed = timeline_translate_chat(await h.storage.get_chat())
        assert canon_items(replayed) == canon_items([items[2], items[3]])
