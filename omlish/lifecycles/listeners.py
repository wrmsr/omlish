import typing as ta

from .. import check
from .base import AsyncLifecycle
from .base import Lifecycle


##


class LifecycleListener:
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        try:
            async_lifecycle_listener_cls = AsyncLifecycleListener
        except NameError:
            pass
        else:
            check.not_issubclass(cls, async_lifecycle_listener_cls)

    def on_starting(self, obj: Lifecycle) -> None:
        pass

    def on_started(self, obj: Lifecycle) -> None:
        pass

    def on_stopping(self, obj: Lifecycle) -> None:
        pass

    def on_stopped(self, obj: Lifecycle) -> None:
        pass


class AsyncLifecycleListener:
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        check.not_issubclass(cls, LifecycleListener)

    async def on_starting(self, obj: AsyncLifecycle) -> None:
        pass

    async def on_started(self, obj: AsyncLifecycle) -> None:
        pass

    async def on_stopping(self, obj: AsyncLifecycle) -> None:
        pass

    async def on_stopped(self, obj: AsyncLifecycle) -> None:
        pass


AnyLifecycleListener: ta.TypeAlias = LifecycleListener | AsyncLifecycleListener

ANY_LIFECYCLE_LISTENER_TYPES: tuple[type[LifecycleListener | AsyncLifecycleListener], ...] = (LifecycleListener, AsyncLifecycleListener)  # noqa
