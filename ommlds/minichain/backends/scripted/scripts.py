"""
The script model for the 'scripted' backend: a `ChatScript` is a sequence of turns, each turn describing the exact
stream a backend invocation will emit. Turns are most easily built from messages via `ChatScriptTurn.of`, which derives
realistic delta scripts (chunked content, partial tool-use args, thinking) - the same wire shapes real streaming
backends produce.

Scripts exist to make the full driver loop - streaming, tool round-trips, multi-turn conversations - exercisable
offline, deterministically, with no mocks and no network. See the `scripted.chat` services for the consuming side, and
`ChatScript.gate` for the lock-step lever tests use to interleave actions at exact mid-stream points.
"""
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish.formats.json import all as json

from ...chat.choices.stream.types import AiChoiceDeltas
from ...chat.choices.stream.types import AiChoicesDeltas
from ...chat.choices.types import ChatChoicesOutputs
from ...chat.messages import AiMessage
from ...chat.messages import AnyAiMessage
from ...chat.messages import Chat
from ...chat.messages import ThinkingMessage
from ...chat.messages import ToolUseMessage
from ...chat.stream.types import AiDelta
from ...chat.stream.types import ContentAiDelta
from ...chat.stream.types import PartialToolUseAiDelta
from ...chat.stream.types import ThinkingAiDelta


ChatScriptTurnExpectation: ta.TypeAlias = ta.Callable[[Chat], None]

ChatScriptGate: ta.TypeAlias = ta.Callable[['ChatScriptGatePoint'], ta.Awaitable[None]]


##


class ChatScriptError(Exception):
    pass


class ChatScriptExhaustedError(ChatScriptError):
    """Raised when a service is invoked more times than its script has turns (under `on_exhausted='raise'`)."""


##


@dc.dataclass(frozen=True)
class ChatScriptGatePoint(lang.Final):
    """
    Identifies a point in a stream service's emission sequence: before emission `emission_index` of invocation
    `invocation_index`, plus one final point per invocation with `emission_index == len(turn.emissions)` after the last
    emission (while the stream is still open).
    """

    invocation_index: int
    emission_index: int


##


DEFAULT_CHAT_SCRIPT_CHUNK_SIZE: int = 8


def chunk_script_text(s: str, chunk_size: int | None) -> ta.Sequence[str]:
    if chunk_size is None or chunk_size <= 0 or chunk_size >= len(s):
        return [s]

    return [s[i:i + chunk_size] for i in range(0, len(s), chunk_size)]


def build_ai_message_deltas(
        m: AiMessage,
        *,
        chunk_size: int | None = DEFAULT_CHAT_SCRIPT_CHUNK_SIZE,
) -> ta.Sequence[AiDelta]:
    return [
        ContentAiDelta(c)
        for c in chunk_script_text(check.isinstance(m.c, str), chunk_size)
    ]


def build_thinking_message_deltas(
        m: ThinkingMessage,
        *,
        chunk_size: int | None = DEFAULT_CHAT_SCRIPT_CHUNK_SIZE,
) -> ta.Sequence[AiDelta]:
    return [
        ThinkingAiDelta(c)
        for c in chunk_script_text(m.c, chunk_size)
    ]


def build_tool_use_message_deltas(
        m: ToolUseMessage,
        *,
        chunk_size: int | None = DEFAULT_CHAT_SCRIPT_CHUNK_SIZE,
        index: int | None = None,
) -> ta.Sequence[AiDelta]:
    """
    Emits the partial-tool-use wire shape real backends produce: a head delta carrying id/name, followed by raw-args
    text chunks. Note that turns containing multiple sequential (unindexed) tool uses require the uses to have distinct
    non-None ids for downstream joining to separate them - as real backends provide.
    """

    tu = m.tu

    ra = tu.raw_args if tu.raw_args is not None else json.dumps_compact(dict(tu.args))

    out: list[AiDelta] = [PartialToolUseAiDelta(
        id=tu.id,
        name=tu.name,
        index=index,
    )]

    out.extend(
        PartialToolUseAiDelta(
            raw_args=c,
            index=index,
        )
        for c in chunk_script_text(ra, chunk_size)
        if c
    )

    return out


##


@dc.dataclass(frozen=True)
class ChatScriptTurn(lang.Final):
    """
    One backend invocation's worth of scripted behavior. Each element of `emissions` is delivered as one stream
    emission (one `sink.emit`); the non-stream service joins them. `expect`, if given, is called with the incoming
    request chat before any emission - use it to assert multi-turn conversations are progressing as scripted (and to
    fail at the turn that went wrong, not at the end).
    """

    emissions: ta.Sequence[AiChoicesDeltas]

    _: dc.KW_ONLY

    outputs: ta.Sequence[ChatChoicesOutputs] = ()

    expect: ChatScriptTurnExpectation | None = dc.field(default=None, repr=False)

    @classmethod
    def of(
            cls,
            *messages: AnyAiMessage,
            chunk_size: int | None = DEFAULT_CHAT_SCRIPT_CHUNK_SIZE,
            indexed_tool_uses: bool = False,
            outputs: ta.Sequence[ChatChoicesOutputs] = (),
            expect: ChatScriptTurnExpectation | None = None,
    ) -> ChatScriptTurn:
        """
        Builds a single-choice turn from messages, deriving one delta per emission. With `indexed_tool_uses`, tool use
        messages are emitted in the indexed parallel-call wire form (note that joining emits indexed tool uses after
        all non-indexed messages - list tool uses last for a faithful round-trip).
        """

        deltas: list[AiDelta] = []
        tool_idx = 0

        for m in messages:
            if isinstance(m, AiMessage):
                deltas.extend(build_ai_message_deltas(m, chunk_size=chunk_size))

            elif isinstance(m, ThinkingMessage):
                deltas.extend(build_thinking_message_deltas(m, chunk_size=chunk_size))

            elif isinstance(m, ToolUseMessage):
                deltas.extend(build_tool_use_message_deltas(
                    m,
                    chunk_size=chunk_size,
                    index=tool_idx if indexed_tool_uses else None,
                ))
                tool_idx += 1

            else:
                raise TypeError(m)

        return cls(
            [
                AiChoicesDeltas([AiChoiceDeltas([d])])
                for d in deltas
            ],
            outputs=outputs,
            expect=expect,
        )


@dc.dataclass(frozen=True)
class ChatScript(lang.Final):
    turns: ta.Sequence[ChatScriptTurn]

    _: dc.KW_ONLY

    on_exhausted: ta.Literal['raise', 'repeat_last', 'restart'] = 'raise'

    gate: ChatScriptGate | None = dc.field(default=None, repr=False)


##


class ChatScriptCursor:
    """Mutable consumption state over an immutable script. Each service instance owns one."""

    def __init__(self, script: ChatScript) -> None:
        super().__init__()

        self._script = script

        self._next = 0

    @property
    def script(self) -> ChatScript:
        return self._script

    def next_turn(self) -> ChatScriptTurn:
        turns = self._script.turns

        if (i := self._next) < len(turns):
            self._next = i + 1
            return turns[i]

        if not turns:
            raise ChatScriptExhaustedError

        match self._script.on_exhausted:
            case 'raise':
                raise ChatScriptExhaustedError

            case 'repeat_last':
                return turns[-1]

            case 'restart':
                self._next = 1
                return turns[0]

            case _:
                raise ValueError(self._script.on_exhausted)
