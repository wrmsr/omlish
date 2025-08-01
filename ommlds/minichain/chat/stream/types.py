import operator
import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from ...content.types import Content
from ...stream.services import StreamOptions
from ...types import Option
from ...types import Output
from ..choices.types import ChatChoicesOptions


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
class ToolExecRequestDelta(lang.Final):
    index: int | None = None
    id: str | None = None
    name: str | None = None
    args: str | None = None


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['tool_exec_requests'], omit_if=operator.not_)
class AiMessageDelta(lang.Final):
    c: Content | None = dc.xfield(None, repr_fn=dc.opt_repr)

    tool_exec_requests: ta.Sequence[ToolExecRequestDelta] | None = dc.xfield(None, repr_fn=dc.opt_repr)


@dc.dataclass(frozen=True)
class AiChoiceDelta(lang.Final):
    m: AiMessageDelta


AiChoiceDeltas: ta.TypeAlias = ta.Sequence[AiChoiceDelta]
