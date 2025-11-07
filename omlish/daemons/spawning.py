import abc
import enum
import functools
import os
import threading
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from ..diag import pydevd
from .targets import Target


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

    target: Target | None = None

    inherit_fds: ta.Collection[int] | None = None


class Spawner(lang.ContextManaged, lang.Abstract):
    @abc.abstractmethod
    def spawn(self, spawn: Spawn) -> None:
        raise NotImplementedError


class InProcessSpawner(Spawner, lang.Abstract):
    pass


@functools.singledispatch
def spawner_for(spawning: Spawning) -> Spawner:
    raise TypeError(spawning)


##


class MultiprocessingSpawning(Spawning, kw_only=True):
    class StartMethod(enum.Enum):
        SPAWN = enum.auto()
        FORK = enum.auto()
        # TODO: FORK_SERVER

    # Defaults to 'fork' if under pydevd, else 'spawn'
    start_method: StartMethod | None = None

    #

    # Note: Per multiprocessing docs, `no_linger=True` processes (corresponding to `Process(daemon=True)`) cannot spawn
    # subprocesses, and thus will fail if `Daemon.Config.reparent_process` is set.
    no_linger: bool = False

    #

    @dc.dataclass(frozen=True, kw_only=True)
    class EntrypointArgs:
        spawning: 'MultiprocessingSpawning'
        spawn: Spawn
        start_method: 'MultiprocessingSpawning.StartMethod'

    entrypoint: ta.Callable[[EntrypointArgs], None] | None = None


class MultiprocessingSpawner(Spawner):
    def __init__(self, spawning: MultiprocessingSpawning) -> None:
        super().__init__()

        self._spawning = spawning
        self._process: ta.Optional['mp.process.BaseProcess'] = None  # noqa

    @lang.cached_function
    def _determine_start_method(self) -> 'MultiprocessingSpawning.StartMethod':
        if (start_method := self._spawning.start_method) is not None:
            return start_method

        # Unfortunately, pydevd forces the use of the 'fork' start_method, which cannot be mixed with 'spawn':
        #   https://github.com/python/cpython/blob/a7427f2db937adb4c787754deb4c337f1894fe86/Lib/multiprocessing/spawn.py#L102  # noqa
        if pydevd.is_running():
            return MultiprocessingSpawning.StartMethod.FORK

        return MultiprocessingSpawning.StartMethod.SPAWN

    def _process_cls(self, spawn: Spawn) -> type['mp.process.BaseProcess']:
        start_method = self._determine_start_method()

        ctx: 'mp.context.BaseContext'  # noqa
        if start_method == MultiprocessingSpawning.StartMethod.FORK:
            ctx = mp.get_context(check.non_empty_str('fork'))

        elif start_method == MultiprocessingSpawning.StartMethod.SPAWN:
            ctx = omp_spawn.ExtrasSpawnContext(omp_spawn.SpawnExtras(
                pass_fds=frozenset(spawn.inherit_fds) if spawn.inherit_fds is not None else None,
            ))

        else:
            raise ValueError(start_method)

        return ctx.Process  # type: ignore

    def spawn(self, spawn: Spawn) -> None:
        check.none(self._process)

        target: ta.Callable[[], None]
        if (ep := self._spawning.entrypoint) is not None:
            target = functools.partial(ep, MultiprocessingSpawning.EntrypointArgs(
                spawning=self._spawning,
                spawn=spawn,
                start_method=self._determine_start_method(),
            ))
        else:
            target = spawn.fn

        self._process = self._process_cls(spawn)(
            target=target,
            daemon=self._spawning.no_linger,
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
            raise SystemExit(1) from None
        else:
            raise SystemExit(0)

        raise RuntimeError('Unreachable')  # noqa


@spawner_for.register
def _(spawning: ForkSpawning) -> ForkSpawner:
    return ForkSpawner(spawning)


##


class ThreadSpawning(Spawning, kw_only=True):
    linger: bool = False


class ThreadSpawner(InProcessSpawner):
    def __init__(self, spawning: ThreadSpawning) -> None:
        super().__init__()

        self._spawning = spawning
        self._thread: threading.Thread | None = None

    def spawn(self, spawn: Spawn) -> None:
        check.none(self._thread)
        self._thread = threading.Thread(
            target=spawn.fn,
            daemon=not self._spawning.linger,
        )
        self._thread.start()


@spawner_for.register
def _(spawning: ThreadSpawning) -> ThreadSpawner:
    return ThreadSpawner(spawning)
