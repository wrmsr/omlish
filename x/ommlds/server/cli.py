import contextlib
import os.path
import signal
import typing as ta

from omlish import check
from omlish.argparse import all as ap
from omlish.daemons.spawning import ForkSpawning  # noqa
from omlish.daemons.spawning import MultiprocessingSpawning  # noqa
from omlish.daemons.spawning import ThreadSpawning  # noqa
from omlish.logs import all as logs
from omlish.os.pidfiles.pinning import PidfilePinner
from omlish.os.signals import parse_signal

from .client import McServerClient
from .service import mc_server_service_daemon


log = logs.get_module_logger(globals())


##


class McServerCli(ap.Cli):
    @ap.cmd()
    def launch(self) -> None:
        mc_server_service_daemon().daemon_().launch()

    @ap.cmd(
        ap.arg('prompt'),
        ap.arg('--no-launch', action='store_true'),
    )
    def prompt(self) -> None:
        print(McServerClient().prompt(
            self.args.prompt,
            launch=not self.args.no_launch,
        ))

    #

    @contextlib.contextmanager
    def _pin_pid(self) -> ta.Iterator[int]:
        pid_file = check.non_empty_str(mc_server_service_daemon().daemon_config().pid_file)
        with PidfilePinner.default_impl()().pin_pidfile_owner(pid_file) as pid:
            yield pid

    @ap.cmd()
    def pid(self) -> None:
        with self._pin_pid() as pid:
            print(pid)

    @ap.cmd(
        ap.arg('signal', nargs='?'),
    )
    def kill(self) -> None:
        if (sig_arg := self.args.signal) is not None:
            sig = parse_signal(sig_arg)
        else:
            sig = signal.SIGTERM

        with self._pin_pid() as pid:
            log.info('Killing pid: %d', pid)
            os.kill(pid, sig)


##


def _main() -> None:
    logs.configure_standard_logging('DEBUG')

    McServerCli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
