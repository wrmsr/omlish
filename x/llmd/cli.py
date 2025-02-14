import dataclasses as dc
import logging
import os.path
import sys
import tempfile
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
from omlish.secrets.tests.harness import HarnessSecrets  # noqa

from .server import PORT
from .server import llm_server_main


log = logging.getLogger(__name__)


##


class Cli(ap.Cli):
    @ap.cmd()
    def demo(self) -> None:
        temp_dir = tempfile.mkdtemp()
        pid_file = os.path.join(temp_dir, 'daemon_demo.pid')
        print(f'{pid_file=}')

        #

        daemon = Daemon(Daemon.Config(
            target=FnTarget(llm_server_main),

            spawning=ThreadSpawning(),
            # spawning=MultiprocessingSpawning(),
            # spawning=ForkSpawning(),

            # reparent_process=True,

            # pid_file=pid_file,
            wait=ConnectWait(('localhost', PORT)),
        ))

        daemon.launch()

        #

        if daemon.config.pid_file is not None:
            check.state(daemon.is_running())

        with urllib.request.urlopen(urllib.request.Request(
            f'http://localhost:{PORT}/',
            data='Hi! How are you?'.encode('utf-8'),
        )) as resp:
            print(resp.read().decode('utf-8'))

        for i in range(10, 0, -1):
            print(f'parent process {os.getpid()} sleeping {i}', file=sys.stderr)
            time.sleep(1.)


##


def _main() -> None:
    logs.configure_standard_logging('DEBUG')

    Cli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
