# @om-generated
# ruff: noqa: UP007 UP037 UP045
import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh


##


def _set_class_marshal_options(*, field_naming=msh.Naming.LOW_CAMEL, ignore_unknown=False):
    def inner(cls):
        msh.update_object_options(
            field_naming=field_naming,
            ignore_unknown=ignore_unknown,
            field_defaults=msh.FieldOptions(
                omit_if=lang.is_none,
            ),
        )(cls)

        return cls

    return inner


##


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class Annotations(lang.Final):
    audience: ta.Optional[ta.Sequence[Role]] = None
    last_modified: ta.Optional[str] = None
    priority: ta.Optional[float] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class AudioContent(lang.Final):
    data: str
    mime_type: str
    annotations: ta.Optional[Annotations] = None
    type: ta.Literal['audio'] = dc.xfield(
        'audio',
        repr=False,
    )
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class BaseMetadata(lang.Final):
    name: str
    title: ta.Optional[str] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class BlobResourceContents(lang.Final):
    blob: str
    uri: str
    mime_type: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class BooleanSchema(lang.Final):
    default: ta.Optional[bool] = None
    description: ta.Optional[str] = None
    title: ta.Optional[str] = None
    type: ta.Literal['boolean'] = dc.xfield(
        'boolean',
        repr=False,
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class CallToolRequest(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Params(lang.Final):
        name: str
        arguments: ta.Optional[ta.Mapping[str, ta.Any]] = None

    params: CallToolRequest.Params
    method: ta.Literal['tools/call'] = dc.xfield(
        'tools/call',
        repr=False,
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class CallToolResult(lang.Final):
    content: ta.Sequence[ContentBlock]
    is_error: ta.Optional[bool] = None
    structured_content: ta.Optional[ta.Mapping[str, ta.Any]] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class CancelledNotification(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Params(lang.Final):
        request_id: RequestId
        reason: ta.Optional[str] = None

    params: CancelledNotification.Params
    method: ta.Literal['notifications/cancelled'] = dc.xfield(
        'notifications/cancelled',
        repr=False,
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ClientCapabilities(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Roots(lang.Final):
        list_changed: ta.Optional[bool] = None

    elicitation: ta.Optional[ta.Mapping[str, ta.Any]] = None
    experimental: ta.Optional[ta.Mapping[str, ta.Mapping[str, ta.Any]]] = None
    roots: ta.Optional[ClientCapabilities.Roots] = None
    sampling: ta.Optional[ta.Mapping[str, ta.Any]] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class CompleteRequest(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Params(lang.Final):
        @dc.dataclass(frozen=True, kw_only=True)
        @_set_class_marshal_options()
        class Argument(lang.Final):
            name: str
            value: str

        @dc.dataclass(frozen=True, kw_only=True)
        @_set_class_marshal_options()
        class Context(lang.Final):
            arguments: ta.Optional[ta.Mapping[str, str]] = None

        argument: CompleteRequest.Params.Argument
        ref: ta.Any
        context: ta.Optional[CompleteRequest.Params.Context] = None

    params: CompleteRequest.Params
    method: ta.Literal['completion/complete'] = dc.xfield(
        'completion/complete',
        repr=False,
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class CompleteResult(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Completion(lang.Final):
        values: ta.Sequence[str]
        has_more: ta.Optional[bool] = None
        total: ta.Optional[int] = None

    completion: CompleteResult.Completion
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class CreateMessageRequest(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Params(lang.Final):
        max_tokens: int
        messages: ta.Sequence[SamplingMessage]
        include_context: ta.Optional[ta.Literal['allServers', 'none', 'thisServer']] = None
        metadata: ta.Optional[ta.Mapping[str, ta.Any]] = None
        model_preferences: ta.Optional[ModelPreferences] = None
        stop_sequences: ta.Optional[ta.Sequence[str]] = None
        system_prompt: ta.Optional[str] = None
        temperature: ta.Optional[float] = None

    params: CreateMessageRequest.Params
    method: ta.Literal['sampling/createMessage'] = dc.xfield(
        'sampling/createMessage',
        repr=False,
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class CreateMessageResult(lang.Final):
    content: ta.Any
    model: str
    role: Role
    stop_reason: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ElicitRequest(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Params(lang.Final):
        @dc.dataclass(frozen=True, kw_only=True)
        @_set_class_marshal_options()
        class RequestedSchema(lang.Final):
            properties: ta.Mapping[str, PrimitiveSchemaDefinition]
            required: ta.Optional[ta.Sequence[str]] = None
            type: ta.Literal['object'] = dc.xfield(
                'object',
                repr=False,
            )

        message: str
        requested_schema: ElicitRequest.Params.RequestedSchema

    params: ElicitRequest.Params
    method: ta.Literal['elicitation/create'] = dc.xfield(
        'elicitation/create',
        repr=False,
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ElicitResult(lang.Final):
    action: ta.Literal['accept', 'cancel', 'decline']
    content: ta.Optional[ta.Mapping[str, ta.Union[str, int, bool]]] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class EmbeddedResource(lang.Final):
    resource: ta.Any
    annotations: ta.Optional[Annotations] = None
    type: ta.Literal['resource'] = dc.xfield(
        'resource',
        repr=False,
    )
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class EnumSchema(lang.Final):
    enum: ta.Sequence[str]
    description: ta.Optional[str] = None
    enum_names: ta.Optional[ta.Sequence[str]] = None
    title: ta.Optional[str] = None
    type: ta.Literal['string'] = dc.xfield(
        'string',
        repr=False,
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class GetPromptRequest(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Params(lang.Final):
        name: str
        arguments: ta.Optional[ta.Mapping[str, str]] = None

    params: GetPromptRequest.Params
    method: ta.Literal['prompts/get'] = dc.xfield(
        'prompts/get',
        repr=False,
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class GetPromptResult(lang.Final):
    messages: ta.Sequence[PromptMessage]
    description: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ImageContent(lang.Final):
    data: str
    mime_type: str
    annotations: ta.Optional[Annotations] = None
    type: ta.Literal['image'] = dc.xfield(
        'image',
        repr=False,
    )
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class Implementation(lang.Final):
    name: str
    version: str
    title: ta.Optional[str] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class InitializeRequest(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Params(lang.Final):
        capabilities: ClientCapabilities
        client_info: Implementation
        protocol_version: str

    params: InitializeRequest.Params
    method: ta.Literal['initialize'] = dc.xfield(
        'initialize',
        repr=False,
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class InitializeResult(lang.Final):
    capabilities: ServerCapabilities
    protocol_version: str
    server_info: Implementation
    instructions: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class InitializedNotification(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options(ignore_unknown=True)
    class Params(lang.Final):
        meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
            default=None,
            metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
        )

    method: ta.Literal['notifications/initialized'] = dc.xfield(
        'notifications/initialized',
        repr=False,
    )
    params: ta.Optional[InitializedNotification.Params] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class JSONRPCError(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Error(lang.Final):
        code: int
        message: str
        data: ta.Optional[ta.Any] = None

    error: JSONRPCError.Error
    id: RequestId
    jsonrpc: ta.Literal['2.0'] = dc.xfield(
        '2.0',
        repr=False,
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class JSONRPCNotification(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options(ignore_unknown=True)
    class Params(lang.Final):
        meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
            default=None,
            metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
        )

    method: str
    jsonrpc: ta.Literal['2.0'] = dc.xfield(
        '2.0',
        repr=False,
    )
    params: ta.Optional[JSONRPCNotification.Params] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class JSONRPCRequest(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options(ignore_unknown=True)
    class Params(lang.Final):
        @dc.dataclass(frozen=True, kw_only=True)
        @_set_class_marshal_options(ignore_unknown=True)
        class Meta(lang.Final):
            progress_token: ta.Optional[ProgressToken] = None

        meta: ta.Optional[JSONRPCRequest.Params.Meta] = dc.field(
            default=None,
            metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
        )

    id: RequestId
    method: str
    jsonrpc: ta.Literal['2.0'] = dc.xfield(
        '2.0',
        repr=False,
    )
    params: ta.Optional[JSONRPCRequest.Params] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class JSONRPCResponse(lang.Final):
    id: RequestId
    result: Result
    jsonrpc: ta.Literal['2.0'] = dc.xfield(
        '2.0',
        repr=False,
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ListPromptsRequest(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Params(lang.Final):
        cursor: ta.Optional[str] = None

    method: ta.Literal['prompts/list'] = dc.xfield(
        'prompts/list',
        repr=False,
    )
    params: ta.Optional[ListPromptsRequest.Params] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ListPromptsResult(lang.Final):
    prompts: ta.Sequence[Prompt]
    next_cursor: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ListResourceTemplatesRequest(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Params(lang.Final):
        cursor: ta.Optional[str] = None

    method: ta.Literal['resources/templates/list'] = dc.xfield(
        'resources/templates/list',
        repr=False,
    )
    params: ta.Optional[ListResourceTemplatesRequest.Params] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ListResourceTemplatesResult(lang.Final):
    resource_templates: ta.Sequence[ResourceTemplate]
    next_cursor: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ListResourcesRequest(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Params(lang.Final):
        cursor: ta.Optional[str] = None

    method: ta.Literal['resources/list'] = dc.xfield(
        'resources/list',
        repr=False,
    )
    params: ta.Optional[ListResourcesRequest.Params] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ListResourcesResult(lang.Final):
    resources: ta.Sequence[Resource]
    next_cursor: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ListRootsRequest(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options(ignore_unknown=True)
    class Params(lang.Final):
        @dc.dataclass(frozen=True, kw_only=True)
        @_set_class_marshal_options(ignore_unknown=True)
        class Meta(lang.Final):
            progress_token: ta.Optional[ProgressToken] = None

        meta: ta.Optional[ListRootsRequest.Params.Meta] = dc.field(
            default=None,
            metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
        )

    method: ta.Literal['roots/list'] = dc.xfield(
        'roots/list',
        repr=False,
    )
    params: ta.Optional[ListRootsRequest.Params] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ListRootsResult(lang.Final):
    roots: ta.Sequence[Root]
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ListToolsRequest(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Params(lang.Final):
        cursor: ta.Optional[str] = None

    method: ta.Literal['tools/list'] = dc.xfield(
        'tools/list',
        repr=False,
    )
    params: ta.Optional[ListToolsRequest.Params] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ListToolsResult(lang.Final):
    tools: ta.Sequence[Tool]
    next_cursor: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class LoggingMessageNotification(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Params(lang.Final):
        data: ta.Any
        level: LoggingLevel
        logger: ta.Optional[str] = None

    params: LoggingMessageNotification.Params
    method: ta.Literal['notifications/message'] = dc.xfield(
        'notifications/message',
        repr=False,
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ModelHint(lang.Final):
    name: ta.Optional[str] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ModelPreferences(lang.Final):
    cost_priority: ta.Optional[float] = None
    hints: ta.Optional[ta.Sequence[ModelHint]] = None
    intelligence_priority: ta.Optional[float] = None
    speed_priority: ta.Optional[float] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class Notification(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options(ignore_unknown=True)
    class Params(lang.Final):
        meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
            default=None,
            metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
        )

    method: str
    params: ta.Optional[Notification.Params] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class NumberSchema(lang.Final):
    type: ta.Literal['integer', 'number']
    description: ta.Optional[str] = None
    maximum: ta.Optional[int] = None
    minimum: ta.Optional[int] = None
    title: ta.Optional[str] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class PaginatedRequest(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Params(lang.Final):
        cursor: ta.Optional[str] = None

    method: str
    params: ta.Optional[PaginatedRequest.Params] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class PaginatedResult(lang.Final):
    next_cursor: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class PingRequest(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options(ignore_unknown=True)
    class Params(lang.Final):
        @dc.dataclass(frozen=True, kw_only=True)
        @_set_class_marshal_options(ignore_unknown=True)
        class Meta(lang.Final):
            progress_token: ta.Optional[ProgressToken] = None

        meta: ta.Optional[PingRequest.Params.Meta] = dc.field(
            default=None,
            metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
        )

    method: ta.Literal['ping'] = dc.xfield(
        'ping',
        repr=False,
    )
    params: ta.Optional[PingRequest.Params] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ProgressNotification(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Params(lang.Final):
        progress: float
        progress_token: ProgressToken
        message: ta.Optional[str] = None
        total: ta.Optional[float] = None

    params: ProgressNotification.Params
    method: ta.Literal['notifications/progress'] = dc.xfield(
        'notifications/progress',
        repr=False,
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class Prompt(lang.Final):
    name: str
    arguments: ta.Optional[ta.Sequence[PromptArgument]] = None
    description: ta.Optional[str] = None
    title: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class PromptArgument(lang.Final):
    name: str
    description: ta.Optional[str] = None
    required: ta.Optional[bool] = None
    title: ta.Optional[str] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class PromptListChangedNotification(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options(ignore_unknown=True)
    class Params(lang.Final):
        meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
            default=None,
            metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
        )

    method: ta.Literal['notifications/prompts/list_changed'] = dc.xfield(
        'notifications/prompts/list_changed',
        repr=False,
    )
    params: ta.Optional[PromptListChangedNotification.Params] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class PromptMessage(lang.Final):
    content: ContentBlock
    role: Role


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class PromptReference(lang.Final):
    name: str
    title: ta.Optional[str] = None
    type: ta.Literal['ref/prompt'] = dc.xfield(
        'ref/prompt',
        repr=False,
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ReadResourceRequest(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Params(lang.Final):
        uri: str

    params: ReadResourceRequest.Params
    method: ta.Literal['resources/read'] = dc.xfield(
        'resources/read',
        repr=False,
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ReadResourceResult(lang.Final):
    contents: ta.Sequence[ta.Any]
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class Request(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options(ignore_unknown=True)
    class Params(lang.Final):
        @dc.dataclass(frozen=True, kw_only=True)
        @_set_class_marshal_options(ignore_unknown=True)
        class Meta(lang.Final):
            progress_token: ta.Optional[ProgressToken] = None

        meta: ta.Optional[Request.Params.Meta] = dc.field(
            default=None,
            metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
        )

    method: str
    params: ta.Optional[Request.Params] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class Resource(lang.Final):
    name: str
    uri: str
    annotations: ta.Optional[Annotations] = None
    description: ta.Optional[str] = None
    mime_type: ta.Optional[str] = None
    size: ta.Optional[int] = None
    title: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ResourceContents(lang.Final):
    uri: str
    mime_type: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ResourceLink(lang.Final):
    name: str
    uri: str
    annotations: ta.Optional[Annotations] = None
    description: ta.Optional[str] = None
    mime_type: ta.Optional[str] = None
    size: ta.Optional[int] = None
    title: ta.Optional[str] = None
    type: ta.Literal['resource_link'] = dc.xfield(
        'resource_link',
        repr=False,
    )
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ResourceListChangedNotification(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options(ignore_unknown=True)
    class Params(lang.Final):
        meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
            default=None,
            metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
        )

    method: ta.Literal['notifications/resources/list_changed'] = dc.xfield(
        'notifications/resources/list_changed',
        repr=False,
    )
    params: ta.Optional[ResourceListChangedNotification.Params] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ResourceTemplate(lang.Final):
    name: str
    uri_template: str
    annotations: ta.Optional[Annotations] = None
    description: ta.Optional[str] = None
    mime_type: ta.Optional[str] = None
    title: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ResourceTemplateReference(lang.Final):
    uri: str
    type: ta.Literal['ref/resource'] = dc.xfield(
        'ref/resource',
        repr=False,
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ResourceUpdatedNotification(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Params(lang.Final):
        uri: str

    params: ResourceUpdatedNotification.Params
    method: ta.Literal['notifications/resources/updated'] = dc.xfield(
        'notifications/resources/updated',
        repr=False,
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options(ignore_unknown=True)
class Result(lang.Final):
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class Root(lang.Final):
    uri: str
    name: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class RootsListChangedNotification(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options(ignore_unknown=True)
    class Params(lang.Final):
        meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
            default=None,
            metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
        )

    method: ta.Literal['notifications/roots/list_changed'] = dc.xfield(
        'notifications/roots/list_changed',
        repr=False,
    )
    params: ta.Optional[RootsListChangedNotification.Params] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class SamplingMessage(lang.Final):
    content: ta.Any
    role: Role


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ServerCapabilities(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Prompts(lang.Final):
        list_changed: ta.Optional[bool] = None

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Resources(lang.Final):
        list_changed: ta.Optional[bool] = None
        subscribe: ta.Optional[bool] = None

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Tools(lang.Final):
        list_changed: ta.Optional[bool] = None

    completions: ta.Optional[ta.Mapping[str, ta.Any]] = None
    experimental: ta.Optional[ta.Mapping[str, ta.Mapping[str, ta.Any]]] = None
    logging: ta.Optional[ta.Mapping[str, ta.Any]] = None
    prompts: ta.Optional[ServerCapabilities.Prompts] = None
    resources: ta.Optional[ServerCapabilities.Resources] = None
    tools: ta.Optional[ServerCapabilities.Tools] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class SetLevelRequest(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Params(lang.Final):
        level: LoggingLevel

    params: SetLevelRequest.Params
    method: ta.Literal['logging/setLevel'] = dc.xfield(
        'logging/setLevel',
        repr=False,
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class StringSchema(lang.Final):
    description: ta.Optional[str] = None
    format: ta.Optional[ta.Literal['date', 'date-time', 'email', 'uri']] = None
    max_length: ta.Optional[int] = None
    min_length: ta.Optional[int] = None
    title: ta.Optional[str] = None
    type: ta.Literal['string'] = dc.xfield(
        'string',
        repr=False,
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class SubscribeRequest(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Params(lang.Final):
        uri: str

    params: SubscribeRequest.Params
    method: ta.Literal['resources/subscribe'] = dc.xfield(
        'resources/subscribe',
        repr=False,
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class TextContent(lang.Final):
    text: str
    annotations: ta.Optional[Annotations] = None
    type: ta.Literal['text'] = dc.xfield(
        'text',
        repr=False,
    )
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class TextResourceContents(lang.Final):
    text: str
    uri: str
    mime_type: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class Tool(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class InputSchema(lang.Final):
        properties: ta.Optional[ta.Mapping[str, ta.Mapping[str, ta.Any]]] = None
        required: ta.Optional[ta.Sequence[str]] = None
        type: ta.Literal['object'] = dc.xfield(
            'object',
            repr=False,
        )

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class OutputSchema(lang.Final):
        properties: ta.Optional[ta.Mapping[str, ta.Mapping[str, ta.Any]]] = None
        required: ta.Optional[ta.Sequence[str]] = None
        type: ta.Literal['object'] = dc.xfield(
            'object',
            repr=False,
        )

    input_schema: Tool.InputSchema
    name: str
    annotations: ta.Optional[ToolAnnotations] = None
    description: ta.Optional[str] = None
    output_schema: ta.Optional[Tool.OutputSchema] = None
    title: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ToolAnnotations(lang.Final):
    destructive_hint: ta.Optional[bool] = None
    idempotent_hint: ta.Optional[bool] = None
    open_world_hint: ta.Optional[bool] = None
    read_only_hint: ta.Optional[bool] = None
    title: ta.Optional[str] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class ToolListChangedNotification(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options(ignore_unknown=True)
    class Params(lang.Final):
        meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
            default=None,
            metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
        )

    method: ta.Literal['notifications/tools/list_changed'] = dc.xfield(
        'notifications/tools/list_changed',
        repr=False,
    )
    params: ta.Optional[ToolListChangedNotification.Params] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options()
class UnsubscribeRequest(lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options()
    class Params(lang.Final):
        uri: str

    params: UnsubscribeRequest.Params
    method: ta.Literal['resources/unsubscribe'] = dc.xfield(
        'resources/unsubscribe',
        repr=False,
    )


##


Cursor: ta.TypeAlias = str


EmptyResult: ta.TypeAlias = Result


ProgressToken: ta.TypeAlias = ta.Union[str, int]


RequestId: ta.TypeAlias = ta.Union[str, int]


##


LoggingLevel: ta.TypeAlias = ta.Literal[
    'alert',
    'critical',
    'debug',
    'emergency',
    'error',
    'info',
    'notice',
    'warning',
]


Role: ta.TypeAlias = ta.Literal['assistant', 'user']


##


ClientNotification: ta.TypeAlias = ta.Any


ClientRequest: ta.TypeAlias = ta.Any


ClientResult: ta.TypeAlias = ta.Any


ContentBlock: ta.TypeAlias = ta.Any


JSONRPCMessage: ta.TypeAlias = ta.Any


PrimitiveSchemaDefinition: ta.TypeAlias = ta.Any


ServerNotification: ta.TypeAlias = ta.Any


ServerRequest: ta.TypeAlias = ta.Any


ServerResult: ta.TypeAlias = ta.Any
