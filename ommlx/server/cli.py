import functools
import logging
import os.path
import signal
import time
import urllib.request

from omdev.home.paths import get_run_dir
from omlish import cached
from omlish import check
from omlish.argparse import all as ap
from omlish.daemons.daemon import Daemon
from omlish.daemons.spawning import ForkSpawning  # noqa
from omlish.daemons.spawning import MultiprocessingSpawning  # noqa
from omlish.daemons.spawning import ThreadSpawning  # noqa
from omlish.daemons.targets import FnTarget
from omlish.daemons.waiting import ConnectWait
from omlish.logs import all as logs
from omlish.os.pidfiles.pinning import PidfilePinner
from omlish.secrets.tests.harness import HarnessSecrets  # noqa
from omlish.sockets.bind import TcpSocketBinder

from .server import Server


log = logging.getLogger(__name__)


##


class Cli(ap.Cli):
    @cached.function
    def pid_file(self) -> str:
        return os.path.join(get_run_dir(), 'minichain', 'server', 'pid')

    @ap.cmd()
    def demo(self) -> None:
        server_config = Server.Config(
            backend='local',
        )
        port = check.isinstance(server_config.bind, TcpSocketBinder.Config).port

        pid_file = self.pid_file()
        os.makedirs(os.path.dirname(pid_file), exist_ok=True)

        daemon = Daemon(
            FnTarget(functools.partial(Server.run_config, server_config)),
            Daemon.Config(
                spawning=(spawning := ThreadSpawning()),
                # spawning=(spawning := MultiprocessingSpawning()),
                # spawning=(spawning := ForkSpawning()),

                reparent_process=not isinstance(spawning, ThreadSpawning),

                pid_file=pid_file,
                wait=ConnectWait(('localhost', port)),

                wait_timeout=10.,
            ),
        )

        if not daemon.is_pidfile_locked():
            daemon.launch()

        #

        if daemon.config.pid_file is not None:
            check.state(daemon.is_pidfile_locked())

        log.info('Client continuing')

        with urllib.request.urlopen(urllib.request.Request(
            f'http://localhost:{port}/',
            data='Hi! How are you?'.encode('utf-8'),  # noqa
        )) as resp:
            log.info('Parent got response: %s', resp.read().decode('utf-8'))

        for i in range(60, 0, -1):
            log.info('Parent process %d sleeping %d', os.getpid(), i)
            time.sleep(1.)

    @ap.cmd()
    def pid(self) -> None:
        with PidfilePinner.default_impl()().pin_pidfile_owner(self.pid_file()) as pid:
            print(pid)

    @ap.cmd()
    def kill(self) -> None:
        with PidfilePinner.default_impl()().pin_pidfile_owner(self.pid_file()) as pid:
            log.info('Killing pid: %d', pid)
            os.kill(pid, signal.SIGTERM)


##


def _main() -> None:
    logs.configure_standard_logging('DEBUG')

    Cli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
