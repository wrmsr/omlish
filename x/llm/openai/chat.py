import typing as ta

from omlish import dataclasses as dc

from .types import Body
from .types import Headers
from .types import NOT_GIVEN
from .types import NotGiven
from .types import Query


##


@dc.dataclass(frozen=True)
class ChatCompletionTokenLogprob:
    token: str

    bytes: ta.Sequence[int] | None = None

    logprob: float

    @dc.dataclass(frozen=True)
    class TopLogprob:
        token: str
        bytes: ta.Sequence[int] | None = None
        logprob: float

    top_logprobs: ta.Sequence[TopLogprob]


@dc.dataclass(frozen=True)
class ChatCompletionMessageToolCall:
    id: str

    @dc.dataclass(frozen=True)
    class Function:
        arguments: str
        name: str

    function: Function

    type: ta.Literal['function']


@dc.dataclass(frozen=True)
class ChatCompletionMessage:
    content: str | None = None

    refusal: str | None = None

    role: ta.Literal['assistant']

    @dc.dataclass(frozen=True)
    class FunctionCall:
        arguments: str
        name: str

    function_call: FunctionCall | None = None

    tool_calls: ta.Sequence[ChatCompletionMessageToolCall] | None = None


@dc.dataclass(frozen=True)
class ChatCompletion:
    id: str

    @dc.dataclass(frozen=True)
    class ChoiceLogprobs:
        content: ta.Sequence[ChatCompletionTokenLogprob] | None = None
        refusal: ta.Sequence[ChatCompletionTokenLogprob] | None = None

    @dc.dataclass(frozen=True)
    class Choice:
        finish_reason: ta.Literal['stop', 'length', 'tool_calls', 'content_filter', 'function_call']
        index: int
        message: ChatCompletionMessage
        logprobs: ta.Optional['ChatCompletion.ChoiceLogprobs'] = None

    choices: ta.Sequence[Choice]

    created: int

    model: str

    object: ta.Literal['chat.completion']

    service_tier: ta.Literal['scale', 'default'] | None = None

    system_fingerprint: str | None = None

    usage: CompletionUsage | None = None


#


class ChatCompletionContentPartTextParam(ta.TypedDict, total=False):
    text: ta.Required[str]
    type: ta.Required[ta.Literal['text']]


class ChatCompletionSystemMessageParam(ta.TypedDict, total=False):
    content: ta.Required[str | ta.Iterable[ChatCompletionContentPartTextParam]]
    role: ta.Required[ta.Literal['system']]
    name: str


class ChatCompletionContentPartImageParamImageURL(ta.TypedDict, total=False):
    url: ta.Required[str]
    detail: ta.Literal['auto', 'low', 'high']


class ChatCompletionContentPartImageParam(ta.TypedDict, total=False):
    image_url: ta.Required[ChatCompletionContentPartImageParamImageURL]
    type: ta.Required[ta.Literal['image_url']]


ChatCompletionContentPartParam: ta.TypeAlias = ta.Union[
    ChatCompletionContentPartTextParam,
    ChatCompletionContentPartImageParam,
]


class ChatCompletionUserMessageParam(ta.TypedDict, total=False):
    content: ta.Required[str | ta.Iterable[ChatCompletionContentPartParam]]
    role: ta.Required[ta.Literal['user']]
    name: str


class ChatCompletionAssistantMessageParamFunctionCall(ta.TypedDict, total=False):
    arguments: ta.Required[str]
    name: ta.Required[str]


class ChatCompletionContentPartRefusalParam(ta.TypedDict, total=False):
    refusal: ta.Required[str]
    type: ta.Required[ta.Literal['refusal']]


ContentArrayOfContentPart: ta.TypeAlias = ta.Union[
    ChatCompletionContentPartTextParam,
    ChatCompletionContentPartRefusalParam,
]


class ChatCompletionMessageToolCallParamFunction(ta.TypedDict, total=False):
    arguments: ta.Required[str]
    name: ta.Required[str]


class ChatCompletionMessageToolCallParam(ta.TypedDict, total=False):
    id: ta.Required[str]
    function: ta.Required[ChatCompletionMessageToolCallParamFunction]
    type: ta.Required[ta.Literal['function']]


class ChatCompletionAssistantMessageParam(ta.TypedDict, total=False):
    role: ta.Required[ta.Literal['assistant']]
    content: str | ta.Iterable[ContentArrayOfContentPart] | None
    function_call: ChatCompletionAssistantMessageParamFunctionCall | None
    name: str
    refusal: str | None
    tool_calls: ta.Iterable[ChatCompletionMessageToolCallParam]


class ChatCompletionToolMessageParam(ta.TypedDict, total=False):
    content: ta.Required[str | None | ta.Iterable[ChatCompletionContentPartTextParam]]
    role: ta.Required[ta.Literal['tool']]
    tool_call_id: ta.Required[str]


class ChatCompletionFunctionMessageParam(ta.TypedDict, total=False):
    content: ta.Required[str | None]
    name: ta.Required[str]
    role: ta.Required[ta.Literal['function']]


ChatCompletionMessageParam: ta.TypeAlias = ta.Union[
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionFunctionMessageParam,
]


class ChatCompletionFunctionCallOptionParam(ta.TypedDict, total=False):
    name: ta.Required[str]


CompletionCreateParamsFunctionCall: ta.TypeAlias = ta.Union[
    ta.Literal['none', 'auto'],
    ChatCompletionFunctionCallOptionParam,
]


class CompletionCreateParamsFunction(TypedDict, total=False):
    name: Required[str]
    description: str
    parameters: FunctionParameters


@dc.dataclass(frozen=True)
class ChatCompletionRequest:
    messages: ta.Iterable[ChatCompletionMessageParam]
    model: str
    frequency_penalty: float | None | NotGiven = NOT_GIVEN
    function_call: CompletionCreateParamsFunctionCall | NotGiven = NOT_GIVEN
    functions: ta.Iterable[completion_create_params.Function] | NotGiven = NOT_GIVEN
    logit_bias: ta.Mapping[str, int] | None | NotGiven = NOT_GIVEN
    logprobs: bool | None | NotGiven = NOT_GIVEN
    max_tokens: int | None | NotGiven = NOT_GIVEN
    n: int | None | NotGiven = NOT_GIVEN
    parallel_tool_calls: bool | NotGiven = NOT_GIVEN
    presence_penalty: float | None | NotGiven = NOT_GIVEN
    response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN
    seed: int | None | NotGiven = NOT_GIVEN
    service_tier: ta.Literal['auto', 'default'] | None | NotGiven = NOT_GIVEN
    stop: str | None | ta.Sequence[str] | NotGiven = NOT_GIVEN
    stream: ta.Literal[False] | None | NotGiven = NOT_GIVEN
    stream_options: ChatCompletionStreamOptionsParam | None | NotGiven = NOT_GIVEN
    temperature: float | None | NotGiven = NOT_GIVEN
    tool_choice: ChatCompletionToolChoiceOptionParam | NotGiven = NOT_GIVEN
    tools: ta.Iterable[ChatCompletionToolParam] | NotGiven = NOT_GIVEN
    top_logprobs: int | None | NotGiven = NOT_GIVEN
    top_p: float | None | NotGiven = NOT_GIVEN
    user: str | NotGiven = NOT_GIVEN
    extra_headers: Headers | None = None
    extra_query: Query | None = None
    extra_body: Body | None = None
    timeout: float | None | NotGiven = NOT_GIVEN
