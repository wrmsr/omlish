import abc
import os
import signal
import sys
import time
import typing as ta

from .. import check
from .forkhooks import get_fork_depth


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
            signal: int | None = signal.SIGTERM,
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


class PipeDeathpact(BaseDeathpact):
    """
    TODO:
     - while not a goal to futilely try to support threads+forks, still vulnerable to a case of a parent with active
       pacts forking into child codepaths that never call _close_wfd_if_not_parent, thus leaving the wfd open.
    """

    _COOKIE: ta.ClassVar[bytes] = os.urandom(16)

    def __init__(self, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

        self._rfd: int | None = None
        self._wfd: int | None = None

        self._cookie: bytes | None = self._COOKIE
        self._fork_depth: int | None = get_fork_depth()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(rfd={self._rfd}, wfd={self._wfd})'

    @property
    def pass_fd(self) -> int:
        return check.not_none(self._rfd)

    def is_parent(self) -> bool:
        return (self._COOKIE, get_fork_depth()) == (self._cookie, self._fork_depth)

    #

    def __enter__(self) -> ta.Self:
        check.none(self._rfd)
        check.none(self._wfd)

        self._rfd, self._wfd = os.pipe()

        os.set_blocking(self._rfd, False)

        return self

    def _close_wfd_if_not_parent(self) -> None:
        if self._wfd is not None:
            if self.is_parent():
                os.close(check.not_none(self._wfd))
            self._wfd = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._rfd is not None:
            os.close(self._rfd)
            self._rfd = None

        self._close_wfd_if_not_parent()

    #

    def __getstate__(self):
        return dict(
            **self.__dict__,
            _wfd=None,
            _cookie=None,
            _fork_depth=None,
        )

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
