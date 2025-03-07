"""
TODO:
 - Config? dedupe defaults with Daemon
 - ExitStacked? hold ref to Spawner, which holds refs to thread/proc - which will likely outlive it, but still
"""
import contextlib
import functools
import logging
import threading
import typing as ta

from .. import check
from .. import lang
from ..os.pidfiles.manager import open_inheritable_pidfile
from ..os.pidfiles.pidfile import Pidfile
from .reparent import reparent_process
from .spawning import InProcessSpawner
from .spawning import Spawn
from .spawning import Spawner
from .spawning import Spawning
from .spawning import spawner_for
from .targets import Target
from .targets import target_runner_for


log = logging.getLogger(__name__)


##


class Launcher:
    def __init__(
            self,
            *,
            target: Target,
            spawning: Spawning,

            pid_file: str | None = None,
            reparent_process: bool = False,  # noqa
            launched_timeout_s: float = 5.,
    ) -> None:
        super().__init__()

        self._target = target
        self._spawning = spawning

        self._pid_file = pid_file
        self._reparent_process = reparent_process
        self._launched_timeout_s = launched_timeout_s

    def _inner_launch(
            self,
            *,
            pidfile_manager: ta.ContextManager | None,
            callback: ta.Callable[[], None] | None = None,
    ) -> None:
        callback_called = False

        try:
            if self._reparent_process:
                log.info('Reparenting')
                reparent_process()

            with contextlib.ExitStack() as es:
                pidfile: Pidfile | None = None  # noqa
                if pidfile_manager is not None:
                    pidfile = check.isinstance(es.enter_context(pidfile_manager), Pidfile)
                    pidfile.write()

                if callback is not None:
                    callback_called = True
                    callback()

                runner = target_runner_for(self._target)
                runner.run()

        finally:
            if callback is not None and not callback_called:
                callback()

    def launch(self) -> bool:
        with contextlib.ExitStack() as es:
            spawner: Spawner = es.enter_context(spawner_for(self._spawning))

            #

            inherit_fds: set[int] = set()
            launched_event: threading.Event | None = None

            pidfile: Pidfile | None = None  # noqa
            pidfile_manager: ta.ContextManager | None = None

            if (pid_file := self._pid_file) is not None:
                if not isinstance(spawner, InProcessSpawner):
                    pidfile = es.enter_context(open_inheritable_pidfile(pid_file))
                    pidfile_manager = lang.NopContextManager(pidfile)

                else:
                    check.state(not self._reparent_process)
                    pidfile = es.enter_context(Pidfile(pid_file))
                    pidfile_manager = pidfile.dup()
                    launched_event = threading.Event()

                if not pidfile.try_acquire_lock():
                    return False

                inherit_fds.add(check.isinstance(pidfile.fileno(), int))

            #

            spawner.spawn(Spawn(
                functools.partial(
                    self._inner_launch,
                    pidfile_manager=pidfile_manager,
                    callback=launched_event.set if launched_event is not None else None,
                ),
                target=self._target,
                inherit_fds=inherit_fds,
            ))

            if launched_event is not None:
                check.state(launched_event.wait(timeout=self._launched_timeout_s))

            return True
