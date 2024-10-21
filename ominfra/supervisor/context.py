# ruff: noqa: UP006 UP007
import errno
import fcntl
import grp
import logging
import os
import pwd
import re
import resource
import signal
import stat
import typing as ta
import warnings

from .compat import SignalReceiver
from .compat import close_fd
from .compat import mktempfile
from .compat import real_exit
from .compat import try_unlink
from .configs import ServerConfig
from .datatypes import gid_for_uid
from .datatypes import name_to_uid
from .exceptions import NoPermissionError
from .exceptions import NotExecutableError
from .exceptions import NotFoundError
from .poller import Poller
from .states import SupervisorState
from .states import SupervisorStates
from .types import AbstractServerContext
from .types import AbstractSubprocess


log = logging.getLogger(__name__)


class ServerContext(AbstractServerContext):
    first = False
    test = False

    ##

    def __init__(self, config: ServerConfig) -> None:
        super().__init__()

        self._config = config

        self._pid_history: ta.Dict[int, AbstractSubprocess] = {}
        self._state: SupervisorState = SupervisorStates.RUNNING

        self.signal_receiver = SignalReceiver()

        self.poller = Poller()

        if self.config.user is not None:
            uid = name_to_uid(self.config.user)
            self.uid = uid
            self.gid = gid_for_uid(uid)
        else:
            self.uid = None
            self.gid = None

        self.unlink_pidfile = False

    @property
    def config(self) -> ServerConfig:
        return self._config

    @property
    def state(self) -> SupervisorState:
        return self._state

    def set_state(self, state: SupervisorState) -> None:
        self._state = state

    @property
    def pid_history(self) -> ta.Dict[int, AbstractSubprocess]:
        return self._pid_history

    uid: ta.Optional[int]
    gid: ta.Optional[int]

    ##

    def set_signals(self) -> None:
        self.signal_receiver.install(
            signal.SIGTERM,
            signal.SIGINT,
            signal.SIGQUIT,
            signal.SIGHUP,
            signal.SIGCHLD,
            signal.SIGUSR2,
        )

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

    def set_uid_or_exit(self) -> None:
        """
        Set the uid of the supervisord process.  Called during supervisord startup only.  No return value.  Exits the
        process via usage() if privileges could not be dropped.
        """
        if self.uid is None:
            if os.getuid() == 0:
                warnings.warn(
                    'Supervisor is running as root.  Privileges were not dropped because no user is specified in the '
                    'config file.  If you intend to run as root, you can set user=root in the config file to avoid '
                    'this message.',
                )
        else:
            msg = drop_privileges(self.uid)
            if msg is None:
                log.info('Set uid to user %s succeeded', self.uid)
            else:  # failed to drop privileges
                raise RuntimeError(msg)

    def set_rlimits_or_exit(self) -> None:
        """
        Set the rlimits of the supervisord process.  Called during supervisord startup only.  No return value.  Exits
        the process via usage() if any rlimits could not be set.
        """

        limits = []

        if hasattr(resource, 'RLIMIT_NOFILE'):
            limits.append({
                'msg': (
                    'The minimum number of file descriptors required to run this process is %(min_limit)s as per the '
                    '"minfds" command-line argument or config file setting. The current environment will only allow '
                    'you to open %(hard)s file descriptors.  Either raise the number of usable file descriptors in '
                    'your environment (see README.rst) or lower the minfds setting in the config file to allow the '
                    'process to start.'
                ),
                'min': self.config.minfds,
                'resource': resource.RLIMIT_NOFILE,
                'name': 'RLIMIT_NOFILE',
            })

        if hasattr(resource, 'RLIMIT_NPROC'):
            limits.append({
                'msg': (
                    'The minimum number of available processes required to run this program is %(min_limit)s as per '
                    'the "minprocs" command-line argument or config file setting. The current environment will only '
                    'allow you to open %(hard)s processes.  Either raise the number of usable processes in your '
                    'environment (see README.rst) or lower the minprocs setting in the config file to allow the '
                    'program to start.'
                ),
                'min': self.config.minprocs,
                'resource': resource.RLIMIT_NPROC,
                'name': 'RLIMIT_NPROC',
            })

        for limit in limits:
            min_limit = limit['min']
            res = limit['resource']
            msg = limit['msg']
            name = limit['name']

            soft, hard = resource.getrlimit(res)  # type: ignore

            # -1 means unlimited
            if soft < min_limit and soft != -1:  # type: ignore
                if hard < min_limit and hard != -1:  # type: ignore
                    # setrlimit should increase the hard limit if we are root, if not then setrlimit raises and we print
                    # usage
                    hard = min_limit  # type: ignore

                try:
                    resource.setrlimit(res, (min_limit, hard))  # type: ignore
                    log.info('Increased %s limit to %s', name, min_limit)
                except (resource.error, ValueError):
                    raise RuntimeError(msg % dict(  # type: ignore  # noqa
                        min_limit=min_limit,
                        res=res,
                        name=name,
                        soft=soft,
                        hard=hard,
                    ))

    def cleanup(self) -> None:
        if self.unlink_pidfile:
            try_unlink(self.config.pidfile)
        self.poller.close()

    def cleanup_fds(self) -> None:
        # try to close any leaked file descriptors (for reload)
        start = 5
        os.closerange(start, self.config.minfds)

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
        self.poller.before_daemonize()
        self._daemonize()
        self.poller.after_daemonize()

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

    def get_signal(self) -> ta.Optional[int]:
        return self.signal_receiver.get_signal()

    def write_pidfile(self) -> None:
        pid = os.getpid()
        try:
            with open(self.config.pidfile, 'w') as f:
                f.write(f'{pid}\n')
        except OSError:
            log.critical('could not write pidfile %s', self.config.pidfile)
        else:
            self.unlink_pidfile = True
            log.info('supervisord started with pid %s', pid)


