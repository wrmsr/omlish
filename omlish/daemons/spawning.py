import abc
import functools
import os
import sys
import threading
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from ..diag import pydevd


if ta.TYPE_CHECKING:
    import multiprocessing as mp
    import multiprocessing.context
    import multiprocessing.process  # noqa

    from ..multiprocessing import spawn as omp_spawn

else:
    mp = lang.proxy_import('multiprocessing', extras=['context', 'process'])
    subprocess = lang.proxy_import('subprocess')

    omp_spawn = lang.proxy_import('..multiprocessing.spawn', __package__)


##


class Spawning(dc.Case):
    pass


class Spawn(dc.Frozen, final=True):
    fn: ta.Callable[[], None]

    _: dc.KW_ONLY

    inherit_fds: ta.Collection[int] | None = None


class Spawner(lang.ContextManaged, abc.ABC):
    @abc.abstractmethod
    def spawn(self, spawn: Spawn) -> None:
        raise NotImplementedError


class InProcessSpawner(Spawner, abc.ABC):
    pass


@functools.singledispatch
def spawner_for(spawning: Spawning) -> Spawner:
    raise TypeError(spawning)


##


class MultiprocessingSpawning(Spawning, kw_only=True):
    # Defaults to 'fork' if under pydevd, else 'spawn'
    start_method: str | None = None

    non_daemon: bool = False


class MultiprocessingSpawner(Spawner):
    def __init__(self, spawning: MultiprocessingSpawning) -> None:
        super().__init__()

        self._spawning = spawning
        self._process: ta.Optional['mp.process.BaseProcess'] = None  # noqa

    def _process_cls(self, spawn: Spawn) -> type['mp.process.BaseProcess']:
        if (start_method := self._spawning.start_method) is None:
            # Unfortunately, pydevd forces the use of the 'fork' start_method, which cannot be mixed with 'spawn':
            #   https://github.com/python/cpython/blob/a7427f2db937adb4c787754deb4c337f1894fe86/Lib/multiprocessing/spawn.py#L102  # noqa
            if pydevd.is_running():
                start_method = 'fork'
            else:
                start_method = 'spawn'

        ctx: 'mp.context.BaseContext'  # noqa
        if start_method == 'fork':
            ctx = mp.get_context(check.non_empty_str(start_method))

        elif start_method == 'spawn':
            ctx = omp_spawn.ExtrasSpawnContext(omp_spawn.SpawnExtras(
                pass_fds=frozenset(spawn.inherit_fds) if spawn.inherit_fds is not None else None,
            ))

        else:
            raise ValueError(start_method)

        return ctx.Process  # type: ignore

    def spawn(self, spawn: Spawn) -> None:
        check.none(self._process)
        self._process = self._process_cls(spawn)(
            target=spawn.fn,
            daemon=not self._spawning.non_daemon,
        )
        self._process.start()


@spawner_for.register
def _(spawning: MultiprocessingSpawning) -> MultiprocessingSpawner:
    return MultiprocessingSpawner(spawning)


##


class ForkSpawning(Spawning):
    pass


class ForkSpawner(Spawner, dc.Frozen):
    spawning: ForkSpawning

    def spawn(self, spawn: Spawn) -> None:
        if (pid := os.fork()):  # noqa
            return

        try:
            spawn.fn()
        except BaseException:  # noqa
            sys.exit(1)
        else:
            sys.exit(0)

        raise RuntimeError('Unreachable')  # noqa


@spawner_for.register
def _(spawning: ForkSpawning) -> ForkSpawner:
    return ForkSpawner(spawning)


##


class ThreadSpawning(Spawning, kw_only=True):
    non_daemon: bool = False


class ThreadSpawner(InProcessSpawner):
    def __init__(self, spawning: ThreadSpawning) -> None:
        super().__init__()

        self._spawning = spawning
        self._thread: threading.Thread | None = None

    def spawn(self, spawn: Spawn) -> None:
        check.none(self._thread)
        self._thread = threading.Thread(
            target=spawn.fn,
            daemon=not self._spawning.non_daemon,
        )
        self._thread.start()


@spawner_for.register
def _(spawning: ThreadSpawning) -> ThreadSpawner:
    return ThreadSpawner(spawning)
