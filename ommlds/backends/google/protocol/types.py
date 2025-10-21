"""
https://ai.google.dev/api/generate-content
"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh


##


def _set_class_marshal_options(cls):
    msh.update_object_metadata(
        cls,
        field_naming=msh.Naming.LOW_CAMEL,
        field_defaults=msh.FieldMetadata(
            options=msh.FieldOptions(
                omit_if=lang.is_none,
            ),
        ),
    )

    return cls


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
@msh.update_fields_metadata(
    ['data'],
    marshaler=msh.Base64MarshalerUnmarshaler(bytes),
    unmarshaler=msh.Base64MarshalerUnmarshaler(bytes),
)
class Blob(lang.Final):
    mine_type: str
    data: bytes


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class FunctionCall(lang.Final):
    id: str | None = None
    name: str
    args: ta.Mapping[str, ta.Any] | None = None


Scheduling: ta.TypeAlias = ta.Literal[
    # This value is unused.
    'SCHEDULING_UNSPECIFIED',

    # Only add the result to the conversation context, do not interrupt or trigger generation.
    'SILENT',

    # Add the result to the conversation context, and prompt to generate output without interrupting ongoing
    # generation.
    'WHEN_IDLE',

    # Add the result to the conversation context, interrupt ongoing generation and prompt to generate output.
    'INTERRUPT',
]


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class FunctionResponse(lang.Final):
    id: str | None = None
    name: str
    response: ta.Mapping[str, ta.Any] | None = None
    will_continue: bool | None = None
    scheduling: Scheduling | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class FileData(lang.Final):
    mime_type: str
    file_uri: str


Language: ta.TypeAlias = ta.Literal[
    # Unspecified language. This value should not be used.
    'LANGUAGE_UNSPECIFIED',

    # Python >= 3.10, with numpy and simpy available.
    'PYTHON',
]


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ExecutableCode(lang.Final):
    language: Language
    code: str


Outcome: ta.TypeAlias = ta.Literal[
    # Unspecified status. This value should not be used.
    'OUTCOME_UNSPECIFIED',

    # Code execution completed successfully.
    'OUTCOME_OK',

    # Code execution finished but with a failure. stderr should contain the reason.
    'OUTCOME_FAILED',

    # Code execution ran for too long, and was cancelled. There may or may not be a partial output present.
    'OUTCOME_DEADLINE_EXCEEDED',
]


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class CodeExecutionResult(lang.Final):
    outcome: Outcome
    output: str


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class VideoMetadata(lang.Final):
    start_offset: str  # Duration
    end_offset: str  # Duration
    fps: float


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(
    ['thought_signature'],
    marshaler=msh.OptionalMarshaler(msh.Base64MarshalerUnmarshaler(bytes)),
    unmarshaler=msh.OptionalUnmarshaler(msh.Base64MarshalerUnmarshaler(bytes)),
)
@_set_class_marshal_options
class Part(lang.Final):
    # TODO: data: msh.oneof ...
    text: str | None = None
    inline_data: Blob | None = None
    function_call: FunctionCall | None = None
    function_response: FunctionResponse | None = None
    file_data: FileData | None = None
    executable_code: ExecutableCode | None = None
    code_execution_result: CodeExecutionResult | None = None

    thought: bool | None = None
    thought_signature: bytes | None = None

    # TODO: metadata: msh.oneof ...
    video_metadata: VideoMetadata | None = None


ContentRole: ta.TypeAlias = ta.Literal['user', 'model']


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class Content(lang.Final):
    parts: ta.Sequence[Part] | None = None
    role: ContentRole | None = None


##


Type: ta.TypeAlias = ta.Literal[
    # Not specified, should not be used.
    'TYPE_UNSPECIFIED',

    # String type.
    'STRING',

    # Number type.
    'NUMBER',

    # Integer type.
    'INTEGER',

    # Boolean type.
    'BOOLEAN',

    # Array type.
    'ARRAY',

    # Object type.
    'OBJECT',

    # Null type.
    'NULL',
]


Struct: ta.TypeAlias = ta.Mapping[str, 'Value']


@dc.dataclass(frozen=True)
class Value(lang.Abstract, lang.Sealed):
    """https://protobuf.dev/reference/protobuf/google.protobuf/#value"""


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class NullValue(Value, lang.Final):
    null_value: None = None


