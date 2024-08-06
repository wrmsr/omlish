import typing as ta

from .. import cached
from .. import dataclasses as dc
from .. import lang
from .base import Lifecycle


AbstractLifecycleT = ta.TypeVar('AbstractLifecycleT', bound='AbstractLifecycle')


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
