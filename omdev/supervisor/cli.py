"""
TODO:
 - omlish.daemon?
  - add subprocess backend? is that 'too weak' to justify the daemon subsystem?
 - classic daemon cli - start/stop/status
 - STRICTLY USE AMALG SCRIPT ONLY
"""
import os
import sys
import typing as ta

from omlish import lang
from omlish.argparse import all as ap


##


@lang.cached_function
def import_script() -> ta.Any:
    from ominfra.scripts import supervisor  # noqa

    return supervisor


@lang.cached_function
def script_path() -> ta.Any:
    return import_script().__file__


##


class Cli(ap.Cli):
    @ap.cmd()
    def path(self) -> None:
        print(script_path())

    @ap.cmd(
        ap.arg('args', nargs=ap.REMAINDER),
        accepts_unknown=True,
    )
    def run(self) -> None:
        exe = sys.executable
        fp = script_path()

        os.execvp(
            exe,
            [
                exe,
                fp,
                *self.unknown_args,
                *(self.args.args or []),
            ],
        )


def _main() -> None:
    Cli()()


if __name__ == '__main__':
    _main()
