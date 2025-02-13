import abc
import os
import signal
import sys
import time
import typing as ta
import weakref

from .. import check
from .forkhooks import ForkHook
from .forkhooks import ProcessOriginTracker


##


class Deathpact(abc.ABC):
    @abc.abstractmethod
    def poll(self) -> None:
        raise NotImplementedError


class NopDeathpact(Deathpact):
    def poll(self) -> None:
        pass


##


class BaseDeathpact(Deathpact, abc.ABC):
    def __init__(
            self,
            *,
            interval_s: float = .5,
            signal: int | None = signal.SIGTERM,  # noqa
            output: ta.Literal['stdout', 'stderr'] | None = 'stderr',
            on_die: ta.Callable[[], None] | None = None,
    ) -> None:
        super().__init__()

        self._interval_s = interval_s
        self._signal = signal
        self._output = output
        self._on_die = on_die

        self._last_check_t: float | None = None

    def _print(self, msg: str) -> None:
        match self._output:
            case 'stdout':
                f = sys.stdout
            case 'stderr':
                f = sys.stderr
            case _:
                return
        print(f'{self} pid={os.getpid()}: {msg}', file=f)

    def die(self) -> None:
        self._print('Triggered! Process terminating!')

        if self._on_die is not None:
            self._on_die()

        if self._signal is not None:
            os.kill(os.getpid(), self._signal)

        sys.exit(1)

    @abc.abstractmethod
    def should_die(self) -> bool:
        raise NotImplementedError

    def maybe_die(self) -> None:
        if self.should_die():
            self.die()

    def poll(self) -> None:
        if self._last_check_t is None or (time.monotonic() - self._last_check_t) >= self._interval_s:
            self.maybe_die()
            self._last_check_t = time.monotonic()


##


class HeartbeatFileDeathpact(BaseDeathpact):
    def __init__(self, path: str, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

        self._path = path

    def should_die(self) -> bool:
        raise NotImplementedError


##


class PipeDeathpact(BaseDeathpact):
    """
    NOTE: Closes write side in children lazily on poll - does not proactively close write sides on fork. This means
          parents which fork children into codepaths unaware of live PipeDeathpacts will leave write sides open in those
          children, potentially leading to zombies (if those children outlast the parent). Use ForkAwarePipeDeathpact to
          handle such cases.
    """

    def __init__(self, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

        self._rfd: int | None = None
        self._wfd: int | None = None

        self._process_origin = ProcessOriginTracker()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(rfd={self._rfd}, wfd={self._wfd})'

    @property
    def pass_fd(self) -> int:
        return check.not_none(self._rfd)

    def is_parent(self) -> bool:
        return self._process_origin.is_in_origin_process()

    #

    def __enter__(self) -> ta.Self:
        check.none(self._rfd)
        check.none(self._wfd)

        self._rfd, self._wfd = os.pipe()

        os.set_blocking(self._rfd, False)

        return self

    def close(self) -> None:
        if self._rfd is not None:
            os.close(self._rfd)
            self._rfd = None

        if self._wfd is not None:
            if self.is_parent():
                os.close(check.not_none(self._wfd))
            self._wfd = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _close_wfd_if_not_parent(self) -> None:
        if self._wfd is not None:
            if not self.is_parent():
                os.close(check.not_none(self._wfd))
            self._wfd = None

    #

    def __getstate__(self):
        return {
            **self.__dict__,
            **dict(
                _wfd=None,
            ),
        }

    def __setstate__(self, state):
        self.__dict__.update(state)

    #

    def should_die(self) -> bool:
        self._close_wfd_if_not_parent()

        try:
            buf = os.read(check.not_none(self._rfd), 1)
        except BlockingIOError:
            return False

        if buf:
            self._print(f'Read data from pipe! This should not happen! Process state corrupt!')
            self.die()

        return True


#


class ForkAwarePipeDeathpact(PipeDeathpact):
    """
    TODO:
     - Despite no correct way to do threads+forks, still audit thread-safety. Is WeakSet threadsafe? Probably not..
    """

    _PARENTS: ta.ClassVar[ta.MutableSet['ForkAwarePipeDeathpact']] = weakref.WeakSet()

    def __init__(self, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

        self._ForkHook.install()
        self._PARENTS.add(self)

    class _ForkHook(ForkHook):
        @classmethod
        def _after_fork_in_child(cls) -> None:
            for pdp in ForkAwarePipeDeathpact._PARENTS:
                pdp._close_wfd_if_not_parent()  # noqa
            ForkAwarePipeDeathpact._PARENTS.clear()
