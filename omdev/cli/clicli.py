import inspect
import os
import subprocess
import sys

from omlish import __about__
from omlish import argparse as ap

from . import install
from .types import CliModule


class CliCli(ap.Cli):

    @ap.command(name='version')
    def print_version(self) -> None:
        print(__about__.__version__)

    @ap.command(name='revision')
    def print_revision(self) -> None:
        print(__about__.__revision__)

    @ap.command(
        ap.arg('extra_deps', nargs='*'),
    )
    def reinstall(self) -> None:
        mod_name = globals()['__spec__'].name
        tool_name = '.'.join([mod_name.partition('.')[0], 'tools', 'piptools'])

        out = subprocess.check_output([
            sys.executable,
            '-m',
            tool_name,
            'list-root-dists',
        ]).decode()

        deps = sorted(
            ({s for l in out.splitlines() if (s := l.strip())} | set(self.args.extra_deps or []))
            - {install.DEFAULT_CLI_PKG}  # noqa
        )

        if deps:
            print('Reinstalling with following additional dependencies:')
            print('\n'.join('  ' + d for d in deps))
        else:
            print('No additional dependencies detected.')
        print()
        print('Continue with reinstall? (ctrl-c to cancel)')
        input()

        install_src = inspect.getsource(install)

        os.execl(
            sys.executable,
            sys.executable,
            '-c',
            install_src,
            *deps,
        )


# @omlish-manifest
_CLI_MODULE = CliModule('cli', __name__)


def _main() -> None:
    CliCli()()


if __name__ == '__main__':
    _main()
