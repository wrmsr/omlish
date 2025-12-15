import typing as ta

from .. import check
from .. import lang
from .base import AsyncLifecycle
from .base import AsyncLifecycleListener
from .base import Lifecycle
from .base import LifecycleListener
from .states import LifecycleState
from .states import LifecycleStates
from .transitions import LifecycleTransition
from .transitions import LifecycleTransitions


##


class LifecycleController(Lifecycle, lang.Final):
    def __init__(
            self,
            lifecycle: Lifecycle,
            *,
            lock: lang.DefaultLockable = None,
    ) -> None:
        super().__init__()

        self._lifecycle: Lifecycle = check.isinstance(lifecycle, Lifecycle)
        self._lock = lang.default_lock(lock, None)

        self._state = LifecycleStates.NEW
        self._listeners: list[LifecycleListener] = []

    __repr__ = lang.attr_ops(lambda o: (o.lifecycle, o.state)).repr

    @property
    def lifecycle(self) -> Lifecycle:
        return self._lifecycle

    @property
    def state(self) -> LifecycleState:
        return self._state

    def add_listener(self, listener: LifecycleListener) -> ta.Self:
        self._listeners.append(check.isinstance(listener, LifecycleListener))
        return self

    #

    def _advance(
            self,
            transition: LifecycleTransition,
            lifecycle_fn: ta.Callable[[], None],
            pre_listener_fn: ta.Callable[[LifecycleListener], ta.Callable[[Lifecycle], None]] | None = None,
            post_listener_fn: ta.Callable[[LifecycleListener], ta.Callable[[Lifecycle], None]] | None = None,
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


##


class AsyncLifecycleController(AsyncLifecycle, lang.Final):
    def __init__(
            self,
            lifecycle: AsyncLifecycle,
            *,
            lock: lang.DefaultAsyncLockable = None,
    ) -> None:
        super().__init__()

        self._lifecycle: AsyncLifecycle = check.isinstance(lifecycle, AsyncLifecycle)
        self._lock = lang.default_async_lock(lock, None)

        self._state = LifecycleStates.NEW
        self._listeners: list[AsyncLifecycleListener] = []

    __repr__ = lang.attr_ops(lambda o: (o.lifecycle, o.state)).repr

    @property
    def lifecycle(self) -> AsyncLifecycle:
        return self._lifecycle

    @property
    def state(self) -> LifecycleState:
        return self._state

    def add_listener(self, listener: AsyncLifecycleListener) -> ta.Self:
        self._listeners.append(check.isinstance(listener, AsyncLifecycleListener))
        return self

    #

    async def _advance(
            self,
            transition: LifecycleTransition,
            lifecycle_fn: ta.Callable[[], ta.Awaitable[None]],
            pre_listener_fn: ta.Callable[[AsyncLifecycleListener], ta.Callable[[AsyncLifecycle], ta.Awaitable[None]]] | None = None,  # noqa
            post_listener_fn: ta.Callable[[AsyncLifecycleListener], ta.Callable[[AsyncLifecycle], ta.Awaitable[None]]] | None = None,  # noqa
    ) -> None:
        async with self._lock():
            if pre_listener_fn is not None:
                for listener in self._listeners:
                    await pre_listener_fn(listener)(self._lifecycle)

            check.state(self._state in transition.old)
            self._state = transition.new_intermediate

            try:
                await lifecycle_fn()
            except Exception:
                self._state = transition.new_failed
                raise

            self._state = transition.new_succeeded

            if post_listener_fn is not None:
                for listener in self._listeners:
                    await post_listener_fn(listener)(self._lifecycle)

    ##

    @ta.override
    async def lifecycle_construct(self) -> None:
        await self._advance(
            LifecycleTransitions.CONSTRUCT,
            self._lifecycle.lifecycle_construct,
        )

    @ta.override
    async def lifecycle_start(self) -> None:
        await self._advance(
            LifecycleTransitions.START,
            self._lifecycle.lifecycle_start,
            lambda l: l.on_starting,
            lambda l: l.on_started,
        )

    @ta.override
    async def lifecycle_stop(self) -> None:
        await self._advance(
            LifecycleTransitions.STOP,
            self._lifecycle.lifecycle_stop,
            lambda l: l.on_stopping,
            lambda l: l.on_stopped,
        )

    @ta.override
    async def lifecycle_destroy(self) -> None:
        await self._advance(
            LifecycleTransitions.DESTROY,
            self._lifecycle.lifecycle_destroy,
        )
