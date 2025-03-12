import typing as ta

from .. import check
from .. import defs
from .. import lang
from .base import Lifecycle
from .states import LifecycleState
from .states import LifecycleStates
from .transitions import LifecycleTransition
from .transitions import LifecycleTransitions


LifecycleT = ta.TypeVar('LifecycleT', bound='Lifecycle')


class LifecycleListener(ta.Generic[LifecycleT]):
    def on_starting(self, obj: LifecycleT) -> None:
        pass

    def on_started(self, obj: LifecycleT) -> None:
        pass

    def on_stopping(self, obj: LifecycleT) -> None:
        pass

    def on_stopped(self, obj: LifecycleT) -> None:
        pass


class LifecycleController(Lifecycle, ta.Generic[LifecycleT]):
    def __init__(
            self,
            lifecycle: LifecycleT,
            *,
            lock: lang.DefaultLockable = None,
    ) -> None:
        super().__init__()

        self._lifecycle: LifecycleT = check.isinstance(lifecycle, Lifecycle)  # type: ignore
        self._lock = lang.default_lock(lock, False)

        self._state = LifecycleStates.NEW
        self._listeners: list[LifecycleListener[LifecycleT]] = []

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
            transition: LifecycleTransition,
            lifecycle_fn: ta.Callable[[], None],
            pre_listener_fn: ta.Callable[[LifecycleListener[LifecycleT]], ta.Callable[[LifecycleT], None]] | None = None,  # noqa
            post_listener_fn: ta.Callable[[LifecycleListener[LifecycleT]], ta.Callable[[LifecycleT], None]] | None = None,  # noqa
    ) -> None:
        with self._lock():
            if pre_listener_fn is not None:
                for listener in self._listeners:
                    pre_listener_fn(listener)(self._lifecycle)
            check.state(self._state in transition.old)
            self._state = transition.new_intermediate
            try:
                lifecycle_fn()
            except Exception:
                self._state = transition.new_failed
                raise
            self._state = transition.new_succeeded
            if post_listener_fn is not None:
                for listener in self._listeners:
                    post_listener_fn(listener)(self._lifecycle)

    ##

    @ta.override
    def lifecycle_construct(self) -> None:
        self._advance(
            LifecycleTransitions.CONSTRUCT,
            self._lifecycle.lifecycle_construct,
        )

    @ta.override
    def lifecycle_start(self) -> None:
        self._advance(
            LifecycleTransitions.START,
            self._lifecycle.lifecycle_start,
            lambda l: l.on_starting,
            lambda l: l.on_started,
        )

    @ta.override
    def lifecycle_stop(self) -> None:
        self._advance(
            LifecycleTransitions.STOP,
            self._lifecycle.lifecycle_stop,
            lambda l: l.on_stopping,
            lambda l: l.on_stopped,
        )

    @ta.override
    def lifecycle_destroy(self) -> None:
        self._advance(
            LifecycleTransitions.DESTROY,
            self._lifecycle.lifecycle_destroy,
        )
