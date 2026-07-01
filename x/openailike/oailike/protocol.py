import dataclasses as dc
import typing as ta


##


JsonObject: ta.TypeAlias = ta.Mapping[str, ta.Any]
JsonValue: ta.TypeAlias = ta.Any

OaiLikeChatCompletionStop: ta.TypeAlias = str | ta.Sequence[str]


##
# Common content parts.


class OaiLikeChatCompletionContentPart:
    pass


@dc.dataclass(frozen=True, kw_only=True)
class TextOaiLikeChatCompletionContentPart(OaiLikeChatCompletionContentPart):
    text: str
    type: ta.Literal['text'] = 'text'


@dc.dataclass(frozen=True, kw_only=True)
class ImageUrlOaiLikeChatCompletionContentPart[
    ImageUrlT: object = object,
](
    OaiLikeChatCompletionContentPart,
):
    image_url: ImageUrlT
    type: ta.Literal['image_url'] = 'image_url'


##
# Common response_format objects.


class OaiLikeChatCompletionResponseFormat:
    pass


@dc.dataclass(frozen=True, kw_only=True)
class TextOaiLikeChatCompletionResponseFormat(OaiLikeChatCompletionResponseFormat):
    type: ta.Literal['text'] = 'text'


@dc.dataclass(frozen=True, kw_only=True)
class JsonObjectOaiLikeChatCompletionResponseFormat(OaiLikeChatCompletionResponseFormat):
    type: ta.Literal['json_object'] = 'json_object'


@dc.dataclass(frozen=True, kw_only=True)
class JsonSchemaOaiLikeChatCompletionResponseFormat[
    JsonSchemaT: object = object,
](
    OaiLikeChatCompletionResponseFormat,
):
    json_schema: JsonSchemaT
    type: ta.Literal['json_schema'] = 'json_schema'


##
# Common function-tool request objects.


@dc.dataclass(frozen=True, kw_only=True)
class OaiLikeChatCompletionFunctionDefinition:
    name: str
    description: str | None = None
    parameters: JsonObject | None = None


class OaiLikeChatCompletionTool:
    pass


@dc.dataclass(frozen=True, kw_only=True)
class FunctionOaiLikeChatCompletionTool[
    FunctionT: OaiLikeChatCompletionFunctionDefinition = OaiLikeChatCompletionFunctionDefinition,
](
    OaiLikeChatCompletionTool,
):
    function: FunctionT
    type: ta.Literal['function'] = 'function'


class OaiLikeChatCompletionToolChoice:
    pass


OaiLikeChatCompletionToolChoiceMode: ta.TypeAlias = ta.Literal[
    'none',
    'auto',
    'required',
]

OaiLikeChatCompletionToolChoiceOption: ta.TypeAlias = ta.Union[
    OaiLikeChatCompletionToolChoiceMode,
    OaiLikeChatCompletionToolChoice,
]


@dc.dataclass(frozen=True, kw_only=True)
class OaiLikeChatCompletionNamedToolChoiceFunction:
    name: str


@dc.dataclass(frozen=True, kw_only=True)
class FunctionOaiLikeChatCompletionToolChoice[
    FunctionT: OaiLikeChatCompletionNamedToolChoiceFunction = OaiLikeChatCompletionNamedToolChoiceFunction,
](
    OaiLikeChatCompletionToolChoice,
):
    function: FunctionT
    type: ta.Literal['function'] = 'function'


##
# Common opt-in field groups.


@dc.dataclass(frozen=True, kw_only=True)
class HasOaiLikeChatCompletionSampling:
    frequency_penalty: float | None = None
    max_tokens: int | None = None
    presence_penalty: float | None = None
    stop: OaiLikeChatCompletionStop | None = None
    temperature: float | None = None
    top_p: float | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasOaiLikeChatCompletionResponseFormat[
    ResponseFormatT: OaiLikeChatCompletionResponseFormat = OaiLikeChatCompletionResponseFormat,
]:
    response_format: ResponseFormatT | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasOaiLikeChatCompletionToolControls[
    ToolT: OaiLikeChatCompletionTool = OaiLikeChatCompletionTool,
    ToolChoiceT: OaiLikeChatCompletionToolChoiceOption = OaiLikeChatCompletionToolChoiceOption,
]:
    tool_choice: ToolChoiceT | None = None
    tools: ta.Sequence[ToolT] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasOaiLikeChatCompletionLogprobsRequest:
    logprobs: bool | None = None
    top_logprobs: int | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasOaiLikeParallelToolCalls:
    parallel_tool_calls: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasOaiLikeChatCompletionSystemFingerprint:
    system_fingerprint: str | None = None


##
# Common generated tool-call objects.


class OaiLikeChatCompletionResponseToolCall:
    pass


@dc.dataclass(frozen=True, kw_only=True)
class OaiLikeChatCompletionResponseToolCallFunction:
    arguments: str
    name: str


