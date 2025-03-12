import typing as ta

from .. import dataclasses as dc
from .. import lang


LifecycleT = ta.TypeVar('LifecycleT', bound='Lifecycle')
LifecycleCallback: ta.TypeAlias = ta.Callable[[LifecycleT], None]


class Lifecycle:
    def lifecycle_construct(self) -> None:
        pass

    def lifecycle_start(self) -> None:
        pass

    def lifecycle_stop(self) -> None:
        pass

    def lifecycle_destroy(self) -> None:
        pass


@dc.dataclass(frozen=True, kw_only=True)
class CallbackLifecycle(Lifecycle, lang.Final, ta.Generic[LifecycleT]):
    on_construct: LifecycleCallback['CallbackLifecycle[LifecycleT]'] | None = None
    on_start: LifecycleCallback['CallbackLifecycle[LifecycleT]'] | None = None
    on_stop: LifecycleCallback['CallbackLifecycle[LifecycleT]'] | None = None
    on_destroy: LifecycleCallback['CallbackLifecycle[LifecycleT]'] | None = None

    @ta.override
    def lifecycle_construct(self) -> None:
        if self.on_construct is not None:
            self.on_construct(self)

    @ta.override
    def lifecycle_start(self) -> None:
        if self.on_start is not None:
            self.on_start(self)

    @ta.override
    def lifecycle_stop(self) -> None:
        if self.on_stop is not None:
            self.on_stop(self)

    @ta.override
    def lifecycle_destroy(self) -> None:
        if self.on_destroy is not None:
            self.on_destroy(self)
