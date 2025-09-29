"""
https://docs.claude.com/en/api/messages
"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh


##


def _set_class_marshal_options(cls):
    msh.update_object_metadata(
        cls,
        field_defaults=msh.FieldMetadata(
            options=msh.FieldOptions(
                omit_if=lang.is_none,
            ),
        ),
    )

    return cls


##


class Content(lang.Abstract, lang.Sealed):
    class CacheControl(lang.Abstract, lang.Sealed):
        """https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching"""

    @dc.dataclass(frozen=True)
    class EphemeralCacheControl(CacheControl):
        pass


@dc.dataclass(frozen=True)
@_set_class_marshal_options
class Text(Content):
    text: str

    _: dc.KW_ONLY

    cache_control: Content.CacheControl | None = dc.xfield(default=None, repr_fn=dc.opt_repr)


@dc.dataclass(frozen=True)
@_set_class_marshal_options
class ToolUse(Content):
    id: str
    name: str
    input: ta.Mapping[str, ta.Any]

    _: dc.KW_ONLY

    cache_control: Content.CacheControl | None = dc.xfield(default=None, repr_fn=dc.opt_repr)


@dc.dataclass(frozen=True)
@_set_class_marshal_options
class ToolResult(Content):
    tool_use_id: str
    content: str


##


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class CacheCreation:
    ephemeral_5m_input_tokens: int | None = None
    ephemeral_1h_input_tokens: int | None = None


##


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class Usage:
    input_tokens: int | None = None
    output_tokens: int | None = None

    cache_creation_input_tokens: int | None = None
    cache_read_input_tokens: int | None = None
    cache_creation: CacheCreation | None = None

    service_tier: str | None = None


##


@dc.dataclass(frozen=True, kw_only=True)
@_set_class_marshal_options
class Message:
    id: str | None = None

    role: ta.Literal['user', 'assistant']

    model: str | None = None

    content: str | ta.Sequence[Content] | None = None

    stop_reason: str | None = None
    stop_sequence: str | None = None

    usage: Usage | None = None


##


@dc.dataclass(frozen=True)
@_set_class_marshal_options
class ToolSpec:
    name: str
    description: str
    input_schema: ta.Any


##


@dc.dataclass(frozen=True)
@_set_class_marshal_options
class MessagesRequest:
    model: str

    messages: ta.Sequence[Message]

    _: dc.KW_ONLY

    system: str | ta.Sequence[Content] | None = None

    tools: ta.Sequence[ToolSpec] | None = None

    temperature: float | None = None
    max_tokens: int | None = None

    stream: bool | None = None

    betas: ta.Sequence[str] | None = None
    metadata: ta.Mapping[str, str] | None = None
