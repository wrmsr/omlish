"""
The 'scripted' backend: programmable chat-choices services driven by a `ChatScript`. The streaming service emits a
turn's scripted deltas through the standard stream machinery; the non-stream service 'talks down' by joining the same
deltas through the real `AiDeltaJoiner`. Constructed with no script, both fall back to a looping demo script - handy
for poking frontends offline (`-b scripted`).

Unlike most backends these services are deliberately stateful across invocations: consecutive invocations consume
consecutive script turns, which is exactly what multi-round-trip (tool-looping) driver tests need.
"""
import typing as ta

from omlish import check
from omlish import lang
from omlish import typedvalues as tv

from ...chat.choices.services import ChatChoicesRequest
from ...chat.choices.services import ChatChoicesResponse
from ...chat.choices.services import static_check_is_chat_choices_service
from ...chat.choices.types import ChatChoices
from ...chat.generations import ChatGeneration
from ...chat.messages import AiMessage
from ...chat.messages import ThinkingMessage
from ...chat.stream.choices.services import ChatChoicesStreamRequest
from ...chat.stream.choices.joining import AiChoicesDeltaJoiner
from ...chat.stream.choices.services import ChatChoicesStreamResponse
from ...chat.stream.choices.services import static_check_is_chat_choices_stream_service
from ...chat.stream.choices.types import AiChoicesDeltas
from ...chat.stream.choices.types import ChatChoicesStreamResult
from ...chat.stream.joining import AiDeltaJoiner
from ...configs import Config
from ...resources import UseResources
from ...services import StreamResponseSink
from ...services import new_stream_response
from .scripts import ChatScript
from .scripts import ChatScriptCursor
from .scripts import ChatScriptGatePoint
from .scripts import ChatScriptTurn


##


class ScriptedChatScript(tv.UniqueScalarTypedValue[ChatScript], Config):
    pass


class ScriptedChatCursor(tv.UniqueScalarTypedValue[ChatScriptCursor], Config):
    """
    A *shared* consumption cursor. Service-provider machinery may instantiate a fresh backend per invocation (the
    registry path does); passing a cursor instead of a bare script keeps multi-turn consumption stateful across
    instantiations.
    """


@lang.cached_function
def default_demo_chat_script() -> ChatScript:
    return ChatScript(
        [
            ChatScriptTurn.of(
                ThinkingMessage(
                    'The user has said something. I should respond with some demonstrative markdown.',
                ),
                AiMessage('\n'.join([
                    'Hello! This is the **scripted** backend\'s built-in demo script. It streams:',
                    '',
                    '- some `thinking`,',
                    '- some *markdown* prose,',
                    '- and a code block:',
                    '',
                    '```python',
                    'def greet(name: str) -> str:',
                    "    return f'hello, {name}!'",
                    '```',
                ])),
            ),
            ChatScriptTurn.of(
                AiMessage('\n'.join([
                    'And this is the demo script\'s second (and final) turn - it restarts from here.',
                    '',
                    '> Scripts are consumed turn by turn, one turn per backend invocation.',
                ])),
            ),
        ],
        on_exhausted='restart',
    )


##


class _ScriptedChatChoicesServiceBase:
    def __init__(self, *configs: Config) -> None:
        super().__init__()

        with tv.consume(*configs) as cc:
            cursor_cfg = cc.pop(ScriptedChatCursor, None)
            script_cfg = cc.pop(ScriptedChatScript, None)

        if cursor_cfg is not None:
            check.none(script_cfg)
            self._cursor = cursor_cfg.v
            self._script = self._cursor.script

        else:
            self._script = script_cfg.v if script_cfg is not None else default_demo_chat_script()
            self._cursor = ChatScriptCursor(self._script)

        self._invocations = 0

    @property
    def script(self) -> ChatScript:
        return self._script

    @property
    def invocations(self) -> int:
        return self._invocations

    def _next_turn(self, chat: ta.Any) -> tuple[int, ChatScriptTurn]:
        turn = self._cursor.next_turn()

        invocation_index = self._invocations
        self._invocations += 1

        if (e := turn.expect) is not None:
            e(chat)

        return (invocation_index, turn)


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='scripted',
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class ScriptedChatChoicesService(_ScriptedChatChoicesServiceBase):
    async def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        _, turn = self._next_turn(request.v)

        num_choices_set = {len(em.choices) for em in turn.emissions}
        num_choices = check.single(num_choices_set) if num_choices_set else 1

        joiners = [AiDeltaJoiner() for _ in range(num_choices)]
        for em in turn.emissions:
            for joiner, acd in zip(joiners, em.choices):
                joiner.add(acd.deltas)

        return ChatChoicesResponse(
            ChatChoices([ChatGeneration(joiner.build()) for joiner in joiners]),
            turn.outputs,
        )


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='scripted',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class ScriptedChatChoicesStreamService(_ScriptedChatChoicesServiceBase):
    async def invoke(self, request: ChatChoicesStreamRequest) -> ChatChoicesStreamResponse:
        invocation_index, turn = self._next_turn(request.v)

        gate = self._script.gate

        async with UseResources.or_new(request.options) as rs:
            async def inner(sink: StreamResponseSink[AiChoicesDeltas]) -> ChatChoicesStreamResult:
                joiner = AiChoicesDeltaJoiner()

                for i, em in enumerate(turn.emissions):
                    if gate is not None:
                        await gate(ChatScriptGatePoint(invocation_index, i))

                    joiner.add(em.choices)

                    await sink.emit(em)

                if gate is not None:
                    await gate(ChatScriptGatePoint(invocation_index, len(turn.emissions)))

                return ChatChoicesStreamResult(
                    ChatChoices([
                        ChatGeneration(jc)
                        for jc in joiner.build()
                    ]),
                )

            return await new_stream_response(rs, inner)


##


# @omlish-manifest $.minichain.specs.manifests.BackendStringsManifest(
#     [
#         'ChatChoicesService',
#         'ChatChoicesStreamService',
#     ],
#     'scripted',
# )
