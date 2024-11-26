# ruff: noqa: UP006 UP007
import os
import re
import resource
import typing as ta
import warnings

from omlish.lite.cached import cached_nullary
from omlish.lite.logs import log

from .configs import ServerConfig
from .privileges import drop_privileges
from .setup import DaemonizeListeners
from .setup import SupervisorSetup
from .setup import SupervisorUser
from .types import ServerEpoch
from .utils.fs import try_unlink
from .utils.os import real_exit
from .utils.ostypes import Rc


##


class SupervisorSetupImpl(SupervisorSetup):
    def __init__(
            self,
            *,
            config: ServerConfig,
            user: ta.Optional[SupervisorUser] = None,
            epoch: ServerEpoch = ServerEpoch(0),
            daemonize_listeners: DaemonizeListeners = DaemonizeListeners([]),
    ) -> None:
        super().__init__()

        self._config = config
        self._user = user
        self._epoch = epoch
        self._daemonize_listeners = daemonize_listeners

    #

    @property
    def first(self) -> bool:
        return not self._epoch

    #

    @cached_nullary
    def setup(self) -> None:
        if not self.first:
            # prevent crash on libdispatch-based systems, at least for the first request
            self._cleanup_fds()

        self._set_uid_or_exit()

        if self.first:
            self._set_rlimits_or_exit()

        # this sets the options.logger object delay logger instantiation until after setuid
        if not self._config.nocleanup:
            # clean up old automatic logs
            self._clear_auto_child_logdir()

        if not self._config.nodaemon and self.first:
            self._daemonize()

        # writing pid file needs to come *after* daemonizing or pid will be wrong
        self._write_pidfile()

    @cached_nullary
    def cleanup(self) -> None:
        self._cleanup_pidfile()

    #

    def _cleanup_fds(self) -> None:
        # try to close any leaked file descriptors (for reload)
        start = 5
        os.closerange(start, self._config.min_fds)

    #

    def _set_uid_or_exit(self) -> None:
        """
        Set the uid of the supervisord process. Called during supervisord startup only. No return value. Exits the
        process via usage() if privileges could not be dropped.
        """

        if self._user is None:
            if os.getuid() == 0:
                warnings.warn(
                    'Supervisor is running as root. Privileges were not dropped because no user is specified in the '
                    'config file. If you intend to run as root, you can set user=root in the config file to avoid '
                    'this message.',
                )
        else:
            msg = drop_privileges(self._user.uid)
            if msg is None:
                log.info('Set uid to user %s succeeded', self._user.uid)
            else:  # failed to drop privileges
                raise RuntimeError(msg)

    #

    def _set_rlimits_or_exit(self) -> None:
        """
        Set the rlimits of the supervisord process. Called during supervisord startup only. No return value. Exits the
        process via usage() if any rlimits could not be set.
        """

        limits = []

        if hasattr(resource, 'RLIMIT_NOFILE'):
            limits.append({
                'msg': (
                    'The minimum number of file descriptors required to run this process is %(min_limit)s as per the '
                    '"min_fds" command-line argument or config file setting. The current environment will only allow '
                    'you to open %(hard)s file descriptors. Either raise the number of usable file descriptors in '
                    'your environment (see README.rst) or lower the min_fds setting in the config file to allow the '
                    'process to start.'
                ),
                'min': self._config.min_fds,
                'resource': resource.RLIMIT_NOFILE,
                'name': 'RLIMIT_NOFILE',
            })

        if hasattr(resource, 'RLIMIT_NPROC'):
            limits.append({
                'msg': (
                    'The minimum number of available processes required to run this program is %(min_limit)s as per '
                    'the "minprocs" command-line argument or config file setting. The current environment will only '
                    'allow you to open %(hard)s processes. Either raise the number of usable processes in your '
                    'environment (see README.rst) or lower the minprocs setting in the config file to allow the '
                    'program to start.'
                ),
                'min': self._config.min_procs,
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

    #

    _unlink_pidfile = False

    def _write_pidfile(self) -> None:
        pid = os.getpid()
        try:
            with open(self._config.pidfile, 'w') as f:
                f.write(f'{pid}\n')
        except OSError:
            log.critical('could not write pidfile %s', self._config.pidfile)
        else:
            self._unlink_pidfile = True
            log.info('supervisord started with pid %s', pid)

    def _cleanup_pidfile(self) -> None:
        if self._unlink_pidfile:
            try_unlink(self._config.pidfile)

    #

    def _clear_auto_child_logdir(self) -> None:
        # must be called after realize()
        child_logdir = self._config.child_logdir
        if child_logdir == '/dev/null':
            return

        fnre = re.compile(rf'.+?---{self._config.identifier}-\S+\.log\.?\d{{0,4}}')
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

    #

    def _daemonize(self) -> None:
        for dl in self._daemonize_listeners:
            dl.before_daemonize()

        self._do_daemonize()

        for dl in self._daemonize_listeners:
            dl.after_daemonize()

    def _do_daemonize(self) -> None:
        # To daemonize, we need to become the leader of our own session (process) group. If we do not, signals sent to
        # our parent process will also be sent to us. This might be bad because signals such as SIGINT can be sent to
        # our parent process during normal (uninteresting) operations such as when we press Ctrl-C in the parent
        # terminal window to escape from a logtail command. To disassociate ourselves from our parent's session group we
        # use os.setsid. It means "set session id", which has the effect of disassociating a process from is current
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
            real_exit(Rc(0))

        # Child
        log.info('daemonizing the supervisord process')
        if self._config.directory:
            try:
                os.chdir(self._config.directory)
            except OSError as err:
                log.critical("can't chdir into %r: %s", self._config.directory, err)
            else:
                log.info('set current directory: %r', self._config.directory)

        os.dup2(0, os.open('/dev/null', os.O_RDONLY))
        os.dup2(1, os.open('/dev/null', os.O_WRONLY))
        os.dup2(2, os.open('/dev/null', os.O_WRONLY))

        # XXX Stevens, in his Advanced Unix book, section 13.3 (page 417) recommends calling umask(0) and closing unused
        # file descriptors. In his Network Programming book, he additionally recommends ignoring SIGHUP and forking
        # again after the setsid() call, for obscure SVR4 reasons.
        os.setsid()
        os.umask(self._config.umask)
