"""
Wire-format fidelity for the timeline surface - the substrate of the web/remote story. Timeline events recorded from a
real scripted run (streaming, thinking, tools) must round-trip through the marshal system stably (marshal -> unmarshal
-> marshal is a fixed point), as must windows and their cursors.
"""
import pytest

from omlish import marshal as msh

from ....backends.scripted.scripts import ChatScript
from ....backends.scripted.scripts import ChatScriptTurn
from ....chat.messages import AiMessage
from ....chat.messages import ThinkingMessage
from ....chat.messages import ToolUseMessage
from ....events.types import Event
from ....modules.weathertest.inject import bind_weather_test
from ....tools.types import ToolUse
from ..events import TimelineEvent
from ..history import TimelineWindow
from .harness import timeline_driver_harness


##


@pytest.mark.asyncs('asyncio')
async def test_timeline_events_marshal_round_trip():
    script = ChatScript([
        ChatScriptTurn.of(
            ThinkingMessage('thinking...'),
            AiMessage('checking the weather now'),
            ToolUseMessage(ToolUse(id='call_1', name='weather', args={'location': 'Tokyo'})),
        ),
        ChatScriptTurn.of(AiMessage('all done')),
    ])

    async with timeline_driver_harness(
        script,
        enable_tools=True,
        extra_elements=[bind_weather_test()],
    ) as h:
        await h.send_user_text('weather?')

        tl_events = [e for e in h.events if isinstance(e, TimelineEvent)]
        assert tl_events

        for ev in tl_events:
            m1 = msh.marshal(ev, Event)
            ev2 = msh.unmarshal(m1, Event)

            assert isinstance(ev2, TimelineEvent)
            assert type(ev2) is type(ev)
            assert ev2.timeline_id == ev.timeline_id
            assert ev2.watermark == ev.watermark

            m2 = msh.marshal(ev2, Event)
            assert m2 == m1


@pytest.mark.asyncs('asyncio')
async def test_timeline_window_marshal_round_trip():
    script = ChatScript([
        ChatScriptTurn.of(
            AiMessage('let me look'),
            ToolUseMessage(ToolUse(id='call_1', name='weather', args={'location': 'Kyoto'})),
        ),
        ChatScriptTurn.of(AiMessage('done')),
    ])

    async with timeline_driver_harness(
        script,
        enable_tools=True,
        extra_elements=[bind_weather_test()],
    ) as h:
        await h.send_user_text('hi')

        window = await h.timeline.get_latest(3)
        assert window.items
        assert window.before_cursor is not None

        m1 = msh.marshal(window, TimelineWindow)
        w2 = msh.unmarshal(m1, TimelineWindow)

        assert [type(it) for it in w2.items] == [type(it) for it in window.items]
        assert [it.id for it in w2.items] == [it.id for it in window.items]
        assert w2.before_cursor == window.before_cursor
        assert w2.has_before == window.has_before

        m2 = msh.marshal(w2, TimelineWindow)
        assert m2 == m1
