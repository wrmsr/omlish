"""
TODO:
 - OK.. this is useful for non-system-daemons too... which have no pidfile..
 - split out pidfile concern to.. identity?
 - async[io] support, really just waiting
 - helpers for http, json, etc
 - heartbeat? status checks? heartbeat file?
 - zmq
 - cli, cfg reload
 - bootstrap
  - rsrc limit
  - logs
 - https://github.com/Homebrew/homebrew-services
 - deathpacts
 - timebomb
 - pickle protocol, revision / venv check, multiprocessing manager support
"""
import contextlib
import functools
import logging
import os.path
import threading
import time
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from ..os.pidfiles.manager import _PidfileManager  # noqa
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
from .waiting import Wait
from .waiting import waiter_for


log = logging.getLogger(__name__)


##


class Daemon:
    @dc.dataclass(frozen=True, kw_only=True)
    class Config:
        target: Target
        spawning: Spawning

        #

        reparent_process: bool = False

        pid_file: str | None = None

        #

        wait: Wait | None = None

        wait_timeout: lang.TimeoutLike = 10.
        wait_sleep_s: float = .1

        launched_timeout_s: float = 5.

        #

        def __post_init__(self) -> None:
            check.isinstance(self.pid_file, (str, None))

    def __init__(self, config: Config) -> None:
        super().__init__()

        self._config = config

    @property
    def config(self) -> Config:
        return self._config

    #

    @property
    def has_pidfile(self) -> bool:
        return self._config.pid_file is not None

    def _non_inheritable_pidfile(self) -> Pidfile:
        check.state(self.has_pidfile)
        return Pidfile(
            check.non_empty_str(self._config.pid_file),
            inheritable=False,
        )

    def is_running(self) -> bool:
        check.state(self.has_pidfile)

        if not os.path.isfile(check.non_empty_str(self._config.pid_file)):
            return False

        with self._non_inheritable_pidfile() as pf:
            return not pf.try_acquire_lock()

    #

    def _inner_launch(
            self,
            *,
            pidfile_manager: ta.ContextManager | None,
            launched_callback: ta.Callable[[], None] | None = None,
    ) -> None:
        try:
            if self._config.reparent_process:
                log.info('Reparenting')
                reparent_process()

            with contextlib.ExitStack() as es:
                pidfile: Pidfile | None = None  # noqa
                if pidfile_manager is not None:
                    pidfile = check.isinstance(es.enter_context(pidfile_manager), Pidfile)
                    pidfile.write()

                if launched_callback is not None:
                    launched_callback()

                runner = target_runner_for(self._config.target)
                runner.run()

        finally:
            if launched_callback is not None:
                launched_callback()

    def launch_no_wait(self) -> bool:
        with contextlib.ExitStack() as es:
            spawner: Spawner = es.enter_context(spawner_for(self._config.spawning))

            #

            inherit_fds: set[int] = set()
            launched_event: threading.Event | None = None

            pidfile: Pidfile | None = None  # noqa
            pidfile_manager: ta.ContextManager | None = None

            if (pid_file := self._config.pid_file) is not None:
                if not isinstance(spawner, InProcessSpawner):
                    pidfile = es.enter_context(open_inheritable_pidfile(pid_file))
                    pidfile_manager = lang.NopContextManager(pidfile)

                else:
                    check.state(not self._config.reparent_process)
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
                    launched_callback=launched_event.set if launched_event is not None else None,
                ),
                inherit_fds=inherit_fds,
            ))

            if launched_event is not None:
                check.state(launched_event.wait(timeout=self._config.launched_timeout_s))

            return True

    #

    def wait_sync(self, timeout: lang.TimeoutLike = lang.Timeout.Default) -> None:
        if self._config.wait is None:
            return

        timeout = lang.Timeout.of(timeout, self._config.wait_timeout)
        waiter = waiter_for(self._config.wait)
        while not waiter.do_wait():
            timeout()
            time.sleep(self._config.wait_sleep_s or 0.)

    #

    class _NOT_SET(lang.Marker):  # noqa
        pass

    def launch(self, timeout: lang.TimeoutLike = lang.Timeout.Default) -> None:
        self.launch_no_wait()

        self.wait_sync(timeout)
