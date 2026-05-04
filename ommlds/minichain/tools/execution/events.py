from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from ...events.types import Event
from .execution import ToolUseExecution
from .execution import ToolUseResult


##


@dc.dataclass(frozen=True)
class ToolUseEvent(Event, lang.Final):
    tue: ToolUseExecution


@dc.dataclass(frozen=True)
class ToolUseResultEvent(Event, lang.Final):
    tue: ToolUseExecution
    tur: ToolUseResult


##


@msh.register_global_lazy_init
def _setup_marshal(cfgs: msh.ConfigRegistry) -> None:
    cfgs.update(Event, *[msh.OpenPolymorphismImpl(et) for et in [
        ToolUseEvent,
        ToolUseResultEvent,
    ]])
