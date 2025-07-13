import urllib.request

from omlish import check
from omlish.daemons.spawning import ForkSpawning  # noqa
from omlish.daemons.spawning import MultiprocessingSpawning  # noqa
from omlish.daemons.spawning import ThreadSpawning  # noqa
from omlish.sockets.bind import TcpSocketBinder
from omlish.sockets.wait import socket_can_connect
from omlish.sockets.wait import socket_wait_until_can_connect

from .service import mc_server_service_daemon


##


class McServerClient:
    def prompt(
            self,
            prompt: str,
            *,
            launch: bool = False,
            timeout: float = 60.,
    ) -> str:
        ssd = mc_server_service_daemon()

        server_config = ssd.service_config().server
        port = check.isinstance(server_config.bind, TcpSocketBinder.Config).port

        #

        if launch:
            if not socket_can_connect(
                ('localhost', port),
                timeout=timeout,
            ):
                daemon = ssd.daemon_()
                daemon.launch()

                if daemon.config.pid_file is not None:
                    check.state(daemon.is_pidfile_locked())

                socket_wait_until_can_connect(
                    ('localhost', port),
                    timeout=timeout,
                )

        elif not socket_can_connect(
                ('localhost', port),
                timeout=timeout,
        ):
            raise Exception(f'Cannot connect to server on port {port}')

        #

        with urllib.request.urlopen(urllib.request.Request(
                f'http://localhost:{port}/',
                data=prompt.encode('utf-8'),
        )) as resp:
            resp_str = resp.read().decode('utf-8')

        return resp_str
