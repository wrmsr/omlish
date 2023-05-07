import contextlib
import typing as ta

from .. import check
from .. import lang
from .. import pydevd
from .controller import LifecycleController
from .controller import LifecycleState
from .controller import LifecycleStates
from .types import CallbackLifecycle
from .types import Lifecycle


AbstractLifecycleT = ta.TypeVar('AbstractLifecycleT', bound='AbstractLifecycle')


class AbstractLifecycle(Lifecycle, lang.Abstract):

    def __init__(self: AbstractLifecycleT, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)  # type: ignore

        def _lifecycle_stop(_) -> None:
            if self._lifecycle_exit_stack_instance is not None:
                self._lifecycle_exit_stack_instance.__exit__(None, None, None)
            self._do_lifecycle_stop()

        self._lifecycle_delegate = CallbackLifecycle(
            construct=lambda _: self._do_lifecycle_construct(),
            start=lambda _: self._do_lifecycle_start(),
            stop=_lifecycle_stop,
            destroy=lambda _: self._do_lifecycle_destroy(),
        )
        self._lifecycle_controller: LifecycleController[AbstractLifecycleT] = LifecycleController(self._lifecycle_delegate)  # noqa
        self._lifecycle_exit_stack_instance: ta.Optional[contextlib.ExitStack] = None

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        lang.check_finals(cls, AbstractLifecycle)

    @property
    def lifecycle_controller(self: AbstractLifecycleT) -> 'LifecycleController[AbstractLifecycleT]':
        return self._lifecycle_controller

    @property
    def lifecycle_state(self) -> LifecycleState:
        return self._lifecycle_controller.state

    @property
    def is_lifecycle_started(self) -> bool:
        return self._lifecycle_controller.state == LifecycleStates.STARTED

    @property
    def _lifecycle_exit_stack(self) -> contextlib.ExitStack:
        if self._lifecycle_exit_stack_instance is None:
            pydevd.forbid_debugger_call()
            check.state(self._lifecycle_controller.state.phase >= LifecycleStates.STARTED.phase)
            self._lifecycle_exit_stack_instance = contextlib.ExitStack()
            self._lifecycle_exit_stack_instance.__enter__()
        return self._lifecycle_exit_stack_instance

    @lang.final
    def lifecycle_construct(self) -> None:
        self._lifecycle_controller.lifecycle_construct()

    def _do_lifecycle_construct(self) -> None:
        pass

    @lang.final
    def lifecycle_start(self) -> None:
        self._lifecycle_controller.lifecycle_start()

    def _do_lifecycle_start(self) -> None:
        pass

    @lang.final
    def lifecycle_stop(self) -> None:
        self._lifecycle_controller.lifecycle_stop()

    def _do_lifecycle_stop(self) -> None:
        pass

    @lang.final
    def lifecycle_destroy(self) -> None:
        self._lifecycle_controller.lifecycle_destroy()

    def _do_lifecycle_destroy(self) -> None:
        pass
