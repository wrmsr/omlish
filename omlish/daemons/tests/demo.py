import os.path
import sys
import tempfile
import time
import urllib.request

from ... import check
from ...http.coro.simple import make_simple_http_server
from ...http.handlers import StringResponseHttpHandler
from ...logs import all as logs
from ...sockets.bind import SocketBinder
from ..daemon import Daemon
from ..spawning import ForkSpawning  # noqa
from ..spawning import MultiprocessingSpawning  # noqa
from ..spawning import ThreadSpawning  # noqa
from ..targets import FnTarget
from ..waiting import ConnectWait


##


PORT = 5066


def hi_server() -> None:
    print(f'server running: {os.getpid()=}', file=sys.stderr)
    try:

        with make_simple_http_server(
                SocketBinder.Config.of(PORT),
                StringResponseHttpHandler('Hi!'),
        ) as server:

            deadline = time.time() + 10.
            with server.loop_context(poll_interval=5.) as loop:
                for _ in loop:
                    if time.time() >= deadline:
                        break

    finally:
        print(f'server exiting: {os.getpid()=}', file=sys.stderr)

#


def _main() -> None:
    logs.configure_standard_logging('DEBUG')

    temp_dir = tempfile.mkdtemp()
    pid_file = os.path.join(temp_dir, 'daemon_demo.pid')
    print(f'{pid_file=}')

    #

    daemon = Daemon(Daemon.Config(
        target=FnTarget(hi_server),

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

    req_str = 'Hi! How are you?'

    with urllib.request.urlopen(urllib.request.Request(
        f'http://localhost:{PORT}/',
        data=req_str.encode('utf-8'),
    )) as resp:
        resp_str = resp.read().decode('utf-8')

    print(resp_str)

    for i in range(10, 0, -1):
        print(f'parent process {os.getpid()} sleeping {i}', file=sys.stderr)
        time.sleep(1.)


if __name__ == '__main__':
    _main()
