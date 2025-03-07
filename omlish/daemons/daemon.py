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
import itertools
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
        spawning: Spawning | None = None

        #

        pid_file: str | None = None

        #

        # TODO: None, defaults, figure out from spawn method
        reparent_process: bool = False

        launched_timeout_s: float = 5.

        #

        wait: Wait | None = None

        wait_timeout: lang.TimeoutLike = 10.
        wait_sleep_s: float = .1

        #

        def __post_init__(self) -> None:
            check.isinstance(self.pid_file, (str, None))

    def __init__(
            self,
            target: Target,
            config: Config = Config(),
    ) -> None:
        super().__init__()

        self._target = target
        self._config = config

    @property
    def target(self) -> Target:
        return self._target

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

    def is_pidfile_locked(self) -> bool:
        check.state(self.has_pidfile)

        if not os.path.isfile(check.non_empty_str(self._config.pid_file)):
            return False

        with self._non_inheritable_pidfile() as pf:
            return not pf.try_acquire_lock()

    #

    def wait_sync(
            self,
            timeout: lang.TimeoutLike = lang.Timeout.Default,
            *,
            max_tries: int | None = None,
    ) -> None:
        if self._config.wait is None:
            return

        timeout = lang.Timeout.of(timeout, self._config.wait_timeout)
        waiter = waiter_for(self._config.wait)
        for i in itertools.count():
            if max_tries is not None and i >= max_tries:
                raise TimeoutError
            timeout()
            if waiter.do_wait():
                break
            time.sleep(self._config.wait_sleep_s or 0.)

    #

    def launch_no_wait(self) -> bool:
        launcher = Launcher(
            target=self._target,
            spawning=check.not_none(self._config.spawning),

            pid_file=self._config.pid_file,
            reparent_process=self._config.reparent_process,
            launched_timeout_s=self._config.launched_timeout_s,
        )

        return launcher.launch()

    def launch(self, timeout: lang.TimeoutLike = lang.Timeout.Default) -> None:
        self.launch_no_wait()

        self.wait_sync(timeout)
