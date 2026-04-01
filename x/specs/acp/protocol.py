# @omlish-generated
# ruff: noqa: UP007
import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh


##


def _set_class_marshal_options(cls):
    msh.update_object_options(
        cls,
        field_naming=msh.Naming.LOW_CAMEL,
        field_defaults=msh.FieldOptions(
            omit_if=lang.is_none,
        ),
    )
    return cls


##


class ContentBlock(lang.Abstract, lang.Sealed):
    pass


class RequestPermissionOutcome(lang.Abstract, lang.Sealed):
    pass


class SessionConfigOption(lang.Abstract, lang.Sealed):
    pass


class SessionUpdate(lang.Abstract, lang.Sealed):
    pass


class ToolCallContent(lang.Abstract, lang.Sealed):
    pass


##


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class AgentCapabilities(lang.Final):
    load_session: bool = False
    mcp_capabilities: ta.Optional['McpCapabilities'] = None
    prompt_capabilities: ta.Optional['PromptCapabilities'] = None
    session_capabilities: ta.Optional['SessionCapabilities'] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class AgentNotification(lang.Final):
    method: str
    params: ta.Optional[ta.Any] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class AgentRequest(lang.Final):
    id: 'RequestId'
    method: str
    params: ta.Optional[ta.Any] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class Annotations(lang.Final):
    audience: ta.Optional[ta.Sequence['Role']] = None
    last_modified: ta.Optional[str] = None
    priority: ta.Optional[float] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class AudioContent(lang.Final):
    data: str
    mime_type: str
    annotations: ta.Optional['Annotations'] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class AuthMethodAgent(lang.Final):
    id: str
    name: str
    description: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class AuthenticateRequest(lang.Final):
    method_id: str
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class AuthenticateResponse(lang.Final):
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class AvailableCommand(lang.Final):
    description: str
    name: str
    input: ta.Optional['AvailableCommandInput'] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class AvailableCommandsUpdate(lang.Final):
    available_commands: ta.Sequence['AvailableCommand']
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class BlobResourceContents(lang.Final):
    blob: str
    uri: str
    mime_type: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class CancelNotification(lang.Final):
    session_id: 'SessionId'
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ClientCapabilities(lang.Final):
    fs: ta.Optional['FileSystemCapabilities'] = None
    terminal: bool = False
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ClientNotification(lang.Final):
    method: str
    params: ta.Optional[ta.Any] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ClientRequest(lang.Final):
    id: 'RequestId'
    method: str
    params: ta.Optional[ta.Any] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ConfigOptionUpdate(lang.Final):
    config_options: ta.Sequence['SessionConfigOption']
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class Content(lang.Final):
    content: 'ContentBlock'
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ContentChunk(lang.Final):
    content: 'ContentBlock'
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class CreateTerminalRequest(lang.Final):
    command: str
    session_id: 'SessionId'
    args: ta.Optional[ta.Sequence[str]] = None
    cwd: ta.Optional[str] = None
    env: ta.Optional[ta.Sequence['EnvVariable']] = None
    output_byte_limit: ta.Optional[int] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class CreateTerminalResponse(lang.Final):
    terminal_id: str
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class CurrentModeUpdate(lang.Final):
    current_mode_id: 'SessionModeId'
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class Diff(lang.Final):
    new_text: str
    path: str
    old_text: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class EmbeddedResource(lang.Final):
    resource: 'EmbeddedResourceResource'
    annotations: ta.Optional['Annotations'] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class EnvVariable(lang.Final):
    name: str
    value: str
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class Error(lang.Final):
    code: 'ErrorCode'
    message: str
    data: ta.Optional[ta.Any] = None


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class FileSystemCapabilities(lang.Final):
    read_text_file: bool = False
    write_text_file: bool = False
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class HttpHeader(lang.Final):
    name: str
    value: str
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ImageContent(lang.Final):
    data: str
    mime_type: str
    annotations: ta.Optional['Annotations'] = None
    uri: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class Implementation(lang.Final):
    name: str
    version: str
    title: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class InitializeRequest(lang.Final):
    protocol_version: 'ProtocolVersion'
    client_capabilities: ta.Optional['ClientCapabilities'] = None
    client_info: ta.Optional['Implementation'] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class InitializeResponse(lang.Final):
    protocol_version: 'ProtocolVersion'
    agent_capabilities: ta.Optional['AgentCapabilities'] = None
    agent_info: ta.Optional['Implementation'] = None
    auth_methods: ta.Optional[ta.Sequence['AuthMethod']] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class KillTerminalRequest(lang.Final):
    session_id: 'SessionId'
    terminal_id: str
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class KillTerminalResponse(lang.Final):
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ListSessionsRequest(lang.Final):
    cursor: ta.Optional[str] = None
    cwd: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ListSessionsResponse(lang.Final):
    sessions: ta.Sequence['SessionInfo']
    next_cursor: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class LoadSessionRequest(lang.Final):
    cwd: str
    mcp_servers: ta.Sequence['McpServer']
    session_id: 'SessionId'
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class LoadSessionResponse(lang.Final):
    config_options: ta.Optional[ta.Sequence['SessionConfigOption']] = None
    modes: ta.Optional['SessionModeState'] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class McpCapabilities(lang.Final):
    http: bool = False
    sse: bool = False
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class McpServerHttp(lang.Final):
    headers: ta.Sequence['HttpHeader']
    name: str
    url: str
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class McpServerSse(lang.Final):
    headers: ta.Sequence['HttpHeader']
    name: str
    url: str
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class McpServerStdio(lang.Final):
    args: ta.Sequence[str]
    command: str
    env: ta.Sequence['EnvVariable']
    name: str
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class NewSessionRequest(lang.Final):
    cwd: str
    mcp_servers: ta.Sequence['McpServer']
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class NewSessionResponse(lang.Final):
    session_id: 'SessionId'
    config_options: ta.Optional[ta.Sequence['SessionConfigOption']] = None
    modes: ta.Optional['SessionModeState'] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class PermissionOption(lang.Final):
    kind: 'PermissionOptionKind'
    name: str
    option_id: 'PermissionOptionId'
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class Plan(lang.Final):
    entries: ta.Sequence['PlanEntry']
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class PlanEntry(lang.Final):
    content: str
    priority: 'PlanEntryPriority'
    status: 'PlanEntryStatus'
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class PromptCapabilities(lang.Final):
    audio: bool = False
    embedded_context: bool = False
    image: bool = False
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class PromptRequest(lang.Final):
    prompt: ta.Sequence['ContentBlock']
    session_id: 'SessionId'
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class PromptResponse(lang.Final):
    stop_reason: 'StopReason'
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ReadTextFileRequest(lang.Final):
    path: str
    session_id: 'SessionId'
    limit: ta.Optional[int] = None
    line: ta.Optional[int] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ReadTextFileResponse(lang.Final):
    content: str
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ReleaseTerminalRequest(lang.Final):
    session_id: 'SessionId'
    terminal_id: str
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ReleaseTerminalResponse(lang.Final):
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class RequestPermissionRequest(lang.Final):
    options: ta.Sequence['PermissionOption']
    session_id: 'SessionId'
    tool_call: 'ToolCallUpdate'
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class RequestPermissionResponse(lang.Final):
    outcome: 'RequestPermissionOutcome'
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ResourceLink(lang.Final):
    name: str
    uri: str
    annotations: ta.Optional['Annotations'] = None
    description: ta.Optional[str] = None
    mime_type: ta.Optional[str] = None
    size: ta.Optional[int] = None
    title: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SelectedPermissionOutcome(lang.Final):
    option_id: 'PermissionOptionId'
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SessionCapabilities(lang.Final):
    list: ta.Optional['SessionListCapabilities'] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SessionConfigSelect(lang.Final):
    current_value: 'SessionConfigValueId'
    options: 'SessionConfigSelectOptions'


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SessionConfigSelectGroup(lang.Final):
    group: 'SessionConfigGroupId'
    name: str
    options: ta.Sequence['SessionConfigSelectOption']
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SessionConfigSelectOption(lang.Final):
    name: str
    value: 'SessionConfigValueId'
    description: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SessionInfo(lang.Final):
    cwd: str
    session_id: 'SessionId'
    title: ta.Optional[str] = None
    updated_at: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SessionInfoUpdate(lang.Final):
    title: ta.Optional[str] = None
    updated_at: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SessionListCapabilities(lang.Final):
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SessionMode(lang.Final):
    id: 'SessionModeId'
    name: str
    description: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SessionModeState(lang.Final):
    available_modes: ta.Sequence['SessionMode']
    current_mode_id: 'SessionModeId'
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SessionNotification(lang.Final):
    session_id: 'SessionId'
    update: 'SessionUpdate'
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SetSessionConfigOptionRequest(lang.Final):
    config_id: 'SessionConfigId'
    session_id: 'SessionId'
    value: 'SessionConfigValueId'
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SetSessionConfigOptionResponse(lang.Final):
    config_options: ta.Sequence['SessionConfigOption']
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SetSessionModeRequest(lang.Final):
    mode_id: 'SessionModeId'
    session_id: 'SessionId'
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SetSessionModeResponse(lang.Final):
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class Terminal(lang.Final):
    terminal_id: str
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class TerminalExitStatus(lang.Final):
    exit_code: ta.Optional[int] = None
    signal: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class TerminalOutputRequest(lang.Final):
    session_id: 'SessionId'
    terminal_id: str
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class TerminalOutputResponse(lang.Final):
    output: str
    truncated: bool
    exit_status: ta.Optional['TerminalExitStatus'] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class TextContent(lang.Final):
    text: str
    annotations: ta.Optional['Annotations'] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class TextResourceContents(lang.Final):
    text: str
    uri: str
    mime_type: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ToolCall(lang.Final):
    title: str
    tool_call_id: 'ToolCallId'
    content: ta.Optional[ta.Sequence['ToolCallContent']] = None
    kind: ta.Optional['ToolKind'] = None
    locations: ta.Optional[ta.Sequence['ToolCallLocation']] = None
    raw_input: ta.Optional[ta.Any] = None
    raw_output: ta.Optional[ta.Any] = None
    status: ta.Optional['ToolCallStatus'] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ToolCallLocation(lang.Final):
    path: str
    line: ta.Optional[int] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ToolCallUpdate(lang.Final):
    tool_call_id: 'ToolCallId'
    content: ta.Optional[ta.Sequence['ToolCallContent']] = None
    kind: ta.Optional['ToolKind'] = None
    locations: ta.Optional[ta.Sequence['ToolCallLocation']] = None
    raw_input: ta.Optional[ta.Any] = None
    raw_output: ta.Optional[ta.Any] = None
    status: ta.Optional['ToolCallStatus'] = None
    title: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class UnstructuredCommandInput(lang.Final):
    hint: str
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class WaitForTerminalExitRequest(lang.Final):
    session_id: 'SessionId'
    terminal_id: str
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class WaitForTerminalExitResponse(lang.Final):
    exit_code: ta.Optional[int] = None
    signal: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class WriteTextFileRequest(lang.Final):
    content: str
    path: str
    session_id: 'SessionId'
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class WriteTextFileResponse(lang.Final):
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


