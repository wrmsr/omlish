import abc
import os
import signal
import sys
import time
import typing as ta


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
