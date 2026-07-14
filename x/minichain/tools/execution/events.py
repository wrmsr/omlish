from omcore import dataclasses as dc
from omcore import lang
from omcore import marshal as msh

from ...events.types import Event
from ...tools.types import ToolUse
from .execution import ToolUseExecution
from .execution import ToolUseResult


##


@dc.dataclass(frozen=True)
@msh.update_field_options('tue', no_marshal=True, no_unmarshal=True)
class ToolUseEvent(Event, lang.Final):
    use: ToolUse

    _: dc.KW_ONLY

    tue: ToolUseExecution | None = None


@dc.dataclass(frozen=True)
@msh.update_field_options('tue', no_marshal=True, no_unmarshal=True)
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
