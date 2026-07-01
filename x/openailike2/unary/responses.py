import dataclasses as dc
import typing as ta


##


class ResponseToolCall:
    pass


@dc.dataclass(frozen=True, kw_only=True)
class ResponseToolCallFunction:
    arguments: str
    name: str


@dc.dataclass(frozen=True, kw_only=True)
class FunctionResponse[
FunctionT: ResponseToolCallFunction = ResponseToolCallFunction,
](
    ResponseToolCall,
):
    id: str
    function: FunctionT
    type: ta.Literal['function'] = 'function'


##


class ResponseMessage:
    pass


@dc.dataclass(frozen=True, kw_only=True)
class AssistantResponseMessage[
    ToolCallT: ResponseToolCall = ResponseToolCall,
](
    ResponseMessage,
):
    content: str | None = None
    role: ta.Literal['assistant'] = 'assistant'
    tool_calls: ta.Sequence[ToolCallT] | None = None


##


@dc.dataclass(frozen=True, kw_only=True)
class Choice[
    MessageT: ResponseMessage = ResponseMessage,
    FinishReasonT: str = str,
]:
    index: int
    message: MessageT
    finish_reason: FinishReasonT | None


##


@dc.dataclass(frozen=True, kw_only=True)
class Response[
    ChoiceT: Choice = Choice,
    UsageT: Usage = Usage,
]:
    id: str
    object: ta.Literal['chat.completion'] = 'chat.completion'
    created: int
    model: str
    choices: ta.Sequence[ChoiceT]
    usage: UsageT | None = None
