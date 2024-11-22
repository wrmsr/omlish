# ruff: noqa: UP006 UP007
import errno
import os
import typing as ta

from omlish.lite.logs import log

from .configs import ServerConfig
from .poller import Poller
from .states import SupervisorState
from .types import Process
from .types import ServerContext
from .utils import mktempfile
from .types import ServerEpoch


class ServerContextImpl(ServerContext):
    def __init__(
            self,
            config: ServerConfig,
            poller: Poller,
            *,
            epoch: ServerEpoch = ServerEpoch(0),
    ) -> None:
        super().__init__()

        self._config = config
        self._poller = poller
        self._epoch = epoch

        self._pid_history: ta.Dict[int, Process] = {}
        self._state: SupervisorState = SupervisorState.RUNNING

    @property
    def config(self) -> ServerConfig:
        return self._config

    @property
    def epoch(self) -> ServerEpoch:
        return self._epoch

    @property
    def first(self) -> bool:
        return not self._epoch

    @property
    def state(self) -> SupervisorState:
        return self._state

    def set_state(self, state: SupervisorState) -> None:
        self._state = state

    @property
    def pid_history(self) -> ta.Dict[int, Process]:
        return self._pid_history

    @property
    def uid(self) -> ta.Optional[int]:
        return self._uid

    @property
    def gid(self) -> ta.Optional[int]:
        return self._gid

    ##

    def waitpid(self) -> ta.Tuple[ta.Optional[int], ta.Optional[int]]:
        # Need pthread_sigmask here to avoid concurrent sigchld, but Python doesn't offer in Python < 3.4.  There is
        # still a race condition here; we can get a sigchld while we're sitting in the waitpid call. However, AFAICT, if
        # waitpid is interrupted by SIGCHLD, as long as we call waitpid again (which happens every so often during the
        # normal course in the mainloop), we'll eventually reap the child that we tried to reap during the interrupted
        # call. At least on Linux, this appears to be true, or at least stopping 50 processes at once never left zombies
        # lying around.
        try:
            pid, sts = os.waitpid(-1, os.WNOHANG)
        except OSError as exc:
            code = exc.args[0]
            if code not in (errno.ECHILD, errno.EINTR):
                log.critical('waitpid error %r; a process may not be cleaned up properly', code)
            if code == errno.EINTR:
                log.debug('EINTR during reap')
            pid, sts = None, None
        return pid, sts


    def get_auto_child_log_name(self, name: str, identifier: str, channel: str) -> str:
        prefix = f'{name}-{channel}---{identifier}-'
        logfile = mktempfile(
            suffix='.log',
            prefix=prefix,
            dir=self.config.child_logdir,
        )
        return logfile