@dc.dataclass(frozen=True)
@_set_class_marshal_options
class NumberValue(Value, lang.Final):
    number_value: float


@dc.dataclass(frozen=True)
@_set_class_marshal_options
class StringValue(Value, lang.Final):
    string_value: str


@dc.dataclass(frozen=True)
@_set_class_marshal_options
class BoolValue(Value, lang.Final):
    bool_value: bool


@dc.dataclass(frozen=True)
@_set_class_marshal_options
class StructValue(Value, lang.Final):
    struct_value: Struct


@dc.dataclass(frozen=True)
@_set_class_marshal_options
class ListValue(Value, lang.Final):
    list_value: ta.Sequence[Value]


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class Schema(lang.Final):
    type: Type | None = None  # FIXME: required
    format: str | None = None
    title: str | None = None
    description: str | None = None
    nullable: bool | None = None
    enum: ta.Sequence[str] | None = None
    max_items: str | None = None  # int64
    min_items: str | None = None  # int64
    properties: ta.Mapping[str, 'Schema'] | None = None
    required: ta.Sequence[str] | None = None
    min_properties: str | None = None  # int64
    max_properties: str | None = None  # int64
    min_length: str | None = None  # int64
    max_length: str | None = None  # int64
    pattern: str | None = None
    example: Value | None = None
    any_of: ta.Sequence['Schema'] | None = None
    property_ordering: ta.Sequence[str] | None = None
    default: Value | None = None
    items: ta.Optional['Schema'] = None
    minimum: float | None = None
    maximum: float | None = None


FunctionBehavior: ta.TypeAlias = ta.Literal[
    #This value is unused.
    'UNSPECIFIED',

    # If set, the system will wait to receive the function response before continuing the conversation.
    'BLOCKING',

    # If set, the system will not wait to receive the function response. Instead, it will attempt to handle function
    # responses as they become available while maintaining the conversation between the user and the model.
    'NON_BLOCKING',
]


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class FunctionDeclaration(lang.Final):
    name: str
    description: str

    behavior: FunctionBehavior | None = None

    parameters: Schema | None = None
    parameters_json_schema: Value | None = None

    response: Schema | None = None
    response_json_schema: Value | None = None


DynamicRetrievalMode: ta.TypeAlias = ta.Literal[
    # Always trigger retrieval.
    'MODE_UNSPECIFIED',

    # Run retrieval only when system decides it is necessary.
    'MODE_DYNAMIC',
]


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class DynamicRetrievalConfig(lang.Final):
    mode: DynamicRetrievalMode | None = None

    dynamic_threshold: int | float | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class GoogleSearchRetrieval(lang.Final):
    dynamic_retrieval_config: DynamicRetrievalConfig


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class CodeExecution(lang.Final):
    pass


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class Interval(lang.Final):
    start_time: str  # Timestamp
    end_time: str  # Timestamp


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class GoogleSearch(lang.Final):
    time_range_filter: Interval | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class UrlContext(lang.Final):
    pass


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class Tool(lang.Final):
    function_declarations: ta.Sequence[FunctionDeclaration] | None = None
    google_search_retrieval: GoogleSearchRetrieval | None = None
    code_execution: CodeExecution | None = None
    google_search: GoogleSearch | None = None
    url_context: UrlContext | None = None