def drop_privileges(user: ta.Union[int, str, None]) -> ta.Optional[str]:
    """
    Drop privileges to become the specified user, which may be a username or uid.  Called for supervisord startup
    and when spawning subprocesses.  Returns None on success or a string error message if privileges could not be
    dropped.
    """
    if user is None:
        return 'No user specified to setuid to!'

    # get uid for user, which can be a number or username
    try:
        uid = int(user)
    except ValueError:
        try:
            pwrec = pwd.getpwnam(user)  # type: ignore
        except KeyError:
            return f"Can't find username {user!r}"
        uid = pwrec[2]
    else:
        try:
            pwrec = pwd.getpwuid(uid)
        except KeyError:
            return f"Can't find uid {uid!r}"

    current_uid = os.getuid()

    if current_uid == uid:
        # do nothing and return successfully if the uid is already the current one.  this allows a supervisord
        # running as an unprivileged user "foo" to start a process where the config has "user=foo" (same user) in
        # it.
        return None

    if current_uid != 0:
        return "Can't drop privilege as nonroot user"

    gid = pwrec[3]
    if hasattr(os, 'setgroups'):
        user = pwrec[0]
        groups = [grprec[2] for grprec in grp.getgrall() if user in grprec[3]]

        # always put our primary gid first in this list, otherwise we can lose group info since sometimes the first
        # group in the setgroups list gets overwritten on the subsequent setgid call (at least on freebsd 9 with
        # python 2.7 - this will be safe though for all unix /python version combos)
        groups.insert(0, gid)
        try:
            os.setgroups(groups)
        except OSError:
            return 'Could not set groups of effective user'
    try:
        os.setgid(gid)
    except OSError:
        return 'Could not set group id of effective user'
    os.setuid(uid)
    return None


def make_pipes(stderr=True) -> ta.Mapping[str, int]:
    """
    Create pipes for parent to child stdin/stdout/stderr communications.  Open fd in non-blocking mode so we can
    read them in the mainloop without blocking.  If stderr is False, don't create a pipe for stderr.
    """

    pipes: ta.Dict[str, ta.Optional[int]] = {
        'child_stdin': None,
        'stdin': None,
        'stdout': None,
        'child_stdout': None,
        'stderr': None,
        'child_stderr': None,
    }
    try:
        stdin, child_stdin = os.pipe()
        pipes['child_stdin'], pipes['stdin'] = stdin, child_stdin
        stdout, child_stdout = os.pipe()
        pipes['stdout'], pipes['child_stdout'] = stdout, child_stdout
        if stderr:
            stderr, child_stderr = os.pipe()
            pipes['stderr'], pipes['child_stderr'] = stderr, child_stderr
        for fd in (pipes['stdout'], pipes['stderr'], pipes['stdin']):
            if fd is not None:
                flags = fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NDELAY
                fcntl.fcntl(fd, fcntl.F_SETFL, flags)
        return pipes  # type: ignore
    except OSError:
        for fd in pipes.values():
            if fd is not None:
                close_fd(fd)
        raise


def close_parent_pipes(pipes: ta.Mapping[str, int]) -> None:
    for fdname in ('stdin', 'stdout', 'stderr'):
        fd = pipes.get(fdname)
        if fd is not None:
            close_fd(fd)


def close_child_pipes(pipes: ta.Mapping[str, int]) -> None:
    for fdname in ('child_stdin', 'child_stdout', 'child_stderr'):
        fd = pipes.get(fdname)
        if fd is not None:
            close_fd(fd)


def check_execv_args(filename, argv, st) -> None:
    if st is None:
        raise NotFoundError(f"can't find command {filename!r}")

    elif stat.S_ISDIR(st[stat.ST_MODE]):
        raise NotExecutableError(f'command at {filename!r} is a directory')

    elif not (stat.S_IMODE(st[stat.ST_MODE]) & 0o111):
        raise NotExecutableError(f'command at {filename!r} is not executable')

    elif not os.access(filename, os.X_OK):
        raise NoPermissionError(f'no permission to run command {filename!r}')
