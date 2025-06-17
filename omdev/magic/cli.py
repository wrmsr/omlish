# ruff: noqa: UP006 UP007 UP045
import typing as ta

from omlish.argparse.cli import ArgparseCli
from omlish.argparse.cli import argparse_arg
from omlish.argparse.cli import argparse_cmd

from .find import find_magic_files
from .find import find_magic_py_modules
from .styles import C_MAGIC_STYLE
from .styles import PY_MAGIC_STYLE


##


class MagicCli(ArgparseCli):
    @argparse_cmd(
        argparse_arg('--style', '-s', default='py'),
        argparse_arg('--key', '-k', dest='keys', action='append'),
        argparse_arg('--modules', action='store_true'),
        argparse_arg('roots', nargs='*'),
    )
    def find(self) -> None:
        style = {
            'py': PY_MAGIC_STYLE,
            'c': C_MAGIC_STYLE,
        }[self.args.style]

        kw: dict = dict(
            roots=self.args.roots,
            style=style,
            keys=self.args.keys,
        )

        fn: ta.Callable
        if self.args.modules:
            fn = find_magic_py_modules
        else:
            fn = find_magic_files

        for out in fn(**kw):
            print(out)


##


def _main(argv=None) -> None:
    MagicCli(argv).cli_run_and_exit()


if __name__ == '__main__':
    _main()
