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


VllmChatCompletionToolChoiceMode: ta.TypeAlias = OaiLikeChatCompletionToolChoiceMode

VllmChatCompletionToolChoiceOption: ta.TypeAlias = ta.Union[
    VllmChatCompletionToolChoiceMode,
    VllmChatCompletionToolChoice,
]


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