##


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ExtNotification(lang.Final):
    pass


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ExtRequest(lang.Final):
    pass


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ExtResponse(lang.Final):
    pass


##


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class AgentMessageChunkSessionUpdate(SessionUpdate, lang.Final):
    content: 'ContentBlock'
    session_update: ta.Literal['agent_message_chunk'] = dc.xfield('agent_message_chunk', repr=False)
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class AgentThoughtChunkSessionUpdate(SessionUpdate, lang.Final):
    content: 'ContentBlock'
    session_update: ta.Literal['agent_thought_chunk'] = dc.xfield('agent_thought_chunk', repr=False)
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class AudioContentBlock(ContentBlock, lang.Final):
    data: str
    mime_type: str
    type: ta.Literal['audio'] = dc.xfield('audio', repr=False)
    annotations: ta.Optional['Annotations'] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class AvailableCommandsUpdateSessionUpdate(SessionUpdate, lang.Final):
    available_commands: ta.Sequence['AvailableCommand']
    session_update: ta.Literal['available_commands_update'] = dc.xfield('available_commands_update', repr=False)
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class CancelledRequestPermissionOutcome(RequestPermissionOutcome, lang.Final):
    outcome: ta.Literal['cancelled'] = dc.xfield('cancelled', repr=False)


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ConfigOptionUpdateSessionUpdate(SessionUpdate, lang.Final):
    config_options: ta.Sequence['SessionConfigOption']
    session_update: ta.Literal['config_option_update'] = dc.xfield('config_option_update', repr=False)
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ContentToolCallContent(ToolCallContent, lang.Final):
    content: 'ContentBlock'
    type: ta.Literal['content'] = dc.xfield('content', repr=False)
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class CurrentModeUpdateSessionUpdate(SessionUpdate, lang.Final):
    current_mode_id: 'SessionModeId'
    session_update: ta.Literal['current_mode_update'] = dc.xfield('current_mode_update', repr=False)
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class DiffToolCallContent(ToolCallContent, lang.Final):
    new_text: str
    path: str
    type: ta.Literal['diff'] = dc.xfield('diff', repr=False)
    old_text: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ImageContentBlock(ContentBlock, lang.Final):
    data: str
    mime_type: str
    type: ta.Literal['image'] = dc.xfield('image', repr=False)
    annotations: ta.Optional['Annotations'] = None
    uri: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class PlanSessionUpdate(SessionUpdate, lang.Final):
    entries: ta.Sequence['PlanEntry']
    session_update: ta.Literal['plan'] = dc.xfield('plan', repr=False)
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ResourceContentBlock(ContentBlock, lang.Final):
    resource: 'EmbeddedResourceResource'
    type: ta.Literal['resource'] = dc.xfield('resource', repr=False)
    annotations: ta.Optional['Annotations'] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ResourceLinkContentBlock(ContentBlock, lang.Final):
    name: str
    uri: str
    type: ta.Literal['resource_link'] = dc.xfield('resource_link', repr=False)
    annotations: ta.Optional['Annotations'] = None
    description: ta.Optional[str] = None
    mime_type: ta.Optional[str] = None
    size: ta.Optional[int] = None
    title: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SelectSessionConfigOption(SessionConfigOption, lang.Final):
    current_value: 'SessionConfigValueId'
    options: 'SessionConfigSelectOptions'
    type: ta.Literal['select'] = dc.xfield('select', repr=False)


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SelectedRequestPermissionOutcome(RequestPermissionOutcome, lang.Final):
    option_id: 'PermissionOptionId'
    outcome: ta.Literal['selected'] = dc.xfield('selected', repr=False)
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class SessionInfoUpdateSessionUpdate(SessionUpdate, lang.Final):
    session_update: ta.Literal['session_info_update'] = dc.xfield('session_info_update', repr=False)
    title: ta.Optional[str] = None
    updated_at: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class TerminalToolCallContent(ToolCallContent, lang.Final):
    terminal_id: str
    type: ta.Literal['terminal'] = dc.xfield('terminal', repr=False)
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class TextContentBlock(ContentBlock, lang.Final):
    text: str
    type: ta.Literal['text'] = dc.xfield('text', repr=False)
    annotations: ta.Optional['Annotations'] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ToolCallSessionUpdate(SessionUpdate, lang.Final):
    title: str
    tool_call_id: 'ToolCallId'
    session_update: ta.Literal['tool_call'] = dc.xfield('tool_call', repr=False)
    content: ta.Optional[ta.Sequence['ToolCallContent']] = None
    kind: ta.Optional['ToolKind'] = None
    locations: ta.Optional[ta.Sequence['ToolCallLocation']] = None
    raw_input: ta.Optional[ta.Any] = None
    raw_output: ta.Optional[ta.Any] = None
    status: ta.Optional['ToolCallStatus'] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class ToolCallUpdateSessionUpdate(SessionUpdate, lang.Final):
    tool_call_id: 'ToolCallId'
    session_update: ta.Literal['tool_call_update'] = dc.xfield('tool_call_update', repr=False)
    content: ta.Optional[ta.Sequence['ToolCallContent']] = None
    kind: ta.Optional['ToolKind'] = None
    locations: ta.Optional[ta.Sequence['ToolCallLocation']] = None
    raw_input: ta.Optional[ta.Any] = None
    raw_output: ta.Optional[ta.Any] = None
    status: ta.Optional['ToolCallStatus'] = None
    title: ta.Optional[str] = None
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class UserMessageChunkSessionUpdate(SessionUpdate, lang.Final):
    content: 'ContentBlock'
    session_update: ta.Literal['user_message_chunk'] = dc.xfield('user_message_chunk', repr=False)
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = dc.field(
        default=None,
        metadata={msh.FieldOptions: msh.FieldOptions(name='_meta')},
    )


