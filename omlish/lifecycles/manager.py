import typing as ta

from .. import check
from .. import collections as col
from .. import dataclasses as dc
from .. import lang
from .base import AnyLifecycle
from .base import AsyncLifecycle
from .base import Lifecycle
from .base import as_async_lifecycle
from .controller import AnyLifecycleController
from .controller import AsyncLifecycleController
from .controller import LifecycleController
from .managed import AsyncLifecycleManaged
from .managed import LifecycleManaged
from .states import LifecycleState
from .states import LifecycleStateError
from .states import LifecycleStates


LifecycleControllerT = ta.TypeVar('LifecycleControllerT', bound=AnyLifecycleController)


##


@dc.dataclass(frozen=True, eq=False)
class LifecycleManagerEntry(lang.Final, ta.Generic[LifecycleControllerT]):
    controller: LifecycleControllerT

    dependencies: ta.MutableSet['LifecycleManagerEntry'] = dc.field(default_factory=set)
    dependents: ta.MutableSet['LifecycleManagerEntry'] = dc.field(default_factory=set)


#


@ta.final
class _InnerLifecycleManager(AsyncLifecycleManaged, lang.Final):
    def __init__(
            self,
            get_state: ta.Callable[[], LifecycleState],
    ) -> None:
        super().__init__()

        self._get_state = get_state

        self._entries_by_lifecycle: ta.MutableMapping[AnyLifecycle, LifecycleManagerEntry] = col.IdentityKeyDict()

    #

    def _get_or_make_controller(self, lifecycle: AnyLifecycle) -> AnyLifecycleController:
        if isinstance(lifecycle, (LifecycleController, AsyncLifecycleController)):
            return lifecycle

        elif isinstance(lifecycle, Lifecycle):
            return LifecycleController(lifecycle)

        elif isinstance(lifecycle, AsyncLifecycle):
            return AsyncLifecycleController(lifecycle)

        else:
            raise TypeError(lifecycle)

    def _add_internal(self, lifecycle: AnyLifecycle, dependencies: ta.Iterable[AnyLifecycle]) -> LifecycleManagerEntry:
        check.state(self._get_state() < LifecycleStates.STOPPING and not self._get_state().is_failed)

        check.isinstance(lifecycle, (Lifecycle, AsyncLifecycle))
        try:
            entry = self._entries_by_lifecycle[lifecycle]
        except KeyError:
            controller = self._get_or_make_controller(lifecycle)
            entry = self._entries_by_lifecycle[lifecycle] = LifecycleManagerEntry(controller)

        for dep in dependencies:
            check.isinstance(dep, (Lifecycle, AsyncLifecycle))
            dep_entry = self._add_internal(dep, [])
            entry.dependencies.add(dep_entry)
            dep_entry.dependents.add(entry)

        return entry

    async def add(
            self,
            lifecycle: AnyLifecycle,
            dependencies: ta.Iterable[AnyLifecycle] = (),
    ) -> LifecycleManagerEntry:
        check.state(self._get_state() < LifecycleStates.STOPPING and not self._get_state().is_failed)

        entry = self._add_internal(lifecycle, dependencies)

        if self._get_state() >= LifecycleStates.CONSTRUCTING:
            async def rec(e):
                if e.controller.state < LifecycleStates.CONSTRUCTED:
                    for dep in e.dependencies:
                        await rec(dep)

                    await as_async_lifecycle(e.controller).lifecycle_construct()

            await rec(entry)

        if self._get_state() >= LifecycleStates.STARTING:
            async def rec(e):
                if e.controller.state < LifecycleStates.STARTED:
                    for dep in e.dependencies:
                        await rec(dep)

                    await as_async_lifecycle(e.controller).lifecycle_start()

            await rec(entry)

        return entry

    ##

    @ta.override
    async def _lifecycle_construct(self) -> None:
        async def rec(e: LifecycleManagerEntry) -> None:
            for dep in e.dependencies:
                await rec(dep)

            if e.controller.state.is_failed:
                raise LifecycleStateError(e.controller)

            if e.controller.state < LifecycleStates.CONSTRUCTED:
                await as_async_lifecycle(e.controller).lifecycle_construct()

        for entry in self._entries_by_lifecycle.values():
            await rec(entry)

    @ta.override
    async def _lifecycle_start(self) -> None:
        async def rec(e: LifecycleManagerEntry) -> None:
            for dep in e.dependencies:
                await rec(dep)

            if e.controller.state.is_failed:
                raise LifecycleStateError(e.controller)

            if e.controller.state < LifecycleStates.CONSTRUCTED:
                await as_async_lifecycle(e.controller).lifecycle_construct()

            if e.controller.state < LifecycleStates.STARTED:
                await as_async_lifecycle(e.controller).lifecycle_start()

        for entry in self._entries_by_lifecycle.values():
            await rec(entry)

    @ta.override
    async def _lifecycle_stop(self) -> None:
        async def rec(e: LifecycleManagerEntry) -> None:
            for dep in e.dependents:
                await rec(dep)

            if e.controller.state.is_failed:
                raise LifecycleStateError(e.controller)

            if e.controller.state is LifecycleStates.STARTED:
                await as_async_lifecycle(e.controller).lifecycle_stop()

        for entry in self._entries_by_lifecycle.values():
            await rec(entry)

    @ta.override
    async def _lifecycle_destroy(self) -> None:
        async def rec(e: LifecycleManagerEntry) -> None:
            for dep in e.dependents:
                await rec(dep)

            if e.controller.state < LifecycleStates.DESTROYED:
                await as_async_lifecycle(e.controller).lifecycle_destroy()

        for entry in self._entries_by_lifecycle.values():
            await rec(entry)


