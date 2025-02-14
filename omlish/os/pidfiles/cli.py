"""
TODO:
 - F_SETLK mode
 - timeout [kw]arg for pin
"""
import os
import typing as ta

from ... import lang
from ...argparse import all as ap
from ..pidfiles.pidfile import Pidfile
from ..pidfiles.pinning import PidfilePinner
from ..signals import parse_signal


class Cli(ap.Cli):
    _PID_FILE_ARGS: ta.ClassVar[ta.Sequence[ap.Arg]] = [
        ap.arg('pid-file'),
        ap.arg('--create', action='store_true'),
    ]

    def _pid_file_args(self) -> lang.Args:
        return lang.Args(
            self.args.pid_file,
            inheritable=False,
            no_create=not self._args.create,
        )

    def _args_pidfile(self) -> Pidfile:
        return self._pid_file_args()(Pidfile)

    def _args_pidfile_pinner(self) -> ta.ContextManager[int]:
        return self._pid_file_args()(PidfilePinner.default_impl()().pin_pidfile_owner)

    #

    @ap.cmd(*_PID_FILE_ARGS)
    def read(self) -> None:
        with self._args_pidfile() as pf:
            print(pf.read())

    @ap.cmd(*_PID_FILE_ARGS)
    def pin(self) -> None:
        with self._args_pidfile_pinner() as pid:
            print(pid)
            input()

    @ap.cmd(
        *_PID_FILE_ARGS,
        ap.arg('signal'),
    )
    def kill(self) -> None:
        sig = parse_signal(self._args.signal)
        with self._args_pidfile_pinner() as pid:
            os.kill(pid, sig)


def _main() -> None:
    Cli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