##


AuthMethod: ta.TypeAlias = AuthMethodAgent


AvailableCommandInput: ta.TypeAlias = UnstructuredCommandInput


ErrorCode: ta.TypeAlias = int


PermissionOptionId: ta.TypeAlias = str


ProtocolVersion: ta.TypeAlias = int


SessionConfigGroupId: ta.TypeAlias = str


SessionConfigId: ta.TypeAlias = str


SessionConfigOptionCategory: ta.TypeAlias = str


SessionConfigValueId: ta.TypeAlias = str


SessionId: ta.TypeAlias = str


SessionModeId: ta.TypeAlias = str


ToolCallId: ta.TypeAlias = str


##


PermissionOptionKind: ta.TypeAlias = ta.Literal['allow_once', 'allow_always', 'reject_once', 'reject_always']


PlanEntryPriority: ta.TypeAlias = ta.Literal['high', 'medium', 'low']


PlanEntryStatus: ta.TypeAlias = ta.Literal['pending', 'in_progress', 'completed']


Role: ta.TypeAlias = ta.Literal['assistant', 'user']


StopReason: ta.TypeAlias = ta.Literal['end_turn', 'max_tokens', 'max_turn_requests', 'refusal', 'cancelled']


ToolCallStatus: ta.TypeAlias = ta.Literal['pending', 'in_progress', 'completed', 'failed']


