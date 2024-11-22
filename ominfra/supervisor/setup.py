import abc
import errno
import os
import re
import resource
import typing as ta
import warnings

from omlish.lite.cached import cached_nullary
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


class SupervisorSetup(abc.ABC):
    @abc.abstractmethod
    def setup(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def cleanup(self) -> None:
        raise NotImplementedError


class SupervisorSetupImpl(SupervisorSetup):
    def __init__(
            self,
            *,
            config: ServerConfig,
    ) -> None:
        super().__init__()

        self._config = config

    @cached_nullary
    def setup(self) -> None:
        if not self._context.first:
            # prevent crash on libdispatch-based systems, at least for the first request
            self.cleanup_fds()

        self.set_uid_or_exit()

        if self._context.first:
            self.set_rlimits_or_exit()

        # this sets the options.logger object delay logger instantiation until after setuid
        if not self._context.config.nocleanup:
            # clean up old automatic logs
            self._context.clear_auto_child_logdir()

        if not self._context.config.nodaemon and self._context.first:
            self._context.daemonize()

        # writing pid file needs to come *after* daemonizing or pid will be wrong
        self._context.write_pidfile()

    @cached_nullary
    def cleanup(self) -> None:
        if self._unlink_pidfile:
            try_unlink(self.config.pidfile)

    def cleanup_fds(self) -> None:
        # try to close any leaked file descriptors (for reload)
        start = 5
        os.closerange(start, self.config.minfds)

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
