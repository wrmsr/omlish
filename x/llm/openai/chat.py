import typing as ta

from omlish import dataclasses as dc

from .types import Body
from .types import Headers
from .types import NOT_GIVEN
from .types import NotGiven
from .types import Query


##


class ContentPartTextParam(ta.TypedDict, total=False):
    type: ta.Required[ta.Literal['text']]
    text: ta.Required[str]


class SystemMessageParam(ta.TypedDict, total=False):
    content: ta.Required[str | ta.Iterable[ContentPartTextParam]]
    role: ta.Required[ta.Literal['system']]
    name: str


class ImageUrlParam(ta.TypedDict, total=False):
    url: ta.Required[str]
    detail: ta.Literal['auto', 'low', 'high']


class ContentPartImageParam(ta.TypedDict, total=False):
    type: ta.Required[ta.Literal["image_url"]]
    image_url: ta.Required[ImageUrlParam]


class UserMessageParam(ta.TypedDict, total=False):
    content: ta.Required[str | ta.Iterable[ContentPartTextParam | ContentPartImageParam]]
    role: ta.Required[ta.Literal['user']]
    name: str


class FunctionCallParam(ta.TypedDict, total=False):
    arguments: ta.Required[str]
    name: ta.Required[str]


class ContentPartRefusalParam(ta.TypedDict, total=False):
    type: ta.Required[ta.Literal['refusal']]
    refusal: ta.Required[str]


class MessageToolCallParamFunction(ta.TypedDict, total=False):
    arguments: ta.Required[str]
    name: ta.Required[str]


class MessageToolCallParam(ta.TypedDict, total=False):
    type: ta.Required[ta.Literal['function']]
    id: ta.Required[str]
    function: ta.Required[MessageToolCallParamFunction]


class AssistantMessageParam(ta.TypedDict, total=False):
    role: ta.Required[ta.Literal['assistant']]
    content: str | ta.Iterable[ContentPartTextParam | ContentPartRefusalParam] | None
    function_call: FunctionCallParam | None
    name: str
    refusal: str | None
    tool_calls: ta.Iterable[MessageToolCallParam]


class ToolMessageParam(ta.TypedDict, total=False):
    content: ta.Required[str | ta.Iterable[ContentPartTextParam]]
    role: ta.Required[ta.Literal['tool']]
    tool_call_id: ta.Required[str]


class FunctionMessageParam(ta.TypedDict, total=False):
    content: ta.Required[str | None]
    name: ta.Required[str]
    role: ta.Required[ta.Literal['function']]


class FunctionCallOptionParam(ta.TypedDict, total=False):
    name: ta.Required[str]


class FunctionParam(ta.TypedDict, total=False):
    name: ta.Required[str]
    description: str
    parameters: ta.Mapping[str, object]


class ResponseFormatText(ta.TypedDict, total=False):
    type: ta.Required[ta.Literal['text']]


class ResponseFormatJsonObject(ta.TypedDict, total=False):
    type: ta.Required[ta.Literal['json_object']]


class JsonSchema(ta.TypedDict, total=False):
    name: ta.Required[str]
    description: str
    schema: ta.Mapping[str, object]
    strict: bool | None


class ResponseFormatJsonSchema(ta.TypedDict, total=False):
    type: ta.Required[ta.Literal['json_schema']]
    json_schema: ta.Required[JsonSchema]


class StreamOptionsParam(ta.TypedDict, total=False):
    include_usage: bool


class NamedToolChoiceParamFunction(ta.TypedDict, total=False):
    name: ta.Required[str]


class NamedToolChoiceParam(ta.TypedDict, total=False):
    type: ta.Required[ta.Literal['function']]
    function: ta.Required[NamedToolChoiceParamFunction]


class ToolParamFunctionDefinition(ta.TypedDict, total=False):
    name: ta.Required[str]
    description: str
    parameters: ta.Mapping[str, ta.Any]
    strict: bool | None


class ToolParam(ta.TypedDict, total=False):
    type: ta.Required[ta.Literal['function']]
    function: ta.Required[ToolParamFunctionDefinition]


