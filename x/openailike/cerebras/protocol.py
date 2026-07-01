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


CerebrasChatCompletionToolChoiceMode: ta.TypeAlias = OaiLikeChatCompletionToolChoiceMode

CerebrasChatCompletionToolChoiceOption: ta.TypeAlias = ta.Union[
    CerebrasChatCompletionToolChoiceMode,
    CerebrasChatCompletionToolChoice,
]


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
