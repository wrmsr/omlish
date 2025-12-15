import typing as ta

from .. import cached
from .. import dataclasses as dc
from .. import lang
from .base import AsyncLifecycle
from .base import Lifecycle


LifecycleManagedT = ta.TypeVar('LifecycleManagedT', bound='LifecycleManaged')

AsyncLifecycleManagedT = ta.TypeVar('AsyncLifecycleManagedT', bound='AsyncLifecycleManaged')


##


class LifecycleManaged(lang.Abstract):
    @ta.final
    @dc.dataclass(frozen=True)
    class _Lifecycle(
        Lifecycle,
        lang.Final,
        ta.Generic[LifecycleManagedT],
    ):
        obj: LifecycleManagedT

        def lifecycle_construct(self) -> None:
            self.obj._lifecycle_construct()  # noqa

        def lifecycle_start(self) -> None:
            self.obj._lifecycle_start()  # noqa

        def lifecycle_stop(self) -> None:
            self.obj._lifecycle_stop()  # noqa

        def lifecycle_destroy(self) -> None:
            self.obj._lifecycle_destroy()  # noqa

    @cached.property
    def _lifecycle(self) -> _Lifecycle[ta.Self]:
        return LifecycleManaged._Lifecycle(self)

    def _lifecycle_construct(self) -> None:
        pass

    def _lifecycle_start(self) -> None:
        pass

    def _lifecycle_stop(self) -> None:
        pass

    def _lifecycle_destroy(self) -> None:
        pass


##


class AsyncLifecycleManaged(lang.Abstract):
    @ta.final
    @dc.dataclass(frozen=True)
    class _Lifecycle(
        AsyncLifecycle,
        lang.Final,
        ta.Generic[AsyncLifecycleManagedT],
    ):
        obj: AsyncLifecycleManagedT

        async def lifecycle_construct(self) -> None:
            await self.obj._lifecycle_construct()  # noqa

        async def lifecycle_start(self) -> None:
            await self.obj._lifecycle_start()  # noqa

        async def lifecycle_stop(self) -> None:
            await self.obj._lifecycle_stop()  # noqa

        async def lifecycle_destroy(self) -> None:
            await self.obj._lifecycle_destroy()  # noqa

    @cached.property
    def _lifecycle(self) -> _Lifecycle[ta.Self]:
        return AsyncLifecycleManaged._Lifecycle(self)

    async def _lifecycle_construct(self) -> None:
        pass

    async def _lifecycle_start(self) -> None:
        pass

    async def _lifecycle_stop(self) -> None:
        pass

    async def _lifecycle_destroy(self) -> None:
        pass
