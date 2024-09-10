import abc
import dataclasses as dc
import multiprocessing as mp
import multiprocessing.popen_spawn_posix
import os
import signal
import sys
import time
import typing as ta

from . import check
from . import lang
from . import libc


T = ta.TypeVar('T')


##


@ta.runtime_checkable
class ValueProxy(ta.Protocol[T]):
    # value = property(get, set)

    def get(self) -> T:
        ...

    def set(self, value: T) -> None:
        ...


@dc.dataclass()
@lang.protocol_check(ValueProxy)
class DummyValueProxy(ValueProxy[T]):
    value: T

    def get(self) -> T:
        return self.value

    def set(self, value: T) -> None:
        self.value = value


##


@dc.dataclass(frozen=True, kw_only=True)
class SpawnExtras:
    pass_fds: ta.AbstractSet[int] | None = None
    deathsig: int | None = None


class ExtrasSpawnPosixPopen(mp.popen_spawn_posix.Popen):
    def __init__(self, process_obj: 'ExtrasSpawnProcess', *, extras: SpawnExtras) -> None:
        self.__extras = extras
        self.__pass_fds = extras.pass_fds
        super().__init__(process_obj)

    def _launch(self, process_obj: 'ExtrasSpawnProcess') -> None:
        if self.__pass_fds:
            for fd in self.__pass_fds:
                self.duplicate_for_child(fd)
            self._extra_fds = None

        super()._launch(process_obj)  # type: ignore  # noqa


class ExtrasSpawnProcess(mp.context.SpawnProcess):
    def __init__(self, *args: ta.Any, extras: SpawnExtras, **kwargs: ta.Any) -> None:
        self.__extras = extras
        super().__init__(*args, **kwargs)

    def _Popen(self, process_obj: 'ExtrasSpawnProcess') -> ExtrasSpawnPosixPopen:  # type: ignore  # noqa
        return ExtrasSpawnPosixPopen(
            check.isinstance(process_obj, ExtrasSpawnProcess),
            extras=self.__extras,
        )

    def run(self) -> None:
        if self.__extras.deathsig is not None and sys.platform == 'linux':
            libc.prctl(libc.PR_SET_PDEATHSIG, self.__extras.deathsig, 0, 0, 0, 0)

        super().run()


class ExtrasSpawnContext(mp.context.SpawnContext):
    def __init__(self, extras: SpawnExtras = SpawnExtras()) -> None:
        self.__extras = extras
        super().__init__()

    def Process(self, *args: ta.Any, **kwargs: ta.Any):  # type: ignore  # noqa
        return ExtrasSpawnProcess(*args, extras=self.__extras, **kwargs)


##


class Deathpact(abc.ABC):
    @abc.abstractmethod
    def poll(self) -> None:
        raise NotImplementedError


class NopDeathpact(Deathpact):
    def poll(self) -> None:
        pass


#


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


#


class PipeDeathpact(BaseDeathpact):
    def __init__(self, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

        self._rfd: int | None = None
        self._wfd: int | None = None

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(rfd={self._rfd}, wfd={self._wfd})'

    @property
    def pass_fd(self) -> int:
        return check.not_none(self._rfd)

    def __enter__(self) -> ta.Self:
        check.none(self._rfd)
        check.none(self._wfd)

        self._rfd, self._wfd = os.pipe()

        os.set_inheritable(self._rfd, True)
        os.set_blocking(self._rfd, False)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._rfd is not None:
            os.close(check.not_none(self._wfd))
            self._wfd = None

            os.close(self._rfd)
            self._rfd = None

    def should_die(self) -> bool:
        try:
            buf = os.read(check.not_none(self._rfd), 1)
        except BlockingIOError:
            return False

        if buf:
            self._print(f'Read data from pipe! This should not happen! Process state corrupt!')
            self.die()

        return True
