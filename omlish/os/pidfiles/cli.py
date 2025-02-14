import typing as ta

from ...argparse import all as ap
from ..pidfiles.pidfile import Pidfile


class Cli(ap.Cli):
    _PID_FILE_ARGS: ta.ClassVar[ta.Sequence[ap.Arg]] = [
        ap.arg('pid-file'),
        ap.arg('--create', action='store_true'),
    ]

    def _args_pid_file(self) -> Pidfile:
        return Pidfile(
            self.args.pid_file,
            no_create=not self._args.create,
        )

    #

    @ap.cmd(*_PID_FILE_ARGS)
    def read(self) -> None:
        with self._args_pid_file() as pf:
            print(pf.read())

    @ap.cmd(*_PID_FILE_ARGS)
    def pin(self) -> None:
        raise NotImplementedError

    @ap.cmd(*_PID_FILE_ARGS)
    def kill(self) -> None:
        raise NotImplementedError


def _main() -> None:
    Cli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
