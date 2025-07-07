import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh


##


class Content(lang.Abstract, lang.Sealed):
    class CacheControl(lang.Abstract, lang.Sealed):
        pass

    class EphemeralCacheControl(CacheControl):
        pass


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['cache_control'], omit_if=lang.is_none)
class TextContent(Content):
    text: str

    _: dc.KW_ONLY

    cache_control: Content.CacheControl | None = None


#


@dc.dataclass(frozen=True)
class Message:
    role: str

    content: ta.Sequence[Content]


#


@dc.dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: ta.Any


#


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_defaults=msh.FieldMetadata(options=msh.FieldOptions(omit_if=lang.is_none)))
class MessagesRequest:
    model: str

    messages: ta.Sequence[Message]

    _: dc.KW_ONLY

    system: ta.Sequence[TextContent] | None = None

    tools: ta.Sequence[ToolSpec] | None = None

    betas: ta.Sequence[str] | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    metadata: ta.Mapping[str, str] | None = None
