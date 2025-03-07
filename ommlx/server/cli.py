import contextlib
import logging
import os.path
import signal
import typing as ta
import urllib.request

from omlish import check
from omlish.argparse import all as ap
from omlish.daemons.spawning import ForkSpawning  # noqa
from omlish.daemons.spawning import MultiprocessingSpawning  # noqa
from omlish.daemons.spawning import ThreadSpawning  # noqa
from omlish.logs import all as logs
from omlish.os.pidfiles.pinning import PidfilePinner
from omlish.secrets.tests.harness import HarnessSecrets  # noqa
from omlish.sockets.bind import TcpSocketBinder
from omlish.sockets.wait import socket_wait_until_can_connect

from .service import mc_service_daemon


log = logging.getLogger(__name__)


##


class McCli(ap.Cli):
    @ap.cmd()
    def launch(self) -> None:
        mc_service_daemon().daemon_().launch()

    @ap.cmd(
        ap.arg('prompt'),
    )
    def demo(self) -> None:
        daemon = mc_service_daemon().daemon_()
        if daemon.config.pid_file is not None:
            check.state(daemon.is_pidfile_locked())

        server_config = mc_service_daemon().service_config().server
        port = check.isinstance(server_config.bind, TcpSocketBinder.Config).port

        socket_wait_until_can_connect(
            ('localhost', port),
            timeout=5.,
        )

        req_str = 'Hi! How are you?'

        with urllib.request.urlopen(urllib.request.Request(
                f'http://localhost:{port}/',
                data=req_str.encode('utf-8'),
        )) as resp:
            resp_str = resp.read().decode('utf-8')

        log.info('Response: %r', resp_str)

    #

    @contextlib.contextmanager
    def _pin_pid(self) -> ta.Iterator[int]:
        pid_file = check.non_empty_str(mc_service_daemon().daemon_config().pid_file)
        with PidfilePinner.default_impl()().pin_pidfile_owner(pid_file) as pid:
            yield pid

    @ap.cmd()
    def pid(self) -> None:
        with self._pin_pid() as pid:
            print(pid)

    @ap.cmd()
    def kill(self) -> None:
        with self._pin_pid() as pid:
            log.info('Killing pid: %d', pid)
            os.kill(pid, signal.SIGTERM)


##


def _main() -> None:
    logs.configure_standard_logging('DEBUG')

    McCli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
