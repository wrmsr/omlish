import inspect
import os
import subprocess
import sys
import typing as ta
import urllib.parse
import urllib.request

from omlish import __about__
from omlish import lang
from omlish.argparse import all as ap

from ..pip import get_root_dists
from ..pip import lookup_latest_package_version
from . import install
from .types import CliModule


DEFAULT_REINSTALL_URL = 'https://raw.githubusercontent.com/wrmsr/omlish/master/omdev/cli/install.py'


class CliCli(ap.Cli):

    #

    @ap.cmd(name='version', aliases=['ver'])
    def print_version(self) -> None:
        print(__about__.__version__)

    @ap.cmd(name='revision', aliases=['rev'])
    def print_revision(self) -> None:
        print(__about__.__revision__)

    @ap.cmd(name='home')
    def print_home(self) -> None:
        print(sys.prefix)

    #

    def _passthrough_args_cmd(
            self,
            exe: str,
            pre_args: ta.Sequence[str] = (),
            post_args: ta.Sequence[str] = (),
    ) -> ta.NoReturn:
        os.execvp(
            exe,
            [
                sys.executable,
                *pre_args,
                *self.unknown_args,
                *self.args.args,
                *post_args,
            ],
        )

    @ap.cmd(
        ap.arg('args', nargs=ap.REMAINDER),
        name='python',
        accepts_unknown=True,
    )
    def python_cmd(self) -> None:
        self._passthrough_args_cmd(sys.executable)

    @ap.cmd(
        ap.arg('args', nargs=ap.REMAINDER),
        name='pip',
        accepts_unknown=True,
    )
    def pip_cmd(self) -> None:
        self._passthrough_args_cmd(sys.executable, ['-m', 'pip'])

    #

    @ap.cmd(
        ap.arg('--url', default=DEFAULT_REINSTALL_URL),
        ap.arg('--local', action='store_true'),
        ap.arg('extra_deps', nargs='*'),
    )
    def reinstall(self) -> None:
        latest_version = lookup_latest_package_version(__package__.split('.')[0])

        #

        root_dists = get_root_dists()
        deps = sorted(
            (set(root_dists) | set(self.args.extra_deps or []))
            - {install.DEFAULT_CLI_PKG}  # noqa
        )

        #

        if lang.can_import('pip'):
            print('Checking pip install')
            subprocess.check_call([
                sys.executable,
                '-m',
                'pip',
                'install',
                '--dry-run',
                *deps,
            ])
            print('Pip install check successful')
        else:
            print('Pip not present, cannot check install')

        #

        if deps:
            print('Reinstalling with following additional dependencies:')
            print('\n'.join('  ' + d for d in deps))
        else:
            print('No additional dependencies detected.')
        print()

        #

        if self.args.local:
            print('Reinstalling from local installer.')
        else:
            print(f'Reinstalling from script url: {self.args.url}')
        print()

        #

        print(f'Current version: {__about__.__version__}')
        print(f'Latest version: {latest_version}')
        print()

        #

        print('Continue with reinstall? (ctrl-c to cancel)')
        input()

        #

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
