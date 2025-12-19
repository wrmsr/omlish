import contextlib
import types
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .base import AsyncLifecycle
from .base import Lifecycle
from .controller import AsyncLifecycleController
from .controller import LifecycleController
from .states import LifecycleState
from .states import LifecycleStates
from .unwrap import unwrap_async_lifecycle
from .unwrap import unwrap_lifecycle


T = ta.TypeVar('T')

ContextManagerT = ta.TypeVar('ContextManagerT', bound=ta.ContextManager)
AsyncContextManagerT = ta.TypeVar('AsyncContextManagerT', bound=ta.AsyncContextManager)

LifecycleT = ta.TypeVar('LifecycleT', bound=Lifecycle)
AsyncLifecycleT = ta.TypeVar('AsyncLifecycleT', bound=AsyncLifecycle)


##


@ta.final
@dc.dataclass(frozen=True)
class ContextManagerLifecycle(Lifecycle, lang.Final, ta.Generic[ContextManagerT]):
    cm: ContextManagerT

    @ta.override
    def lifecycle_start(self) -> None:
        self.cm.__enter__()

    @ta.override
    def lifecycle_stop(self) -> None:
        self.cm.__exit__(None, None, None)


@ta.final
@dc.dataclass(frozen=True)
class AsyncContextManagerLifecycle(AsyncLifecycle, lang.Final, ta.Generic[AsyncContextManagerT]):
    cm: AsyncContextManagerT

    @ta.override
    async def lifecycle_start(self) -> None:
        await self.cm.__aenter__()

    @ta.override
    async def lifecycle_stop(self) -> None:
        await self.cm.__aexit__(None, None, None)


##


@ta.final
class LifecycleContextManager(lang.Final, ta.Generic[LifecycleT]):
    def __init__(self, lifecycle: LifecycleT) -> None:
        super().__init__()

        self._lifecycle = lifecycle
        self._controller = lifecycle if isinstance(lifecycle, LifecycleController) else LifecycleController(lifecycle)

    __repr__ = lang.attr_ops(lambda o: (o.lifecycle, o.state)).repr

    #

    @property
    def lifecycle(self) -> LifecycleT:
        return self._lifecycle

    @property
    def controller(self) -> LifecycleController:
        return self._controller

    @property
    def state(self) -> LifecycleState:
        return self._controller.state

    #

    def __enter__(self) -> LifecycleT:
        try:
            self._controller.lifecycle_construct()
            self._controller.lifecycle_start()
        except Exception:
            self._controller.lifecycle_destroy()
            raise
        return self._lifecycle

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: types.TracebackType | None,
    ) -> bool | None:
        try:
            if self._controller.state is LifecycleStates.STARTED:
                self._controller.lifecycle_stop()
        except Exception:
            self._controller.lifecycle_destroy()
            raise
        else:
            self._controller.lifecycle_destroy()
        return None


@ta.final
class AsyncLifecycleContextManager(lang.Final, ta.Generic[AsyncLifecycleT]):
    def __init__(self, lifecycle: AsyncLifecycleT) -> None:
        super().__init__()

        self._lifecycle = lifecycle
        self._controller = lifecycle if isinstance(lifecycle, AsyncLifecycleController) else AsyncLifecycleController(lifecycle)  # noqa

    __repr__ = lang.attr_ops(lambda o: (o.lifecycle, o.state)).repr

    #

    @property
    def lifecycle(self) -> AsyncLifecycleT:
        return self._lifecycle

    @property
    def controller(self) -> AsyncLifecycleController:
        return self._controller

    @property
    def state(self) -> LifecycleState:
        return self._controller.state

    #

    async def __aenter__(self) -> AsyncLifecycleT:
        try:
            await self._controller.lifecycle_construct()
            await self._controller.lifecycle_start()
        except Exception:
            await self._controller.lifecycle_destroy()
            raise
        return self._lifecycle

    async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: types.TracebackType | None,
    ) -> bool | None:
        try:
            if self._controller.state is LifecycleStates.STARTED:
                await self._controller.lifecycle_stop()
        except Exception:
            await self._controller.lifecycle_destroy()
            raise
        else:
            await self._controller.lifecycle_destroy()
        return None


##


def lifecycle_context_manage(obj: T) -> ta.ContextManager[T]:
    @contextlib.contextmanager
    def inner():
        lc = check.not_none(unwrap_lifecycle(obj))
        with LifecycleContextManager(lc):
            yield obj

    return inner()


def async_lifecycle_context_manage(obj: T) -> ta.AsyncContextManager[T]:
    @contextlib.asynccontextmanager
    async def inner():
        lc = check.not_none(unwrap_async_lifecycle(obj))
        async with AsyncLifecycleContextManager(lc):
            yield obj

    return inner()
