import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from ...events.types import Event
from ...tools.types import ToolUse
from .execution import ToolUseExecution
from .execution import ToolUseResult


##


_MARSHAL_FIELD_CONST_NONE_KWARGS: ta.Mapping[str, ta.Any] = dict(
    marshal_via=msh.MarshalVia(msh.ConstMarshaler(None)),
    unmarshal_via=msh.UnmarshalVia(msh.ConstUnmarshaler(None)),
)


#


@dc.dataclass(frozen=True)
@msh.update_field_options('tue', **_MARSHAL_FIELD_CONST_NONE_KWARGS)
class ToolUseEvent(Event, lang.Final):
    use: ToolUse

    _: dc.KW_ONLY

    tue: ToolUseExecution | None = None


@dc.dataclass(frozen=True)
@msh.update_field_options('tue', **_MARSHAL_FIELD_CONST_NONE_KWARGS)
class ToolUseResultEvent(Event, lang.Final):
    use: ToolUse
    tur: ToolUseResult

    _: dc.KW_ONLY

    tue: ToolUseExecution | None = None


##


@msh.register_global_lazy_init
def _setup_marshal(cfgs: msh.ConfigRegistry) -> None:
    cfgs.update(Event, *[msh.OpenPolymorphismImpl(et) for et in [
        ToolUseEvent,
        ToolUseResultEvent,
    ]])
