import dataclasses as dc
import typing as ta


##


JsonObject = ta.Mapping[str, ta.Any]
JsonValue = ta.Any

OaiLikeChatCompletionStop = str | ta.Sequence[str]


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


OaiLikeChatCompletionToolChoiceMode = ta.Literal[
    'none',
    'auto',
    'required',
]

OaiLikeChatCompletionToolChoiceOption = (
    OaiLikeChatCompletionToolChoiceMode |
    OaiLikeChatCompletionToolChoice
)


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


###
# OpenAI Chat Completions.


OaiChatCompletionFinishReason = ta.Literal[
    'stop',
    'length',
    'tool_calls',
    'content_filter',
    'function_call',
]

OaiChatCompletionReasoningEffort = ta.Literal[
    'none',
    'minimal',
    'low',
    'medium',
    'high',
    'xhigh',
]

OaiChatCompletionPromptCacheRetention = ta.Literal[
    'in_memory',
    '24h',
]

OaiChatCompletionServiceTier = ta.Literal[
    'auto',
    'default',
    'flex',
    'scale',
    'priority',
]

OaiChatCompletionVerbosity = ta.Literal[
    'low',
    'medium',
    'high',
]


@dc.dataclass(frozen=True, kw_only=True)
class HasOaiChatCompletionRequestIdentity:
    safety_identifier: str | None = None
    user: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasOaiChatCompletionRequestMetadata:
    metadata: ta.Mapping[str, str] | None = None
    store: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasOaiChatCompletionRequestTokenControls:
    logit_bias: ta.Mapping[str, float] | None = None
    max_completion_tokens: int | None = None
    n: int | None = None
    seed: int | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasOaiChatCompletionPromptCaching:
    prompt_cache_key: str | None = None
    prompt_cache_retention: OaiChatCompletionPromptCacheRetention | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasOaiChatCompletionReasoningEffort:
    reasoning_effort: OaiChatCompletionReasoningEffort | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasOaiChatCompletionServiceTier:
    service_tier: OaiChatCompletionServiceTier | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasOaiChatCompletionVerbosity:
    verbosity: OaiChatCompletionVerbosity | None = None


##
# OpenAI content parts.


class OaiChatCompletionContentPart(OaiLikeChatCompletionContentPart):
    pass


class OaiChatCompletionUserRequestContentPart(OaiChatCompletionContentPart):
    pass


class OaiChatCompletionAssistantRequestContentPart(OaiChatCompletionContentPart):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class TextOaiChatCompletionContentPart(
    TextOaiLikeChatCompletionContentPart,
    OaiChatCompletionUserRequestContentPart,
    OaiChatCompletionAssistantRequestContentPart,
):
    text: str
    type: ta.Literal['text'] = 'text'


@dc.dataclass(frozen=True, kw_only=True)
class OaiChatCompletionImageUrl:
    url: str
    detail: ta.Literal['auto', 'low', 'high'] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class ImageUrlOaiChatCompletionContentPart(
    ImageUrlOaiLikeChatCompletionContentPart[
        OaiChatCompletionImageUrl,
    ],
    OaiChatCompletionUserRequestContentPart,
):
    image_url: OaiChatCompletionImageUrl
    type: ta.Literal['image_url'] = 'image_url'


@dc.dataclass(frozen=True, kw_only=True)
class RefusalOaiChatCompletionContentPart(OaiChatCompletionAssistantRequestContentPart):
    refusal: str
    type: ta.Literal['refusal'] = 'refusal'


##
# OpenAI response_format objects.


class OaiChatCompletionResponseFormat(OaiLikeChatCompletionResponseFormat):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class TextOaiChatCompletionResponseFormat(
    TextOaiLikeChatCompletionResponseFormat,
    OaiChatCompletionResponseFormat,
):
    type: ta.Literal['text'] = 'text'


@dc.dataclass(frozen=True, kw_only=True)
class JsonObjectOaiChatCompletionResponseFormat(
    JsonObjectOaiLikeChatCompletionResponseFormat,
    OaiChatCompletionResponseFormat,
):
    type: ta.Literal['json_object'] = 'json_object'


@dc.dataclass(frozen=True, kw_only=True)
class OaiChatCompletionJsonSchema:
    name: str
    description: str | None = None
    schema: JsonObject | None = None
    strict: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class JsonSchemaOaiChatCompletionResponseFormat(
    JsonSchemaOaiLikeChatCompletionResponseFormat[
        OaiChatCompletionJsonSchema,
    ],
    OaiChatCompletionResponseFormat,
):
    json_schema: OaiChatCompletionJsonSchema
    type: ta.Literal['json_schema'] = 'json_schema'


##
# OpenAI tools and tool choices.


@dc.dataclass(frozen=True, kw_only=True)
class OaiChatCompletionFunctionDefinition(OaiLikeChatCompletionFunctionDefinition):
    name: str
    description: str | None = None
    parameters: JsonObject | None = None
    strict: bool | None = None


class OaiChatCompletionTool(OaiLikeChatCompletionTool):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class FunctionOaiChatCompletionTool(
    FunctionOaiLikeChatCompletionTool[
        OaiChatCompletionFunctionDefinition,
    ],
    OaiChatCompletionTool,
):
    function: OaiChatCompletionFunctionDefinition
    type: ta.Literal['function'] = 'function'


class OaiChatCompletionToolChoice(OaiLikeChatCompletionToolChoice):
    pass


OaiChatCompletionToolChoiceMode = OaiLikeChatCompletionToolChoiceMode
OaiChatCompletionToolChoiceOption = (
    OaiChatCompletionToolChoiceMode |
    OaiChatCompletionToolChoice
)


@dc.dataclass(frozen=True, kw_only=True)
class OaiChatCompletionNamedToolChoiceFunction(
    OaiLikeChatCompletionNamedToolChoiceFunction,
):
    name: str


@dc.dataclass(frozen=True, kw_only=True)
class FunctionOaiChatCompletionToolChoice(
    FunctionOaiLikeChatCompletionToolChoice[
        OaiChatCompletionNamedToolChoiceFunction,
    ],
    OaiChatCompletionToolChoice,
):
    function: OaiChatCompletionNamedToolChoiceFunction
    type: ta.Literal['function'] = 'function'


##
# OpenAI generated tool calls.


class OaiChatCompletionResponseToolCall(OaiLikeChatCompletionResponseToolCall):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class OaiChatCompletionResponseToolCallFunction(
    OaiLikeChatCompletionResponseToolCallFunction,
):
    arguments: str
    name: str


@dc.dataclass(frozen=True, kw_only=True)
class FunctionOaiChatCompletionResponseToolCall(
    FunctionOaiLikeChatCompletionResponseToolCall[
        OaiChatCompletionResponseToolCallFunction,
    ],
    OaiChatCompletionResponseToolCall,
):
    id: str
    function: OaiChatCompletionResponseToolCallFunction
    type: ta.Literal['function'] = 'function'


class OaiChatCompletionStreamDeltaToolCall(OaiLikeChatCompletionStreamDeltaToolCall):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class OaiChatCompletionStreamDeltaToolCallFunction(
    OaiLikeChatCompletionStreamDeltaToolCallFunction,
):
    arguments: str | None = None
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class FunctionOaiChatCompletionStreamDeltaToolCall(
    FunctionOaiLikeChatCompletionStreamDeltaToolCall[
        OaiChatCompletionStreamDeltaToolCallFunction,
    ],
    OaiChatCompletionStreamDeltaToolCall,
):
    index: int
    function: OaiChatCompletionStreamDeltaToolCallFunction | None = None
    id: str | None = None
    type: ta.Literal['function'] | None = None


##
# OpenAI request messages.


class OaiChatCompletionRequestMessage(OaiLikeChatCompletionRequestMessage):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class DeveloperOaiChatCompletionRequestMessage(
    OaiChatCompletionRequestMessage,
):
    content: str | ta.Sequence[TextOaiChatCompletionContentPart]
    name: str | None = None
    role: ta.Literal['developer'] = 'developer'


@dc.dataclass(frozen=True, kw_only=True)
class SystemOaiChatCompletionRequestMessage(
    SystemOaiLikeChatCompletionRequestMessage[
        TextOaiChatCompletionContentPart,
    ],
    OaiChatCompletionRequestMessage,
):
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class UserOaiChatCompletionRequestMessage(
    UserOaiLikeChatCompletionRequestMessage[
        OaiChatCompletionUserRequestContentPart,
    ],
    OaiChatCompletionRequestMessage,
):
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class AssistantOaiChatCompletionRequestMessage(
    AssistantOaiLikeChatCompletionRequestMessage[
        OaiChatCompletionAssistantRequestContentPart,
        OaiChatCompletionResponseToolCall,
    ],
    OaiChatCompletionRequestMessage,
):
    name: str | None = None
    refusal: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class ToolOaiChatCompletionRequestMessage(
    ToolOaiLikeChatCompletionRequestMessage[
        TextOaiChatCompletionContentPart,
    ],
    OaiChatCompletionRequestMessage,
):
    pass


##
# OpenAI response messages and stream deltas.


class OaiChatCompletionResponseMessage(OaiLikeChatCompletionResponseMessage):
    pass


class OaiChatCompletionAnnotation:
    pass


@dc.dataclass(frozen=True, kw_only=True)
class OaiChatCompletionUrlCitation:
    end_index: int
    start_index: int
    title: str
    url: str


@dc.dataclass(frozen=True, kw_only=True)
class UrlCitationOaiChatCompletionAnnotation(OaiChatCompletionAnnotation):
    url_citation: OaiChatCompletionUrlCitation
    type: ta.Literal['url_citation'] = 'url_citation'


@dc.dataclass(frozen=True, kw_only=True)
class AssistantOaiChatCompletionResponseMessage(
    AssistantOaiLikeChatCompletionResponseMessage[
        OaiChatCompletionResponseToolCall,
    ],
    OaiChatCompletionResponseMessage,
):
    annotations: ta.Sequence[OaiChatCompletionAnnotation] | None = None
    refusal: str | None = None


class OaiChatCompletionStreamDelta(OaiLikeChatCompletionStreamDelta):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class AssistantOaiChatCompletionStreamDelta(
    AssistantOaiLikeChatCompletionStreamDelta[
        OaiChatCompletionStreamDeltaToolCall,
    ],
    OaiChatCompletionStreamDelta,
):
    refusal: str | None = None


##
# OpenAI logprobs.


@dc.dataclass(frozen=True, kw_only=True)
class OaiChatCompletionTopLogprob(
    OaiLikeChatCompletionTopLogprob,
):
    logprob: float
    token: str
    bytes: ta.Sequence[int] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OaiChatCompletionTokenLogprob(
    OaiLikeChatCompletionTokenLogprob[
        OaiChatCompletionTopLogprob,
    ],
):
    logprob: float
    token: str
    bytes: ta.Sequence[int] | None = None
    top_logprobs: ta.Sequence[OaiChatCompletionTopLogprob] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OaiChatCompletionLogprobs(
    OaiLikeChatCompletionLogprobs[
        OaiChatCompletionTokenLogprob,
    ],
):
    content: ta.Sequence[OaiChatCompletionTokenLogprob] | None = None
    refusal: ta.Sequence[OaiChatCompletionTokenLogprob] | None = None


##
# OpenAI choices, usage, responses, and stream chunks.


