import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh


##


class Content(lang.Abstract, lang.Sealed):
    class CacheControl(lang.Abstract, lang.Sealed):
        """https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching"""

    @dc.dataclass(frozen=True)
    class EphemeralCacheControl(CacheControl):
        pass


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['cache_control'], omit_if=lang.is_none)
class Text(Content):
    text: str

    _: dc.KW_ONLY

    cache_control: Content.CacheControl | None = dc.xfield(default=None, repr_fn=dc.opt_repr)


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['cache_control'], omit_if=lang.is_none)
class ToolUse(Content):
    id: str
    name: str
    input: ta.Mapping[str, ta.Any]

    _: dc.KW_ONLY

    cache_control: Content.CacheControl | None = dc.xfield(default=None, repr_fn=dc.opt_repr)


@dc.dataclass(frozen=True)
class ToolResult(Content):
    tool_use_id: str
    content: str


##


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_object_metadata(field_defaults=msh.FieldMetadata(options=msh.FieldOptions(omit_if=lang.is_none)))
class CacheCreation:
    ephemeral_5m_input_tokens: int | None = None
    ephemeral_1h_input_tokens: int | None = None


##


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_object_metadata(field_defaults=msh.FieldMetadata(options=msh.FieldOptions(omit_if=lang.is_none)))
class Usage:
    input_tokens: int | None = None
    output_tokens: int | None = None

    cache_creation_input_tokens: int | None = None
    cache_read_input_tokens: int | None = None
    cache_creation: CacheCreation | None = None

    service_tier: str | None = None


##


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_object_metadata(field_defaults=msh.FieldMetadata(options=msh.FieldOptions(omit_if=lang.is_none)))
class Message:
    id: str | None = None

    role: str | None = None

    model: str | None = None

    content: ta.Sequence[Content] | None = None

    stop_reason: str | None = None
    stop_sequence: str | None = None

    usage: Usage | None = None


##


@dc.dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: ta.Any


##


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_defaults=msh.FieldMetadata(options=msh.FieldOptions(omit_if=lang.is_none)))
class MessagesRequest:
    model: str

    messages: ta.Sequence[Message]

    _: dc.KW_ONLY

    system: ta.Sequence[Content] | None = None

    tools: ta.Sequence[ToolSpec] | None = None

    temperature: float | None = None
    max_tokens: int | None = None

    stream: bool | None = None

    betas: ta.Sequence[str] | None = None
    metadata: ta.Mapping[str, str] | None = None
