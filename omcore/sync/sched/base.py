import abc
import threading

from ... import check
from ... import lang
from .types import ScheduledRunner
from .types import ScheduledRunnerState
from .types import ScheduledRunnerStateError


##


class BaseScheduledRunner(ScheduledRunner, lang.Abstract):
    def __init__(self) -> None:
        super().__init__()

        self._cv = threading.Condition()

    #

    _state: ScheduledRunnerState = ScheduledRunnerState.NEW

    def get_state(self) -> ScheduledRunnerState:
        with self._cv:
            return self._state

    def _check_state(self, *valid_states: ScheduledRunnerState) -> ScheduledRunnerState:
        if self._state not in valid_states:
            raise ScheduledRunnerStateError(self._state)
        return self._state

    def _check_state_not(self, *invalid_states: ScheduledRunnerState) -> ScheduledRunnerState:
        if self._state in invalid_states:
            raise ScheduledRunnerStateError(self._state)
        return self._state

    #

    _thread: threading.Thread | None = None

    def shutdown(
            self,
            *,
            cancel_all: bool = False,
            no_wait: bool = False,
            timeout: float | None = None,
    ) -> None:
        with self._cv:
            if self._state == ScheduledRunnerState.NEW:
                check.none(self._thread)
                return

            elif self._state == ScheduledRunnerState.RUNNING:
                if cancel_all:
                    self._state = ScheduledRunnerState.STOPPING
                else:
                    self._state = ScheduledRunnerState.DRAINING
                self._cv.notify()

            elif self._state in (ScheduledRunnerState.STOPPING, ScheduledRunnerState.DRAINING):
                pass

            elif self._state == ScheduledRunnerState.STOPPED:
                return

            else:
                raise ScheduledRunnerStateError(self._state)

        if no_wait:
            return

        self.wait(timeout=timeout)

    def wait(self, timeout: float | None = None) -> None:
        with self._cv:
            if self._state == ScheduledRunnerState.STOPPED:
                return

            self._check_state(ScheduledRunnerState.STOPPING, ScheduledRunnerState.DRAINING)

        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=timeout)

            if self._thread.is_alive():
                raise TimeoutError

        with self._cv:
            self._check_state(ScheduledRunnerState.STOPPED)

    #

    def _ensure_thread_locked(self) -> None:
        if self._thread is not None:
            self._check_state_not(ScheduledRunnerState.NEW)
            return

        self._check_state(ScheduledRunnerState.NEW)

        t = threading.Thread(
            target=self.__thread_main,
            name=type(self).__name__,
            daemon=True,
        )

        self._thread = t

        t.start()

        self._state = ScheduledRunnerState.RUNNING

    def __thread_main(self) -> None:
        with self._cv:
            # May have requested shutdown before thread got scheduled
            if self._state in (ScheduledRunnerState.STOPPING, ScheduledRunnerState.DRAINING):
                self._state = ScheduledRunnerState.STOPPED
                return

            self._check_state(ScheduledRunnerState.RUNNING)
            check.state(self._thread is threading.current_thread())

        try:
            self._thread_main()

        finally:
            with self._cv:
                check.state(self._thread is threading.current_thread())
                self._state = ScheduledRunnerState.STOPPED

    @abc.abstractmethod
    def _thread_main(self) -> None:
        raise NotImplementedError
