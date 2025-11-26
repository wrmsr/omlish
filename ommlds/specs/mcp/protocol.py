"""
https://modelcontextprotocol.io/specification/2025-06-18
https://modelcontextprotocol.io/specification/2025-06-18/schema

TODO:
 - https://modelcontextprotocol.io/specification/2025-06-18/basic/utilities/cancellation
 - https://modelcontextprotocol.io/specification/2025-06-18/basic/utilities/progress
 - https://modelcontextprotocol.io/specification/2025-06-18/client/sampling
 - https://modelcontextprotocol.io/specification/2025-06-18/client/elicitation
 - https://modelcontextprotocol.io/specification/2025-06-18/server/prompts
 - https://modelcontextprotocol.io/specification/2025-06-18/server/resources
 - https://modelcontextprotocol.io/specification/2025-06-18/server/utilities/logging
"""
import abc
import typing as ta

from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh


ClientRequestT = ta.TypeVar('ClientRequestT', bound='ClientRequest')
ClientResultT = ta.TypeVar('ClientResultT', bound='ClientResult')

ServerRequestT = ta.TypeVar('ServerRequestT', bound='ServerRequest')
ServerResultT = ta.TypeVar('ServerResultT', bound='ServerResult')

CursorClientRequestT = ta.TypeVar('CursorClientRequestT', bound='CursorClientRequest')
CursorClientResultT = ta.TypeVar('CursorClientResultT', bound='CursorClientResult')


msh.register_global_module_import('._marshal', __package__)


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


##


@dc.dataclass(frozen=True, kw_only=True)
class Message(lang.Sealed, lang.Abstract):
    @property
    @abc.abstractmethod
    def json_rpc_method_name(self) -> str:
        raise NotImplementedError


#


class ClientRequest(Message, lang.Abstract, ta.Generic[ClientResultT]):
    pass


class ClientResult(Message, lang.Abstract, ta.Generic[ClientRequestT]):
    pass


#


class ServerRequest(Message, lang.Abstract, ta.Generic[ServerResultT]):
    pass


class ServerResult(Message, lang.Abstract, ta.Generic[ServerRequestT]):
    pass


#


class Notification(Message, lang.Abstract):
    pass


##


@dc.dataclass(frozen=True, kw_only=True)
class WithMeta(lang.Sealed, lang.Abstract):
    meta_: ta.Mapping[str, ta.Any] | None = dc.field(default=None) | msh.with_field_metadata(name='_meta')


##


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class Implementation(lang.Final):
    name: str
    version: str


DEFAULT_PROTOCOL_VERSION = '2025-06-18'


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ClientCapabilities(lang.Final):
    elicitation: ta.Any | None = None

    experimental: ta.Mapping[str, ta.Any] | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class Roots:
        list_changed: bool | None = None

    roots: Roots | None = None

    sampling: ta.Any | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class InitializeRequest(ClientRequest['InitializeResult']):
    json_rpc_method_name: ta.ClassVar[str] = 'initialize'

    client_info: Implementation
    protocol_version: str = DEFAULT_PROTOCOL_VERSION
    capabilities: ClientCapabilities = ClientCapabilities()


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ServerCapabilities:
    completions: ta.Any | None = None

    experimental: ta.Mapping[str, ta.Any] | None = None

    logging: ta.Any | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class Prompts:
        list_changed: bool | None = None

    prompts: Prompts | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class Resources:
        list_changed: bool | None = None
        subscribe: bool | None = None

    resources: Resources | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    @_set_class_marshal_options
    class Tools:
        list_changed: bool | None = None

    tools: Tools | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class InitializeResult(ClientResult[InitializeRequest], WithMeta):
    json_rpc_method_name: ta.ClassVar[str] = 'initialize'

    server_info: Implementation
    protocol_version: str
    capabilities: ServerCapabilities
    instructions: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class InitializedNotification(Notification):
    json_rpc_method_name: ta.ClassVar[str] = 'initialized'


##


@dc.dataclass(frozen=True, kw_only=True)
class CursorClientRequest(ClientRequest[CursorClientResultT], lang.Abstract):
    cursor: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class CursorClientResult(ClientResult[CursorClientRequestT], lang.Abstract):
    next_cursor: str | None = None


##


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ToolAnnotations(lang.Final):
    destructive_hint: bool | None = None
    idempotent_hint: bool | None = None
    open_world_hint: bool | None = None
    read_only_hint: bool | None = None
    title: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class Tool(WithMeta, lang.Final):
    name: str
    title: str | None = None

    description: str | None = None

    annotations: ToolAnnotations | None = None

    input_schema: ta.Any
    output_schema: ta.Any | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ListToolsRequest(CursorClientRequest['ListToolsResult']):
    json_rpc_method_name: ta.ClassVar[str] = 'tools/list'


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ListToolsResult(CursorClientResult[ListToolsRequest], WithMeta):
    json_rpc_method_name: ta.ClassVar[str] = 'tools/list'

    tools: ta.Sequence[Tool]


##


class ContentBlock(lang.Abstract):
    pass


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class TextContentBlock(ContentBlock, lang.Final):
    text: str


##


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class CallToolRequest(ClientRequest['CallToolResult']):
    json_rpc_method_name: ta.ClassVar[str] = 'tools/call'

    name: str
    arguments: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class CallToolResult(ClientResult[CallToolRequest], WithMeta):
    json_rpc_method_name: ta.ClassVar[str] = 'tools/call'

    content: ta.Sequence[ContentBlock]
    is_error: bool | None = None
    structured_content: ta.Mapping[str, ta.Any] | None = None


##


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class PingClientRequest(ClientRequest['PingClientResult'], WithMeta):
    json_rpc_method_name: ta.ClassVar[str] = 'ping'


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class PingClientResult(ClientResult[PingClientRequest]):
    json_rpc_method_name: ta.ClassVar[str] = 'ping'


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class PingServerRequest(ServerRequest['PingServerResult'], WithMeta):
    json_rpc_method_name: ta.ClassVar[str] = 'ping'


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class PingServerResult(ServerResult[PingServerRequest]):
    json_rpc_method_name: ta.ClassVar[str] = 'ping'


##


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class PromptArgument(lang.Final):
    name: str
    title: str | None = None

    description: str | None = None

    required: bool | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class Prompt(WithMeta, lang.Final):
    name: str
    title: str | None = None

    description: str | None = None

    arguments: ta.Sequence[PromptArgument] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ListPromptsRequest(CursorClientRequest['ListPromptsResult']):
    json_rpc_method_name: ta.ClassVar[str] = 'prompts/list'


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ListPromptsResult(CursorClientResult[ListPromptsRequest], WithMeta):
    json_rpc_method_name: ta.ClassVar[str] = 'prompts/list'

    prompts: ta.Sequence[Prompt]


##


LoggingLevel: ta.TypeAlias = ta.Literal[
    'debug',
    'info',
    'notice',
    'warning',
    'error',
    'critical',
    'alert',
    'emergency',
]


##


MESSAGE_TYPES_BY_JSON_RPC_METHOD_NAME: ta.Mapping[type[Message], ta.Mapping[str, type[Message]]] = {
    bty: col.make_map_by(lambda mty: mty.json_rpc_method_name, lang.deep_subclasses(bty, concrete_only=True))  # type: ignore  # noqa
    for bty in [
        ClientRequest,
        ClientResult,
        ServerRequest,
        ServerResult,
        Notification,
    ]
}