##


class LifecycleManager(LifecycleManaged, lang.Final):
    def __init__(
            self,
            *,
            lock: lang.DefaultLockable = None,
    ) -> None:
        super().__init__()

        self._lock = lang.default_lock(lock, None)

        self._inner = _InnerLifecycleManager(lambda: self._inner_controller.state)

        self._inner_controller = AsyncLifecycleController(
            self._inner._lifecycle,  # noqa
            lock=lambda: lang.SyncToAsyncContextManager(self._lock()),
        )

    #

    @property
    def state(self) -> LifecycleState:
        return self._inner_controller.state

    #

    def add(
            self,
            lifecycle: Lifecycle,
            dependencies: ta.Iterable[Lifecycle] = (),
    ) -> LifecycleManagerEntry[LifecycleController]:
        return lang.sync_await(self._inner.add(
            check.isinstance(lifecycle, Lifecycle),
            [check.isinstance(d, Lifecycle) for d in dependencies],
        ))

    #

    @ta.override
    def _lifecycle_construct(self) -> None:
        return lang.sync_await(self._inner_controller.lifecycle_construct())

    @ta.override
    def _lifecycle_start(self) -> None:
        return lang.sync_await(self._inner_controller.lifecycle_start())

    @ta.override
    def _lifecycle_stop(self) -> None:
        return lang.sync_await(self._inner_controller.lifecycle_stop())

    @ta.override
    def _lifecycle_destroy(self) -> None:
        return lang.sync_await(self._inner_controller.lifecycle_destroy())


#


class AsyncLifecycleManager(AsyncLifecycleManaged, lang.Final):
    def __init__(
            self,
            *,
            lock: lang.DefaultAsyncLockable = None,
    ) -> None:
        super().__init__()

        self._lock = lang.default_async_lock(lock, None)

        self._inner = _InnerLifecycleManager(lambda: self._inner_controller.state)

        self._inner_controller = AsyncLifecycleController(
            self._inner._lifecycle,  # noqa
            lock=self._lock,
        )

    #

    @property
    def state(self) -> LifecycleState:
        return self._inner_controller.state

    #

    async def add(
            self,
            lifecycle: AnyLifecycle,
            dependencies: ta.Iterable[AnyLifecycle] = (),
    ) -> LifecycleManagerEntry[AnyLifecycleController]:
        return await self._inner.add(
            lifecycle,
            dependencies,
        )

    #

    @ta.override
    async def _lifecycle_construct(self) -> None:
        return await self._inner_controller.lifecycle_construct()

    @ta.override
    async def _lifecycle_start(self) -> None:
        return await self._inner_controller.lifecycle_start()

    @ta.override
    async def _lifecycle_stop(self) -> None:
        return await self._inner_controller.lifecycle_stop()

    @ta.override
    async def _lifecycle_destroy(self) -> None:
        return await self._inner_controller.lifecycle_destroy()
