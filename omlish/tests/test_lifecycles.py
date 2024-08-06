import functools
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import defs
from omlish import lang


LifecycleT = ta.TypeVar('LifecycleT', bound='Lifecycle')
LifecycleCallback: ta.TypeAlias = ta.Callable[[LifecycleT], None]


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


class LifecycleStates(lang.Namespace):
    NEW = LifecycleState('NEW', 0, False)

    CONSTRUCTING = LifecycleState('CONSTRUCTING', 1, False)
    FAILED_CONSTRUCTING = LifecycleState('FAILED_CONSTRUCTING', 2, True)
    CONSTRUCTED = LifecycleState('CONSTRUCTED', 3, False)

    STARTING = LifecycleState('STARTING', 5, False)
    FAILED_STARTING = LifecycleState('FAILED_STARTING', 6, True)
    STARTED = LifecycleState('STARTED', 7, False)

    STOPPING = LifecycleState('STOPPING', 8, False)
    FAILED_STOPPING = LifecycleState('FAILED_STOPPING', 9, True)
    STOPPED = LifecycleState('STOPPED', 10, False)

    DESTROYING = LifecycleState('DESTROYING', 11, False)
    FAILED_DESTROYING = LifecycleState('FAILED_DESTROYING', 12, True)
    DESTROYED = LifecycleState('DESTROYED', 13, False)


class Lifecycle:

    def lifecycle_construct(self) -> None:
        pass

    def lifecycle_start(self) -> None:
        pass

    def lifecycle_stop(self) -> None:
        pass

    def lifecycle_destroy(self) -> None:
        pass


@dc.dataclass(frozen=True, kw_only=True)
class CallbackLifecycle(Lifecycle, lang.Final, ta.Generic[LifecycleT]):
    on_construct: LifecycleCallback['CallbackLifecycle[LifecycleT]'] | None = None
    on_start: LifecycleCallback['CallbackLifecycle[LifecycleT]'] | None = None
    on_stop: LifecycleCallback['CallbackLifecycle[LifecycleT]'] | None = None
    on_destroy: LifecycleCallback['CallbackLifecycle[LifecycleT]'] | None = None

    def lifecycle_construct(self) -> None:
        if self.on_construct is not None:
            self.on_construct(self)

    def lifecycle_start(self) -> None:
        if self.on_start is not None:
            self.on_start(self)

    def lifecycle_stop(self) -> None:
        if self.on_stop is not None:
            self.on_stop(self)

    def lifecycle_destroy(self) -> None:
        if self.on_destroy is not None:
            self.on_destroy(self)


class LifecycleListener(ta.Generic[LifecycleT]):

    def on_starting(self, obj: LifecycleT) -> None:
        pass

    def on_started(self, obj: LifecycleT) -> None:
        pass

    def on_stopping(self, obj: LifecycleT) -> None:
        pass

    def on_stopped(self, obj: LifecycleT) -> None:
        pass


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

    def lifecycle_construct(self) -> None:
        self._advance(
            LifecycleTransitions.CONSTRUCT,
            self._lifecycle.lifecycle_construct,
        )

    def lifecycle_start(self) -> None:
        self._advance(
            LifecycleTransitions.START,
            self._lifecycle.lifecycle_start,
            lambda l: l.on_starting,
            lambda l: l.on_started,
        )

    def lifecycle_stop(self) -> None:
        self._advance(
            LifecycleTransitions.STOP,
            self._lifecycle.lifecycle_stop,
            lambda l: l.on_stopping,
            lambda l: l.on_stopped,
        )

    def lifecycle_destroy(self) -> None:
        self._advance(
            LifecycleTransitions.DESTROY,
            self._lifecycle.lifecycle_destroy,
        )
