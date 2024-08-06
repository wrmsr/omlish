from .. import check
from .. import dataclasses as dc
from .. import lang
from .states import LifecycleState
from .states import LifecycleStates


@dc.dataclass(frozen=True)
class LifecycleTransition(lang.Final):
    old: frozenset[LifecycleState]
    new_intermediate: LifecycleState
    new_failed: LifecycleState
    new_succeeded: LifecycleState

    def __post_init__(self) -> None:
        dc.maybe_post_init(super())
        check.unique([*self.old, self.new_intermediate, self.new_succeeded, self.new_failed])
        check.arg(all(self.new_intermediate > o for o in self.old))
        check.arg(self.new_failed > self.new_intermediate)
        check.arg(self.new_succeeded > self.new_failed)


class LifecycleTransitions(lang.Namespace):
    CONSTRUCT = LifecycleTransition(
        frozenset([LifecycleStates.NEW]),
        LifecycleStates.CONSTRUCTING,
        LifecycleStates.FAILED_CONSTRUCTING,
        LifecycleStates.CONSTRUCTED,
    )

    START = LifecycleTransition(
        frozenset([LifecycleStates.CONSTRUCTED]),
        LifecycleStates.STARTING,
        LifecycleStates.FAILED_STARTING,
        LifecycleStates.STARTED,
    )

    STOP = LifecycleTransition(
        frozenset([LifecycleStates.STARTED]),
        LifecycleStates.STOPPING,
        LifecycleStates.FAILED_STOPPING,
        LifecycleStates.STOPPED,
    )

    DESTROY = LifecycleTransition(
        frozenset([
            LifecycleStates.NEW,

            LifecycleStates.CONSTRUCTING,
            LifecycleStates.FAILED_CONSTRUCTING,
            LifecycleStates.CONSTRUCTED,

            LifecycleStates.STARTING,
            LifecycleStates.FAILED_STARTING,
            LifecycleStates.STARTED,

            LifecycleStates.STOPPING,
            LifecycleStates.FAILED_STOPPING,
            LifecycleStates.STOPPED,
        ]),
        LifecycleStates.DESTROYING,
        LifecycleStates.FAILED_DESTROYING,
        LifecycleStates.DESTROYED,
    )
