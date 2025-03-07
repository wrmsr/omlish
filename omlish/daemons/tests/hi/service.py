import dataclasses as dc
import logging
import os.path
import time
import typing as ta

from .... import cached
from .... import check
from ....http.coro.simple import make_simple_http_server
from ....http.handlers import LoggingHttpHandler
from ....http.handlers import StringResponseHttpHandler
from ....logs import all as logs
from ....sockets.bind import SocketBinder
from ... import spawning
from ...daemon import Daemon
from ...services import Service
from ...services import ServiceDaemon
from ...services import ServiceTarget


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

    @property
    def config(self) -> Config:
        return self._config

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
    @dc.dataclass(frozen=True)
    class Config(Service.Config):
        server: HiServer.Config = HiServer.Config()

    def __init__(self, config: Config = Config()) -> None:
        super().__init__(config)

        self._server = HiServer(config.server)

    @property
    def server(self) -> HiServer:
        return self._server

    def _run(self) -> None:
        self._server.run()


##


def _hi_service_multiprocessing_entrypoint(args: spawning.MultiprocessingSpawning.EntrypointArgs) -> None:
    svc = check.isinstance(check.isinstance(args.spawn.target, ServiceTarget).svc, HiService)  # noqa

    if args.start_method == spawning.MultiprocessingSpawning.StartMethod.SPAWN:
        logs.configure_standard_logging('DEBUG')

    args.spawn.fn()


@cached.function(lock=True)
def hi_service_daemon() -> ServiceDaemon[HiService, HiService.Config]:
    # FIXME: lol
    pid_file = os.path.abspath(os.path.join(os.getcwd(), 'hi.pid'))

    return ServiceDaemon(
        HiService.Config(
            HiServer.Config(),
        ),

        Daemon.Config(
            # spawning=spawning.ThreadSpawning(),
            spawning=spawning.MultiprocessingSpawning(entrypoint=_hi_service_multiprocessing_entrypoint),
            # spawning=spawning.ForkSpawning(),

            pid_file=pid_file,
        ),
    )
