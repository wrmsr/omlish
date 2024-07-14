import typing as ta

from .. import check
from .. import defs
from .. import lang
from .types import Lifecycle
from .types import LifecycleListener
from .types import LifecycleState
from .types import LifecycleStates
from .types import LifecycleT


class LifecycleController(Lifecycle, ta.Generic[LifecycleT]):

    def __init__(
            self,
            lifecycle: LifecycleT,
            *,
            lock: lang.DefaultLockable = None,
    ) -> None:
        super().__init__()

        self._lifecycle = check.isinstance(lifecycle, Lifecycle)
        self._lock = lang.default_lock(lock, True)

        self._state = LifecycleStates.NEW
        self._listeners: ta.List[LifecycleListener[LifecycleT]] = []

    defs.repr('lifecycle', 'state')

    @property
    def lifecycle(self) -> LifecycleT:
        return self._lifecycle

    @property
    def state(self) -> LifecycleState:
        return self._state

    def add_listener(self, listener: LifecycleListener[LifecycleT]) -> 'LifecycleController':
        self._listeners.append(check.isinstance(listener, LifecycleListener))
        return self

    def _advance(
            self,
            old: ta.Set[LifecycleState],
            new_intermediate: LifecycleState,
            new_failed: LifecycleState,
            new_succeeded: LifecycleState,
            lifecycle_fn: ta.Callable[[], None],
            pre_listener_fn: ta.Callable[[LifecycleListener[LifecycleT]], ta.Callable[[LifecycleT], None]] = None,
            post_listener_fn: ta.Callable[[LifecycleListener[LifecycleT]], ta.Callable[[LifecycleT], None]] = None,
    ) -> None:
        check.unique(list(old) + [new_intermediate, new_succeeded, new_failed])
        check.arg(all(new_intermediate.phase > o.phase for o in old))
        check.arg(new_failed.phase > new_intermediate.phase)
        check.arg(new_succeeded.phase > new_failed.phase)
        with self._lock():
            if pre_listener_fn is not None:
                for listener in self._listeners:
                    pre_listener_fn(listener)(self._lifecycle)
            check.state(self._state in old)
            self._state = new_intermediate
            try:
                lifecycle_fn()
            except Exception:
                self._state = new_failed
                raise
            self._state = new_succeeded
            if post_listener_fn is not None:
                for listener in self._listeners:
                    post_listener_fn(listener)(self._lifecycle)

    def lifecycle_construct(self) -> None:
        self._advance(
            {LifecycleStates.NEW},
            LifecycleStates.CONSTRUCTING,
            LifecycleStates.FAILED_CONSTRUCTING,
            LifecycleStates.CONSTRUCTED,
            self._lifecycle.lifecycle_construct,
        )

    def lifecycle_start(self) -> None:
        self._advance(
            {LifecycleStates.CONSTRUCTED},
            LifecycleStates.STARTING,
            LifecycleStates.FAILED_STARTING,
            LifecycleStates.STARTED,
            self._lifecycle.lifecycle_start,
            lambda l: l.on_starting,
            lambda l: l.on_started,
        )

    def lifecycle_stop(self) -> None:
        self._advance(
            {LifecycleStates.STARTED},
            LifecycleStates.STOPPING,
            LifecycleStates.FAILED_STOPPING,
            LifecycleStates.STOPPED,
            self._lifecycle.lifecycle_stop,
            lambda l: l.on_stopping,
            lambda l: l.on_stopped,
        )

    def lifecycle_destroy(self) -> None:
        self._advance(
            {
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
            },
            LifecycleStates.DESTROYING,
            LifecycleStates.FAILED_DESTROYING,
            LifecycleStates.DESTROYED,
            self._lifecycle.lifecycle_destroy,
        )
