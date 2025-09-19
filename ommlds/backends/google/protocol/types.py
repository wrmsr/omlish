import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh


##


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class Blob(lang.Final):
    mine_type: str
    data: bytes


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class FunctionCall(lang.Final):
    id: str
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
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class FunctionResponse(lang.Final):
    id: str
    name: str
    response: ta.Mapping[str, ta.Any] | None = None
    will_continue: bool | None = None
    scheduling: Scheduling | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
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
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
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
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class CodeExecutionResult(lang.Final):
    outcome: Outcome
    output: str


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class VideoMetadata(lang.Final):
    start_offset: str  # Duration
    end_offset: str  # Duration
    fps: float


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
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


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class Content(lang.Final):
    parts: ta.Sequence[Part] | None = None
    role: ta.Literal['user', 'model'] | None = None


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


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class Value(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class NullValue(Value, lang.Final):
    null_value: None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class NumberValue(Value, lang.Final):
    number_value: float


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class StringValue(Value, lang.Final):
    string_value: str


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class BoolValue(Value, lang.Final):
    bool_value: bool


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class StructValue(Value, lang.Final):
    struct_value: Struct


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class ListValue(Value, lang.Final):
    list_value: ta.Sequence[Value]


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class Schema(lang.Final):
    type: Type | None = None
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
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class FunctionDeclaration(lang.Final):
    name: str
    description: str

    behavior: FunctionBehavior

    parameters: Schema
    parameters_json_schema: Value

    response: Schema
    response_json_schema: Value


DynamicRetrievalMode: ta.TypeAlias = ta.Literal[
    # Always trigger retrieval.
    'MODE_UNSPECIFIED',

    # Run retrieval only when system decides it is necessary.
    'MODE_DYNAMIC',
]


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class DynamicRetrievalConfig(lang.Final):
    mode: DynamicRetrievalMode | None = None

    dynamic_threshold: int | float | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class GoogleSearchRetrieval(lang.Final):
    dynamic_retrieval_config: DynamicRetrievalConfig


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class CodeExecution(lang.Final):
    pass


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class Interval(lang.Final):
    start_time: str  # Timestamp
    end_time: str  # Timestamp


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class GoogleSearch(lang.Final):
    time_range_filter: Interval | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class UrlContext(lang.Final):
    pass


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class Tool(lang.Final):
    function_declarations: ta.Sequence[FunctionDeclaration] | None = None
    google_search_retrieval: GoogleSearchRetrieval | None = None
    code_execution: CodeExecution | None = None
    google_search: GoogleSearch | None = None
    url_context: UrlContext | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class GenerateContentRequest(lang.Final):
    """https://ai.google.dev/api/generate-content#request-body"""

    contents: ta.Sequence[Content] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_fields_metadata(omit_if=lang.is_none)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class GenerateContentResponse(lang.Final):
    """https://ai.google.dev/api/generate-content#v1beta.GenerateContentResponse"""

    @dc.dataclass(frozen=True, kw_only=True)
    @msh.update_fields_metadata(omit_if=lang.is_none)
    @msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
    class Candidate(lang.Final):
        content: Content | None = None
        finish_reason: ta.Literal['STOP'] | None = None
        index: int | None = None

    candidates: ta.Sequence[Candidate] | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    @msh.update_fields_metadata(omit_if=lang.is_none)
    @msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
    class UsageMetadata(lang.Final):
        prompt_token_count: int | None = None
        cached_content_token_count: int | None = None
        candidates_token_count: int | None = None
        total_token_count: int | None = None
        thoughts_token_count: int | None = None

        @dc.dataclass(frozen=True, kw_only=True)
        @msh.update_fields_metadata(omit_if=lang.is_none)
        @msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
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
