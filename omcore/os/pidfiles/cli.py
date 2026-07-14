# @om-lite
# @om-amalg ../../../omdev/scripts/pidfiles.py
"""
TODO:
 - F_SETLK mode
"""
import os
import typing as ta

from ...argparse.cli import ArgparseCli
from ...argparse.parsers import ArgparseArg
from ...argparse.parsers import argparse_arg
from ...argparse.parsers import argparse_cmd
from ...lite.args import Args
from ..pidfiles.pidfile import Pidfile
from ..pidfiles.pinning import PidfilePinner
from ..signals import parse_signal


##


class Cli(ArgparseCli):
    _PIDFILE_ARGS: ta.ClassVar[ta.Sequence[ArgparseArg]] = [
        argparse_arg('pid-file'),
        argparse_arg('--create', action='store_true'),
    ]

    def _pidfile_args(self) -> Args:
        return Args(
            self.args.pid_file,
            inheritable=False,
            no_create=not self._args.create,
        )

    def _args_pidfile(self) -> Pidfile:
        return self._pidfile_args()(Pidfile)

    #

    @argparse_cmd(*_PIDFILE_ARGS)
    def read_no_verify(self) -> None:
        with self._args_pidfile() as pidfile:
            print(pidfile.read())

    @argparse_cmd(*_PIDFILE_ARGS)
    def lock(self) -> None:
        with self._args_pidfile() as pidfile:
            pidfile.acquire_lock()
            print(os.getpid())
            input()

    #

    _PIDFILE_PINNER_ARGS: ta.ClassVar[ta.Sequence[ArgparseArg]] = [
        *_PIDFILE_ARGS,
        argparse_arg('--timeout', type=float),
    ]

    def _pidfile_pinner_args(self) -> Args:
        return self._pidfile_args().update(
            timeout=self._args.timeout,
        )

    def _args_pidfile_pinner(self) -> ta.ContextManager[int]:
        return self._pidfile_pinner_args()(PidfilePinner.default_impl()().pin_pidfile_owner)

    #

    @argparse_cmd(*_PIDFILE_PINNER_ARGS)
    def read(self) -> None:
        with self._args_pidfile_pinner() as pid:
            print(pid)

    @argparse_cmd(*_PIDFILE_PINNER_ARGS)
    def pin(self) -> None:
        with self._args_pidfile_pinner() as pid:
            print(pid)
            input()

    @argparse_cmd(
        *_PIDFILE_PINNER_ARGS,
        argparse_arg('signal'),
    )
    def kill(self) -> None:
        sig = parse_signal(self._args.signal)
        with self._args_pidfile_pinner() as pid:
            os.kill(pid, sig)


def _main() -> None:
    Cli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
