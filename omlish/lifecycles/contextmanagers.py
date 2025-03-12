import types
import typing as ta

from .. import dataclasses as dc
from .. import defs
from .. import lang
from .base import Lifecycle
from .controller import LifecycleController
from .states import LifecycleState
from .states import LifecycleStates


LifecycleT = ta.TypeVar('LifecycleT', bound='Lifecycle')
ContextManagerT = ta.TypeVar('ContextManagerT', bound=ta.ContextManager)


@dc.dataclass(frozen=True)
class ContextManagerLifecycle(Lifecycle, lang.Final, ta.Generic[ContextManagerT]):
    cm: ContextManagerT

    @ta.override
    def lifecycle_start(self) -> None:
        self.cm.__enter__()

    @ta.override
    def lifecycle_stop(self) -> None:
        self.cm.__exit__(None, None, None)


class LifecycleContextManager(ta.Generic[LifecycleT]):
    def __init__(self, lifecycle: LifecycleT) -> None:
        super().__init__()
        self._lifecycle = lifecycle
        self._controller = lifecycle if isinstance(lifecycle, LifecycleController) else LifecycleController(lifecycle)

    defs.repr('lifecycle', 'state')

    @property
    def lifecycle(self) -> LifecycleT:
        return self._lifecycle

    @property
    def controller(self) -> LifecycleController:
        return self._controller

    @property
    def state(self) -> LifecycleState:
        return self._controller.state

    def __enter__(self) -> ta.Self:
        try:
            self._controller.lifecycle_construct()
            self._controller.lifecycle_start()
        except Exception:
            self._controller.lifecycle_destroy()
            raise
        return self

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
