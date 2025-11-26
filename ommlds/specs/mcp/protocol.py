"""
https://modelcontextprotocol.io/specification/2025-06-18
https://modelcontextprotocol.io/specification/2025-06-18/schema
"""
import abc
import typing as ta

from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh


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


class ClientRequest(Message, lang.Abstract):
    pass


class ClientResult(Message, lang.Abstract):
    pass


class ServerRequest(Message, lang.Abstract):
    pass


class ServerResult(Message, lang.Abstract):
    pass


class Notification(Message, lang.Abstract):
    pass


#


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
class ClientCapabilities:
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
class InitializeRequest(ClientRequest):
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
class InitializeResult(ClientResult, WithMeta):
    json_rpc_method_name: ta.ClassVar[str] = 'initialize'

    server_info: Implementation
    protocol_version: str
    capabilities: ServerCapabilities


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class InitializedNotification(Notification):
    json_rpc_method_name: ta.ClassVar[str] = 'initialized'


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
class Tool(lang.Final):
    name: str
    title: str | None = None

    description: str | None = None

    annotations: ToolAnnotations | None = None

    input_schema: ta.Any
    output_schema: ta.Any | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ListToolsRequest(ClientRequest):
    json_rpc_method_name: ta.ClassVar[str] = 'tools/list'

    cursor: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ListToolsResult(ClientResult, WithMeta):
    json_rpc_method_name: ta.ClassVar[str] = 'tools/list'

    tools: ta.Sequence[Tool]
    next_cursor: str | None = None


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
class CallToolRequest(ClientRequest):
    json_rpc_method_name: ta.ClassVar[str] = 'tools/call'

    name: str
    arguments: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class CallToolResult(ClientResult, WithMeta):
    json_rpc_method_name: ta.ClassVar[str] = 'tools/call'

    content: ta.Sequence[ContentBlock]
    is_error: bool | None = None
    structured_content: ta.Mapping[str, ta.Any] | None = None


##


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class PingRequest(ClientRequest, WithMeta):
    json_rpc_method_name: ta.ClassVar[str] = 'ping'


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class PingResult(ClientResult):
    json_rpc_method_name: ta.ClassVar[str] = 'ping'


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
