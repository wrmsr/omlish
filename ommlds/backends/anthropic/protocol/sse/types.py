import dataclasses as dc
import typing as ta

from omlish import lang
from omlish import marshal as msh


##


@dc.dataclass(frozen=True)
class AnthropicSseMessage:
    id: str
    role: str
    model: str

    class Content(lang.Abstract):
        pass

    @dc.dataclass(frozen=True)
    class Text(Content):
        text: str

    @dc.dataclass(frozen=True)
    class ToolUse(Content):
        id: str
        name: str
        input: ta.Mapping[str, ta.Any]

    content: ta.Sequence[Content] = ()

    stop_reason: str | None = None
    stop_sequence: str | None = None

    @dc.dataclass(frozen=True, kw_only=True)
    @msh.update_object_metadata(field_defaults=msh.FieldMetadata(options=msh.FieldOptions(omit_if=lang.is_none)))
    class Usage:
        input_tokens: int | None = None
        output_tokens: int | None = None

        cache_creation_input_tokens: int | None = None
        cache_read_input_tokens: int | None = None

        service_tier: str | None = None

    usage: Usage | None = None
