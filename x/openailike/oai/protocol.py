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


###
# OpenAI Chat Completions.


OaiChatCompletionFinishReason: ta.TypeAlias = ta.Literal[
    'stop',
    'length',
    'tool_calls',
    'content_filter',
    'function_call',
]

OaiChatCompletionReasoningEffort: ta.TypeAlias = ta.Literal[
    'none',
    'minimal',
    'low',
    'medium',
    'high',
    'xhigh',
]

OaiChatCompletionPromptCacheRetention: ta.TypeAlias = ta.Literal[
    'in_memory',
    '24h',
]

OaiChatCompletionServiceTier: ta.TypeAlias = ta.Literal[
    'auto',
    'default',
    'flex',
    'scale',
    'priority',
]

OaiChatCompletionVerbosity: ta.TypeAlias = ta.Literal[
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


OaiChatCompletionToolChoiceMode: ta.TypeAlias = OaiLikeChatCompletionToolChoiceMode

OaiChatCompletionToolChoiceOption: ta.TypeAlias = ta.Union[
    OaiChatCompletionToolChoiceMode,
    OaiChatCompletionToolChoice,
]


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
