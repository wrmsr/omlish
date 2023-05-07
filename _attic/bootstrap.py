"""
TODO:
 - logging
 - env vars, files
 - repl server
 - packaging fixups
 - profiling
 - rlimits
 - chdir
"""
import faulthandler
import gc
import logging
import os
import pwd
import signal
import typing as ta

from . import configs as cfgs
from . import dataclasses as dc
from . import lifecycles as lc
from . import logs


log = logging.getLogger(__name__)


class Bootstrap(cfgs.Configurable['Bootstrap.Config'], lc.ContextManageableLifecycle):

    class Config(cfgs.Config):
        debug: bool = dc.field(False, check_type=bool)

        log: ta.Optional[str] = dc.field('standard', check_type=(str, None))

        setuid: ta.Optional[str] = dc.field(None, check_type=(str, None))
        nice: ta.Optional[int] = dc.field(None, check_type=(int, None))

        gc_debug: bool = dc.field(False, check_type=bool)
        gc_disable: bool = dc.field(False, check_type=bool)

        faulthandler_enabled: bool = dc.field(False, check_type=bool)

        prctl_dumpable: bool = dc.field(False, check_type=bool)
        prctl_deathsig: ta.Union[bool, int, None] = dc.field(False, check_type=(bool, int, None))

    def __init__(self, config: Config = Config()) -> None:
        super().__init__(config)

    def _do_lifecycle_start(self) -> None:
        super()._do_lifecycle_start()

        if self._config.log:
            if self._config.log.lower() == 'standard':
                logs.configure_standard_logging(logging.INFO)
            else:
                raise ValueError(f'Invalid log config value: {self._config.log}')

        if self._config.setuid:
            user = pwd.getpwnam(self._config.setuid)
            log.info(f'Setting uid {user}')
            os.setuid(user.pw_uid)

        if self._config.nice is not None:
            os.nice(self._config.nice)

        if self._config.gc_debug:
            gc.set_debug(gc.DEBUG_STATS)

        if self._config.gc_disable:
            log.warning('Disabling gc')
            gc.disable()

        if self._config.faulthandler_enabled:
            faulthandler.enable()

        if self._config.prctl_dumpable or self._config.prctl_deathsig not in (None, False):
            from omnibus import libc

            if hasattr(libc, 'prctl'):
                if self._config.prctl_dumpable:
                    libc.prctl(libc.PR_SET_DUMPABLE, 1, 0, 0, 0, 0)

                if self._config.prctl_deathsig not in (None, False):
                    sig = self._config.prctl_deathsig if isinstance(self._config.prctl_deathsig, int) else signal.SIGTERM  # noqa
                    libc.prctl(libc.PR_SET_PDEATHSIG, sig, 0, 0, 0, 0)

            else:
                log.warning('No prctl')
