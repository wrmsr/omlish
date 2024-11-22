# ruff: noqa: UP006 UP007
import errno
import os
import re
import resource
import typing as ta
import warnings

from omlish.lite.logs import log

from .configs import ServerConfig
from .datatypes import gid_for_uid
from .datatypes import name_to_uid
from .poller import Poller
from .privileges import drop_privileges
from .states import SupervisorState
from .types import Process
from .types import ServerContext
from .utils import mktempfile
from .utils import real_exit
from .utils import try_unlink
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

        if config.user is not None:
            uid = name_to_uid(config.user)
            self._uid: ta.Optional[int] = uid
            self._gid: ta.Optional[int] = gid_for_uid(uid)
        else:
            self._uid = None
            self._gid = None

        self._unlink_pidfile = False

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


    def clear_auto_child_logdir(self) -> None:
        # must be called after realize()
        child_logdir = self.config.child_logdir
        fnre = re.compile(rf'.+?---{self.config.identifier}-\S+\.log\.?\d{{0,4}}')
        try:
            filenames = os.listdir(child_logdir)
        except OSError:
            log.warning('Could not clear child_log dir')
            return

        for filename in filenames:
            if fnre.match(filename):
                pathname = os.path.join(child_logdir, filename)
                try:
                    os.remove(pathname)
                except OSError:
                    log.warning('Failed to clean up %r', pathname)

    def daemonize(self) -> None:
        self._poller.before_daemonize()
        self._daemonize()
        self._poller.after_daemonize()

    def _daemonize(self) -> None:
        # To daemonize, we need to become the leader of our own session (process) group.  If we do not, signals sent to
        # our parent process will also be sent to us.   This might be bad because signals such as SIGINT can be sent to
        # our parent process during normal (uninteresting) operations such as when we press Ctrl-C in the parent
        # terminal window to escape from a logtail command. To disassociate ourselves from our parent's session group we
        # use os.setsid.  It means "set session id", which has the effect of disassociating a process from is current
        # session and process group and setting itself up as a new session leader.
        #
        # Unfortunately we cannot call setsid if we're already a session group leader, so we use "fork" to make a copy
        # of ourselves that is guaranteed to not be a session group leader.
        #
        # We also change directories, set stderr and stdout to null, and change our umask.
        #
        # This explanation was (gratefully) garnered from
        # http://www.cems.uwe.ac.uk/~irjohnso/coursenotes/lrc/system/daemons/d3.htm

        pid = os.fork()
        if pid != 0:
            # Parent
            log.debug('supervisord forked; parent exiting')
            real_exit(0)

        # Child
        log.info('daemonizing the supervisord process')
        if self.config.directory:
            try:
                os.chdir(self.config.directory)
            except OSError as err:
                log.critical("can't chdir into %r: %s", self.config.directory, err)
            else:
                log.info('set current directory: %r', self.config.directory)

        os.dup2(0, os.open('/dev/null', os.O_RDONLY))
        os.dup2(1, os.open('/dev/null', os.O_WRONLY))
        os.dup2(2, os.open('/dev/null', os.O_WRONLY))

        os.setsid()

        os.umask(self.config.umask)

        # XXX Stevens, in his Advanced Unix book, section 13.3 (page 417) recommends calling umask(0) and closing unused
        # file descriptors.  In his Network Programming book, he additionally recommends ignoring SIGHUP and forking
        # again after the setsid() call, for obscure SVR4 reasons.

    def get_auto_child_log_name(self, name: str, identifier: str, channel: str) -> str:
        prefix = f'{name}-{channel}---{identifier}-'
        logfile = mktempfile(
            suffix='.log',
            prefix=prefix,
            dir=self.config.child_logdir,
        )
        return logfile

    def write_pidfile(self) -> None:
        pid = os.getpid()
        try:
            with open(self.config.pidfile, 'w') as f:
                f.write(f'{pid}\n')
        except OSError:
            log.critical('could not write pidfile %s', self.config.pidfile)
        else:
            self._unlink_pidfile = True
            log.info('supervisord started with pid %s', pid)
