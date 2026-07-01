import dataclasses as dc
import typing as ta

from .content import TextContentPart
from .content import ContentPart


##


class RequestMessage:
    pass


#


@dc.dataclass(frozen=True, kw_only=True)
class SystemRequestMessage[
    TextContentPartT: TextContentPart = TextContentPart,
](
    RequestMessage,
):
    content: str | ta.Sequence[TextContentPartT]
    role: ta.Literal['system'] = 'system'


#


@dc.dataclass(frozen=True, kw_only=True)
class UserRequestMessage[
    ContentPartT: ContentPart = ContentPart,
](
    RequestMessage,
):
    content: str | ta.Sequence[ContentPartT]
    role: ta.Literal['user'] = 'user'


#


@dc.dataclass(frozen=True, kw_only=True)
class AssistantRequestMessage[
    ContentPartT: ContentPart = ContentPart,
    ToolCallT: ResponseToolCall = ResponseToolCall,
](
    RequestMessage,
):
    content: str | ta.Sequence[ContentPartT] | None = None
    role: ta.Literal['assistant'] = 'assistant'
    tool_calls: ta.Sequence[ToolCallT] | None = None


#


@dc.dataclass(frozen=True, kw_only=True)
class ToolRequestMessage[
    TextContentPartT: TextContentPart = TextContentPart,
](
    RequestMessage,
):
    content: str | ta.Sequence[TextContentPartT]
    tool_call_id: str
    role: ta.Literal['tool'] = 'tool'


##


@dc.dataclass(frozen=True, kw_only=True)
class RequestBase[
    MessageT: RequestMessage = RequestMessage,
]:
    model: str
    messages: ta.Sequence[MessageT]


##


@dc.dataclass(frozen=True, kw_only=True)
class HasRequestTools[
    ToolT: Tool = Tool,
    ToolChoiceT: ToolChoiceOption = ToolChoiceOption,
]:
    tool_choice: ToolChoiceT | None = None
    tools: ta.Sequence[ToolT] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasRequestParallelToolCalls:
    parallel_tool_calls: bool | None = None


#


@dc.dataclass(frozen=True, kw_only=True)
class HasRequestLogprobs:
    logprobs: bool | None = None
    top_logprobs: int | None = None


#


class ResponseFormat:
    pass


@dc.dataclass(frozen=True, kw_only=True)
class TextResponseFormat(ResponseFormat):
    type: ta.Literal['text'] = 'text'


@dc.dataclass(frozen=True, kw_only=True)
class JsonObjectResponseFormat(ResponseFormat):
    type: ta.Literal['json_object'] = 'json_object'


@dc.dataclass(frozen=True, kw_only=True)
class JsonSchemaResponseFormat[
    JsonSchemaT: object = object,
](
    ResponseFormat,
):
    json_schema: JsonSchemaT
    type: ta.Literal['json_schema'] = 'json_schema'


@dc.dataclass(frozen=True, kw_only=True)
class HasRequestResponseFormat[
    ResponseFormatT: ResponseFormat = ResponseFormat,
]:
    response_format: ResponseFormatT | None = None


#


SamplingStop: ta.TypeAlias = str | ta.Sequence[str]


@dc.dataclass(frozen=True, kw_only=True)
class HasRequestSampling:
    frequency_penalty: float | None = None
    max_tokens: int | None = None
    presence_penalty: float | None = None
    stop: SamplingStop | None = None
    temperature: float | None = None
    top_p: float | None = None