@dc.dataclass(frozen=True, kw_only=True)
class OaiChatCompletionChoice(
    LogprobsOaiLikeChatCompletionChoice[
        AssistantOaiChatCompletionResponseMessage,
        OaiChatCompletionFinishReason,
        OaiChatCompletionLogprobs,
    ],
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class OaiChatCompletionStreamChoice(
    LogprobsOaiLikeChatCompletionStreamChoice[
        AssistantOaiChatCompletionStreamDelta,
        OaiChatCompletionFinishReason,
        OaiChatCompletionLogprobs,
    ],
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class OaiChatCompletionPromptTokensDetails:
    audio_tokens: int | None = None
    cached_tokens: int | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OaiChatCompletionCompletionTokensDetails:
    accepted_prediction_tokens: int | None = None
    audio_tokens: int | None = None
    reasoning_tokens: int | None = None
    rejected_prediction_tokens: int | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OaiChatCompletionUsage(OaiLikeChatCompletionUsage):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int
    completion_tokens_details: OaiChatCompletionCompletionTokensDetails | None = None
    prompt_tokens_details: OaiChatCompletionPromptTokensDetails | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OaiChatCompletionResponse(
    HasOaiLikeChatCompletionSystemFingerprint,
    HasOaiChatCompletionServiceTier,
    OaiLikeChatCompletionResponse[
        OaiChatCompletionChoice,
        OaiChatCompletionUsage,
    ],
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class OaiChatCompletionStreamChunk(
    HasOaiLikeChatCompletionSystemFingerprint,
    HasOaiChatCompletionServiceTier,
    OaiLikeChatCompletionStreamChunk[
        OaiChatCompletionStreamChoice,
        OaiChatCompletionUsage,
    ],
):
    pass


##
# OpenAI requests.


@dc.dataclass(frozen=True, kw_only=True)
class OaiChatCompletionStreamOptions(
    OaiLikeChatCompletionStreamOptions,
):
    include_obfuscation: bool | None = None
    include_usage: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OaiChatCompletionRequest(
    HasOaiLikeChatCompletionLogprobsRequest,
    HasOaiLikeParallelToolCalls,
    HasOaiChatCompletionPromptCaching,
    HasOaiChatCompletionReasoningEffort,
    HasOaiChatCompletionRequestIdentity,
    HasOaiChatCompletionRequestMetadata,
    HasOaiChatCompletionRequestTokenControls,
    HasOaiChatCompletionServiceTier,
    HasOaiChatCompletionVerbosity,
    OaiLikeChatCompletionRequest[
        OaiChatCompletionRequestMessage,
        OaiChatCompletionTool,
        OaiChatCompletionToolChoiceOption,
        OaiChatCompletionResponseFormat,
    ],
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class OaiChatCompletionStreamRequest(
    HasOaiLikeChatCompletionLogprobsRequest,
    HasOaiLikeParallelToolCalls,
    HasOaiChatCompletionPromptCaching,
    HasOaiChatCompletionReasoningEffort,
    HasOaiChatCompletionRequestIdentity,
    HasOaiChatCompletionRequestMetadata,
    HasOaiChatCompletionRequestTokenControls,
    HasOaiChatCompletionServiceTier,
    HasOaiChatCompletionVerbosity,
    OaiLikeChatCompletionStreamRequest[
        OaiChatCompletionRequestMessage,
        OaiChatCompletionTool,
        OaiChatCompletionToolChoiceOption,
        OaiChatCompletionResponseFormat,
        OaiChatCompletionStreamOptions,
    ],
):
    pass


###
# Ollama OpenAI-compatible Chat Completions.


OllamaChatCompletionReasoningEffort = ta.Literal[
    'high',
    'medium',
    'low',
    'max',
    'none',
]


@dc.dataclass(frozen=True, kw_only=True)
class OllamaChatCompletionReasoning:
    effort: OllamaChatCompletionReasoningEffort | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasOllamaChatCompletionReasoningControls[
    ReasoningT: OllamaChatCompletionReasoning = OllamaChatCompletionReasoning,
]:
    reasoning: ReasoningT | None = None
    reasoning_effort: OllamaChatCompletionReasoningEffort | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasOllamaChatCompletionRequestIdentity:
    user: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasOllamaChatCompletionRequestTokenControls:
    logit_bias: ta.Mapping[str, float] | None = None
    n: int | None = None
    seed: int | None = None


##
# Ollama content parts.


class OllamaChatCompletionContentPart(OaiLikeChatCompletionContentPart):
    pass


class OllamaChatCompletionUserRequestContentPart(OllamaChatCompletionContentPart):
    pass


class OllamaChatCompletionAssistantRequestContentPart(OllamaChatCompletionContentPart):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class TextOllamaChatCompletionContentPart(
    TextOaiLikeChatCompletionContentPart,
    OllamaChatCompletionUserRequestContentPart,
    OllamaChatCompletionAssistantRequestContentPart,
):
    text: str
    type: ta.Literal['text'] = 'text'


@dc.dataclass(frozen=True, kw_only=True)
class OllamaChatCompletionImageUrl:
    url: str


OllamaChatCompletionImageUrlValue = str | OllamaChatCompletionImageUrl


@dc.dataclass(frozen=True, kw_only=True)
class ImageUrlOllamaChatCompletionContentPart(
    ImageUrlOaiLikeChatCompletionContentPart[
        OllamaChatCompletionImageUrlValue,
    ],
    OllamaChatCompletionUserRequestContentPart,
):
    image_url: OllamaChatCompletionImageUrlValue
    type: ta.Literal['image_url'] = 'image_url'


##
# Ollama response_format objects.


class OllamaChatCompletionResponseFormat(OaiLikeChatCompletionResponseFormat):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class JsonObjectOllamaChatCompletionResponseFormat(
    JsonObjectOaiLikeChatCompletionResponseFormat,
    OllamaChatCompletionResponseFormat,
):
    type: ta.Literal['json_object'] = 'json_object'


@dc.dataclass(frozen=True, kw_only=True)
class OllamaChatCompletionJsonSchema:
    schema: JsonValue


@dc.dataclass(frozen=True, kw_only=True)
class JsonSchemaOllamaChatCompletionResponseFormat(
    JsonSchemaOaiLikeChatCompletionResponseFormat[
        OllamaChatCompletionJsonSchema,
    ],
    OllamaChatCompletionResponseFormat,
):
    json_schema: OllamaChatCompletionJsonSchema
    type: ta.Literal['json_schema'] = 'json_schema'


##
# Ollama tools and tool choices.


@dc.dataclass(frozen=True, kw_only=True)
class OllamaChatCompletionFunctionDefinition(OaiLikeChatCompletionFunctionDefinition):
    name: str
    description: str | None = None
    parameters: JsonObject | None = None


class OllamaChatCompletionTool(OaiLikeChatCompletionTool):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class FunctionOllamaChatCompletionTool(
    FunctionOaiLikeChatCompletionTool[
        OllamaChatCompletionFunctionDefinition,
    ],
    OllamaChatCompletionTool,
):
    function: OllamaChatCompletionFunctionDefinition
    type: ta.Literal['function'] = 'function'


class OllamaChatCompletionToolChoice(OaiLikeChatCompletionToolChoice):
    pass


OllamaChatCompletionToolChoiceMode = OaiLikeChatCompletionToolChoiceMode
OllamaChatCompletionToolChoiceOption = (
    OllamaChatCompletionToolChoiceMode |
    OllamaChatCompletionToolChoice
)


@dc.dataclass(frozen=True, kw_only=True)
class OllamaChatCompletionNamedToolChoiceFunction(
    OaiLikeChatCompletionNamedToolChoiceFunction,
):
    name: str


@dc.dataclass(frozen=True, kw_only=True)
class FunctionOllamaChatCompletionToolChoice(
    FunctionOaiLikeChatCompletionToolChoice[
        OllamaChatCompletionNamedToolChoiceFunction,
    ],
    OllamaChatCompletionToolChoice,
):
    function: OllamaChatCompletionNamedToolChoiceFunction
    type: ta.Literal['function'] = 'function'


##
# Ollama generated tool calls.


class OllamaChatCompletionResponseToolCall(OaiLikeChatCompletionResponseToolCall):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class OllamaChatCompletionResponseToolCallFunction(
    OaiLikeChatCompletionResponseToolCallFunction,
):
    arguments: str
    name: str


@dc.dataclass(frozen=True, kw_only=True)
class FunctionOllamaChatCompletionResponseToolCall(
    FunctionOaiLikeChatCompletionResponseToolCall[
        OllamaChatCompletionResponseToolCallFunction,
    ],
    OllamaChatCompletionResponseToolCall,
):
    id: str
    function: OllamaChatCompletionResponseToolCallFunction
    index: int | None = None
    type: ta.Literal['function'] = 'function'


class OllamaChatCompletionStreamDeltaToolCall(OaiLikeChatCompletionStreamDeltaToolCall):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class OllamaChatCompletionStreamDeltaToolCallFunction(
    OaiLikeChatCompletionStreamDeltaToolCallFunction,
):
    arguments: str | None = None
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class FunctionOllamaChatCompletionStreamDeltaToolCall(
    FunctionOaiLikeChatCompletionStreamDeltaToolCall[
        OllamaChatCompletionStreamDeltaToolCallFunction,
    ],
    OllamaChatCompletionStreamDeltaToolCall,
):
    index: int
    function: OllamaChatCompletionStreamDeltaToolCallFunction | None = None
    id: str | None = None
    type: ta.Literal['function'] | None = None


##
# Ollama request messages.


class OllamaChatCompletionRequestMessage(OaiLikeChatCompletionRequestMessage):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class SystemOllamaChatCompletionRequestMessage(
    SystemOaiLikeChatCompletionRequestMessage[
        TextOllamaChatCompletionContentPart,
    ],
    OllamaChatCompletionRequestMessage,
):
    name: str | None = None
    reasoning: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class UserOllamaChatCompletionRequestMessage(
    UserOaiLikeChatCompletionRequestMessage[
        OllamaChatCompletionUserRequestContentPart,
    ],
    OllamaChatCompletionRequestMessage,
):
    name: str | None = None
    reasoning: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class AssistantOllamaChatCompletionRequestMessage(
    AssistantOaiLikeChatCompletionRequestMessage[
        OllamaChatCompletionAssistantRequestContentPart,
        OllamaChatCompletionResponseToolCall,
    ],
    OllamaChatCompletionRequestMessage,
):
    name: str | None = None
    reasoning: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class ToolOllamaChatCompletionRequestMessage(
    ToolOaiLikeChatCompletionRequestMessage[
        TextOllamaChatCompletionContentPart,
    ],
    OllamaChatCompletionRequestMessage,
):
    name: str | None = None
    reasoning: str | None = None


##
# Ollama response messages and stream deltas.


class OllamaChatCompletionResponseMessage(OaiLikeChatCompletionResponseMessage):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class AssistantOllamaChatCompletionResponseMessage(
    AssistantOaiLikeChatCompletionResponseMessage[
        OllamaChatCompletionResponseToolCall,
    ],
    OllamaChatCompletionResponseMessage,
):
    reasoning: str | None = None


class OllamaChatCompletionStreamDelta(OaiLikeChatCompletionStreamDelta):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class AssistantOllamaChatCompletionStreamDelta(
    AssistantOaiLikeChatCompletionStreamDelta[
        OllamaChatCompletionStreamDeltaToolCall,
    ],
    OllamaChatCompletionStreamDelta,
):
    reasoning: str | None = None


##
# Ollama logprobs.


@dc.dataclass(frozen=True, kw_only=True)
class OllamaChatCompletionTopLogprob(
    OaiLikeChatCompletionTopLogprob,
):
    logprob: float
    token: str
    bytes: ta.Sequence[int] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OllamaChatCompletionTokenLogprob(
    OaiLikeChatCompletionTokenLogprob[
        OllamaChatCompletionTopLogprob,
    ],
):
    logprob: float
    token: str
    bytes: ta.Sequence[int] | None = None
    top_logprobs: ta.Sequence[OllamaChatCompletionTopLogprob] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OllamaChatCompletionLogprobs(
    OaiLikeChatCompletionLogprobs[
        OllamaChatCompletionTokenLogprob,
    ],
):
    content: ta.Sequence[OllamaChatCompletionTokenLogprob] | None = None
    refusal: ta.Sequence[OllamaChatCompletionTokenLogprob] | None = None


##
# Ollama choices, responses, and stream chunks.


@dc.dataclass(frozen=True, kw_only=True)
class OllamaChatCompletionChoice(
    LogprobsOaiLikeChatCompletionChoice[
        AssistantOllamaChatCompletionResponseMessage,
        str,
        OllamaChatCompletionLogprobs,
    ],
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class OllamaChatCompletionStreamChoice(
    LogprobsOaiLikeChatCompletionStreamChoice[
        AssistantOllamaChatCompletionStreamDelta,
        str,
        OllamaChatCompletionLogprobs,
    ],
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class OllamaChatCompletionResponse(
    HasOaiLikeChatCompletionSystemFingerprint,
    OaiLikeChatCompletionResponse[
        OllamaChatCompletionChoice,
        OaiLikeChatCompletionUsage,
    ],
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class OllamaChatCompletionStreamChunk(
    HasOaiLikeChatCompletionSystemFingerprint,
    OaiLikeChatCompletionStreamChunk[
        OllamaChatCompletionStreamChoice,
        OaiLikeChatCompletionUsage,
    ],
):
    pass


##
# Ollama requests.


@dc.dataclass(frozen=True, kw_only=True)
class OllamaChatCompletionStreamOptions(
    OaiLikeChatCompletionStreamOptions,
):
    include_usage: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OllamaChatCompletionRequest(
    HasOaiLikeChatCompletionLogprobsRequest,
    HasOllamaChatCompletionReasoningControls[
        OllamaChatCompletionReasoning,
    ],
    HasOllamaChatCompletionRequestIdentity,
    HasOllamaChatCompletionRequestTokenControls,
    OaiLikeChatCompletionRequest[
        OllamaChatCompletionRequestMessage,
        OllamaChatCompletionTool,
        OllamaChatCompletionToolChoiceOption,
        OllamaChatCompletionResponseFormat,
    ],
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class OllamaChatCompletionStreamRequest(
    HasOaiLikeChatCompletionLogprobsRequest,
    HasOllamaChatCompletionReasoningControls[
        OllamaChatCompletionReasoning,
    ],
    HasOllamaChatCompletionRequestIdentity,
    HasOllamaChatCompletionRequestTokenControls,
    OaiLikeChatCompletionStreamRequest[
        OllamaChatCompletionRequestMessage,
        OllamaChatCompletionTool,
        OllamaChatCompletionToolChoiceOption,
        OllamaChatCompletionResponseFormat,
        OllamaChatCompletionStreamOptions,
    ],
):
    pass



###
# vLLM OpenAI-compatible Chat Completions.


@dc.dataclass(frozen=True, kw_only=True)
class HasVllmChatCompletionExtraSampling:
    allowed_token_ids: ta.Sequence[int] | None = None
    bad_words: ta.Sequence[str] | None = None
    ignore_eos: bool | None = None
    include_stop_str_in_output: bool | None = None
    length_penalty: float | None = None
    min_p: float | None = None
    min_tokens: int | None = None
    prompt_logprobs: int | None = None
    repetition_penalty: float | None = None
    skip_special_tokens: bool | None = None
    spaces_between_special_tokens: bool | None = None
    stop_token_ids: ta.Sequence[int] | None = None
    top_k: int | None = None
    truncate_prompt_tokens: int | None = None
    use_beam_search: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasVllmChatCompletionTemplateControls:
    add_generation_prompt: bool | None = None
    add_special_tokens: bool | None = None
    chat_template: str | None = None
    chat_template_kwargs: JsonObject | None = None
    continue_final_message: bool | None = None
    documents: ta.Sequence[JsonObject] | None = None
    echo: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasVllmChatCompletionMultimodalControls:
    media_io_kwargs: JsonObject | None = None
    mm_processor_kwargs: JsonObject | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasVllmChatCompletionOutputControls:
    return_prompt_text: bool | None = None
    return_token_ids: bool | None = None
    return_tokens_as_token_ids: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasVllmChatCompletionRequestIdentity:
    request_id: str | None = None
    user: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasVllmChatCompletionPriority:
    priority: int | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasVllmChatCompletionPrefixCaching:
    cache_salt: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasVllmChatCompletionStructuredOutputs:
    structured_outputs: JsonObject | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasVllmChatCompletionReasoningEffort:
    reasoning_effort: str | None = None


##
# vLLM content parts.


class VllmChatCompletionContentPart(OaiLikeChatCompletionContentPart):
    pass


class VllmChatCompletionUserRequestContentPart(VllmChatCompletionContentPart):
    pass


class VllmChatCompletionAssistantRequestContentPart(VllmChatCompletionContentPart):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class TextVllmChatCompletionContentPart(
    TextOaiLikeChatCompletionContentPart,
    VllmChatCompletionUserRequestContentPart,
    VllmChatCompletionAssistantRequestContentPart,
):
    text: str
    type: ta.Literal['text'] = 'text'


@dc.dataclass(frozen=True, kw_only=True)
class VllmChatCompletionImageUrl:
    url: str


VllmChatCompletionImageUrlValue = str | VllmChatCompletionImageUrl


@dc.dataclass(frozen=True, kw_only=True)
class ImageUrlVllmChatCompletionContentPart(
    ImageUrlOaiLikeChatCompletionContentPart[
        VllmChatCompletionImageUrlValue,
    ],
    VllmChatCompletionUserRequestContentPart,
):
    image_url: VllmChatCompletionImageUrlValue
    type: ta.Literal['image_url'] = 'image_url'


##
# vLLM response_format objects.


class VllmChatCompletionResponseFormat(OaiLikeChatCompletionResponseFormat):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class TextVllmChatCompletionResponseFormat(
    TextOaiLikeChatCompletionResponseFormat,
    VllmChatCompletionResponseFormat,
):
    type: ta.Literal['text'] = 'text'


@dc.dataclass(frozen=True, kw_only=True)
class JsonObjectVllmChatCompletionResponseFormat(
    JsonObjectOaiLikeChatCompletionResponseFormat,
    VllmChatCompletionResponseFormat,
):
    type: ta.Literal['json_object'] = 'json_object'


@dc.dataclass(frozen=True, kw_only=True)
class VllmChatCompletionJsonSchema:
    name: str | None = None
    description: str | None = None
    schema: JsonObject | None = None
    strict: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class JsonSchemaVllmChatCompletionResponseFormat(
    JsonSchemaOaiLikeChatCompletionResponseFormat[
        VllmChatCompletionJsonSchema,
    ],
    VllmChatCompletionResponseFormat,
):
    json_schema: VllmChatCompletionJsonSchema
    type: ta.Literal['json_schema'] = 'json_schema'


##
# vLLM tools and tool choices.


@dc.dataclass(frozen=True, kw_only=True)
class VllmChatCompletionFunctionDefinition(OaiLikeChatCompletionFunctionDefinition):
    name: str
    description: str | None = None
    parameters: JsonObject | None = None
    strict: bool | None = None


class VllmChatCompletionTool(OaiLikeChatCompletionTool):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class FunctionVllmChatCompletionTool(
    FunctionOaiLikeChatCompletionTool[
        VllmChatCompletionFunctionDefinition,
    ],
    VllmChatCompletionTool,
):
    function: VllmChatCompletionFunctionDefinition
    type: ta.Literal['function'] = 'function'


class VllmChatCompletionToolChoice(OaiLikeChatCompletionToolChoice):
    pass


VllmChatCompletionToolChoiceMode = OaiLikeChatCompletionToolChoiceMode
VllmChatCompletionToolChoiceOption = (
    VllmChatCompletionToolChoiceMode |
    VllmChatCompletionToolChoice
)


@dc.dataclass(frozen=True, kw_only=True)
class VllmChatCompletionNamedToolChoiceFunction(
    OaiLikeChatCompletionNamedToolChoiceFunction,
):
    name: str


@dc.dataclass(frozen=True, kw_only=True)
class FunctionVllmChatCompletionToolChoice(
    FunctionOaiLikeChatCompletionToolChoice[
        VllmChatCompletionNamedToolChoiceFunction,
    ],
    VllmChatCompletionToolChoice,
):
    function: VllmChatCompletionNamedToolChoiceFunction
    type: ta.Literal['function'] = 'function'


##
# vLLM generated tool calls.


class VllmChatCompletionResponseToolCall(OaiLikeChatCompletionResponseToolCall):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class VllmChatCompletionResponseToolCallFunction(
    OaiLikeChatCompletionResponseToolCallFunction,
):
    arguments: str
    name: str


@dc.dataclass(frozen=True, kw_only=True)
class FunctionVllmChatCompletionResponseToolCall(
    FunctionOaiLikeChatCompletionResponseToolCall[
        VllmChatCompletionResponseToolCallFunction,
    ],
    VllmChatCompletionResponseToolCall,
):
    id: str
    function: VllmChatCompletionResponseToolCallFunction
    type: ta.Literal['function'] = 'function'


class VllmChatCompletionStreamDeltaToolCall(OaiLikeChatCompletionStreamDeltaToolCall):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class VllmChatCompletionStreamDeltaToolCallFunction(
    OaiLikeChatCompletionStreamDeltaToolCallFunction,
):
    arguments: str | None = None
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class FunctionVllmChatCompletionStreamDeltaToolCall(
    FunctionOaiLikeChatCompletionStreamDeltaToolCall[
        VllmChatCompletionStreamDeltaToolCallFunction,
    ],
    VllmChatCompletionStreamDeltaToolCall,
):
    index: int
    function: VllmChatCompletionStreamDeltaToolCallFunction | None = None
    id: str | None = None
    type: ta.Literal['function'] | None = None


##
# vLLM request messages.


class VllmChatCompletionRequestMessage(OaiLikeChatCompletionRequestMessage):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class SystemVllmChatCompletionRequestMessage(
    SystemOaiLikeChatCompletionRequestMessage[
        TextVllmChatCompletionContentPart,
    ],
    VllmChatCompletionRequestMessage,
):
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class UserVllmChatCompletionRequestMessage(
    UserOaiLikeChatCompletionRequestMessage[
        VllmChatCompletionUserRequestContentPart,
    ],
    VllmChatCompletionRequestMessage,
):
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class AssistantVllmChatCompletionRequestMessage(
    AssistantOaiLikeChatCompletionRequestMessage[
        VllmChatCompletionAssistantRequestContentPart,
        VllmChatCompletionResponseToolCall,
    ],
    VllmChatCompletionRequestMessage,
):
    name: str | None = None
    reasoning: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class ToolVllmChatCompletionRequestMessage(
    ToolOaiLikeChatCompletionRequestMessage[
        TextVllmChatCompletionContentPart,
    ],
    VllmChatCompletionRequestMessage,
):
    pass


##
# vLLM response messages and stream deltas.


class VllmChatCompletionResponseMessage(OaiLikeChatCompletionResponseMessage):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class AssistantVllmChatCompletionResponseMessage(
    AssistantOaiLikeChatCompletionResponseMessage[
        VllmChatCompletionResponseToolCall,
    ],
    VllmChatCompletionResponseMessage,
):
    reasoning: str | None = None


class VllmChatCompletionStreamDelta(OaiLikeChatCompletionStreamDelta):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class AssistantVllmChatCompletionStreamDelta(
    AssistantOaiLikeChatCompletionStreamDelta[
        VllmChatCompletionStreamDeltaToolCall,
    ],
    VllmChatCompletionStreamDelta,
):
    reasoning: str | None = None


##
# vLLM logprobs.


@dc.dataclass(frozen=True, kw_only=True)
class VllmChatCompletionTopLogprob(
    OaiLikeChatCompletionTopLogprob,
):
    logprob: float
    token: str
    bytes: ta.Sequence[int] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class VllmChatCompletionTokenLogprob(
    OaiLikeChatCompletionTokenLogprob[
        VllmChatCompletionTopLogprob,
    ],
):
    logprob: float
    token: str
    bytes: ta.Sequence[int] | None = None
    top_logprobs: ta.Sequence[VllmChatCompletionTopLogprob] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class VllmChatCompletionLogprobs(
    OaiLikeChatCompletionLogprobs[
        VllmChatCompletionTokenLogprob,
    ],
):
    content: ta.Sequence[VllmChatCompletionTokenLogprob] | None = None
    refusal: ta.Sequence[VllmChatCompletionTokenLogprob] | None = None


##
# vLLM choices, responses, and stream chunks.


@dc.dataclass(frozen=True, kw_only=True)
class VllmChatCompletionChoice(
    LogprobsOaiLikeChatCompletionChoice[
        AssistantVllmChatCompletionResponseMessage,
        str,
        VllmChatCompletionLogprobs,
    ],
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class VllmChatCompletionStreamChoice(
    LogprobsOaiLikeChatCompletionStreamChoice[
        AssistantVllmChatCompletionStreamDelta,
        str,
        VllmChatCompletionLogprobs,
    ],
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class VllmChatCompletionResponse(
    HasOaiLikeChatCompletionSystemFingerprint,
    OaiLikeChatCompletionResponse[
        VllmChatCompletionChoice,
        OaiLikeChatCompletionUsage,
    ],
):
    prompt_text: str | None = None
    prompt_token_ids: ta.Sequence[int] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class VllmChatCompletionStreamChunk(
    HasOaiLikeChatCompletionSystemFingerprint,
    OaiLikeChatCompletionStreamChunk[
        VllmChatCompletionStreamChoice,
        OaiLikeChatCompletionUsage,
    ],
):
    prompt_text: str | None = None
    prompt_token_ids: ta.Sequence[int] | None = None


##
# vLLM requests.


@dc.dataclass(frozen=True, kw_only=True)
class VllmChatCompletionStreamOptions(
    OaiLikeChatCompletionStreamOptions,
):
    include_usage: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class VllmChatCompletionRequest(
    HasOaiLikeChatCompletionLogprobsRequest,
    HasOaiLikeParallelToolCalls,
    HasVllmChatCompletionExtraSampling,
    HasVllmChatCompletionMultimodalControls,
    HasVllmChatCompletionOutputControls,
    HasVllmChatCompletionPrefixCaching,
    HasVllmChatCompletionPriority,
    HasVllmChatCompletionReasoningEffort,
    HasVllmChatCompletionRequestIdentity,
    HasVllmChatCompletionStructuredOutputs,
    HasVllmChatCompletionTemplateControls,
    OaiLikeChatCompletionRequest[
        VllmChatCompletionRequestMessage,
        VllmChatCompletionTool,
        VllmChatCompletionToolChoiceOption,
        VllmChatCompletionResponseFormat,
    ],
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class VllmChatCompletionStreamRequest(
    HasOaiLikeChatCompletionLogprobsRequest,
    HasOaiLikeParallelToolCalls,
    HasVllmChatCompletionExtraSampling,
    HasVllmChatCompletionMultimodalControls,
    HasVllmChatCompletionOutputControls,
    HasVllmChatCompletionPrefixCaching,
    HasVllmChatCompletionPriority,
    HasVllmChatCompletionReasoningEffort,
    HasVllmChatCompletionRequestIdentity,
    HasVllmChatCompletionStructuredOutputs,
    HasVllmChatCompletionTemplateControls,
    OaiLikeChatCompletionStreamRequest[
        VllmChatCompletionRequestMessage,
        VllmChatCompletionTool,
        VllmChatCompletionToolChoiceOption,
        VllmChatCompletionResponseFormat,
        VllmChatCompletionStreamOptions,
    ],
):
    pass


###
# OpenRouter Chat Completions.


OpenrouterChatCompletionFinishReason = ta.Literal[
    'tool_calls',
    'stop',
    'length',
    'content_filter',
    'error',
]


OpenrouterChatCompletionReasoningEffort = ta.Literal[
    'max',
    'xhigh',
    'high',
    'medium',
    'low',
    'minimal',
    'none',
]


OpenrouterChatCompletionModality = ta.Literal[
    'text',
    'image',
    'audio',
]


OpenrouterChatCompletionServiceTier = ta.Literal[
    'auto',
    'default',
    'flex',
]


@dc.dataclass(frozen=True, kw_only=True)
class OpenrouterChatCompletionReasoning:
    effort: OpenrouterChatCompletionReasoningEffort | None = None
    max_tokens: int | None = None
    exclude: bool | None = None
    enabled: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasOpenrouterChatCompletionCacheControls:
    cache_control: JsonObject | None = None
    session_id: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasOpenrouterChatCompletionProviderRouting:
    models: ta.Sequence[str] | None = None
    provider: JsonObject | None = None
    route: JsonValue | None = None
    service_tier: OpenrouterChatCompletionServiceTier | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasOpenrouterChatCompletionReasoningControls[
    ReasoningT: OpenrouterChatCompletionReasoning = OpenrouterChatCompletionReasoning,
]:
    reasoning: ReasoningT | None = None
    reasoning_effort: OpenrouterChatCompletionReasoningEffort | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasOpenrouterChatCompletionRequestMetadata:
    metadata: ta.Mapping[str, str] | None = None
    user: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasOpenrouterChatCompletionRequestTokenControls:
    image_config: JsonValue | None = None
    logit_bias: ta.Mapping[str, float] | None = None
    max_completion_tokens: int | None = None
    min_p: float | None = None
    modalities: ta.Sequence[OpenrouterChatCompletionModality] | None = None
    repetition_penalty: float | None = None
    seed: int | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasOpenrouterChatCompletionDebugControls:
    debug: JsonObject | None = None


##
# OpenRouter content parts.


class OpenrouterChatCompletionContentPart(OaiLikeChatCompletionContentPart):
    pass


class OpenrouterChatCompletionUserRequestContentPart(OpenrouterChatCompletionContentPart):
    pass


class OpenrouterChatCompletionAssistantRequestContentPart(OpenrouterChatCompletionContentPart):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class TextOpenrouterChatCompletionContentPart(
    TextOaiLikeChatCompletionContentPart,
    OpenrouterChatCompletionUserRequestContentPart,
    OpenrouterChatCompletionAssistantRequestContentPart,
):
    text: str
    type: ta.Literal['text'] = 'text'


@dc.dataclass(frozen=True, kw_only=True)
class OpenrouterChatCompletionImageUrl:
    url: str
    detail: str | None = None


OpenrouterChatCompletionImageUrlValue = str | OpenrouterChatCompletionImageUrl


@dc.dataclass(frozen=True, kw_only=True)
class ImageUrlOpenrouterChatCompletionContentPart(
    ImageUrlOaiLikeChatCompletionContentPart[
        OpenrouterChatCompletionImageUrlValue,
    ],
    OpenrouterChatCompletionUserRequestContentPart,
):
    image_url: OpenrouterChatCompletionImageUrlValue
    type: ta.Literal['image_url'] = 'image_url'


##
# OpenRouter response_format objects.


class OpenrouterChatCompletionResponseFormat(OaiLikeChatCompletionResponseFormat):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class TextOpenrouterChatCompletionResponseFormat(
    TextOaiLikeChatCompletionResponseFormat,
    OpenrouterChatCompletionResponseFormat,
):
    type: ta.Literal['text'] = 'text'


@dc.dataclass(frozen=True, kw_only=True)
class JsonObjectOpenrouterChatCompletionResponseFormat(
    JsonObjectOaiLikeChatCompletionResponseFormat,
    OpenrouterChatCompletionResponseFormat,
):
    type: ta.Literal['json_object'] = 'json_object'


@dc.dataclass(frozen=True, kw_only=True)
class OpenrouterChatCompletionJsonSchema:
    name: str | None = None
    description: str | None = None
    schema: JsonObject | None = None
    strict: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class JsonSchemaOpenrouterChatCompletionResponseFormat(
    JsonSchemaOaiLikeChatCompletionResponseFormat[
        OpenrouterChatCompletionJsonSchema,
    ],
    OpenrouterChatCompletionResponseFormat,
):
    json_schema: OpenrouterChatCompletionJsonSchema
    type: ta.Literal['json_schema'] = 'json_schema'


##
# OpenRouter tools and tool choices.


@dc.dataclass(frozen=True, kw_only=True)
class OpenrouterChatCompletionFunctionDefinition(OaiLikeChatCompletionFunctionDefinition):
    name: str
    description: str | None = None
    parameters: JsonObject | None = None
    strict: bool | None = None


class OpenrouterChatCompletionTool(OaiLikeChatCompletionTool):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class FunctionOpenrouterChatCompletionTool(
    FunctionOaiLikeChatCompletionTool[
        OpenrouterChatCompletionFunctionDefinition,
    ],
    OpenrouterChatCompletionTool,
):
    function: OpenrouterChatCompletionFunctionDefinition
    type: ta.Literal['function'] = 'function'


class OpenrouterChatCompletionToolChoice(OaiLikeChatCompletionToolChoice):
    pass


OpenrouterChatCompletionToolChoiceMode = OaiLikeChatCompletionToolChoiceMode
OpenrouterChatCompletionToolChoiceOption = (
    OpenrouterChatCompletionToolChoiceMode |
    OpenrouterChatCompletionToolChoice
)


@dc.dataclass(frozen=True, kw_only=True)
class OpenrouterChatCompletionNamedToolChoiceFunction(
    OaiLikeChatCompletionNamedToolChoiceFunction,
):
    name: str


@dc.dataclass(frozen=True, kw_only=True)
class FunctionOpenrouterChatCompletionToolChoice(
    FunctionOaiLikeChatCompletionToolChoice[
        OpenrouterChatCompletionNamedToolChoiceFunction,
    ],
    OpenrouterChatCompletionToolChoice,
):
    function: OpenrouterChatCompletionNamedToolChoiceFunction
    type: ta.Literal['function'] = 'function'


##
# OpenRouter generated tool calls.


class OpenrouterChatCompletionResponseToolCall(OaiLikeChatCompletionResponseToolCall):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class OpenrouterChatCompletionResponseToolCallFunction(
    OaiLikeChatCompletionResponseToolCallFunction,
):
    arguments: str
    name: str


@dc.dataclass(frozen=True, kw_only=True)
class FunctionOpenrouterChatCompletionResponseToolCall(
    FunctionOaiLikeChatCompletionResponseToolCall[
        OpenrouterChatCompletionResponseToolCallFunction,
    ],
    OpenrouterChatCompletionResponseToolCall,
):
    id: str
    function: OpenrouterChatCompletionResponseToolCallFunction
    type: ta.Literal['function'] = 'function'


class OpenrouterChatCompletionStreamDeltaToolCall(OaiLikeChatCompletionStreamDeltaToolCall):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class OpenrouterChatCompletionStreamDeltaToolCallFunction(
    OaiLikeChatCompletionStreamDeltaToolCallFunction,
):
    arguments: str | None = None
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class FunctionOpenrouterChatCompletionStreamDeltaToolCall(
    FunctionOaiLikeChatCompletionStreamDeltaToolCall[
        OpenrouterChatCompletionStreamDeltaToolCallFunction,
    ],
    OpenrouterChatCompletionStreamDeltaToolCall,
):
    index: int
    function: OpenrouterChatCompletionStreamDeltaToolCallFunction | None = None
    id: str | None = None
    type: ta.Literal['function'] | None = None


##
# OpenRouter request messages.


class OpenrouterChatCompletionRequestMessage(OaiLikeChatCompletionRequestMessage):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class SystemOpenrouterChatCompletionRequestMessage(
    SystemOaiLikeChatCompletionRequestMessage[
        TextOpenrouterChatCompletionContentPart,
    ],
    OpenrouterChatCompletionRequestMessage,
):
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class UserOpenrouterChatCompletionRequestMessage(
    UserOaiLikeChatCompletionRequestMessage[
        OpenrouterChatCompletionUserRequestContentPart,
    ],
    OpenrouterChatCompletionRequestMessage,
):
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class AssistantOpenrouterChatCompletionRequestMessage(
    AssistantOaiLikeChatCompletionRequestMessage[
        OpenrouterChatCompletionAssistantRequestContentPart,
        OpenrouterChatCompletionResponseToolCall,
    ],
    OpenrouterChatCompletionRequestMessage,
):
    name: str | None = None
    reasoning: str | None = None
    reasoning_content: str | None = None
    reasoning_details: ta.Sequence[JsonObject] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class ToolOpenrouterChatCompletionRequestMessage(
    ToolOaiLikeChatCompletionRequestMessage[
        TextOpenrouterChatCompletionContentPart,
    ],
    OpenrouterChatCompletionRequestMessage,
):
    pass


##
# OpenRouter response messages and stream deltas.


class OpenrouterChatCompletionResponseMessage(OaiLikeChatCompletionResponseMessage):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class AssistantOpenrouterChatCompletionResponseMessage(
    AssistantOaiLikeChatCompletionResponseMessage[
        OpenrouterChatCompletionResponseToolCall,
    ],
    OpenrouterChatCompletionResponseMessage,
):
    reasoning: str | None = None
    reasoning_details: ta.Sequence[JsonObject] | None = None


class OpenrouterChatCompletionStreamDelta(OaiLikeChatCompletionStreamDelta):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class AssistantOpenrouterChatCompletionStreamDelta(
    AssistantOaiLikeChatCompletionStreamDelta[
        OpenrouterChatCompletionStreamDeltaToolCall,
    ],
    OpenrouterChatCompletionStreamDelta,
):
    reasoning: str | None = None
    reasoning_details: ta.Sequence[JsonObject] | None = None


##
# OpenRouter choice errors, usage, choices, responses, and stream chunks.


@dc.dataclass(frozen=True, kw_only=True)
class OpenrouterChatCompletionError:
    code: int
    message: str
    metadata: JsonObject | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OpenrouterChatCompletionCostDetails:
    upstream_inference_cost: float | None = None
    upstream_inference_prompt_cost: float | None = None
    upstream_inference_completions_cost: float | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OpenrouterChatCompletionPromptTokensDetails:
    cached_tokens: int | None = None
    cache_write_tokens: int | None = None
    audio_tokens: int | None = None
    video_tokens: int | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OpenrouterChatCompletionCompletionTokensDetails:
    reasoning_tokens: int | None = None
    audio_tokens: int | None = None
    image_tokens: int | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OpenrouterChatCompletionServerToolUse:
    web_search_requests: int | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OpenrouterChatCompletionUsage(OaiLikeChatCompletionUsage):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int
    completion_tokens_details: OpenrouterChatCompletionCompletionTokensDetails | None = None
    cost: float | None = None
    cost_details: OpenrouterChatCompletionCostDetails | None = None
    is_byok: bool | None = None
    prompt_tokens_details: OpenrouterChatCompletionPromptTokensDetails | None = None
    server_tool_use: OpenrouterChatCompletionServerToolUse | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OpenrouterChatCompletionChoice(
    OaiLikeChatCompletionChoice[
        AssistantOpenrouterChatCompletionResponseMessage,
        OpenrouterChatCompletionFinishReason,
    ],
):
    native_finish_reason: str | None = None
    error: OpenrouterChatCompletionError | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OpenrouterChatCompletionStreamChoice(
    OaiLikeChatCompletionStreamChoice[
        AssistantOpenrouterChatCompletionStreamDelta,
        OpenrouterChatCompletionFinishReason,
    ],
):
    native_finish_reason: str | None = None
    error: OpenrouterChatCompletionError | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OpenrouterChatCompletionResponse(
    HasOaiLikeChatCompletionSystemFingerprint,
    OaiLikeChatCompletionResponse[
        OpenrouterChatCompletionChoice,
        OpenrouterChatCompletionUsage,
    ],
):
    openrouter_metadata: JsonObject | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OpenrouterChatCompletionStreamChunk(
    HasOaiLikeChatCompletionSystemFingerprint,
    OaiLikeChatCompletionStreamChunk[
        OpenrouterChatCompletionStreamChoice,
        OpenrouterChatCompletionUsage,
    ],
):
    openrouter_metadata: JsonObject | None = None


##
# OpenRouter requests.


@dc.dataclass(frozen=True, kw_only=True)
class OpenrouterChatCompletionStreamOptions(
    OaiLikeChatCompletionStreamOptions,
):
    include_usage: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class OpenrouterChatCompletionRequest(
    HasOaiLikeChatCompletionLogprobsRequest,
    HasOaiLikeParallelToolCalls,
    HasOpenrouterChatCompletionCacheControls,
    HasOpenrouterChatCompletionDebugControls,
    HasOpenrouterChatCompletionProviderRouting,
    HasOpenrouterChatCompletionReasoningControls[
        OpenrouterChatCompletionReasoning,
    ],
    HasOpenrouterChatCompletionRequestMetadata,
    HasOpenrouterChatCompletionRequestTokenControls,
    OaiLikeChatCompletionRequest[
        OpenrouterChatCompletionRequestMessage,
        OpenrouterChatCompletionTool,
        OpenrouterChatCompletionToolChoiceOption,
        OpenrouterChatCompletionResponseFormat,
    ],
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class OpenrouterChatCompletionStreamRequest(
    HasOaiLikeChatCompletionLogprobsRequest,
    HasOaiLikeParallelToolCalls,
    HasOpenrouterChatCompletionCacheControls,
    HasOpenrouterChatCompletionDebugControls,
    HasOpenrouterChatCompletionProviderRouting,
    HasOpenrouterChatCompletionReasoningControls[
        OpenrouterChatCompletionReasoning,
    ],
    HasOpenrouterChatCompletionRequestMetadata,
    HasOpenrouterChatCompletionRequestTokenControls,
    OaiLikeChatCompletionStreamRequest[
        OpenrouterChatCompletionRequestMessage,
        OpenrouterChatCompletionTool,
        OpenrouterChatCompletionToolChoiceOption,
        OpenrouterChatCompletionResponseFormat,
        OpenrouterChatCompletionStreamOptions,
    ],
):
    pass


###
# Groq OpenAI-compatible Chat Completions.


GroqChatCompletionReasoningEffort = ta.Literal[
    'none',
    'default',
    'low',
    'medium',
    'high',
]


GroqChatCompletionReasoningFormat = ta.Literal[
    'hidden',
    'raw',
    'parsed',
]


GroqChatCompletionCitationOptions = ta.Literal[
    'enabled',
    'disabled',
]


GroqChatCompletionServiceTier = ta.Literal[
    'auto',
    'on_demand',
    'flex',
    'performance',
]


@dc.dataclass(frozen=True, kw_only=True)
class HasGroqChatCompletionReasoningControls:
    include_reasoning: bool | None = None
    reasoning_effort: GroqChatCompletionReasoningEffort | None = None
    reasoning_format: GroqChatCompletionReasoningFormat | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasGroqChatCompletionRequestTokenControls:
    logit_bias: ta.Mapping[str, float] | None = None
    max_completion_tokens: int | None = None
    n: int | None = None
    seed: int | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasGroqChatCompletionRequestIdentity:
    user: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasGroqChatCompletionRequestMetadata:
    metadata: JsonObject | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasGroqChatCompletionServiceTier:
    service_tier: GroqChatCompletionServiceTier | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasGroqChatCompletionCompoundControls:
    citation_options: GroqChatCompletionCitationOptions | None = None
    compound_custom: JsonObject | None = None
    disable_tool_validation: bool | None = None
    documents: ta.Sequence[JsonObject] | None = None
    search_settings: JsonObject | None = None


##
# Groq content parts.


class GroqChatCompletionContentPart(OaiLikeChatCompletionContentPart):
    pass


class GroqChatCompletionUserRequestContentPart(GroqChatCompletionContentPart):
    pass


class GroqChatCompletionAssistantRequestContentPart(GroqChatCompletionContentPart):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class TextGroqChatCompletionContentPart(
    TextOaiLikeChatCompletionContentPart,
    GroqChatCompletionUserRequestContentPart,
    GroqChatCompletionAssistantRequestContentPart,
):
    text: str
    type: ta.Literal['text'] = 'text'


@dc.dataclass(frozen=True, kw_only=True)
class GroqChatCompletionImageUrl:
    url: str
    detail: str | None = None


GroqChatCompletionImageUrlValue = str | GroqChatCompletionImageUrl


@dc.dataclass(frozen=True, kw_only=True)
class ImageUrlGroqChatCompletionContentPart(
    ImageUrlOaiLikeChatCompletionContentPart[
        GroqChatCompletionImageUrlValue,
    ],
    GroqChatCompletionUserRequestContentPart,
):
    image_url: GroqChatCompletionImageUrlValue
    type: ta.Literal['image_url'] = 'image_url'


##
# Groq response_format objects.


class GroqChatCompletionResponseFormat(OaiLikeChatCompletionResponseFormat):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class TextGroqChatCompletionResponseFormat(
    TextOaiLikeChatCompletionResponseFormat,
    GroqChatCompletionResponseFormat,
):
    type: ta.Literal['text'] = 'text'


@dc.dataclass(frozen=True, kw_only=True)
class JsonObjectGroqChatCompletionResponseFormat(
    JsonObjectOaiLikeChatCompletionResponseFormat,
    GroqChatCompletionResponseFormat,
):
    type: ta.Literal['json_object'] = 'json_object'


@dc.dataclass(frozen=True, kw_only=True)
class GroqChatCompletionJsonSchema:
    name: str | None = None
    description: str | None = None
    schema: JsonObject | None = None
    strict: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class JsonSchemaGroqChatCompletionResponseFormat(
    JsonSchemaOaiLikeChatCompletionResponseFormat[
        GroqChatCompletionJsonSchema,
    ],
    GroqChatCompletionResponseFormat,
):
    json_schema: GroqChatCompletionJsonSchema
    type: ta.Literal['json_schema'] = 'json_schema'


##
# Groq tools and tool choices.


@dc.dataclass(frozen=True, kw_only=True)
class GroqChatCompletionFunctionDefinition(OaiLikeChatCompletionFunctionDefinition):
    name: str
    description: str | None = None
    parameters: JsonObject | None = None
    strict: bool | None = None


class GroqChatCompletionTool(OaiLikeChatCompletionTool):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class FunctionGroqChatCompletionTool(
    FunctionOaiLikeChatCompletionTool[
        GroqChatCompletionFunctionDefinition,
    ],
    GroqChatCompletionTool,
):
    function: GroqChatCompletionFunctionDefinition
    type: ta.Literal['function'] = 'function'


class GroqChatCompletionToolChoice(OaiLikeChatCompletionToolChoice):
    pass


GroqChatCompletionToolChoiceMode = OaiLikeChatCompletionToolChoiceMode
GroqChatCompletionToolChoiceOption = (
    GroqChatCompletionToolChoiceMode |
    GroqChatCompletionToolChoice
)


@dc.dataclass(frozen=True, kw_only=True)
class GroqChatCompletionNamedToolChoiceFunction(
    OaiLikeChatCompletionNamedToolChoiceFunction,
):
    name: str


@dc.dataclass(frozen=True, kw_only=True)
class FunctionGroqChatCompletionToolChoice(
    FunctionOaiLikeChatCompletionToolChoice[
        GroqChatCompletionNamedToolChoiceFunction,
    ],
    GroqChatCompletionToolChoice,
):
    function: GroqChatCompletionNamedToolChoiceFunction
    type: ta.Literal['function'] = 'function'


##
# Groq generated tool calls.


class GroqChatCompletionResponseToolCall(OaiLikeChatCompletionResponseToolCall):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class GroqChatCompletionResponseToolCallFunction(
    OaiLikeChatCompletionResponseToolCallFunction,
):
    arguments: str
    name: str


@dc.dataclass(frozen=True, kw_only=True)
class FunctionGroqChatCompletionResponseToolCall(
    FunctionOaiLikeChatCompletionResponseToolCall[
        GroqChatCompletionResponseToolCallFunction,
    ],
    GroqChatCompletionResponseToolCall,
):
    id: str
    function: GroqChatCompletionResponseToolCallFunction
    type: ta.Literal['function'] = 'function'


class GroqChatCompletionStreamDeltaToolCall(OaiLikeChatCompletionStreamDeltaToolCall):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class GroqChatCompletionStreamDeltaToolCallFunction(
    OaiLikeChatCompletionStreamDeltaToolCallFunction,
):
    arguments: str | None = None
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class FunctionGroqChatCompletionStreamDeltaToolCall(
    FunctionOaiLikeChatCompletionStreamDeltaToolCall[
        GroqChatCompletionStreamDeltaToolCallFunction,
    ],
    GroqChatCompletionStreamDeltaToolCall,
):
    index: int
    function: GroqChatCompletionStreamDeltaToolCallFunction | None = None
    id: str | None = None
    type: ta.Literal['function'] | None = None


##
# Groq request messages.


class GroqChatCompletionRequestMessage(OaiLikeChatCompletionRequestMessage):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class SystemGroqChatCompletionRequestMessage(
    SystemOaiLikeChatCompletionRequestMessage[
        TextGroqChatCompletionContentPart,
    ],
    GroqChatCompletionRequestMessage,
):
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class UserGroqChatCompletionRequestMessage(
    UserOaiLikeChatCompletionRequestMessage[
        GroqChatCompletionUserRequestContentPart,
    ],
    GroqChatCompletionRequestMessage,
):
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class AssistantGroqChatCompletionRequestMessage(
    AssistantOaiLikeChatCompletionRequestMessage[
        GroqChatCompletionAssistantRequestContentPart,
        GroqChatCompletionResponseToolCall,
    ],
    GroqChatCompletionRequestMessage,
):
    name: str | None = None
    reasoning: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class ToolGroqChatCompletionRequestMessage(
    ToolOaiLikeChatCompletionRequestMessage[
        TextGroqChatCompletionContentPart,
    ],
    GroqChatCompletionRequestMessage,
):
    pass


##
# Groq response messages and stream deltas.


class GroqChatCompletionResponseMessage(OaiLikeChatCompletionResponseMessage):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class AssistantGroqChatCompletionResponseMessage(
    AssistantOaiLikeChatCompletionResponseMessage[
        GroqChatCompletionResponseToolCall,
    ],
    GroqChatCompletionResponseMessage,
):
    reasoning: str | None = None


class GroqChatCompletionStreamDelta(OaiLikeChatCompletionStreamDelta):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class AssistantGroqChatCompletionStreamDelta(
    AssistantOaiLikeChatCompletionStreamDelta[
        GroqChatCompletionStreamDeltaToolCall,
    ],
    GroqChatCompletionStreamDelta,
):
    reasoning: str | None = None


##
# Groq logprobs, choices, usage, responses, and stream chunks.


@dc.dataclass(frozen=True, kw_only=True)
class GroqChatCompletionTopLogprob(
    OaiLikeChatCompletionTopLogprob,
):
    logprob: float
    token: str
    bytes: ta.Sequence[int] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class GroqChatCompletionTokenLogprob(
    OaiLikeChatCompletionTokenLogprob[
        GroqChatCompletionTopLogprob,
    ],
):
    logprob: float
    token: str
    bytes: ta.Sequence[int] | None = None
    top_logprobs: ta.Sequence[GroqChatCompletionTopLogprob] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class GroqChatCompletionLogprobs(
    OaiLikeChatCompletionLogprobs[
        GroqChatCompletionTokenLogprob,
    ],
):
    content: ta.Sequence[GroqChatCompletionTokenLogprob] | None = None
    refusal: ta.Sequence[GroqChatCompletionTokenLogprob] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class GroqChatCompletionChoice(
    LogprobsOaiLikeChatCompletionChoice[
        AssistantGroqChatCompletionResponseMessage,
        str,
        GroqChatCompletionLogprobs,
    ],
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class GroqChatCompletionStreamChoice(
    LogprobsOaiLikeChatCompletionStreamChoice[
        AssistantGroqChatCompletionStreamDelta,
        str,
        GroqChatCompletionLogprobs,
    ],
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class GroqChatCompletionUsage(OaiLikeChatCompletionUsage):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int
    completion_time: float | None = None
    prompt_time: float | None = None
    queue_time: float | None = None
    total_time: float | None = None


@dc.dataclass(frozen=True, kw_only=True)
class GroqChatCompletionXGroq:
    id: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class GroqChatCompletionResponse(
    HasOaiLikeChatCompletionSystemFingerprint,
    HasGroqChatCompletionServiceTier,
    OaiLikeChatCompletionResponse[
        GroqChatCompletionChoice,
        GroqChatCompletionUsage,
    ],
):
    usage_breakdown: JsonObject | None = None
    x_groq: GroqChatCompletionXGroq | JsonObject | None = None


@dc.dataclass(frozen=True, kw_only=True)
class GroqChatCompletionStreamChunk(
    HasOaiLikeChatCompletionSystemFingerprint,
    HasGroqChatCompletionServiceTier,
    OaiLikeChatCompletionStreamChunk[
        GroqChatCompletionStreamChoice,
        GroqChatCompletionUsage,
    ],
):
    usage_breakdown: JsonObject | None = None


##
# Groq requests.


@dc.dataclass(frozen=True, kw_only=True)
class GroqChatCompletionStreamOptions(
    OaiLikeChatCompletionStreamOptions,
):
    include_usage: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class GroqChatCompletionRequest(
    HasOaiLikeChatCompletionLogprobsRequest,
    HasOaiLikeParallelToolCalls,
    HasGroqChatCompletionCompoundControls,
    HasGroqChatCompletionReasoningControls,
    HasGroqChatCompletionRequestIdentity,
    HasGroqChatCompletionRequestMetadata,
    HasGroqChatCompletionRequestTokenControls,
    HasGroqChatCompletionServiceTier,
    OaiLikeChatCompletionRequest[
        GroqChatCompletionRequestMessage,
        GroqChatCompletionTool,
        GroqChatCompletionToolChoiceOption,
        GroqChatCompletionResponseFormat,
    ],
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class GroqChatCompletionStreamRequest(
    HasOaiLikeChatCompletionLogprobsRequest,
    HasOaiLikeParallelToolCalls,
    HasGroqChatCompletionCompoundControls,
    HasGroqChatCompletionReasoningControls,
    HasGroqChatCompletionRequestIdentity,
    HasGroqChatCompletionRequestMetadata,
    HasGroqChatCompletionRequestTokenControls,
    HasGroqChatCompletionServiceTier,
    OaiLikeChatCompletionStreamRequest[
        GroqChatCompletionRequestMessage,
        GroqChatCompletionTool,
        GroqChatCompletionToolChoiceOption,
        GroqChatCompletionResponseFormat,
        GroqChatCompletionStreamOptions,
    ],
):
    pass


###
# Cerebras OpenAI-compatible Chat Completions.


CerebrasChatCompletionFinishReason = ta.Literal[
    'stop',
    'length',
    'content_filter',
    'tool_calls',
]


CerebrasChatCompletionReasoningEffort = ta.Literal[
    'low',
    'medium',
    'high',
    'none',
]


CerebrasChatCompletionServiceTier = ta.Literal[
    'priority',
    'default',
    'auto',
    'flex',
]


CerebrasChatCompletionServiceTierUsed = ta.Literal[
    'priority',
    'default',
    'flex',
]


@dc.dataclass(frozen=True, kw_only=True)
class HasCerebrasChatCompletionReasoningControls:
    clear_thinking: bool | None = None
    reasoning_effort: CerebrasChatCompletionReasoningEffort | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasCerebrasChatCompletionRequestTokenControls:
    logit_bias: ta.Mapping[str, float] | None = None
    max_completion_tokens: int | None = None
    n: int | None = None
    seed: int | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasCerebrasChatCompletionPromptCaching:
    prompt_cache_key: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasCerebrasChatCompletionRequestIdentity:
    user: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasCerebrasChatCompletionServiceTier:
    service_tier: CerebrasChatCompletionServiceTier | None = None


##
# Cerebras content parts.


class CerebrasChatCompletionContentPart(OaiLikeChatCompletionContentPart):
    pass


class CerebrasChatCompletionUserRequestContentPart(CerebrasChatCompletionContentPart):
    pass


class CerebrasChatCompletionAssistantRequestContentPart(CerebrasChatCompletionContentPart):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class TextCerebrasChatCompletionContentPart(
    TextOaiLikeChatCompletionContentPart,
    CerebrasChatCompletionUserRequestContentPart,
    CerebrasChatCompletionAssistantRequestContentPart,
):
    text: str
    type: ta.Literal['text'] = 'text'


@dc.dataclass(frozen=True, kw_only=True)
class CerebrasChatCompletionImageUrl:
    url: str


CerebrasChatCompletionImageUrlValue = str | CerebrasChatCompletionImageUrl


@dc.dataclass(frozen=True, kw_only=True)
class ImageUrlCerebrasChatCompletionContentPart(
    ImageUrlOaiLikeChatCompletionContentPart[
        CerebrasChatCompletionImageUrlValue,
    ],
    CerebrasChatCompletionUserRequestContentPart,
):
    image_url: CerebrasChatCompletionImageUrlValue
    type: ta.Literal['image_url'] = 'image_url'


##
# Cerebras response_format objects.


class CerebrasChatCompletionResponseFormat(OaiLikeChatCompletionResponseFormat):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class TextCerebrasChatCompletionResponseFormat(
    TextOaiLikeChatCompletionResponseFormat,
    CerebrasChatCompletionResponseFormat,
):
    type: ta.Literal['text'] = 'text'


@dc.dataclass(frozen=True, kw_only=True)
class JsonObjectCerebrasChatCompletionResponseFormat(
    JsonObjectOaiLikeChatCompletionResponseFormat,
    CerebrasChatCompletionResponseFormat,
):
    type: ta.Literal['json_object'] = 'json_object'


@dc.dataclass(frozen=True, kw_only=True)
class CerebrasChatCompletionJsonSchema:
    name: str | None = None
    description: str | None = None
    schema: JsonObject | None = None
    strict: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class JsonSchemaCerebrasChatCompletionResponseFormat(
    JsonSchemaOaiLikeChatCompletionResponseFormat[
        CerebrasChatCompletionJsonSchema,
    ],
    CerebrasChatCompletionResponseFormat,
):
    json_schema: CerebrasChatCompletionJsonSchema
    type: ta.Literal['json_schema'] = 'json_schema'


##
# Cerebras tools and tool choices.


@dc.dataclass(frozen=True, kw_only=True)
class CerebrasChatCompletionFunctionDefinition(OaiLikeChatCompletionFunctionDefinition):
    name: str
    description: str | None = None
    parameters: JsonObject | None = None
    strict: bool | None = None


class CerebrasChatCompletionTool(OaiLikeChatCompletionTool):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class FunctionCerebrasChatCompletionTool(
    FunctionOaiLikeChatCompletionTool[
        CerebrasChatCompletionFunctionDefinition,
    ],
    CerebrasChatCompletionTool,
):
    function: CerebrasChatCompletionFunctionDefinition
    type: ta.Literal['function'] = 'function'


class CerebrasChatCompletionToolChoice(OaiLikeChatCompletionToolChoice):
    pass


CerebrasChatCompletionToolChoiceMode = OaiLikeChatCompletionToolChoiceMode
CerebrasChatCompletionToolChoiceOption = (
    CerebrasChatCompletionToolChoiceMode |
    CerebrasChatCompletionToolChoice
)


@dc.dataclass(frozen=True, kw_only=True)
class CerebrasChatCompletionNamedToolChoiceFunction(
    OaiLikeChatCompletionNamedToolChoiceFunction,
):
    name: str


@dc.dataclass(frozen=True, kw_only=True)
class FunctionCerebrasChatCompletionToolChoice(
    FunctionOaiLikeChatCompletionToolChoice[
        CerebrasChatCompletionNamedToolChoiceFunction,
    ],
    CerebrasChatCompletionToolChoice,
):
    function: CerebrasChatCompletionNamedToolChoiceFunction
    type: ta.Literal['function'] = 'function'


##
# Cerebras generated tool calls.


class CerebrasChatCompletionResponseToolCall(OaiLikeChatCompletionResponseToolCall):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class CerebrasChatCompletionResponseToolCallFunction(
    OaiLikeChatCompletionResponseToolCallFunction,
):
    arguments: str
    name: str


@dc.dataclass(frozen=True, kw_only=True)
class FunctionCerebrasChatCompletionResponseToolCall(
    FunctionOaiLikeChatCompletionResponseToolCall[
        CerebrasChatCompletionResponseToolCallFunction,
    ],
    CerebrasChatCompletionResponseToolCall,
):
    id: str
    function: CerebrasChatCompletionResponseToolCallFunction
    type: ta.Literal['function'] = 'function'


class CerebrasChatCompletionStreamDeltaToolCall(OaiLikeChatCompletionStreamDeltaToolCall):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class CerebrasChatCompletionStreamDeltaToolCallFunction(
    OaiLikeChatCompletionStreamDeltaToolCallFunction,
):
    arguments: str | None = None
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class FunctionCerebrasChatCompletionStreamDeltaToolCall(
    FunctionOaiLikeChatCompletionStreamDeltaToolCall[
        CerebrasChatCompletionStreamDeltaToolCallFunction,
    ],
    CerebrasChatCompletionStreamDeltaToolCall,
):
    index: int
    function: CerebrasChatCompletionStreamDeltaToolCallFunction | None = None
    id: str | None = None
    type: ta.Literal['function'] | None = None


##
# Cerebras request messages.


class CerebrasChatCompletionRequestMessage(OaiLikeChatCompletionRequestMessage):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class DeveloperCerebrasChatCompletionRequestMessage(
    CerebrasChatCompletionRequestMessage,
):
    content: str | ta.Sequence[TextCerebrasChatCompletionContentPart]
    name: str | None = None
    role: ta.Literal['developer'] = 'developer'


@dc.dataclass(frozen=True, kw_only=True)
class SystemCerebrasChatCompletionRequestMessage(
    SystemOaiLikeChatCompletionRequestMessage[
        TextCerebrasChatCompletionContentPart,
    ],
    CerebrasChatCompletionRequestMessage,
):
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class UserCerebrasChatCompletionRequestMessage(
    UserOaiLikeChatCompletionRequestMessage[
        CerebrasChatCompletionUserRequestContentPart,
    ],
    CerebrasChatCompletionRequestMessage,
):
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class AssistantCerebrasChatCompletionRequestMessage(
    AssistantOaiLikeChatCompletionRequestMessage[
        CerebrasChatCompletionAssistantRequestContentPart,
        CerebrasChatCompletionResponseToolCall,
    ],
    CerebrasChatCompletionRequestMessage,
):
    name: str | None = None
    reasoning: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class ToolCerebrasChatCompletionRequestMessage(
    ToolOaiLikeChatCompletionRequestMessage[
        TextCerebrasChatCompletionContentPart,
    ],
    CerebrasChatCompletionRequestMessage,
):
    pass


##
# Cerebras response messages and stream deltas.


class CerebrasChatCompletionResponseMessage(OaiLikeChatCompletionResponseMessage):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class AssistantCerebrasChatCompletionResponseMessage(
    AssistantOaiLikeChatCompletionResponseMessage[
        CerebrasChatCompletionResponseToolCall,
    ],
    CerebrasChatCompletionResponseMessage,
):
    reasoning: str | None = None


class CerebrasChatCompletionStreamDelta(OaiLikeChatCompletionStreamDelta):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class AssistantCerebrasChatCompletionStreamDelta(
    AssistantOaiLikeChatCompletionStreamDelta[
        CerebrasChatCompletionStreamDeltaToolCall,
    ],
    CerebrasChatCompletionStreamDelta,
):
    reasoning: str | None = None


##
# Cerebras logprobs, choices, usage, responses, and stream chunks.


@dc.dataclass(frozen=True, kw_only=True)
class CerebrasChatCompletionTopLogprob(
    OaiLikeChatCompletionTopLogprob,
):
    logprob: float
    token: str
    bytes: ta.Sequence[int] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class CerebrasChatCompletionTokenLogprob(
    OaiLikeChatCompletionTokenLogprob[
        CerebrasChatCompletionTopLogprob,
    ],
):
    logprob: float
    token: str
    bytes: ta.Sequence[int] | None = None
    top_logprobs: ta.Sequence[CerebrasChatCompletionTopLogprob] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class CerebrasChatCompletionLogprobs(
    OaiLikeChatCompletionLogprobs[
        CerebrasChatCompletionTokenLogprob,
    ],
):
    content: ta.Sequence[CerebrasChatCompletionTokenLogprob] | None = None
    refusal: ta.Sequence[CerebrasChatCompletionTokenLogprob] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class CerebrasChatCompletionChoice(
    LogprobsOaiLikeChatCompletionChoice[
        AssistantCerebrasChatCompletionResponseMessage,
        CerebrasChatCompletionFinishReason,
        CerebrasChatCompletionLogprobs,
    ],
):
    reasoning_logprobs: CerebrasChatCompletionLogprobs | None = None


@dc.dataclass(frozen=True, kw_only=True)
class CerebrasChatCompletionStreamChoice(
    LogprobsOaiLikeChatCompletionStreamChoice[
        AssistantCerebrasChatCompletionStreamDelta,
        CerebrasChatCompletionFinishReason,
        CerebrasChatCompletionLogprobs,
    ],
):
    reasoning_logprobs: CerebrasChatCompletionLogprobs | None = None


@dc.dataclass(frozen=True, kw_only=True)
class CerebrasChatCompletionPromptTokensDetails:
    cached_tokens: int | None = None


@dc.dataclass(frozen=True, kw_only=True)
class CerebrasChatCompletionCompletionTokensDetails:
    accepted_prediction_tokens: int | None = None
    rejected_prediction_tokens: int | None = None
    reasoning_tokens: int | None = None


@dc.dataclass(frozen=True, kw_only=True)
class CerebrasChatCompletionUsage(OaiLikeChatCompletionUsage):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int
    completion_tokens_details: CerebrasChatCompletionCompletionTokensDetails | None = None
    image_tokens: int | None = None
    prompt_tokens_details: CerebrasChatCompletionPromptTokensDetails | None = None


@dc.dataclass(frozen=True, kw_only=True)
class CerebrasChatCompletionTimeInfo:
    completion_time: float | None = None
    created: float | None = None
    prompt_time: float | None = None
    queue_time: float | None = None
    total_time: float | None = None


@dc.dataclass(frozen=True, kw_only=True)
class CerebrasChatCompletionResponse(
    HasOaiLikeChatCompletionSystemFingerprint,
    HasCerebrasChatCompletionServiceTier,
    OaiLikeChatCompletionResponse[
        CerebrasChatCompletionChoice,
        CerebrasChatCompletionUsage,
    ],
):
    service_tier_used: CerebrasChatCompletionServiceTierUsed | None = None
    time_info: CerebrasChatCompletionTimeInfo | None = None


@dc.dataclass(frozen=True, kw_only=True)
class CerebrasChatCompletionStreamChunk(
    HasOaiLikeChatCompletionSystemFingerprint,
    HasCerebrasChatCompletionServiceTier,
    OaiLikeChatCompletionStreamChunk[
        CerebrasChatCompletionStreamChoice,
        CerebrasChatCompletionUsage,
    ],
):
    service_tier_used: CerebrasChatCompletionServiceTierUsed | None = None
    time_info: CerebrasChatCompletionTimeInfo | None = None


##
# Cerebras requests.


@dc.dataclass(frozen=True, kw_only=True)
class CerebrasChatCompletionStreamOptions(
    OaiLikeChatCompletionStreamOptions,
):
    include_usage: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class CerebrasChatCompletionRequest(
    HasOaiLikeChatCompletionLogprobsRequest,
    HasOaiLikeParallelToolCalls,
    HasCerebrasChatCompletionPromptCaching,
    HasCerebrasChatCompletionReasoningControls,
    HasCerebrasChatCompletionRequestIdentity,
    HasCerebrasChatCompletionRequestTokenControls,
    HasCerebrasChatCompletionServiceTier,
    OaiLikeChatCompletionRequest[
        CerebrasChatCompletionRequestMessage,
        CerebrasChatCompletionTool,
        CerebrasChatCompletionToolChoiceOption,
        CerebrasChatCompletionResponseFormat,
    ],
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class CerebrasChatCompletionStreamRequest(
    HasOaiLikeChatCompletionLogprobsRequest,
    HasOaiLikeParallelToolCalls,
    HasCerebrasChatCompletionPromptCaching,
    HasCerebrasChatCompletionReasoningControls,
    HasCerebrasChatCompletionRequestIdentity,
    HasCerebrasChatCompletionRequestTokenControls,
    HasCerebrasChatCompletionServiceTier,
    OaiLikeChatCompletionStreamRequest[
        CerebrasChatCompletionRequestMessage,
        CerebrasChatCompletionTool,
        CerebrasChatCompletionToolChoiceOption,
        CerebrasChatCompletionResponseFormat,
        CerebrasChatCompletionStreamOptions,
    ],
):
    pass


###
# Mistral Chat Completions.


MistralChatCompletionToolChoiceMode = ta.Literal[
    'none',
    'auto',
    'any',
    'required',
]


MistralChatCompletionReasoningEffort = ta.Literal[
    'none',
    'minimal',
    'low',
    'medium',
    'high',
    'xhigh',
]


@dc.dataclass(frozen=True, kw_only=True)
class HasMistralChatCompletionReasoningControls:
    prompt_mode: ta.Literal['reasoning'] | None = None
    reasoning_effort: MistralChatCompletionReasoningEffort | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasMistralChatCompletionPromptCaching:
    prompt_cache_key: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasMistralChatCompletionRequestMetadata:
    metadata: JsonObject | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasMistralChatCompletionRequestTokenControls:
    n: int | None = None
    random_seed: int | None = None


@dc.dataclass(frozen=True, kw_only=True)
class HasMistralChatCompletionSafetyAndGuardrails:
    guardrails: ta.Sequence[JsonObject] | None = None
    safe_prompt: bool | None = None


##
# Mistral content parts.


class MistralChatCompletionContentPart(OaiLikeChatCompletionContentPart):
    pass


class MistralChatCompletionUserRequestContentPart(MistralChatCompletionContentPart):
    pass


class MistralChatCompletionAssistantRequestContentPart(MistralChatCompletionContentPart):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class TextMistralChatCompletionContentPart(
    TextOaiLikeChatCompletionContentPart,
    MistralChatCompletionUserRequestContentPart,
    MistralChatCompletionAssistantRequestContentPart,
):
    text: str
    type: ta.Literal['text'] = 'text'


@dc.dataclass(frozen=True, kw_only=True)
class MistralChatCompletionImageUrl:
    url: str


MistralChatCompletionImageUrlValue = str | MistralChatCompletionImageUrl


@dc.dataclass(frozen=True, kw_only=True)
class ImageUrlMistralChatCompletionContentPart(
    ImageUrlOaiLikeChatCompletionContentPart[
        MistralChatCompletionImageUrlValue,
    ],
    MistralChatCompletionUserRequestContentPart,
):
    image_url: MistralChatCompletionImageUrlValue
    type: ta.Literal['image_url'] = 'image_url'


##
# Mistral response_format objects.


class MistralChatCompletionResponseFormat(OaiLikeChatCompletionResponseFormat):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class TextMistralChatCompletionResponseFormat(
    TextOaiLikeChatCompletionResponseFormat,
    MistralChatCompletionResponseFormat,
):
    type: ta.Literal['text'] = 'text'


@dc.dataclass(frozen=True, kw_only=True)
class JsonObjectMistralChatCompletionResponseFormat(
    JsonObjectOaiLikeChatCompletionResponseFormat,
    MistralChatCompletionResponseFormat,
):
    type: ta.Literal['json_object'] = 'json_object'


@dc.dataclass(frozen=True, kw_only=True)
class MistralChatCompletionJsonSchema:
    name: str | None = None
    description: str | None = None
    schema: JsonObject | None = None
    strict: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class JsonSchemaMistralChatCompletionResponseFormat(
    JsonSchemaOaiLikeChatCompletionResponseFormat[
        MistralChatCompletionJsonSchema,
    ],
    MistralChatCompletionResponseFormat,
):
    json_schema: MistralChatCompletionJsonSchema
    type: ta.Literal['json_schema'] = 'json_schema'


##
# Mistral tools and tool choices.


@dc.dataclass(frozen=True, kw_only=True)
class MistralChatCompletionFunctionDefinition(OaiLikeChatCompletionFunctionDefinition):
    name: str
    description: str | None = None
    parameters: JsonObject | None = None
    strict: bool | None = None


class MistralChatCompletionTool(OaiLikeChatCompletionTool):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class FunctionMistralChatCompletionTool(
    FunctionOaiLikeChatCompletionTool[
        MistralChatCompletionFunctionDefinition,
    ],
    MistralChatCompletionTool,
):
    function: MistralChatCompletionFunctionDefinition
    type: ta.Literal['function'] = 'function'


class MistralChatCompletionToolChoice(OaiLikeChatCompletionToolChoice):
    pass


MistralChatCompletionToolChoiceOption = (
    MistralChatCompletionToolChoiceMode |
    MistralChatCompletionToolChoice
)


@dc.dataclass(frozen=True, kw_only=True)
class MistralChatCompletionNamedToolChoiceFunction(
    OaiLikeChatCompletionNamedToolChoiceFunction,
):
    name: str


@dc.dataclass(frozen=True, kw_only=True)
class FunctionMistralChatCompletionToolChoice(
    FunctionOaiLikeChatCompletionToolChoice[
        MistralChatCompletionNamedToolChoiceFunction,
    ],
    MistralChatCompletionToolChoice,
):
    function: MistralChatCompletionNamedToolChoiceFunction
    type: ta.Literal['function'] = 'function'


##
# Mistral generated tool calls.


class MistralChatCompletionResponseToolCall(OaiLikeChatCompletionResponseToolCall):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class MistralChatCompletionResponseToolCallFunction(
    OaiLikeChatCompletionResponseToolCallFunction,
):
    arguments: str
    name: str


@dc.dataclass(frozen=True, kw_only=True)
class FunctionMistralChatCompletionResponseToolCall(
    FunctionOaiLikeChatCompletionResponseToolCall[
        MistralChatCompletionResponseToolCallFunction,
    ],
    MistralChatCompletionResponseToolCall,
):
    id: str
    function: MistralChatCompletionResponseToolCallFunction
    type: ta.Literal['function'] = 'function'


class MistralChatCompletionStreamDeltaToolCall(OaiLikeChatCompletionStreamDeltaToolCall):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class MistralChatCompletionStreamDeltaToolCallFunction(
    OaiLikeChatCompletionStreamDeltaToolCallFunction,
):
    arguments: str | None = None
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class FunctionMistralChatCompletionStreamDeltaToolCall(
    FunctionOaiLikeChatCompletionStreamDeltaToolCall[
        MistralChatCompletionStreamDeltaToolCallFunction,
    ],
    MistralChatCompletionStreamDeltaToolCall,
):
    index: int
    function: MistralChatCompletionStreamDeltaToolCallFunction | None = None
    id: str | None = None
    type: ta.Literal['function'] | None = None


##
# Mistral request messages.


class MistralChatCompletionRequestMessage(OaiLikeChatCompletionRequestMessage):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class SystemMistralChatCompletionRequestMessage(
    SystemOaiLikeChatCompletionRequestMessage[
        TextMistralChatCompletionContentPart,
    ],
    MistralChatCompletionRequestMessage,
):
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class UserMistralChatCompletionRequestMessage(
    UserOaiLikeChatCompletionRequestMessage[
        MistralChatCompletionUserRequestContentPart,
    ],
    MistralChatCompletionRequestMessage,
):
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class AssistantMistralChatCompletionRequestMessage(
    AssistantOaiLikeChatCompletionRequestMessage[
        MistralChatCompletionAssistantRequestContentPart,
        MistralChatCompletionResponseToolCall,
    ],
    MistralChatCompletionRequestMessage,
):
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class ToolMistralChatCompletionRequestMessage(
    ToolOaiLikeChatCompletionRequestMessage[
        TextMistralChatCompletionContentPart,
    ],
    MistralChatCompletionRequestMessage,
):
    pass


##
# Mistral response messages and stream deltas.


class MistralChatCompletionResponseMessage(OaiLikeChatCompletionResponseMessage):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class AssistantMistralChatCompletionResponseMessage(
    AssistantOaiLikeChatCompletionResponseMessage[
        MistralChatCompletionResponseToolCall,
    ],
    MistralChatCompletionResponseMessage,
):
    reasoning: str | None = None


class MistralChatCompletionStreamDelta(OaiLikeChatCompletionStreamDelta):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class AssistantMistralChatCompletionStreamDelta(
    AssistantOaiLikeChatCompletionStreamDelta[
        MistralChatCompletionStreamDeltaToolCall,
    ],
    MistralChatCompletionStreamDelta,
):
    reasoning: str | None = None


##
# Mistral choices, responses, and stream chunks.


@dc.dataclass(frozen=True, kw_only=True)
class MistralChatCompletionChoice(
    OaiLikeChatCompletionChoice[
        AssistantMistralChatCompletionResponseMessage,
        str,
    ],
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class MistralChatCompletionStreamChoice(
    OaiLikeChatCompletionStreamChoice[
        AssistantMistralChatCompletionStreamDelta,
        str,
    ],
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class MistralChatCompletionResponse(
    OaiLikeChatCompletionResponse[
        MistralChatCompletionChoice,
        OaiLikeChatCompletionUsage,
    ],
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class MistralChatCompletionStreamChunk(
    OaiLikeChatCompletionStreamChunk[
        MistralChatCompletionStreamChoice,
        OaiLikeChatCompletionUsage,
    ],
):
    pass


##
# Mistral requests.


@dc.dataclass(frozen=True, kw_only=True)
class MistralChatCompletionStreamOptions(
    OaiLikeChatCompletionStreamOptions,
):
    include_usage: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
class MistralChatCompletionRequest(
    HasOaiLikeParallelToolCalls,
    HasMistralChatCompletionPromptCaching,
    HasMistralChatCompletionReasoningControls,
    HasMistralChatCompletionRequestMetadata,
    HasMistralChatCompletionRequestTokenControls,
    HasMistralChatCompletionSafetyAndGuardrails,
    OaiLikeChatCompletionRequest[
        MistralChatCompletionRequestMessage,
        MistralChatCompletionTool,
        MistralChatCompletionToolChoiceOption,
        MistralChatCompletionResponseFormat,
    ],
):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class MistralChatCompletionStreamRequest(
    HasOaiLikeParallelToolCalls,
    HasMistralChatCompletionPromptCaching,
    HasMistralChatCompletionReasoningControls,
    HasMistralChatCompletionRequestMetadata,
    HasMistralChatCompletionRequestTokenControls,
    HasMistralChatCompletionSafetyAndGuardrails,
    OaiLikeChatCompletionStreamRequest[
        MistralChatCompletionRequestMessage,
        MistralChatCompletionTool,
        MistralChatCompletionToolChoiceOption,
        MistralChatCompletionResponseFormat,
        MistralChatCompletionStreamOptions,
    ],
):
    pass




