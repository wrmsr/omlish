import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh


##


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class GenerateContentRequest:
    """https://ai.google.dev/api/generate-content#request-body"""

    @dc.dataclass(frozen=True, kw_only=True)
    @msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
    class Content(lang.Final):
        @dc.dataclass(frozen=True, kw_only=True)
        @msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
        class Part(lang.Final):
            text: str

        parts: ta.Sequence[Part]
        role: ta.Literal['user', 'model']

    contents: ta.Sequence[Content]


@dc.dataclass(frozen=True, kw_only=True)
@msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
class GenerateContentResponse:
    """https://ai.google.dev/api/generate-content#v1beta.GenerateContentResponse"""

    @dc.dataclass(frozen=True, kw_only=True)
    @msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
    class Candidate(lang.Final):
        @dc.dataclass(frozen=True, kw_only=True)
        @msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
        class Content(lang.Final):
            @dc.dataclass(frozen=True, kw_only=True)
            @msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
            class Part(lang.Final):
                text: str

            parts: ta.Sequence[Part]
            role: ta.Literal['user', 'model']

        content: Content
        finish_reason: ta.Literal['STOP'] | None
        index: int

    candidates: ta.Sequence[Candidate]

    @dc.dataclass(frozen=True, kw_only=True)
    @msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
    class UsageMetadata(lang.Final):
        prompt_token_count: int
        candidates_token_count: int
        total_token_count: int
        thoughts_token_count: int

        @dc.dataclass(frozen=True, kw_only=True)
        @msh.update_object_metadata(field_naming=msh.Naming.LOW_CAMEL)
        class ModalityTokenCount:
            modality: str
            token_count: int

        prompt_tokens_details: ta.Sequence[ModalityTokenCount]

    usage_metadata: UsageMetadata

    model_version: str

    response_id: str
