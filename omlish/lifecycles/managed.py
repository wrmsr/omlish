import typing as ta

from .. import cached
from .. import check
from .. import dataclasses as dc
from .. import lang
from .base import AsyncLifecycle
from .base import Lifecycle
from .states import LifecycleState
from .states import LifecycleStates


LifecycleManagedT = ta.TypeVar('LifecycleManagedT', bound='LifecycleManaged')

AsyncLifecycleManagedT = ta.TypeVar('AsyncLifecycleManagedT', bound='AsyncLifecycleManaged')


##


class LifecycleManaged(lang.Abstract):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        try:
            async_lifecycle_managed_cls = AsyncLifecycleManaged
        except NameError:
            pass
        else:
            check.not_issubclass(cls, async_lifecycle_managed_cls)

    @ta.final
    @dc.dataclass(frozen=True)
    class _Lifecycle(
        Lifecycle,
        lang.Final,
        ta.Generic[LifecycleManagedT],
    ):
        obj: LifecycleManagedT

        def lifecycle_state(self, state: LifecycleState) -> None:
            self.obj._lifecycle_state_ = state

        def lifecycle_construct(self) -> None:
            self.obj._lifecycle_construct()  # noqa

        def lifecycle_start(self) -> None:
            self.obj._lifecycle_start()  # noqa

        def lifecycle_stop(self) -> None:
            self.obj._lifecycle_stop()  # noqa

        def lifecycle_destroy(self) -> None:
            self.obj._lifecycle_destroy()  # noqa

    @ta.final
    @cached.property
    def _lifecycle(self) -> _Lifecycle[ta.Self]:
        return LifecycleManaged._Lifecycle(self)

    _lifecycle_state_: LifecycleState = LifecycleStates.NEW

    @property
    def _lifecycle_state(self) -> LifecycleState:
        return self._lifecycle_state_

    def _lifecycle_construct(self) -> None:
        pass

    def _lifecycle_start(self) -> None:
        pass

    def _lifecycle_stop(self) -> None:
        pass

    def _lifecycle_destroy(self) -> None:
        pass


#


class AsyncLifecycleManaged(lang.Abstract):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        check.not_issubclass(cls, LifecycleManaged)

    @ta.final
    @dc.dataclass(frozen=True)
    class _Lifecycle(
        AsyncLifecycle,
        lang.Final,
        ta.Generic[AsyncLifecycleManagedT],
    ):
        obj: AsyncLifecycleManagedT

        async def lifecycle_state(self, state: LifecycleState) -> None:
            self.obj._lifecycle_state_ = state

        async def lifecycle_construct(self) -> None:
            await self.obj._lifecycle_construct()  # noqa

        async def lifecycle_start(self) -> None:
            await self.obj._lifecycle_start()  # noqa

        async def lifecycle_stop(self) -> None:
            await self.obj._lifecycle_stop()  # noqa

        async def lifecycle_destroy(self) -> None:
            await self.obj._lifecycle_destroy()  # noqa

    @ta.final
    @cached.property
    def _lifecycle(self) -> _Lifecycle[ta.Self]:
        return AsyncLifecycleManaged._Lifecycle(self)

    _lifecycle_state_: LifecycleState = LifecycleStates.NEW

    @property
    def _lifecycle_state(self) -> LifecycleState:
        return self._lifecycle_state_

    async def _lifecycle_construct(self) -> None:
        pass

    async def _lifecycle_start(self) -> None:
        pass

    async def _lifecycle_stop(self) -> None:
        pass

    async def _lifecycle_destroy(self) -> None:
        pass


#


AnyLifecycleManaged: ta.TypeAlias = LifecycleManaged | AsyncLifecycleManaged

ANY_LIFECYCLE_MANAGED_TYPES: tuple[type[LifecycleManaged | AsyncLifecycleManaged], ...] = (LifecycleManaged, AsyncLifecycleManaged)  # noqa
