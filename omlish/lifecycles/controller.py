import typing as ta

from .. import check
from .. import lang
from .base import AsyncLifecycle
from .base import Lifecycle
from .listeners import AsyncLifecycleListener
from .listeners import LifecycleListener
from .states import LifecycleState
from .states import LifecycleStates
from .transitions import LifecycleTransition
from .transitions import LifecycleTransitions


##


@ta.final
class LifecycleController(Lifecycle, lang.Final):
    def __init__(
            self,
            controlled: Lifecycle,
            *,
            lock: lang.DefaultLockable = None,
    ) -> None:
        super().__init__()

        self._controlled: Lifecycle = check.isinstance(controlled, Lifecycle)
        self._lock = lang.default_lock(lock, None)

        self._state = LifecycleStates.NEW
        self._listeners: list[LifecycleListener] = []

    __repr__ = lang.attr_ops(lambda o: (o.controlled, o.state)).repr

    #

    @property
    def controlled(self) -> Lifecycle:
        return self._controlled

    @property
    def state(self) -> LifecycleState:
        return self._state

    def add_listener(self, listener: LifecycleListener) -> ta.Self:
        self._listeners.append(check.isinstance(listener, LifecycleListener))
        return self

    #

    def _set_state(self, state: LifecycleState) -> None:
        self._state = state
        self._controlled.lifecycle_state(state)

    def _advance(
            self,
            transition: LifecycleTransition,
            controlled_fn: ta.Callable[[], None],
            pre_listener_fn: ta.Callable[[LifecycleListener], ta.Callable[[Lifecycle], None]] | None = None,
            post_listener_fn: ta.Callable[[LifecycleListener], ta.Callable[[Lifecycle], None]] | None = None,
    ) -> None:
        with self._lock():
            if pre_listener_fn is not None:
                for listener in self._listeners:
                    pre_listener_fn(listener)(self._controlled)

            check.state(self._state in transition.old)
            self._set_state(transition.new_intermediate)

            try:
                controlled_fn()
            except Exception:
                self._set_state(transition.new_failed)
                raise

            self._set_state(transition.new_succeeded)

            if post_listener_fn is not None:
                for listener in self._listeners:
                    post_listener_fn(listener)(self._controlled)

    ##

    @ta.override
    def lifecycle_construct(self) -> None:
        self._advance(
            LifecycleTransitions.CONSTRUCT,
            self._controlled.lifecycle_construct,
        )

    @ta.override
    def lifecycle_start(self) -> None:
        self._advance(
            LifecycleTransitions.START,
            self._controlled.lifecycle_start,
            lambda l: l.on_starting,
            lambda l: l.on_started,
        )

    @ta.override
    def lifecycle_stop(self) -> None:
        self._advance(
            LifecycleTransitions.STOP,
            self._controlled.lifecycle_stop,
            lambda l: l.on_stopping,
            lambda l: l.on_stopped,
        )

    @ta.override
    def lifecycle_destroy(self) -> None:
        self._advance(
            LifecycleTransitions.DESTROY,
            self._controlled.lifecycle_destroy,
        )


#


@ta.final
class AsyncLifecycleController(AsyncLifecycle, lang.Final):
    def __init__(
            self,
            controlled: AsyncLifecycle,
            *,
            lock: lang.DefaultAsyncLockable = None,
    ) -> None:
        super().__init__()

        self._controlled: AsyncLifecycle = check.isinstance(controlled, AsyncLifecycle)
        self._lock = lang.default_async_lock(lock, None)

        self._state = LifecycleStates.NEW
        self._listeners: list[AsyncLifecycleListener] = []

    __repr__ = lang.attr_ops(lambda o: (o.controlled, o.state)).repr

    #

    @property
    def controlled(self) -> AsyncLifecycle:
        return self._controlled

    @property
    def state(self) -> LifecycleState:
        return self._state

    def add_listener(self, listener: AsyncLifecycleListener) -> ta.Self:
        self._listeners.append(check.isinstance(listener, AsyncLifecycleListener))
        return self

    #

    async def _set_state(self, state: LifecycleState) -> None:
        self._state = state
        await self._controlled.lifecycle_state(state)

    async def _advance(
            self,
            transition: LifecycleTransition,
            controlled_fn: ta.Callable[[], ta.Awaitable[None]],
            pre_listener_fn: ta.Callable[[AsyncLifecycleListener], ta.Callable[[AsyncLifecycle], ta.Awaitable[None]]] | None = None,  # noqa
            post_listener_fn: ta.Callable[[AsyncLifecycleListener], ta.Callable[[AsyncLifecycle], ta.Awaitable[None]]] | None = None,  # noqa
    ) -> None:
        async with self._lock():
            if pre_listener_fn is not None:
                for listener in self._listeners:
                    await pre_listener_fn(listener)(self._controlled)

            check.state(self._state in transition.old)
            await self._set_state(transition.new_intermediate)

            try:
                await controlled_fn()
            except Exception:
                await self._set_state(transition.new_failed)
                raise

            await self._set_state(transition.new_succeeded)

            if post_listener_fn is not None:
                for listener in self._listeners:
                    await post_listener_fn(listener)(self._controlled)

    ##

    @ta.override
    async def lifecycle_construct(self) -> None:
        await self._advance(
            LifecycleTransitions.CONSTRUCT,
            self._controlled.lifecycle_construct,
        )

    @ta.override
    async def lifecycle_start(self) -> None:
        await self._advance(
            LifecycleTransitions.START,
            self._controlled.lifecycle_start,
            lambda l: l.on_starting,
            lambda l: l.on_started,
        )

    @ta.override
    async def lifecycle_stop(self) -> None:
        await self._advance(
            LifecycleTransitions.STOP,
            self._controlled.lifecycle_stop,
            lambda l: l.on_stopping,
            lambda l: l.on_stopped,
        )

    @ta.override
    async def lifecycle_destroy(self) -> None:
        await self._advance(
            LifecycleTransitions.DESTROY,
            self._controlled.lifecycle_destroy,
        )


#


AnyLifecycleController: ta.TypeAlias = LifecycleController | AsyncLifecycleController

ANY_LIFECYCLE_CONTROLLER_TYPES: tuple[type[LifecycleController | AsyncLifecycleController], ...] = (LifecycleController, AsyncLifecycleController)  # noqa