FunctionCallingMode: ta.TypeAlias = ta.Literal[
    # Unspecified function calling mode. This value should not be used.
    'MODE_UNSPECIFIED',

    # Default model behavior, model decides to predict either a function call or a natural language response.
    'AUTO',

    # Model is constrained to always predicting a function call only. If "allowedFunctionNames" are set, the predicted
    # function call will be limited to any one of "allowedFunctionNames", else the predicted function call will be any
    # one of the provided "functionDeclarations".
    'ANY',

    # Model will not predict any function call. Model behavior is same as when not passing any function declarations.
    'NONE',

    # Model decides to predict either a function call or a natural language response, but will validate function calls
    # with constrained decoding. If "allowedFunctionNames" are set, the predicted function call will be limited to any
    # one of "allowedFunctionNames", else the predicted function call will be any one of the provided
    # "functionDeclarations".
    'VALIDATED',
]


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class FunctionCallingConfig(lang.Final):
    mode: FunctionCallingMode | None = None
    allowed_function_names: ta.Sequence[str] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ToolConfig(lang.Final):
    function_calling_config: FunctionCallingConfig | None = None


HarmCategory: ta.TypeAlias = ta.Literal[
    # Category is unspecified.
    'HARM_CATEGORY_UNSPECIFIED',

    # PaLM - Negative or harmful comments targeting identity and/or protected attribute.
    'HARM_CATEGORY_DEROGATORY',

    # PaLM - Content that is rude, disrespectful, or profane.
    'HARM_CATEGORY_TOXICITY',

    # PaLM - Describes scenarios depicting violence against an individual or group, or general descriptions of gore.
    'HARM_CATEGORY_VIOLENCE',

    # PaLM - Contains references to sexual acts or other lewd content.
    'HARM_CATEGORY_SEXUAL',

    # PaLM - Promotes unchecked medical advice.
    'HARM_CATEGORY_MEDICAL',

    # PaLM - Dangerous content that promotes, facilitates, or encourages harmful acts.
    'HARM_CATEGORY_DANGEROUS',

    # Gemini - Harassment content.
    'HARM_CATEGORY_HARASSMENT',

    # Gemini - Hate speech and content.
    'HARM_CATEGORY_HATE_SPEECH',

    # Gemini - Sexually explicit content.
    'HARM_CATEGORY_SEXUALLY_EXPLICIT',

    # Gemini - Dangerous content.
    'HARM_CATEGORY_DANGEROUS_CONTENT',

    # Gemini - Content that may be used to harm civic integrity. DEPRECATED: use enableEnhancedCivicAnswers instead.
    'HARM_CATEGORY_CIVIC_INTEGRITY',
]


HarmBlockThreshold: ta.TypeAlias = ta.Literal[
    # Threshold is unspecified.
    'HARM_BLOCK_THRESHOLD_UNSPECIFIED',

    # Content with NEGLIGIBLE will be allowed.
    'BLOCK_LOW_AND_ABOVE',

    # Content with NEGLIGIBLE and LOW will be allowed.
    'BLOCK_MEDIUM_AND_ABOVE',

    # Content with NEGLIGIBLE, LOW, and MEDIUM will be allowed.
    'BLOCK_ONLY_HIGH',

    # All content will be allowed.
    'BLOCK_NONE',

    # Turn off the safety filter.
    'OFF',
]


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SafetySetting(lang.Final):
    category: HarmCategory
    threshold: HarmBlockThreshold


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ThinkingConfig(lang.Final):
    include_thoughts: bool | None = None
    thinking_budget: int | None = None


Modality: ta.TypeAlias = ta.Literal[
    # Default value.
    'MODALITY_UNSPECIFIED',

    # Indicates the model should return text.
    'TEXT',

    # Indicates the model should return images.
    'IMAGE',

    # Indicates the model should return audio.
    'AUDIO',
]


