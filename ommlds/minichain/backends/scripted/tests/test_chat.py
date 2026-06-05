import pytest

from omlish import check

from ....chat.choices.services import ChatChoicesRequest
from ....chat.choices.stream.services import ChatChoicesStreamRequest
from ....chat.messages import AiMessage
from ....chat.messages import ThinkingMessage
from ....chat.messages import ToolUseMessage
from ....chat.messages import UserMessage
from ....chat.stream.joining import AiDeltaJoiner
from ....chat.stream.types import ContentAiDelta
from ....chat.stream.types import PartialToolUseAiDelta
from ....tools.types import ToolUse
from ..chat import ScriptedChatChoicesService
from ..chat import ScriptedChatChoicesStreamService
from ..chat import ScriptedChatScript
from ..scripts import ChatScript
from ..scripts import ChatScriptExhaustedError
from ..scripts import ChatScriptTurn


def _two_turn_script(**kwargs) -> ChatScript:
    return ChatScript(
        [
            ChatScriptTurn.of(AiMessage('first response')),
            ChatScriptTurn.of(AiMessage('second response')),
        ],
        **kwargs,
    )


@pytest.mark.asyncs('asyncio')
async def test_non_stream_turn_consumption():
    svc = ScriptedChatChoicesService(ScriptedChatScript(_two_turn_script()))

    resp = await svc.invoke(ChatChoicesRequest([UserMessage('hi')]))
    assert [check.isinstance(m, AiMessage).c for m in check.single(resp.v).chat] == ['first response']

    resp = await svc.invoke(ChatChoicesRequest([UserMessage('again')]))
    assert [check.isinstance(m, AiMessage).c for m in check.single(resp.v).chat] == ['second response']

    with pytest.raises(ChatScriptExhaustedError):
        await svc.invoke(ChatChoicesRequest([UserMessage('one more')]))


@pytest.mark.asyncs('asyncio')
async def test_exhaustion_repeat_last():
    svc = ScriptedChatChoicesService(ScriptedChatScript(_two_turn_script(on_exhausted='repeat_last')))

    for expected in ['first response', 'second response', 'second response', 'second response']:
        resp = await svc.invoke(ChatChoicesRequest([UserMessage('hi')]))
        assert [check.isinstance(m, AiMessage).c for m in check.single(resp.v).chat] == [expected]


@pytest.mark.asyncs('asyncio')
async def test_exhaustion_restart():
    svc = ScriptedChatChoicesService(ScriptedChatScript(_two_turn_script(on_exhausted='restart')))

    for expected in ['first response', 'second response', 'first response', 'second response']:
        resp = await svc.invoke(ChatChoicesRequest([UserMessage('hi')]))
        assert [check.isinstance(m, AiMessage).c for m in check.single(resp.v).chat] == [expected]


@pytest.mark.asyncs('asyncio')
async def test_default_demo_script():
    svc = ScriptedChatChoicesService()

    for _ in range(3):
        resp = await svc.invoke(ChatChoicesRequest([UserMessage('hi')]))
        assert check.single(resp.v).chat


@pytest.mark.asyncs('asyncio')
async def test_expect_hook():
    def expect_first(chat):
        assert isinstance(chat[-1], UserMessage)
        assert chat[-1].c == 'the right thing'

    svc = ScriptedChatChoicesService(ScriptedChatScript(ChatScript([
        ChatScriptTurn.of(AiMessage('ok'), expect=expect_first),
    ])))

    with pytest.raises(AssertionError):
        await svc.invoke(ChatChoicesRequest([UserMessage('the wrong thing')]))


