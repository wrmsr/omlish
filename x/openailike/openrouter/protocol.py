import dataclasses as dc
import typing as ta

from ..oailike.protocol import AssistantOaiLikeChatCompletionRequestMessage
from ..oailike.protocol import AssistantOaiLikeChatCompletionResponseMessage
from ..oailike.protocol import AssistantOaiLikeChatCompletionStreamDelta
from ..oailike.protocol import FunctionOaiLikeChatCompletionResponseToolCall
from ..oailike.protocol import FunctionOaiLikeChatCompletionStreamDeltaToolCall
from ..oailike.protocol import FunctionOaiLikeChatCompletionTool
from ..oailike.protocol import FunctionOaiLikeChatCompletionToolChoice
from ..oailike.protocol import HasOaiLikeChatCompletionLogprobsRequest
from ..oailike.protocol import HasOaiLikeChatCompletionSystemFingerprint
from ..oailike.protocol import HasOaiLikeParallelToolCalls
from ..oailike.protocol import ImageUrlOaiLikeChatCompletionContentPart
from ..oailike.protocol import JsonObject
from ..oailike.protocol import JsonObjectOaiLikeChatCompletionResponseFormat
from ..oailike.protocol import JsonSchemaOaiLikeChatCompletionResponseFormat
from ..oailike.protocol import LogprobsOaiLikeChatCompletionChoice
from ..oailike.protocol import LogprobsOaiLikeChatCompletionStreamChoice
from ..oailike.protocol import OaiLikeChatCompletionContentPart
from ..oailike.protocol import OaiLikeChatCompletionFunctionDefinition
from ..oailike.protocol import OaiLikeChatCompletionLogprobs
from ..oailike.protocol import OaiLikeChatCompletionNamedToolChoiceFunction
from ..oailike.protocol import OaiLikeChatCompletionRequestMessage
from ..oailike.protocol import OaiLikeChatCompletionResponse
from ..oailike.protocol import OaiLikeChatCompletionResponseFormat
from ..oailike.protocol import OaiLikeChatCompletionResponseMessage
from ..oailike.protocol import OaiLikeChatCompletionResponseToolCall
from ..oailike.protocol import OaiLikeChatCompletionResponseToolCallFunction
from ..oailike.protocol import OaiLikeChatCompletionStreamDelta
from ..oailike.protocol import OaiLikeChatCompletionStreamDeltaToolCall
from ..oailike.protocol import OaiLikeChatCompletionStreamDeltaToolCallFunction
from ..oailike.protocol import OaiLikeChatCompletionStreamOptions
from ..oailike.protocol import OaiLikeChatCompletionStreamRequest
from ..oailike.protocol import OaiLikeChatCompletionTokenLogprob
from ..oailike.protocol import OaiLikeChatCompletionTool
from ..oailike.protocol import OaiLikeChatCompletionToolChoice
from ..oailike.protocol import OaiLikeChatCompletionToolChoiceMode
from ..oailike.protocol import OaiLikeChatCompletionTopLogprob
from ..oailike.protocol import OaiLikeChatCompletionUsage
from ..oailike.protocol import SystemOaiLikeChatCompletionRequestMessage
from ..oailike.protocol import TextOaiLikeChatCompletionContentPart
from ..oailike.protocol import TextOaiLikeChatCompletionResponseFormat
from ..oailike.protocol import ToolOaiLikeChatCompletionRequestMessage
from ..oailike.protocol import UserOaiLikeChatCompletionRequestMessage
from ..oailike.protocol import OaiLikeChatCompletionRequest
from ..oailike.protocol import OaiLikeChatCompletionStreamChunk
from ..oailike.protocol import JsonValue
from ..oailike.protocol import OaiLikeChatCompletionStreamChoice
from ..oailike.protocol import OaiLikeChatCompletionChoice


##
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


OpenrouterChatCompletionToolChoiceMode: ta.TypeAlias = OaiLikeChatCompletionToolChoiceMode

OpenrouterChatCompletionToolChoiceOption: ta.TypeAlias = ta.Union[
    OpenrouterChatCompletionToolChoiceMode,
    OpenrouterChatCompletionToolChoice,
]


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
