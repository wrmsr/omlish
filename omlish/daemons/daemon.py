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
import logging
import os.path
import time

from .. import check
from .. import dataclasses as dc
from .. import lang
from ..os.pidfiles.pidfile import Pidfile
from .launching import Launcher
from .spawning import Spawning
from .targets import Target
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

        pid_file: str | None = None

        #

        reparent_process: bool = False
        launched_timeout_s: float = 5.

        #

        wait: Wait | None = None

        wait_timeout: lang.TimeoutLike = 10.
        wait_sleep_s: float = .1

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

    def wait_sync(self, timeout: lang.TimeoutLike = lang.Timeout.Default) -> None:
        if self._config.wait is None:
            return

        timeout = lang.Timeout.of(timeout, self._config.wait_timeout)
        waiter = waiter_for(self._config.wait)
        while not waiter.do_wait():
            timeout()
            time.sleep(self._config.wait_sleep_s or 0.)

    #

    def launch_no_wait(self) -> None:
        launcher = Launcher(
            target=self._config.target,
            spawning=self._config.spawning,

            pid_file=self._config.pid_file,
            reparent_process=self._config.reparent_process,
            launched_timeout_s=self._config.launched_timeout_s,
        )

        launcher.launch()

    def launch(self, timeout: lang.TimeoutLike = lang.Timeout.Default) -> None:
        self.launch_no_wait()

        self.wait_sync(timeout)
