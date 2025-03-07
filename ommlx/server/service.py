"""
TODO:
 - debug launch
"""
import dataclasses as dc
import logging
import os.path

from omdev.home.paths import get_home_paths
from omlish import cached
from omlish import check
from omlish.daemons import spawning
from omlish.daemons.daemon import Daemon
from omlish.daemons.services import Service
from omlish.daemons.services import ServiceDaemon
from omlish.daemons.services import ServiceTarget
from omlish.logs import all as logs

from .server import McServer


log = logging.getLogger(__name__)


##


class McService(Service['McService.Config']):
    @dc.dataclass(frozen=True)
    class Config(Service.Config):
        server: McServer.Config = McServer.Config()

    def __init__(self, config: Config = Config()) -> None:
        super().__init__(config)

        self._server = McServer(config.server)

    @property
    def server(self) -> McServer:
        return self._server

    def _run(self) -> None:
        self._server.run()


##


def _mc_service_multiprocessing_entrypoint(args: spawning.MultiprocessingSpawning.EntrypointArgs) -> None:
    svc = check.isinstance(check.isinstance(args.spawn.target, ServiceTarget).svc, McService)  # noqa

    if args.start_method == spawning.MultiprocessingSpawning.StartMethod.SPAWN:
        log_file = os.path.join(get_home_paths().log_dir, 'minichain', 'server.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        logs.configure_standard_logging(
            'DEBUG',
            handler_factory=lambda: logging.FileHandler(log_file),
        )

    log.debug('%r', args)

    args.spawn.fn()


@cached.function(lock=True)
def mc_service_daemon() -> ServiceDaemon[McService, McService.Config]:
    pid_file = os.path.join(get_home_paths().run_dir, 'minichain', 'server.pid')

    return ServiceDaemon(
        McService.Config(
            McServer.Config(),
        ),

        Daemon.Config(
            # spawning=spawning.ThreadSpawning(),
            spawning=spawning.MultiprocessingSpawning(entrypoint=_mc_service_multiprocessing_entrypoint),
            # spawning=spawning.ForkSpawning(),

            pid_file=pid_file,

            reparent_process=True,
        ),
    )