@dc.dataclass(frozen=True)
class ChatCompletionRequest:
    messages: ta.Iterable[ta.Union[
        SystemMessageParam,
        UserMessageParam,
        AssistantMessageParam,
        ToolMessageParam,
        FunctionMessageParam,
    ]]
    model: str
    frequency_penalty: float | None | NotGiven = NOT_GIVEN
    function_call: ta.Union[
        ta.Literal['none', 'auto'],
        FunctionCallOptionParam,
        NotGiven,
    ] = NOT_GIVEN
    functions: ta.Iterable[FunctionParam] | NotGiven = NOT_GIVEN
    logit_bias: ta.Mapping[str, int] | None | NotGiven = NOT_GIVEN
    logprobs: bool | None | NotGiven = NOT_GIVEN
    max_tokens: int | None | NotGiven = NOT_GIVEN
    n: int | None | NotGiven = NOT_GIVEN
    parallel_tool_calls: bool | NotGiven = NOT_GIVEN
    presence_penalty: float | None | NotGiven = NOT_GIVEN
    response_format: ta.Union[
        ResponseFormatText,
        ResponseFormatJsonObject,
        ResponseFormatJsonSchema,
        NotGiven,
    ] = NOT_GIVEN
    seed: int | None | NotGiven = NOT_GIVEN
    service_tier: ta.Literal['auto', 'default'] | None | NotGiven = NOT_GIVEN
    stop: str | None | ta.Sequence[str] | NotGiven = NOT_GIVEN
    stream: bool | None | NotGiven = NOT_GIVEN
    stream_options: StreamOptionsParam | None | NotGiven = NOT_GIVEN
    temperature: float | None | NotGiven = NOT_GIVEN
    tool_choice: ta.Union[
        ta.Literal['none', 'auto', 'required'],
        NamedToolChoiceParam,
        NotGiven,
    ] = NOT_GIVEN,
    tools: ta.Iterable[ToolParam] | NotGiven = NOT_GIVEN
    top_logprobs: int | None | NotGiven = NOT_GIVEN
    top_p: float | None | NotGiven = NOT_GIVEN
    user: str | NotGiven = NOT_GIVEN
    extra_headers: Headers | None = None
    extra_query: Query | None = None
    extra_body: Body | None = None
    timeout: float | None | NotGiven = NOT_GIVEN


##


@dc.dataclass(frozen=True)
class TopLogprob:
    token: str
    bytes: ta.Sequence[int] | None = None
    logprob: float


@dc.dataclass(frozen=True)
class TokenLogprob:
    token: str
    bytes: ta.Sequence[int] | None= None
    logprob: float
    top_logprobs: ta.Sequence[TopLogprob]


@dc.dataclass(frozen=True)
class ChoiceLogprobs:
    content: ta.Sequence[TokenLogprob] | None = None
    refusal: ta.Sequence[TokenLogprob] | None = None


@dc.dataclass(frozen=True)
class MessageFunctionCall:
    arguments: str
    name: str


@dc.dataclass(frozen=True)
class MessageToolCallFunction:
    arguments: str
    name: str


@dc.dataclass(frozen=True)
class MessageToolCall:
    id: str
    function: MessageToolCallFunction
    type: ta.Literal['function']


@dc.dataclass(frozen=True)
class Message:
    content: str | None = None
    refusal: str | None = None
    role: ta.Literal['assistant']
    function_call: MessageFunctionCall | None = None
    tool_calls: ta.Sequence[MessageToolCall] | None = None


@dc.dataclass(frozen=True)
class Choice:
    finish_reason: ta.Literal['stop', 'length', 'tool_calls', 'content_filter', 'function_call']
    index: int
    logprobs: ChoiceLogprobs | None = None
    message: Message


@dc.dataclass(frozen=True)
class Usage:
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int


@dc.dataclass(frozen=True)
class ChatCompletion:
    id: str
    choices: ta.Sequence[Choice]
    created: int
    model: str
    object: ta.Literal['chat.completion']
    service_tier: ta.Literal['scale', 'default'] | None = None
    system_fingerprint: str | None = None
    usage: Usage | None = None


##


def _main() -> None:
    import openai
    openai.chat.completions.create  # noqa
