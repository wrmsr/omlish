import dataclasses as dc
import functools  # noqa
import logging
import os.path
import tempfile
import time
import typing as ta
import urllib.request

from ... import check
from ... import lang  # noqa
from ...http.coro.simple import make_simple_http_server
from ...http.handlers import LoggingHttpHandler
from ...http.handlers import StringResponseHttpHandler
from ...logs import all as logs
from ...sockets.bind import SocketBinder
from ..daemon import Daemon
from ..services import Service
from ..spawning import ForkSpawning  # noqa
from ..spawning import MultiprocessingSpawning  # noqa
from ..spawning import ThreadSpawning  # noqa
from ..targets import NameTarget  # noqa
from ..targets import Target


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


class HiService(Service['HiService.Config']):
    @dc.dataclass(frozen=True, kw_only=True)
    class Config(Service.Config):
        server: HiServer.Config = HiServer.Config()

    def __init__(self, config: Config = Config()) -> None:
        super().__init__(config)

        self._server = HiServer(config.server)

    def _run(self) -> None:
        self._server.run()


##


HI_SERVICE_CONFIG = HiService.Config()


def hi_service_config() -> HiService.Config:
    return HiService.Config()


##


def run_hi_server() -> None:
    HiServer.run_config(HiServer.Config())


##


@dc.dataclass(frozen=True)
class Hi:
    server: HiServer.Config = HiServer.Config()
    daemon: Daemon.Config = Daemon.Config()


##


def _main() -> None:
    logs.configure_standard_logging('DEBUG')

    temp_dir = tempfile.mkdtemp()
    pid_file = os.path.join(temp_dir, 'daemon_demo.pid')
    log.info('pid_file: %s', pid_file)

    #

    hi = Hi()

    daemon = Daemon(
        target=Target.of(
            # functools.partial(HiServer.run_config, hi.server),
            # '.'.join([lang.get_real_module_name(globals()), 'run_hi_server']),
            # NameTarget.for_obj(run_hi_server, no_module_name_lookup=True),
            # 'omlish.daemons.tests.demo.run_hi_server',
            'omlish.daemons.tests.demo.hi_service_config',
        ),
        config=dc.replace(
            hi.daemon,
            spawning=ThreadSpawning(),
            # spawning=MultiprocessingSpawning(),
            # spawning=ForkSpawning(),
        ),
    )

    daemon.launch()

    #

    if daemon.config.pid_file is not None:
        check.state(daemon.is_pidfile_locked())

    req_str = 'Hi! How are you?'

    with urllib.request.urlopen(urllib.request.Request(
        f'http://localhost:{hi.server.port}/',
        data=req_str.encode('utf-8'),
    )) as resp:
        resp_str = resp.read().decode('utf-8')

    log.info('Response: %r', resp_str)

    for i in range(10, 0, -1):
        log.info('Parent process sleeping %d', i)
        time.sleep(1.)


if __name__ == '__main__':
    _main()
