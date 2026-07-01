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
from ..oailike.protocol import OaiLikeChatCompletionRequest
from ..oailike.protocol import OaiLikeChatCompletionRequestMessage
from ..oailike.protocol import OaiLikeChatCompletionResponse
from ..oailike.protocol import OaiLikeChatCompletionResponseFormat
from ..oailike.protocol import OaiLikeChatCompletionResponseMessage
from ..oailike.protocol import OaiLikeChatCompletionResponseToolCall
from ..oailike.protocol import OaiLikeChatCompletionResponseToolCallFunction
from ..oailike.protocol import OaiLikeChatCompletionStreamChunk
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


##
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


GroqChatCompletionToolChoiceMode: ta.TypeAlias = OaiLikeChatCompletionToolChoiceMode

GroqChatCompletionToolChoiceOption: ta.TypeAlias = ta.Union[
    GroqChatCompletionToolChoiceMode,
    GroqChatCompletionToolChoice,
]


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
