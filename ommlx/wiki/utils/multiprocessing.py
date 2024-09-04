import dataclasses as dc
import multiprocessing as mp
import multiprocessing.popen_spawn_posix
import os
import signal
import sys
import time
import typing as ta

from omlish import check
from omlish import libc


##


@dc.dataclass(frozen=True, kw_only=True)
class SpawnExtras:
    fds: ta.AbstractSet[int] | None = None
    deathsig: int | None = None


class ExtrasSpawnPosixPopen(mp.popen_spawn_posix.Popen):
    def __init__(self, process_obj: 'ExtrasSpawnProcess', *, extras: SpawnExtras) -> None:
        self.__extras = extras
        self.__extra_fds = extras.fds
        super().__init__(process_obj)

    def _launch(self, process_obj: 'ExtrasSpawnProcess') -> None:
        if self.__extra_fds:
            for fd in self.__extra_fds:
                self.duplicate_for_child(fd)
            self._extra_fds = None
        super()._launch(process_obj)  # type: ignore  # noqa


class ExtrasSpawnProcess(mp.context.SpawnProcess):
    def __init__(self, *args: ta.Any, extras: SpawnExtras, **kwargs: ta.Any) -> None:
        self.__extras = extras
        super().__init__(*args, **kwargs)

    def _Popen(self, process_obj: 'ExtrasSpawnProcess') -> ExtrasSpawnPosixPopen:  # type: ignore  # noqa
        return ExtrasSpawnPosixPopen(process_obj, extras=self.__extras)

    def run(self) -> None:
        if self.__extras.deathsig is not None and sys.platform == 'linux':
            libc.prctl(libc.PR_SET_PDEATHSIG, self.__extras.deathsig, 0, 0, 0, 0)

        super().run()


class ExtrasSpawnContext(mp.context.SpawnContext):
    def __init__(self, extras: SpawnExtras = SpawnExtras()) -> None:
        super().__init__()
        self.__extras = extras

    def Process(self, *args: ta.Any, **kwargs: ta.Any):  # type: ignore  # noqa
        return ExtrasSpawnProcess(*args, extras=self.__extras, **kwargs)


##


class PipeDeathPact:
    def __init__(
            self,
            *,
            interval_s: float = .5,
    ) -> None:
        super().__init__()

        self._interval_s = interval_s

        self._rfd: int | None = None
        self._wfd: int | None = None
        self._last_check_t: float | None = None

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(rfd={self._rfd}, wfd={self._wfd})'

    @property
    def fd(self) -> int:
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

    def die(self) -> None:
        os.kill(os.getpid(), signal.SIGTERM)
        sys.exit(1)

    def should_die(self) -> bool:
        try:
            buf = os.read(self._rfd, 1)
        except BlockingIOError:
            return False

        if buf:
            print(
                f'{self.__class__.__name__}: Read data from pipe fd={self._rfd}! '
                f'This should not happen! Process state corrupt!',
                file=sys.stderr,
            )
            self.die()

        return True

    def maybe_die(self) -> None:
        if self.should_die():
            self.die()

    def maybe_check(self) -> None:
        if self._last_check_t is None or (time.monotonic() - self._last_check_t) >= self._interval_s:
            self.maybe_die()
            self._last_check_t = time.monotonic()
