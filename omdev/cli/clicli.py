import inspect
import os
import subprocess
import sys
import urllib.parse
import urllib.request

from omlish import __about__
from omlish import argparse as ap

from . import install
from .types import CliModule


DEFAULT_REINSTALL_URL = 'https://raw.githubusercontent.com/wrmsr/omlish/master/omdev/cli/install.py'


class CliCli(ap.Cli):

    @ap.command(name='version')
    def print_version(self) -> None:
        print(__about__.__version__)

    @ap.command(name='revision')
    def print_revision(self) -> None:
        print(__about__.__revision__)

    @ap.command(name='home')
    def print_home(self) -> None:
        print(sys.prefix)

    @ap.command(
        ap.arg('args', nargs=ap.REMAINDER),
        name='python',
        accepts_unknown=True,
    )
    def python_cmd(self) -> None:
        os.execvp(
            sys.executable,
            [
                sys.executable,
                *self.unknown_args,
                *self.args.args,
            ],
        )

    @ap.command(
        ap.arg('--url', default=DEFAULT_REINSTALL_URL),
        ap.arg('--local', action='store_true'),
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

        if self.args.local:
            print('Reinstalling from local installer.')
        else:
            print(f'Reinstalling from script url: {self.args.url}')
        print()

        print('Continue with reinstall? (ctrl-c to cancel)')
        input()

        if self.args.local:
            install_src = inspect.getsource(install)
        else:
            url = self.args.url
            parsed = urllib.parse.urlparse(url)
            if parsed.scheme not in ('https', 'file'):
                raise RuntimeError(f'Insecure url schem: {url}')
            with urllib.request.urlopen(urllib.request.Request(url)) as resp:  # noqa
                install_src = resp.read().decode('utf-8')

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
