import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from ...content.types import Content
from ...stream.services import StreamOptions
from ...types import Option
from ...types import Output
from ..types import ChatOptions


msh.register_global_module_import('._marshal', __package__)


##


class ChatStreamOption(Option, lang.Abstract, lang.PackageSealed):
    pass


ChatStreamOptions: ta.TypeAlias = ChatStreamOption | StreamOptions | ChatOptions


##


class ChatStreamOutput(Output, lang.Abstract, lang.PackageSealed):
    pass


ChatStreamOutputs: ta.TypeAlias = ChatStreamOutput


##


@dc.dataclass(frozen=True)
class AiDelta(lang.Sealed, lang.Abstract):
    pass


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
