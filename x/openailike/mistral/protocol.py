import dataclasses as dc
import typing as ta

from ..oailike.protocol import AssistantOaiLikeChatCompletionRequestMessage
from ..oailike.protocol import AssistantOaiLikeChatCompletionResponseMessage
from ..oailike.protocol import AssistantOaiLikeChatCompletionStreamDelta
from ..oailike.protocol import FunctionOaiLikeChatCompletionResponseToolCall
from ..oailike.protocol import FunctionOaiLikeChatCompletionStreamDeltaToolCall
from ..oailike.protocol import FunctionOaiLikeChatCompletionTool
from ..oailike.protocol import FunctionOaiLikeChatCompletionToolChoice
from ..oailike.protocol import HasOaiLikeParallelToolCalls
from ..oailike.protocol import ImageUrlOaiLikeChatCompletionContentPart
from ..oailike.protocol import JsonObject
from ..oailike.protocol import JsonObjectOaiLikeChatCompletionResponseFormat
from ..oailike.protocol import JsonSchemaOaiLikeChatCompletionResponseFormat
from ..oailike.protocol import OaiLikeChatCompletionChoice
from ..oailike.protocol import OaiLikeChatCompletionContentPart
from ..oailike.protocol import OaiLikeChatCompletionFunctionDefinition
from ..oailike.protocol import OaiLikeChatCompletionNamedToolChoiceFunction
from ..oailike.protocol import OaiLikeChatCompletionRequest
from ..oailike.protocol import OaiLikeChatCompletionRequestMessage
from ..oailike.protocol import OaiLikeChatCompletionResponse
from ..oailike.protocol import OaiLikeChatCompletionResponseFormat
from ..oailike.protocol import OaiLikeChatCompletionResponseMessage
from ..oailike.protocol import OaiLikeChatCompletionResponseToolCall
from ..oailike.protocol import OaiLikeChatCompletionResponseToolCallFunction
from ..oailike.protocol import OaiLikeChatCompletionStreamChoice
from ..oailike.protocol import OaiLikeChatCompletionStreamChunk
from ..oailike.protocol import OaiLikeChatCompletionStreamDelta
from ..oailike.protocol import OaiLikeChatCompletionStreamDeltaToolCall
from ..oailike.protocol import OaiLikeChatCompletionStreamDeltaToolCallFunction
from ..oailike.protocol import OaiLikeChatCompletionStreamOptions
from ..oailike.protocol import OaiLikeChatCompletionStreamRequest
from ..oailike.protocol import OaiLikeChatCompletionTool
from ..oailike.protocol import OaiLikeChatCompletionToolChoice
from ..oailike.protocol import OaiLikeChatCompletionUsage
from ..oailike.protocol import SystemOaiLikeChatCompletionRequestMessage
from ..oailike.protocol import TextOaiLikeChatCompletionContentPart
from ..oailike.protocol import TextOaiLikeChatCompletionResponseFormat
from ..oailike.protocol import ToolOaiLikeChatCompletionRequestMessage
from ..oailike.protocol import UserOaiLikeChatCompletionRequestMessage


##
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


MistralChatCompletionToolChoiceOption: ta.TypeAlias = ta.Union[
    MistralChatCompletionToolChoiceMode,
    MistralChatCompletionToolChoice,
]


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