MediaResolution: ta.TypeAlias = ta.Literal[
    # Media resolution has not been set.
    'MEDIA_RESOLUTION_UNSPECIFIED',

    # Media resolution set to low (64 tokens).
    'MEDIA_RESOLUTION_LOW',

    # Media resolution set to medium (256 tokens).
    'MEDIA_RESOLUTION_MEDIUM',

    # Media resolution set to high (zoomed reframing with 256 tokens).
    'MEDIA_RESOLUTION_HIGH',
]


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class GenerationConfig(lang.Final):
    stop_sequences: ta.Sequence[str] | None = None

    response_mime_type: str | None = None
    response_schema: Schema | None = None
    response_json_schema: Value | None = None
    response_modalities: ta.Sequence[Modality] | None = None

    candidate_count: int | None = None
    max_output_tokens: int | None = None
    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None
    seed: int | None = None
    presence_penalty: float | None = None
    frequency_penalty: float | None = None

    response_logprobs: bool | None = None
    logprobs: int | None = None

    enable_enhanced_civic_answers: bool | None = None

    # speech_config: SpeechConfig | None = None

    thinking_config: ThinkingConfig | None = None

    media_resolution: MediaResolution | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class GenerateContentRequest(lang.Final):
    """https://ai.google.dev/api/generate-content#request-body"""

    contents: ta.Sequence[Content] | None = None
    tools: ta.Sequence[Tool] | None = None
    tool_config: ToolConfig | None = None
    safety_settings: ta.Sequence[SafetySetting] | None = None
    system_instruction: Content | None = None
    generation_config: GenerationConfig | None = None
    cached_content: str | None = None


FinishReason: ta.TypeAlias = ta.Literal[
    # Default value. This value is unused.
    'FINISH_REASON_UNSPECIFIED',

    # Natural stop point of the model or provided stop sequence.
    'STOP',

    # The maximum number of tokens as specified in the request was reached.
    'MAX_TOKENS',

    # The response candidate content was flagged for safety reasons.
    'SAFETY',

    # The response candidate content was flagged for recitation reasons.
    'RECITATION',

    # The response candidate content was flagged for using an unsupported language.
    'LANGUAGE',

    # Unknown reason.
    'OTHER',

    # Token generation stopped because the content contains forbidden terms.
    'BLOCKLIST',

    # Token generation stopped for potentially containing prohibited content.
    'PROHIBITED_CONTENT',

    # Token generation stopped because the content potentially contains Sensitive Personally Identifiable Information
    # (SPII).
    'SPII',

    # The function call generated by the model is invalid.
    'MALFORMED_FUNCTION_CALL',

    # Token generation stopped because generated images contain safety violations.
    'IMAGE_SAFETY',

    # Model generated a tool call but no tools were enabled in the request.
    'UNEXPECTED_TOOL_CALL',

    # Model called too many tools consecutively, thus the system exited execution.
    'TOO_MANY_TOOL_CALLS',
]


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class GenerateContentResponse(lang.Final):
    """https://ai.google.dev/api/generate-content#v1beta.GenerateContentResponse"""

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class Candidate(lang.Final):
        content: Content | None = None
        finish_reason: FinishReason | None = None
        finish_message: str | None = None
        # safety_ratings: ta.Sequence[SafetyRating] | None = None
        # citation_metadata: CitationMetadata | None = None
        token_count: int | None = None
        # grounding_attributions: ta.Sequence[GroundingAttribution] | None = None
        # grounding_metadata: GroundingMetadata | None = None
        avg_logprobs: float | None = None
        # logprobs_result: LogprobsResult | None = None
        # url_context_metadata: UrlContextMetadata | None = None
        index: int | None = None

    candidates: ta.Sequence[Candidate] | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class UsageMetadata(lang.Final):
        prompt_token_count: int | None = None
        cached_content_token_count: int | None = None
        candidates_token_count: int | None = None
        total_token_count: int | None = None
        thoughts_token_count: int | None = None

        @dc.dataclass(frozen=True, kw_only=True)
        @_set_class_marshal_options
        class ModalityTokenCount:
            modality: str | None = None
            token_count: int | None = None

        prompt_tokens_details: ta.Sequence[ModalityTokenCount] | None = None
        cache_tokens_details: ta.Sequence[ModalityTokenCount] | None = None
        candidates_tokens_details: ta.Sequence[ModalityTokenCount] | None = None
        tool_use_prompt_tokens_details: ta.Sequence[ModalityTokenCount] | None = None

    usage_metadata: UsageMetadata | None = None

    model_version: str | None = None

    response_id: str | None = None
