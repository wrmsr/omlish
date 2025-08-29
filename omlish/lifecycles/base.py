import typing as ta

from .. import dataclasses as dc
from .. import lang


R = ta.TypeVar('R')

AnyLifecycleT = ta.TypeVar('AnyLifecycleT', bound='AnyLifecycle')
AnyLifecycleCallback: ta.TypeAlias = ta.Callable[[AnyLifecycleT], R]

LifecycleT = ta.TypeVar('LifecycleT', bound='Lifecycle')
LifecycleCallback: ta.TypeAlias = ta.Callable[[LifecycleT], R]

AsyncLifecycleT = ta.TypeVar('AsyncLifecycleT', bound='AsyncLifecycle')
AsyncLifecycleCallback: ta.TypeAlias = ta.Callable[[AsyncLifecycleT], R]


##


class AnyLifecycle(lang.Abstract, ta.Generic[R]):
    def lifecycle_construct(self) -> R | None:
        return None

    def lifecycle_start(self) -> R | None:
        return None

    def lifecycle_stop(self) -> R | None:
        return None

    def lifecycle_destroy(self) -> R | None:
        return None


@dc.dataclass(frozen=True, kw_only=True)
class AnyCallbackLifecycle(
    AnyLifecycle[R],
    lang.Abstract,
    ta.Generic[AnyLifecycleT, R],
):
    on_construct: AnyLifecycleCallback['AnyCallbackLifecycle[AnyLifecycleT, R]', R] | None = None
    on_start: AnyLifecycleCallback['AnyCallbackLifecycle[AnyLifecycleT, R]', R] | None = None
    on_stop: AnyLifecycleCallback['AnyCallbackLifecycle[AnyLifecycleT, R]', R] | None = None
    on_destroy: AnyLifecycleCallback['AnyCallbackLifecycle[AnyLifecycleT, R]', R] | None = None

    @ta.override
    def lifecycle_construct(self) -> R | None:
        if self.on_construct is not None:
            return self.on_construct(self)
        else:
            return None

    @ta.override
    def lifecycle_start(self) -> R | None:
        if self.on_start is not None:
            return self.on_start(self)
        else:
            return None

    @ta.override
    def lifecycle_stop(self) -> R | None:
        if self.on_stop is not None:
            return self.on_stop(self)
        else:
            return None

    @ta.override
    def lifecycle_destroy(self) -> R | None:
        if self.on_destroy is not None:
            return self.on_destroy(self)
        else:
            return None


##


class Lifecycle(AnyLifecycle[None]):
    pass


class CallbackLifecycle(
    AnyCallbackLifecycle[LifecycleT, None],
    lang.Final,
    ta.Generic[LifecycleT],
):
    pass


##


class AsyncLifecycle(AnyLifecycle[ta.Awaitable[None]]):
    pass


class CallbackAsyncLifecycle(
    AnyCallbackLifecycle[LifecycleT, ta.Awaitable[None]],
    lang.Final,
    ta.Generic[LifecycleT],
):
    pass
