import typing as ta

from .. import cached
from .. import dataclasses as dc
from .. import lang
from .base import AsyncLifecycle
from .base import Lifecycle


AbstractLifecycleT = ta.TypeVar('AbstractLifecycleT', bound='AbstractLifecycle')

AbstractAsyncLifecycleT = ta.TypeVar('AbstractAsyncLifecycleT', bound='AbstractAsyncLifecycle')


##


class AbstractLifecycle(lang.Abstract):
    @dc.dataclass(frozen=True)
    class _Lifecycle(Lifecycle, lang.Final, ta.Generic[AbstractLifecycleT]):
        obj: AbstractLifecycleT

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
        return AbstractLifecycle._Lifecycle(self)

    def _lifecycle_construct(self) -> None:
        pass

    def _lifecycle_start(self) -> None:
        pass

    def _lifecycle_stop(self) -> None:
        pass

    def _lifecycle_destroy(self) -> None:
        pass


##


class AbstractAsyncLifecycle(lang.Abstract):
    @dc.dataclass(frozen=True)
    class _Lifecycle(AsyncLifecycle, lang.Final, ta.Generic[AbstractAsyncLifecycleT]):
        obj: AbstractAsyncLifecycleT

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
        return AbstractAsyncLifecycle._Lifecycle(self)

    async def _lifecycle_construct(self) -> None:
        pass

    async def _lifecycle_start(self) -> None:
        pass

    async def _lifecycle_stop(self) -> None:
        pass

    async def _lifecycle_destroy(self) -> None:
        pass
