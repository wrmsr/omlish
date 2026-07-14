import typing as ta

from omlish import dataclasses as dc

from .content import ContentPart
from .content import TextContentPart
from .json import JsonObject
from .tools import Tool
from .tools import ToolCall
from .typetags import TypeTagged


##


class RequestMessage(
    TypeTagged,
    type_tag_field='role',
):
    pass


#


@dc.dataclass(frozen=True, kw_only=True)
class SystemRequestMessage[
    TextContentPartT: TextContentPart = TextContentPart,
](
    RequestMessage,
    type_tag='system',
):
    content: str | ta.Sequence[TextContentPartT]


#


@dc.dataclass(frozen=True, kw_only=True)
class UserRequestMessage[
    ContentPartT: ContentPart = ContentPart,
](
    RequestMessage,
    type_tag='user',
):
    content: str | ta.Sequence[ContentPartT]


#


@dc.dataclass(frozen=True, kw_only=True)
class AssistantRequestMessage[
    ContentPartT: ContentPart = ContentPart,
    ToolCallT: ToolCall = ToolCall,
](
    RequestMessage,
    type_tag='assistant',
):
    content: str | ta.Sequence[ContentPartT] | None = None
    tool_calls: ta.Sequence[ToolCallT] | None = None


#


@dc.dataclass(frozen=True, kw_only=True)
class ToolRequestMessage[
    TextContentPartT: TextContentPart = TextContentPart,
](
    RequestMessage,
    type_tag='tool',
):
    content: str | ta.Sequence[TextContentPartT]
    tool_call_id: str


##


@dc.dataclass(frozen=True, kw_only=True)
class RequestBase[
    RequestMessageT: RequestMessage = RequestMessage,
]:
    model: str
    messages: ta.Sequence[RequestMessageT]


##


@dc.dataclass(frozen=True, kw_only=True)
class HasRequestTools[
    ToolT: Tool = Tool,
]:
    tools: ta.Sequence[ToolT] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasRequestParallelToolCalls:
    parallel_tool_calls: bool | None = None


##


@dc.dataclass(frozen=True, kw_only=True)
class HasRequestLogprobs:
    logprobs: bool | None = None
    top_logprobs: int | None = None


##


class ResponseFormat(
    TypeTagged,
    type_tag_field='type',
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class TextResponseFormat(
    ResponseFormat,
    type_tag='text',
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class JsonObjectResponseFormat(
    ResponseFormat,
    type_tag='json_object',
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class JsonSchemaResponseFormat[
    JsonSchemaT = JsonObject,
](
    ResponseFormat,
    type_tag='json_schema',
):
    json_schema: JsonSchemaT


@dc.dataclass(frozen=True, kw_only=True)
class HasRequestResponseFormat[
    ResponseFormatT: ResponseFormat = ResponseFormat,
]:
    response_format: ResponseFormatT | None = None


##


SamplingStop: ta.TypeAlias = str | ta.Sequence[str]


@dc.dataclass(frozen=True, kw_only=True)
class HasRequestSampling:
    frequency_penalty: float | None = None
    max_tokens: int | None = None
    presence_penalty: float | None = None
    stop: SamplingStop | None = None
    temperature: float | None = None
    top_p: float | None = None
