"""
TODO:
 - replace outright with omcore.lifecycles? or does this become 'awaiting_user' / 'awaiting_ai' / 'awaiting_tool' ...
"""
import enum
import typing as ta

from omcore import dataclasses as dc


##


class Phase(enum.Enum):
    NEW = enum.auto()

    STARTING = enum.auto()
    STARTED = enum.auto()

    STOPPING = enum.auto()
    STOPPED = enum.auto()


##


@dc.dataclass(frozen=True)
class PhaseCallback:
    phase: Phase = dc.xfield(validate=lambda v: v != Phase.NEW)
    fn: ta.Callable[[], ta.Awaitable[None]] = dc.xfield()


PhaseCallbacks = ta.NewType('PhaseCallbacks', ta.Sequence[PhaseCallback])