@dc.dataclass(frozen=True, kw_only=True)
class FunctionOaiLikeChatCompletionResponseToolCall[
    FunctionT: OaiLikeChatCompletionResponseToolCallFunction = OaiLikeChatCompletionResponseToolCallFunction,
](
    OaiLikeChatCompletionResponseToolCall,
):
    id: str
    function: FunctionT
    type: ta.Literal['function'] = 'function'


class OaiLikeChatCompletionStreamDeltaToolCall:
    pass


@dc.dataclass(frozen=True, kw_only=True)
class OaiLikeChatCompletionStreamDeltaToolCallFunction:
    arguments: str | None = None
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class FunctionOaiLikeChatCompletionStreamDeltaToolCall[
    FunctionT: OaiLikeChatCompletionStreamDeltaToolCallFunction = OaiLikeChatCompletionStreamDeltaToolCallFunction,
](
    OaiLikeChatCompletionStreamDeltaToolCall,
):
    index: int
    function: FunctionT | None = None
    id: str | None = None
    type: ta.Literal['function'] | None = None


##
# Common request messages.


class OaiLikeChatCompletionRequestMessage:
    pass


@dc.dataclass(frozen=True, kw_only=True)
class SystemOaiLikeChatCompletionRequestMessage[
    TextPartT: TextOaiLikeChatCompletionContentPart = TextOaiLikeChatCompletionContentPart,
](
    OaiLikeChatCompletionRequestMessage,
):
    content: str | ta.Sequence[TextPartT]
    role: ta.Literal['system'] = 'system'


@dc.dataclass(frozen=True, kw_only=True)
class UserOaiLikeChatCompletionRequestMessage[
    PartT: OaiLikeChatCompletionContentPart = OaiLikeChatCompletionContentPart,
](
    OaiLikeChatCompletionRequestMessage,
):
    content: str | ta.Sequence[PartT]
    role: ta.Literal['user'] = 'user'


@dc.dataclass(frozen=True, kw_only=True)
class AssistantOaiLikeChatCompletionRequestMessage[
    PartT: OaiLikeChatCompletionContentPart = TextOaiLikeChatCompletionContentPart,
    ToolCallT: OaiLikeChatCompletionResponseToolCall = OaiLikeChatCompletionResponseToolCall,
](
    OaiLikeChatCompletionRequestMessage,
):
    content: str | ta.Sequence[PartT] | None = None
    role: ta.Literal['assistant'] = 'assistant'
    tool_calls: ta.Sequence[ToolCallT] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class ToolOaiLikeChatCompletionRequestMessage[
    TextPartT: TextOaiLikeChatCompletionContentPart = TextOaiLikeChatCompletionContentPart,
](
    OaiLikeChatCompletionRequestMessage,
):
    content: str | ta.Sequence[TextPartT]
    tool_call_id: str
    role: ta.Literal['tool'] = 'tool'


##
# Common response messages and stream deltas.


class OaiLikeChatCompletionResponseMessage:
    pass


@dc.dataclass(frozen=True, kw_only=True)
class AssistantOaiLikeChatCompletionResponseMessage[
    ToolCallT: OaiLikeChatCompletionResponseToolCall = OaiLikeChatCompletionResponseToolCall,
](
    OaiLikeChatCompletionResponseMessage,
):
    content: str | None = None
    role: ta.Literal['assistant'] = 'assistant'
    tool_calls: ta.Sequence[ToolCallT] | None = None


class OaiLikeChatCompletionStreamDelta:
    pass


@dc.dataclass(frozen=True, kw_only=True)
class AssistantOaiLikeChatCompletionStreamDelta[
    ToolCallT: OaiLikeChatCompletionStreamDeltaToolCall = OaiLikeChatCompletionStreamDeltaToolCall,
](
    OaiLikeChatCompletionStreamDelta,
):
    content: str | None = None
    role: ta.Literal['assistant'] | None = None
    tool_calls: ta.Sequence[ToolCallT] | None = None


##
# Common logprobs.


@dc.dataclass(frozen=True, kw_only=True)
class OaiLikeChatCompletionTopLogprob:
    logprob: float
    token: str
    bytes: ta.Sequence[int] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OaiLikeChatCompletionTokenLogprob[
    TopLogprobT: OaiLikeChatCompletionTopLogprob = OaiLikeChatCompletionTopLogprob,
]:
    logprob: float
    token: str
    bytes: ta.Sequence[int] | None = None
    top_logprobs: ta.Sequence[TopLogprobT] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OaiLikeChatCompletionLogprobs[
    TokenLogprobT: OaiLikeChatCompletionTokenLogprob = OaiLikeChatCompletionTokenLogprob,
]:
    content: ta.Sequence[TokenLogprobT] | None = None
    refusal: ta.Sequence[TokenLogprobT] | None = None


##
# Common choices, usage, responses, and stream chunks.


@dc.dataclass(frozen=True, kw_only=True)
class OaiLikeChatCompletionChoice[
    MessageT: OaiLikeChatCompletionResponseMessage = OaiLikeChatCompletionResponseMessage,
    FinishReasonT: str = str,
]:
    index: int
    message: MessageT
    finish_reason: FinishReasonT | None


