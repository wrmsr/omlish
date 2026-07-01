import dataclasses as dc
import typing as ta


##


class StreamDeltaToolCall:
    pass


@dc.dataclass(frozen=True, kw_only=True)
class StreamDeltaToolCallFunction:
    arguments: str | None = None
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class FunctionStreamDeltaToolCall[
    FunctionT: StreamDeltaToolCallFunction = StreamDeltaToolCallFunction,
](
    StreamDeltaToolCall,
):
    index: int
    function: FunctionT | None = None
    id: str | None = None
    type: ta.Literal['function'] | None = None


##


class StreamDelta:
    pass


@dc.dataclass(frozen=True, kw_only=True)
class AssistantStreamDelta[
    ToolCallT: StreamDeltaToolCall = StreamDeltaToolCall,
](
    StreamDelta,
):
    content: str | None = None
    role: ta.Literal['assistant'] | None = None
    tool_calls: ta.Sequence[ToolCallT] | None = None


##


@dc.dataclass(frozen=True, kw_only=True)
class StreamChoice[
    DeltaT: StreamDelta = StreamDelta,
    FinishReasonT: str = str,
]:
    index: int
    delta: DeltaT
    finish_reason: FinishReasonT | None


##


@dc.dataclass(frozen=True, kw_only=True)
class StreamChunk[
    ChoiceT: StreamChoice = StreamChoice,
    UsageT: Usage = Usage,
]:
    id: str
    object: ta.Literal['chat.completion.chunk'] = 'chat.completion.chunk'
    created: int
    model: str
    choices: ta.Sequence[ChoiceT]
    usage: UsageT | None = None
