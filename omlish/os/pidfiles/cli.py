"""
TODO:
 - F_SETLK mode
"""
import os
import typing as ta

from ... import lang
from ...argparse import all as ap
from ..pidfiles.pidfile import Pidfile
from ..pidfiles.pinning import PidfilePinner
from ..signals import parse_signal


##


class Cli(ap.Cli):
    _PIDFILE_ARGS: ta.ClassVar[ta.Sequence[ap.Arg]] = [
        ap.arg('pid-file'),
        ap.arg('--create', action='store_true'),
    ]

    def _pidfile_args(self) -> lang.Args:
        return lang.Args(
            self.args.pid_file,
            inheritable=False,
            no_create=not self._args.create,
        )

    def _args_pidfile(self) -> Pidfile:
        return self._pidfile_args()(Pidfile)

    #

    @ap.cmd(*_PIDFILE_ARGS)
    def read_no_verify(self) -> None:
        with self._args_pidfile() as pidfile:
            print(pidfile.read())

    @ap.cmd(*_PIDFILE_ARGS)
    def lock(self) -> None:
        with self._args_pidfile() as pidfile:
            pidfile.acquire_lock()
            print(os.getpid())
            input()

    #

    _PIDFILE_PINNER_ARGS: ta.ClassVar[ta.Sequence[ap.Arg]] = [
        *_PIDFILE_ARGS,
        ap.arg('--timeout', type=float),
    ]

    def _pidfile_pinner_args(self) -> lang.Args:
        return self._pidfile_args().update(
            timeout=self._args.timeout,
        )

    def _args_pidfile_pinner(self) -> ta.ContextManager[int]:
        return self._pidfile_pinner_args()(PidfilePinner.default_impl()().pin_pidfile_owner)

    #

    @ap.cmd(*_PIDFILE_PINNER_ARGS)
    def read(self) -> None:
        with self._args_pidfile_pinner() as pid:
            print(pid)

    @ap.cmd(*_PIDFILE_PINNER_ARGS)
    def pin(self) -> None:
        with self._args_pidfile_pinner() as pid:
            print(pid)
            input()

    @ap.cmd(
        *_PIDFILE_PINNER_ARGS,
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
