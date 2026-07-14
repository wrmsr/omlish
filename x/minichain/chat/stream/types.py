import typing as ta

from omcore import check
from omcore import dataclasses as dc
from omcore import lang
from omcore import marshal as msh
from omcore import typedvalues as tv

from ..._typedvalues import _tv_field_metadata
from ...chat.generations import ChatGeneration
from ...content.content import Content
from ...metadata import MetadataContainerDataclass
from ...services import StreamOptions
from ...types import Option
from ...types import Output
from ..types import ChatOptions
from .metadata import AiDeltaMetadatas


##


class ChatStreamOption(Option, lang.Abstract, lang.PackageSealed):
    pass


ChatStreamOptions: ta.TypeAlias = ChatStreamOption | StreamOptions | ChatOptions


##


class ChatStreamOutput(Output, lang.Abstract, lang.PackageSealed):
    pass


ChatStreamOutputs: ta.TypeAlias = ChatStreamOutput


##


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class ChatStreamResult:
    g: ChatGeneration

    #

    _outputs: ta.Sequence[ChatStreamOutputs] = dc.field(
        default=(),
        metadata=_tv_field_metadata(
            ChatStreamOutputs,
            marshal_name='outputs',
        ),
    )

    @property
    def outputs(self) -> tv.TypedValues[ChatStreamOutputs]:
        return check.isinstance(self._outputs, tv.TypedValues)


##


@dc.dataclass(frozen=True)
@msh.set_polymorphic_from_subclasses(naming=msh.Naming.SNAKE)
class AiDelta(MetadataContainerDataclass[AiDeltaMetadatas], lang.Abstract, lang.Sealed):
    _metadata: ta.Sequence[AiDeltaMetadatas] = dc.field(default=(), kw_only=True, repr=False)

    MetadataContainerDataclass._configure_metadata_field(_metadata, AiDeltaMetadatas)  # noqa


AiDeltas: ta.TypeAlias = ta.Sequence[AiDelta]


#


@dc.dataclass(frozen=True)
class ContentAiDelta(AiDelta, lang.Final):
    c: Content


#


@dc.dataclass(frozen=True, kw_only=True)
class AnyToolUseAiDelta(AiDelta, lang.Abstract):
    id: str | None = None
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class ToolUseAiDelta(AnyToolUseAiDelta, lang.Final):
    args: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class PartialToolUseAiDelta(AnyToolUseAiDelta, lang.Final):
    raw_args: ta.Any | None = None
    index: int | None = None


#


@dc.dataclass(frozen=True)
class ThinkingAiDelta(AiDelta, lang.Final):
    c: str