ToolKind: ta.TypeAlias = ta.Literal[
    'read',
    'edit',
    'delete',
    'move',
    'search',
    'execute',
    'think',
    'fetch',
    'switch_mode',
    'other',
]


##


AgentResponse: ta.TypeAlias = ta.Any


ClientResponse: ta.TypeAlias = ta.Any


EmbeddedResourceResource: ta.TypeAlias = ta.Any


McpServer: ta.TypeAlias = ta.Any


RequestId: ta.TypeAlias = ta.Union[None, int, str]


SessionConfigSelectOptions: ta.TypeAlias = ta.Any


##


@lang.static_init
def _install_marshaling() -> None:
    msh.install_standard_factories(*msh.standard_polymorphism_factories(
        msh.polymorphism_from_subclasses(
            ContentBlock,
            naming=msh.Naming.SNAKE,
            strip_suffix=msh.AutoStripSuffix,
        ),
        msh.FieldTypeTagging('type'),
    ))

    msh.install_standard_factories(*msh.standard_polymorphism_factories(
        msh.polymorphism_from_subclasses(
            RequestPermissionOutcome,
            naming=msh.Naming.SNAKE,
            strip_suffix=msh.AutoStripSuffix,
        ),
        msh.FieldTypeTagging('outcome'),
    ))

    msh.install_standard_factories(*msh.standard_polymorphism_factories(
        msh.polymorphism_from_subclasses(
            SessionConfigOption,
            naming=msh.Naming.SNAKE,
            strip_suffix=msh.AutoStripSuffix,
        ),
        msh.FieldTypeTagging('type'),
    ))

    msh.install_standard_factories(*msh.standard_polymorphism_factories(
        msh.polymorphism_from_subclasses(
            SessionUpdate,
            naming=msh.Naming.SNAKE,
            strip_suffix=msh.AutoStripSuffix,
        ),
        msh.FieldTypeTagging('sessionUpdate'),
    ))

    msh.install_standard_factories(*msh.standard_polymorphism_factories(
        msh.polymorphism_from_subclasses(
            ToolCallContent,
            naming=msh.Naming.SNAKE,
            strip_suffix=msh.AutoStripSuffix,
        ),
        msh.FieldTypeTagging('type'),
    ))
