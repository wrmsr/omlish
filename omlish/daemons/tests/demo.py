import dataclasses as dc
import functools
import logging
import os.path
import tempfile
import time
import typing as ta
import urllib.request

from ... import check
from ...http.coro.simple import make_simple_http_server
from ...http.handlers import LoggingHttpHandler
from ...http.handlers import StringResponseHttpHandler
from ...logs import all as logs
from ...sockets.bind import SocketBinder
from ..daemon import Daemon
from ..spawning import ForkSpawning  # noqa
from ..spawning import MultiprocessingSpawning  # noqa
from ..spawning import ThreadSpawning  # noqa
from ..targets import FnTarget
from ..waiting import ConnectWait


log = logging.getLogger(__name__)


##


class HiServer:
    @dc.dataclass(frozen=True)
    class Config:
        DEFAULT_PORT: ta.ClassVar[int] = 5066
        port: int = DEFAULT_PORT

    def __init__(self, config: Config = Config()) -> None:
        super().__init__()

        self._config = config

    def run(self) -> None:
        log.info('Server running')
        try:

            with make_simple_http_server(
                    SocketBinder.Config.of(self._config.port),
                    LoggingHttpHandler(StringResponseHttpHandler('Hi!'), log),
            ) as server:

                deadline = time.time() + 10.
                with server.loop_context(poll_interval=5.) as loop:
                    for _ in loop:
                        if time.time() >= deadline:
                            break

        finally:
            log.info('Server exiting')

    @classmethod
    def run_config(cls, config: Config) -> None:
        return cls(config).run()


##


def _main() -> None:
    logs.configure_standard_logging('DEBUG')

    temp_dir = tempfile.mkdtemp()
    pid_file = os.path.join(temp_dir, 'daemon_demo.pid')
    log.info('pid_file: %s', pid_file)

    #

    hi_config = HiServer.Config()

    daemon = Daemon(Daemon.Config(
        target=FnTarget(functools.partial(HiServer.run_config, hi_config)),

        spawning=ThreadSpawning(),
        # spawning=MultiprocessingSpawning(),
        # spawning=ForkSpawning(),

        # reparent_process=True,

        # pid_file=pid_file,
        wait=ConnectWait(('localhost', hi_config.port)),
    ))

    daemon.launch()

    #

    if daemon.config.pid_file is not None:
        check.state(daemon.is_pidfile_locked())

    req_str = 'Hi! How are you?'

    with urllib.request.urlopen(urllib.request.Request(
        f'http://localhost:{hi_config.port}/',
        data=req_str.encode('utf-8'),
    )) as resp:
        resp_str = resp.read().decode('utf-8')

    log.info('Response: %r', resp_str)

    for i in range(10, 0, -1):
        log.info('Parent process sleeping %d', i)
        time.sleep(1.)


if __name__ == '__main__':
    _main()
