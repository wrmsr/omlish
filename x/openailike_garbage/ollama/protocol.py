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
from ..oailike.protocol import ImageUrlOaiLikeChatCompletionContentPart
from ..oailike.protocol import JsonObject
from ..oailike.protocol import JsonObjectOaiLikeChatCompletionResponseFormat
from ..oailike.protocol import JsonSchemaOaiLikeChatCompletionResponseFormat
from ..oailike.protocol import JsonValue
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
from ..oailike.protocol import ToolOaiLikeChatCompletionRequestMessage
from ..oailike.protocol import UserOaiLikeChatCompletionRequestMessage


###
# Ollama OpenAI-compatible Chat Completions.


OllamaChatCompletionReasoningEffort: ta.TypeAlias = ta.Literal[
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


OllamaChatCompletionToolChoiceMode: ta.TypeAlias = OaiLikeChatCompletionToolChoiceMode

OllamaChatCompletionToolChoiceOption: ta.TypeAlias = ta.Union[
    OllamaChatCompletionToolChoiceMode,
    OllamaChatCompletionToolChoice,
]


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
