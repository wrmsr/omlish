import functools
import logging
import os.path
import signal
import time
import urllib.request

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

from .server import LlmServer


log = logging.getLogger(__name__)


##


PID_FILE = 'llmd.pid'


class Cli(ap.Cli):
    @ap.cmd()
    def demo(self) -> None:
        server_config = LlmServer.Config()

        daemon = Daemon(
            FnTarget(functools.partial(LlmServer.run_config, server_config)),
            Daemon.Config(
                spawning=(spawning := ThreadSpawning()),
                # spawning=(spawning := MultiprocessingSpawning()),
                # spawning=(spawning := ForkSpawning()),

                reparent_process=not isinstance(spawning, ThreadSpawning),

                pid_file=PID_FILE,
                wait=ConnectWait(('localhost', server_config.port)),

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
            f'http://localhost:{server_config.port}/',
            data='Hi! How are you?'.encode('utf-8'),
        )) as resp:
            log.info('Parent got response: %s', resp.read().decode('utf-8'))

        for i in range(60, 0, -1):
            log.info(f'Parent process {os.getpid()} sleeping {i}')
            time.sleep(1.)

    @ap.cmd()
    def pid(self) -> None:
        with PidfilePinner.default_impl()().pin_pidfile_owner(PID_FILE) as pid:
            print(pid)

    @ap.cmd()
    def kill(self) -> None:
        with PidfilePinner.default_impl()().pin_pidfile_owner(PID_FILE) as pid:
            log.info('Killing pid: %d', pid)
            os.kill(pid, signal.SIGTERM)


##


def _main() -> None:
    logs.configure_standard_logging('DEBUG')

    Cli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
