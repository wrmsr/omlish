import dataclasses as dc
import typing as ta

from ..responses import Usage
from ..typetags import TypeTagged


##


class StreamDeltaToolCall(
    TypeTagged,
    type_tag_field='type',
):
    pass


#


@dc.dataclass(frozen=True, kw_only=True)
class FunctionStreamDeltaToolCallFunction:
    arguments: str | None = None
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class FunctionStreamDeltaToolCall[
    FunctionStreamDeltaToolCallFunctionT: FunctionStreamDeltaToolCallFunction = FunctionStreamDeltaToolCallFunction,
](
    StreamDeltaToolCall,
    type_tag='function',
):
    index: int
    function: FunctionStreamDeltaToolCallFunctionT | None = None
    id: str | None = None


##


class StreamDelta(
    TypeTagged,
    type_tag_field='role',
):
    pass


#


@dc.dataclass(frozen=True, kw_only=True)
class AssistantStreamDelta[
    StreamDeltaToolCallT: StreamDeltaToolCall = StreamDeltaToolCall,
](
    StreamDelta,
    type_tag='assistant',
):
    content: str | None = None
    tool_calls: ta.Sequence[StreamDeltaToolCallT] | None = None


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
](
    TypeTagged,
    type_tag_field='object',
    type_tag='chat.completion.chunk',
):
    id: str
    created: int
    model: str
    choices: ta.Sequence[ChoiceT]
    usage: UsageT | None = None
