import typing as ta

from omlish import dataclasses as dc
from omlish import marshal as msh


##


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class InitializeParams:
    process_id: int | None
    root_uri: str | None
    capabilities: ta.Mapping[str, ta.Any]
    trace: str | None = 'off'


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class ServerCapabilities:
    text_document_sync: ta.Mapping[str, ta.Any] | None = None
    definition_provider: bool = False


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class InitializeResult:
    # capabilities: ServerCapabilities
    capabilities: ta.Mapping[str, ta.Any]


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class TextDocumentItem:
    uri: str
    language_id: str
    version: int
    text: str


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class DidOpenTextDocumentParams:
    text_document: TextDocumentItem


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class TextDocumentIdentifier:
    uri: str


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class Position:
    line: int
    character: int


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class TextDocumentPositionParams:
    text_document: TextDocumentIdentifier
    position: Position


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class Location:
    uri: str
    range: ta.Mapping[str, ta.Mapping[str, int]]  # { "start": {"line": int, "character": int}, "end": {...} }


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class DefinitionResponse:
    result: ta.Sequence[Location] | None


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class LogMessageParams:
    type: int  # 1 = Error, 2 = Warning, 3 = Info, 4 = Log
    message: str
