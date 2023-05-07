"""
TODO:
 - track history? exceptions? tracebacks?
"""
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang


T = ta.TypeVar('T')
LifecycleT = ta.TypeVar('LifecycleT', bound='Lifecycle')
LifecycleCallback = ta.Callable[[LifecycleT], None]


class LifecycleStateException(Exception):
    pass


@dc.dataclass(frozen=True, eq=False)
class LifecycleState(lang.Sealed):
    name: str
    phase: int
    is_failed: bool


class LifecycleStates(lang.ValueEnum):
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


class CallbackLifecycle(Lifecycle, lang.Final, ta.Generic[LifecycleT]):

    def __init__(
            self,
            *,
            construct: ta.Optional[LifecycleCallback[LifecycleT]] = None,
            start: ta.Optional[LifecycleCallback[LifecycleT]] = None,
            stop: ta.Optional[LifecycleCallback[LifecycleT]] = None,
            destroy: ta.Optional[LifecycleCallback[LifecycleT]] = None,
    ) -> None:
        super().__init__()

        self._construct = check.callable(construct) if construct is not None else None
        self._start = check.callable(start) if construct is not None else None
        self._stop = check.callable(stop) if construct is not None else None
        self._destroy = check.callable(destroy) if construct is not None else None

    def lifecycle_construct(self) -> None:
        if self._construct is not None:
            self._construct(self)

    def lifecycle_start(self) -> None:
        if self._start is not None:
            self._start(self)

    def lifecycle_stop(self) -> None:
        if self._stop is not None:
            self._stop(self)

    def lifecycle_destroy(self) -> None:
        if self._destroy is not None:
            self._destroy(self)


class LifecycleListener(ta.Generic[LifecycleT]):

    def on_starting(self, obj: LifecycleT) -> None:
        pass

    def on_started(self, obj: LifecycleT) -> None:
        pass

    def on_stopping(self, obj: LifecycleT) -> None:
        pass

    def on_stopped(self, obj: LifecycleT) -> None:
        pass


class CallbackLifecycleListener(LifecycleListener[LifecycleT], lang.Final):

    def __init__(
            self,
            *,
            on_starting: LifecycleCallback[LifecycleT] = None,
            on_started: LifecycleCallback[LifecycleT] = None,
            on_stopping: LifecycleCallback[LifecycleT] = None,
            on_stopped: LifecycleCallback[LifecycleT] = None,
    ) -> None:
        super().__init__()

        self._on_starting = check.callable(on_starting) if on_starting is not None else None
        self._on_started = check.callable(on_started) if on_starting is not None else None
        self._on_stopping = check.callable(on_stopping) if on_starting is not None else None
        self._on_stopped = check.callable(on_stopped) if on_starting is not None else None

    def on_starting(self, obj: T) -> None:
        if self._on_starting is not None:
            self._on_starting(obj)

    def on_started(self, obj: T) -> None:
        if self._on_started is not None:
            self._on_started(obj)

    def on_stopping(self, obj: T) -> None:
        if self._on_stopping is not None:
            self._on_stopping(obj)

    def on_stopped(self, obj: T) -> None:
        if self._on_stopped is not None:
            self._on_stopped(obj)
