import functools

from .. import check
from .. import dataclasses as dc
from .. import lang


##


class LifecycleStateError(Exception):
    pass


@dc.dataclass(frozen=True, eq=False)
@functools.total_ordering
class LifecycleState(lang.Final):
    name: str
    phase: int
    is_failed: bool

    def __lt__(self, other):
        return self.phase < check.isinstance(other, LifecycleState).phase

    def __le__(self, other):
        return self.phase <= check.isinstance(other, LifecycleState).phase


class LifecycleStates(lang.Namespace):
    NEW = LifecycleState('NEW', 0, False)

    CONSTRUCTING = LifecycleState('CONSTRUCTING', 1, False)
    FAILED_CONSTRUCTING = LifecycleState('FAILED_CONSTRUCTING', 2, True)
    CONSTRUCTED = LifecycleState('CONSTRUCTED', 3, False)

    STARTING = LifecycleState('STARTING', 4, False)
    FAILED_STARTING = LifecycleState('FAILED_STARTING', 5, True)
    STARTED = LifecycleState('STARTED', 6, False)

    STOPPING = LifecycleState('STOPPING', 7, False)
    FAILED_STOPPING = LifecycleState('FAILED_STOPPING', 8, True)
    STOPPED = LifecycleState('STOPPED', 9, False)

    DESTROYING = LifecycleState('DESTROYING', 10, False)
    FAILED_DESTROYING = LifecycleState('FAILED_DESTROYING', 11, True)
    DESTROYED = LifecycleState('DESTROYED', 12, False)
