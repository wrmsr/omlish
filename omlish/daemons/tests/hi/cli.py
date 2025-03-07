import functools  # noqa
import logging
import urllib.request

from ....argparse import all as ap
from .... import check
from ....logs import all as logs
from ....sockets.wait import socket_wait_until_can_connect
from .service import hi_service_daemon


log = logging.getLogger(__name__)


##


class HiCli(ap.Cli):
    @ap.cmd()
    def launch(self) -> None:
        daemon = hi_service_daemon().daemon_()

        daemon.launch()

    @ap.cmd()
    def post(self) -> None:
        daemon = hi_service_daemon().daemon_()

        if daemon.config.pid_file is not None:
            check.state(daemon.is_pidfile_locked())

        server_config = hi_service_daemon().service_config().server
        port = server_config.port

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


def _main() -> None:
    logs.configure_standard_logging('DEBUG')

    HiCli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
