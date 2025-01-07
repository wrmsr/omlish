import dataclasses as dc
import multiprocessing as mp
import multiprocessing.popen_spawn_posix
import sys
import typing as ta

from .. import check
from .. import libc


T = ta.TypeVar('T')


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
