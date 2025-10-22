import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from ...content.types import Content
from ...stream.services import StreamOptions
from ...types import Option
from ...types import Output
from ..choices.types import ChatChoicesOptions


msh.register_global_module_import('._marshal', __package__)


##


class ChatChoicesStreamOption(Option, lang.Abstract, lang.PackageSealed):
    pass


ChatChoicesStreamOptions: ta.TypeAlias = ChatChoicesStreamOption | StreamOptions | ChatChoicesOptions


##


class ChatChoicesStreamOutput(Output, lang.Abstract, lang.PackageSealed):
    pass


ChatChoicesStreamOutputs: ta.TypeAlias = ChatChoicesStreamOutput


##


@dc.dataclass(frozen=True)
class AiChoiceDelta(lang.Sealed, lang.Abstract):
    pass


#


@dc.dataclass(frozen=True)
class ContentAiChoiceDelta(AiChoiceDelta, lang.Final):
    c: Content


#


@dc.dataclass(frozen=True, kw_only=True)
class AnyToolUseAiChoiceDelta(AiChoiceDelta, lang.Abstract):
    id: str | None = None
    name: str | None = None


@dc.dataclass(frozen=True, kw_only=True)
class ToolUseAiChoiceDelta(AnyToolUseAiChoiceDelta, lang.Final):
    args: ta.Mapping[str, ta.Any] | None = None


@dc.dataclass(frozen=True, kw_only=True)
class PartialToolUseAiChoiceDelta(AnyToolUseAiChoiceDelta, lang.Final):
    raw_args: ta.Any | None = None


#


@dc.dataclass(frozen=True)
class AiChoiceDeltas(lang.Final):
    deltas: ta.Sequence[AiChoiceDelta]


@dc.dataclass(frozen=True)
class AiChoicesDeltas(lang.Final):
    choices: ta.Sequence[AiChoiceDeltas]
