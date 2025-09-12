import abc
import typing as ta

from .. import check
from .. import lang
from .base import AnyLifecycle  # noqa
from .base import Lifecycle  # noqa
from .states import LifecycleState
from .states import LifecycleStates
from .transitions import LifecycleTransition
from .transitions import LifecycleTransitions


R = ta.TypeVar('R')

AnyLifecycleT = ta.TypeVar('AnyLifecycleT', bound='AnyLifecycle')

LifecycleT = ta.TypeVar('LifecycleT', bound='Lifecycle')


##


class AnyLifecycleListener(ta.Generic[AnyLifecycleT, R]):
    def on_starting(self, obj: AnyLifecycleT) -> R | None:
        return None

    def on_started(self, obj: AnyLifecycleT) -> R | None:
        return None

    def on_stopping(self, obj: AnyLifecycleT) -> R | None:
        return None

    def on_stopped(self, obj: AnyLifecycleT) -> R | None:
        return None


class AnyLifecycleController(AnyLifecycle[R], lang.Abstract, ta.Generic[AnyLifecycleT, R]):
    def __init__(
            self,
            lifecycle: AnyLifecycleT,
    ) -> None:
        super().__init__()

        self._lifecycle: AnyLifecycleT = check.isinstance(lifecycle, AnyLifecycle)  # type: ignore

        self._state = LifecycleStates.NEW
        self._listeners: list[AnyLifecycleListener[AnyLifecycleT, R]] = []

    __repr__ = lang.attr_ops(lambda o: (o.lifecycle, o.state)).repr

    @property
    def lifecycle(self) -> AnyLifecycleT:
        return self._lifecycle

    @property
    def state(self) -> LifecycleState:
        return self._state

    def add_listener(self, listener: AnyLifecycleListener[AnyLifecycleT, R]) -> ta.Self:
        self._listeners.append(check.isinstance(listener, AnyLifecycleListener))
        return self

    @abc.abstractmethod
    def _advance(
            self,
            transition: LifecycleTransition,
            lifecycle_fn: ta.Callable[[], R | None],
            pre_listener_fn: ta.Callable[
                [AnyLifecycleListener[AnyLifecycleT, R]],
                ta.Callable[[AnyLifecycleT], R | None],
            ] | None = None,
            post_listener_fn: ta.Callable[
                [AnyLifecycleListener[AnyLifecycleT, R]],
                ta.Callable[[AnyLifecycleT], R | None],
            ] | None = None,
    ) -> R | None:
        raise NotImplementedError

    ##

    @ta.override
    def lifecycle_construct(self) -> R | None:
        return self._advance(
            LifecycleTransitions.CONSTRUCT,
            self._lifecycle.lifecycle_construct,
        )

    @ta.override
    def lifecycle_start(self) -> R | None:
        return self._advance(
            LifecycleTransitions.START,
            self._lifecycle.lifecycle_start,
            lambda l: l.on_starting,
            lambda l: l.on_started,
        )

    @ta.override
    def lifecycle_stop(self) -> R | None:
        return self._advance(
            LifecycleTransitions.STOP,
            self._lifecycle.lifecycle_stop,
            lambda l: l.on_stopping,
            lambda l: l.on_stopped,
        )

    @ta.override
    def lifecycle_destroy(self) -> R | None:
        return self._advance(
            LifecycleTransitions.DESTROY,
            self._lifecycle.lifecycle_destroy,
        )


##


LifecycleListener: ta.TypeAlias = AnyLifecycleListener[LifecycleT, None]


class LifecycleController(
    AnyLifecycleController[LifecycleT, None],
    Lifecycle,
    ta.Generic[LifecycleT],
):
    def __init__(
            self,
            lifecycle: LifecycleT,
            *,
            lock: lang.DefaultLockable = None,
    ) -> None:
        super().__init__(lifecycle)

        self._lock = lang.default_lock(lock, False)

    def _advance(
            self,
            transition: LifecycleTransition,
            lifecycle_fn: ta.Callable[[], None],
            pre_listener_fn: ta.Callable[
                [LifecycleListener[LifecycleT]],
                ta.Callable[[LifecycleT], None],
            ] | None = None,
            post_listener_fn: ta.Callable[
                [LifecycleListener[LifecycleT]],
                ta.Callable[[LifecycleT], None],
            ] | None = None,
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
