"""
Offline end-to-end driver tests over the scripted backend: full streaming generation and a real tool round-trip, with
no network and no mocks. This is the wiring to crib from when writing driver-level tests.
"""
import typing as ta

import pytest

from omcore import check
from omcore import inject as inj

from ...backends.scripted.scripts import ChatScript
from ...backends.scripted.scripts import ChatScriptTurn
from ...chat.events import AiMessagesEvent
from ...chat.events import UserMessagesEvent
from ...chat.messages import AiMessage
from ...chat.messages import Message
from ...chat.messages import ThinkingMessage
from ...chat.messages import ToolUseMessage
from ...chat.messages import ToolUseResultMessage
from ...chat.messages import UserMessage
from ...chat.stream.events import AiStreamBeginEvent
from ...chat.stream.events import AiStreamDeltaEvent
from ...chat.stream.events import AiStreamEndEvent
from ...content.render.standard import render_content_str
from ...events.injection import event_callbacks
from ...events.types import Event
from ...modules.weathertest.inject import bind_weather_test
from ...tools.execution.events import ToolUseEvent
from ...tools.execution.events import ToolUseResultEvent
from ...tools.types import ToolUse
from ..actions import SendUserMessagesAction
from ..ai.configs import AiConfig
from ..configs import DriverConfig
from ..storage.manager import DriverStorageManager
from ..testing import bind_scripted_driver
from ..types import Driver


##


@pytest.mark.asyncs('asyncio')
async def test_scripted_stream_driver():
    script = ChatScript([
        ChatScriptTurn.of(
            ThinkingMessage('thinking about it'),
            AiMessage('a considered response'),
        ),
    ])

    events: list[Event] = []

    async def on_event(event: Event) -> None:
        events.append(event)

    async with inj.create_async_managed_injector(
        bind_scripted_driver(script, DriverConfig(ai=AiConfig(stream=True))),
        event_callbacks().bind_item(to_const=on_event),
    ) as injector:
        driver = await injector[Driver]

        await driver.start()
        await driver.do_action(SendUserMessagesAction([UserMessage('hi there')]))
        await driver.stop()

        chat = await (await injector[DriverStorageManager]).get_chat()

    assert [type(m) for m in chat] == [UserMessage, ThinkingMessage, AiMessage]
    assert check.isinstance(chat[2], AiMessage).c == 'a considered response'

    assert any(isinstance(e, UserMessagesEvent) for e in events)
    assert any(isinstance(e, AiStreamBeginEvent) for e in events)
    assert sum(isinstance(e, AiStreamDeltaEvent) for e in events) > 2  # chunked
    assert any(isinstance(e, AiStreamEndEvent) for e in events)
    assert any(isinstance(e, AiMessagesEvent) and e.streamed for e in events)


@pytest.mark.asyncs('asyncio')
async def test_scripted_stream_driver_tool_loop():
    def expect_tool_result(chat: ta.Sequence[Message]) -> None:
        turm = check.isinstance(chat[-1], ToolUseResultMessage)
        assert 'Foggy in Tokyo' in render_content_str(turm.tur.c)

    script = ChatScript([
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
            expect=expect_tool_result,
        ),
    ])

    events: list[Event] = []

    async def on_event(event: Event) -> None:
        events.append(event)

    async with inj.create_async_managed_injector(
        bind_scripted_driver(
            script,
            DriverConfig(ai=AiConfig(
                stream=True,
                enable_tools=True,
            )),
        ),
        bind_weather_test(),
        event_callbacks().bind_item(to_const=on_event),
    ) as injector:
        driver = await injector[Driver]

        await driver.start()
        await driver.do_action(SendUserMessagesAction([UserMessage('what is the weather in tokyo?')]))
        await driver.stop()

        chat = await (await injector[DriverStorageManager]).get_chat()

    assert [type(m) for m in chat] == [
        UserMessage,
        AiMessage,
        ToolUseMessage,
        ToolUseResultMessage,
        AiMessage,
    ]
    assert check.isinstance(chat[4], AiMessage).c == 'It is foggy in Tokyo.'

    tues = [e for e in events if isinstance(e, ToolUseEvent)]
    turs = [e for e in events if isinstance(e, ToolUseResultEvent)]
    assert len(tues) == 1
    assert len(turs) == 1
    assert tues[0].use.id == 'call_1'
    assert 'Foggy in Tokyo' in render_content_str(turs[0].tur.c)

    # Begin/End demarcate per-message spans within streams (not LLM segments): segment one streams prose then tool
    # partials (two message uuids), segment two streams prose - three spans. Joined messages events are per-segment.
    assert sum(isinstance(e, AiStreamBeginEvent) for e in events) == 3
    assert sum(isinstance(e, AiStreamEndEvent) for e in events) == 3
    assert sum(isinstance(e, AiMessagesEvent) and e.streamed for e in events) == 2
