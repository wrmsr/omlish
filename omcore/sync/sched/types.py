import abc
import enum
import typing as ta

from ... import lang


ScheduledFn: ta.TypeAlias = ta.Callable[[], ta.Any]
ScheduledCallback: ta.TypeAlias = ta.Callable[['ScheduleHandle'], ta.Any]


##


class ScheduledRunnerStateError(Exception):
    pass


class ScheduledCancelledError(RuntimeError):
    pass


class ScheduledTimeoutError(TimeoutError):
    pass


##


class ScheduleHandle(lang.Abstract):
    """
    A cancellable handle for a scheduled function.

    Thread-safe. Callbacks run in the runner thread (so keep them short).
    """

    # status

    @abc.abstractmethod
    def done(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def cancelled(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def running(self) -> bool:
        raise NotImplementedError

    # completion

    @abc.abstractmethod
    def cancel(self) -> bool:
        """Best-effort cancellation. Returns True iff the task was not running/done and is now cancelled."""

        raise NotImplementedError

    @abc.abstractmethod
    def result(self, timeout: float | None = None) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def exception(self, timeout: float | None = None) -> BaseException | None:
        raise NotImplementedError

    @abc.abstractmethod
    def add_done_callback(self, fn: ScheduledCallback) -> None:
        """
        If already done, invokes immediately in the caller thread. Otherwise, callback will run in the runner thread
        right after completion.
        """

        raise NotImplementedError


##


class ScheduledRunnerState(enum.StrEnum):
    NEW = 'new'
    RUNNING = 'running'
    DRAINING = 'draining'
    STOPPING = 'stopping'
    STOPPED = 'stopped'


class ScheduledRunner(lang.Abstract):
    @abc.abstractmethod
    def get_state(self) -> ScheduledRunnerState:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def schedule(self, delay: float, fn: ScheduledFn) -> ScheduleHandle:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def shutdown(
            self,
            *,
            cancel_all: bool = False,
            no_wait: bool = False,
            timeout: float | None = None,
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def wait(self, timeout: float | None = None) -> None:
        raise NotImplementedError