@dc.dataclass(frozen=True, kw_only=True)
class LogprobsOaiLikeChatCompletionChoice[
    MessageT: OaiLikeChatCompletionResponseMessage = OaiLikeChatCompletionResponseMessage,
    FinishReasonT: str = str,
    LogprobsT: OaiLikeChatCompletionLogprobs = OaiLikeChatCompletionLogprobs,
](
    OaiLikeChatCompletionChoice[
        MessageT,
        FinishReasonT,
    ],
):
    logprobs: LogprobsT | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OaiLikeChatCompletionStreamChoice[
    DeltaT: OaiLikeChatCompletionStreamDelta = OaiLikeChatCompletionStreamDelta,
    FinishReasonT: str = str,
]:
    index: int
    delta: DeltaT
    finish_reason: FinishReasonT | None


@dc.dataclass(frozen=True, kw_only=True)
class LogprobsOaiLikeChatCompletionStreamChoice[
    DeltaT: OaiLikeChatCompletionStreamDelta = OaiLikeChatCompletionStreamDelta,
    FinishReasonT: str = str,
    LogprobsT: OaiLikeChatCompletionLogprobs = OaiLikeChatCompletionLogprobs,
](
    OaiLikeChatCompletionStreamChoice[
        DeltaT,
        FinishReasonT,
    ],
):
    logprobs: LogprobsT | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OaiLikeChatCompletionUsage:
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int


@dc.dataclass(frozen=True, kw_only=True)
class OaiLikeChatCompletionResponse[
    ChoiceT: OaiLikeChatCompletionChoice = OaiLikeChatCompletionChoice,
    UsageT: OaiLikeChatCompletionUsage = OaiLikeChatCompletionUsage,
]:
    id: str
    object: ta.Literal['chat.completion'] = 'chat.completion'
    created: int
    model: str
    choices: ta.Sequence[ChoiceT]
    usage: UsageT | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OaiLikeChatCompletionStreamChunk[
    ChoiceT: OaiLikeChatCompletionStreamChoice = OaiLikeChatCompletionStreamChoice,
    UsageT: OaiLikeChatCompletionUsage = OaiLikeChatCompletionUsage,
]:
    id: str
    object: ta.Literal['chat.completion.chunk'] = 'chat.completion.chunk'
    created: int
    model: str
    choices: ta.Sequence[ChoiceT]
    usage: UsageT | None = None


##
# Common requests.


@dc.dataclass(frozen=True, kw_only=True)
class OaiLikeChatCompletionStreamOptions:
    include_usage: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OaiLikeChatCompletionRequestBase[
    MessageT: OaiLikeChatCompletionRequestMessage = OaiLikeChatCompletionRequestMessage,
    ToolT: OaiLikeChatCompletionTool = OaiLikeChatCompletionTool,
    ToolChoiceT: OaiLikeChatCompletionToolChoiceOption = OaiLikeChatCompletionToolChoiceOption,
    ResponseFormatT: OaiLikeChatCompletionResponseFormat = OaiLikeChatCompletionResponseFormat,
](
    HasOaiLikeChatCompletionSampling,
    HasOaiLikeChatCompletionResponseFormat[
        ResponseFormatT,
    ],
    HasOaiLikeChatCompletionToolControls[
        ToolT,
        ToolChoiceT,
    ],
):
    model: str
    messages: ta.Sequence[MessageT]


@dc.dataclass(frozen=True, kw_only=True)
class OaiLikeChatCompletionRequest[
    MessageT: OaiLikeChatCompletionRequestMessage = OaiLikeChatCompletionRequestMessage,
    ToolT: OaiLikeChatCompletionTool = OaiLikeChatCompletionTool,
    ToolChoiceT: OaiLikeChatCompletionToolChoiceOption = OaiLikeChatCompletionToolChoiceOption,
    ResponseFormatT: OaiLikeChatCompletionResponseFormat = OaiLikeChatCompletionResponseFormat,
](
    OaiLikeChatCompletionRequestBase[
        MessageT,
        ToolT,
        ToolChoiceT,
        ResponseFormatT,
    ],
):
    stream: ta.Literal[False] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OaiLikeChatCompletionStreamRequest[
    MessageT: OaiLikeChatCompletionRequestMessage = OaiLikeChatCompletionRequestMessage,
    ToolT: OaiLikeChatCompletionTool = OaiLikeChatCompletionTool,
    ToolChoiceT: OaiLikeChatCompletionToolChoiceOption = OaiLikeChatCompletionToolChoiceOption,
    ResponseFormatT: OaiLikeChatCompletionResponseFormat = OaiLikeChatCompletionResponseFormat,
    StreamOptionsT: OaiLikeChatCompletionStreamOptions = OaiLikeChatCompletionStreamOptions,
](
    OaiLikeChatCompletionRequestBase[
        MessageT,
        ToolT,
        ToolChoiceT,
        ResponseFormatT,
    ],
):
    stream: ta.Literal[True] = True
    stream_options: StreamOptionsT | None = None