@pytest.mark.asyncs('asyncio')
async def test_stream_chunking_and_join_round_trip():
    messages = [
        ThinkingMessage('let me think about this for a bit'),
        AiMessage('I will now call a tool to handle that request.'),
        ToolUseMessage(ToolUse(
            id='call_1',
            name='echo',
            args={'s': 'hello there, how are you?'},
        )),
    ]

    script = ChatScript([ChatScriptTurn.of(*messages, chunk_size=5)])

    svc = ScriptedChatChoicesStreamService(ScriptedChatScript(script))

    emissions = []
    async with (await svc.invoke(ChatChoicesStreamRequest([UserMessage('hi')]))).v as st:
        async for em in st:
            emissions.append(em)

    # One delta per emission, content chunked - far more emissions than messages.
    assert len(emissions) > len(messages)
    deltas = [d for em in emissions for d in check.single(em.choices).deltas]
    assert max(len(check.isinstance(d.c, str)) for d in deltas if isinstance(d, ContentAiDelta)) <= 5

    # Tool use arrives as a head delta plus raw-args chunks.
    ptus = [d for d in deltas if isinstance(d, PartialToolUseAiDelta)]
    assert ptus[0].id == 'call_1'
    assert ptus[0].name == 'echo'
    assert all(p.id is None and p.name is None for p in ptus[1:])

    # And the real joiner reassembles the original messages.
    joiner = AiDeltaJoiner()
    for em in emissions:
        joiner.add(check.single(em.choices).deltas)
    joined = joiner.build()

    assert [type(m) for m in joined] == [ThinkingMessage, AiMessage, ToolUseMessage]
    assert check.isinstance(joined[0], ThinkingMessage).c == messages[0].c  # type: ignore[attr-defined]
    assert check.isinstance(joined[1], AiMessage).c == messages[1].c  # type: ignore[attr-defined]
    jtu = check.isinstance(joined[2], ToolUseMessage).tu
    assert jtu.id == 'call_1'
    assert jtu.name == 'echo'
    assert jtu.args == {'s': 'hello there, how are you?'}


@pytest.mark.asyncs('asyncio')
async def test_stream_multiple_sequential_tool_uses():
    script = ChatScript([ChatScriptTurn.of(
        ToolUseMessage(ToolUse(id='call_a', name='tool_a', args={'x': 1})),
        ToolUseMessage(ToolUse(id='call_b', name='tool_b', args={'y': 2})),
    )])

    svc = ScriptedChatChoicesStreamService(ScriptedChatScript(script))

    joiner = AiDeltaJoiner()
    async with (await svc.invoke(ChatChoicesStreamRequest([UserMessage('hi')]))).v as st:
        async for em in st:
            joiner.add(check.single(em.choices).deltas)
    joined = joiner.build()

    assert [check.isinstance(m, ToolUseMessage).tu.id for m in joined] == ['call_a', 'call_b']
    assert [m.tu.name for m in joined] == ['tool_a', 'tool_b']  # type: ignore[attr-defined]


@pytest.mark.asyncs('asyncio')
async def test_stream_indexed_parallel_tool_uses():
    script = ChatScript([ChatScriptTurn.of(
        ToolUseMessage(ToolUse(id='call_a', name='tool_a', args={'x': 1})),
        ToolUseMessage(ToolUse(id='call_b', name='tool_b', args={'y': 2})),
        indexed_tool_uses=True,
    )])

    svc = ScriptedChatChoicesStreamService(ScriptedChatScript(script))

    deltas: list = []
    async with (await svc.invoke(ChatChoicesStreamRequest([UserMessage('hi')]))).v as st:
        async for em in st:
            deltas.extend(check.single(em.choices).deltas)

    assert {check.isinstance(d, PartialToolUseAiDelta).index for d in deltas} == {0, 1}

    joiner = AiDeltaJoiner()
    joiner.add(deltas)
    joined = joiner.build()

    assert [check.isinstance(m, ToolUseMessage).tu.id for m in joined] == ['call_a', 'call_b']


@pytest.mark.asyncs('asyncio')
async def test_gate_points():
    points = []

    async def gate(pt):
        points.append((pt.invocation_index, pt.emission_index))

    script = ChatScript(
        [
            ChatScriptTurn.of(AiMessage('abcdefghij'), chunk_size=5),
            ChatScriptTurn.of(AiMessage('123'), chunk_size=None),
        ],
        gate=gate,
    )

    svc = ScriptedChatChoicesStreamService(ScriptedChatScript(script))

    for _ in range(2):
        async with (await svc.invoke(ChatChoicesStreamRequest([UserMessage('hi')]))).v as st:
            async for _ in st:  # noqa
                pass

    # Two emissions in turn 0 (2 chunks), one in turn 1 - gated before each plus once after the last.
    assert points == [
        (0, 0), (0, 1), (0, 2),
        (1, 0), (1, 1),
    ]
