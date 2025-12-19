import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .states import LifecycleState


##


class Lifecycle(lang.Abstract):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        try:
            async_lifecycle_cls = AsyncLifecycle
        except NameError:
            pass
        else:
            check.not_issubclass(cls, async_lifecycle_cls)

    def lifecycle_state(self, state: LifecycleState) -> None:
        """
        This method is not intended for actual work - this is intended solely for safe bookkeeping. Only do real work in
        the explicit per-state methods.
        """

    def lifecycle_construct(self) -> None:
        pass

    def lifecycle_start(self) -> None:
        pass

    def lifecycle_stop(self) -> None:
        pass

    def lifecycle_destroy(self) -> None:
        pass


class AsyncLifecycle(lang.Abstract):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        check.not_issubclass(cls, Lifecycle)

    async def lifecycle_state(self, state: LifecycleState) -> None:
        """
        This method is not intended for actual work - this is intended solely for safe bookkeeping. Only do real work in
        the explicit per-state methods.
        """

    async def lifecycle_construct(self) -> None:
        pass

    async def lifecycle_start(self) -> None:
        pass

    async def lifecycle_stop(self) -> None:
        pass

    async def lifecycle_destroy(self) -> None:
        pass


AnyLifecycle: ta.TypeAlias = Lifecycle | AsyncLifecycle

ANY_LIFECYCLE_TYPES: tuple[type[Lifecycle | AsyncLifecycle], ...] = (Lifecycle, AsyncLifecycle)


##


@ta.final
@dc.dataclass(frozen=True)
class _SyncToAsyncLifecycle(AsyncLifecycle, lang.Final):
    lifecycle: Lifecycle

    async def lifecycle_state(self, state: LifecycleState) -> None:
        self.lifecycle.lifecycle_state(state)

    async def lifecycle_construct(self) -> None:
        self.lifecycle.lifecycle_construct()

    async def lifecycle_start(self) -> None:
        self.lifecycle.lifecycle_start()

    async def lifecycle_stop(self) -> None:
        self.lifecycle.lifecycle_stop()

    async def lifecycle_destroy(self) -> None:
        self.lifecycle.lifecycle_destroy()


def sync_to_async_lifecycle(lifecycle: Lifecycle) -> AsyncLifecycle:
    return _SyncToAsyncLifecycle(lifecycle)


def as_async_lifecycle(lifecycle: Lifecycle | AsyncLifecycle) -> AsyncLifecycle:
    if isinstance(lifecycle, Lifecycle):
        return sync_to_async_lifecycle(lifecycle)

    elif isinstance(lifecycle, AsyncLifecycle):
        return lifecycle

    else:
        raise TypeError(lifecycle)


@ta.final
@dc.dataclass(frozen=True)
class _AsyncToSyncLifecycle(Lifecycle, lang.Final):
    lifecycle: AsyncLifecycle

    def lifecycle_state(self, state: LifecycleState) -> None:
        lang.sync_await(self.lifecycle.lifecycle_state(state))

    def lifecycle_construct(self) -> None:
        lang.sync_await(self.lifecycle.lifecycle_construct())

    def lifecycle_start(self) -> None:
        lang.sync_await(self.lifecycle.lifecycle_start())

    def lifecycle_stop(self) -> None:
        lang.sync_await(self.lifecycle.lifecycle_stop())

    def lifecycle_destroy(self) -> None:
        lang.sync_await(self.lifecycle.lifecycle_destroy())


def async_to_sync_lifecycle(lifecycle: AsyncLifecycle) -> Lifecycle:
    return _AsyncToSyncLifecycle(lifecycle)


def as_sync_lifecycle(lifecycle: Lifecycle | AsyncLifecycle) -> Lifecycle:
    if isinstance(lifecycle, Lifecycle):
        return lifecycle

    elif isinstance(lifecycle, AsyncLifecycle):
        return async_to_sync_lifecycle(lifecycle)

    else:
        raise TypeError(lifecycle)


##


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class CallbackLifecycle(Lifecycle, lang.Final):
    on_state: ta.Callable[[LifecycleState], None] | None = None
    on_construct: ta.Callable[[], None] | None = None
    on_start: ta.Callable[[], None] | None = None
    on_stop: ta.Callable[[], None] | None = None
    on_destroy: ta.Callable[[], None] | None = None

    @ta.override
    def lifecycle_state(self, state: LifecycleState) -> None:
        if self.on_state is not None:
            self.on_state(state)

    @ta.override
    def lifecycle_construct(self) -> None:
        if self.on_construct is not None:
            self.on_construct()

    @ta.override
    def lifecycle_start(self) -> None:
        if self.on_start is not None:
            self.on_start()

    @ta.override
    def lifecycle_stop(self) -> None:
        if self.on_stop is not None:
            self.on_stop()

    @ta.override
    def lifecycle_destroy(self) -> None:
        if self.on_destroy is not None:
            self.on_destroy()


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class CallbackAsyncLifecycle(AsyncLifecycle, lang.Final):
    on_state: ta.Callable[[LifecycleState], ta.Awaitable[None]] | None = None
    on_construct: ta.Callable[[], ta.Awaitable[None]] | None = None
    on_start: ta.Callable[[], ta.Awaitable[None]] | None = None
    on_stop: ta.Callable[[], ta.Awaitable[None]] | None = None
    on_destroy: ta.Callable[[], ta.Awaitable[None]] | None = None

    @ta.override
    async def lifecycle_state(self, state: LifecycleState) -> None:
        if self.on_state is not None:
            await self.on_state(state)

    @ta.override
    async def lifecycle_construct(self) -> None:
        if self.on_construct is not None:
            await self.on_construct()

    @ta.override
    async def lifecycle_start(self) -> None:
        if self.on_start is not None:
            await self.on_start()

    @ta.override
    async def lifecycle_stop(self) -> None:
        if self.on_stop is not None:
            await self.on_stop()

    @ta.override
    async def lifecycle_destroy(self) -> None:
        if self.on_destroy is not None:
            await self.on_destroy()
