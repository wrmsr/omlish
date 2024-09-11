import typing as ta

from omlish import dataclasses as dc

from .types import Body
from .types import Headers
from .types import NOT_GIVEN
from .types import NotGiven
from .types import Query


##


class ContentPartTextParam(ta.TypedDict, total=False):
    text: ta.Required[str]
    type: ta.Required[ta.Literal['text']]


class SystemMessageParam(ta.TypedDict, total=False):
    content: ta.Required[str | ta.Iterable[ContentPartTextParam]]
    role: ta.Required[ta.Literal['system']]
    name: str


class ImageUrlParam(ta.TypedDict, total=False):
    url: ta.Required[str]
    detail: ta.Literal['auto', 'low', 'high']


class ContentPartImageParam(ta.TypedDict, total=False):
    image_url: ta.Required[ImageUrlParam]
    type: ta.Required[ta.Literal["image_url"]]


class UserMessageParam(ta.TypedDict, total=False):
    content: ta.Required[str | ta.Iterable[ContentPartTextParam | ContentPartImageParam]]
    role: ta.Required[ta.Literal['user']]
    name: str


class FunctionCallParam(ta.TypedDict, total=False):
    arguments: ta.Required[str]
    name: ta.Required[str]


class ContentPartRefusalParam(ta.TypedDict, total=False):
    refusal: ta.Required[str]
    type: ta.Required[ta.Literal['refusal']]


class MessageToolCallParamFunction(ta.TypedDict, total=False):
    arguments: ta.Required[str]
    name: ta.Required[str]


class MessageToolCallParam(ta.TypedDict, total=False):
    id: ta.Required[str]
    function: ta.Required[MessageToolCallParamFunction]
    type: ta.Required[ta.Literal['function']]


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
    json_schema: ta.Required[JsonSchema]
    type: ta.Required[ta.Literal['json_schema']]


class StreamOptionsParam(ta.TypedDict, total=False):
    include_usage: bool


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
    stream: ta.Literal[False] | None | NotGiven = NOT_GIVEN
    stream_options: StreamOptionsParam | None | NotGiven = NOT_GIVEN
    temperature: float | None | NotGiven = NOT_GIVEN
    tool_choice: ta.Union[
        ta.Literal['none', 'auto', 'required'],
        NamedToolChoiceParam,
        NotGiven,
    ] = NOT_GIVEN,
    tools: ta.Iterable[ChatCompletionToolParam] | NotGiven = NOT_GIVEN
    top_logprobs: int | None | NotGiven = NOT_GIVEN
    top_p: float | None | NotGiven = NOT_GIVEN
    user: str | NotGiven = NOT_GIVEN
    extra_headers: Headers | None = None
    extra_query: Query | None = None
    extra_body: Body | None = None
    timeout: float | None | NotGiven = NOT_GIVEN


def _main() -> None:
    import openai
    openai.chat.completions.create  # noqa
