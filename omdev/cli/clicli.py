import inspect
import os
import re
import shlex
import subprocess
import sys
import typing as ta
import urllib.parse
import urllib.request

from omlish import __about__
from omlish import lang
from omlish.argparse import all as ap
from omlish.os.temp import temp_dir_context

from ..pip import get_root_dists
from ..pip import lookup_latest_package_version
from . import install
from .types import CliModule


##


DEFAULT_REINSTALL_URL = 'https://raw.githubusercontent.com/wrmsr/omlish/master/omdev/cli/install.py'


_VALID_VERSION_STR = re.compile(r'\d+(\.\d+(\.\d+(\.dev\d+)?)?)?')


def _parse_latest_version_str(s: str) -> str:
    if not _VALID_VERSION_STR.fullmatch(s):
        raise ValueError(f'Invalid version string: {s}')
    return s


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
        ap.arg('--no-deps', action='store_true'),
        ap.arg('--no-uv', action='store_true'),
        ap.arg('--dry-run', action='store_true'),
        ap.arg('--version'),
        ap.arg('extra_deps', nargs='*'),
    )
    def reinstall(self) -> None:
        latest_version = _parse_latest_version_str(lookup_latest_package_version(__package__.split('.')[0]))

        if self.args.version is not None:
            target_version: str = self.args.version
        else:
            target_version = latest_version

        #

        dep_set: set[str] = set(self.args.extra_deps or [])
        if not self.args.no_deps:
            root_dists = get_root_dists()
            dep_set.update(set(root_dists))
        deps = sorted(dep_set - {install.DEFAULT_CLI_PKG})  # noqa

        #

        if lang.can_import('venv'):
            print('Checking venv install')

            with temp_dir_context() as tmp_dir:
                venv_dir = os.path.join(tmp_dir, 'venv')
                subprocess.check_call([
                    sys.executable,
                    '-m', 'venv',
                    venv_dir,
                ])
                venv_exe = os.path.join(venv_dir, 'bin', 'python')

                subprocess.check_call([
                    venv_exe,
                    '-m', 'ensurepip',
                    '--upgrade',
                ])

                if self.args.no_uv:
                    pip_install_cmd = [
                        venv_exe,
                        '-m', 'pip',
                        'install',
                    ]
                else:
                    subprocess.check_call([
                        venv_exe,
                        '-m', 'pip',
                        'install',
                        'uv',
                    ])
                    pip_install_cmd = [
                        venv_exe,
                        '-m', 'uv',
                        'pip',
                        'install',
                        '--refresh',
                    ]

                subprocess.check_call([
                    *pip_install_cmd,
                    '--dry-run',
                    f'{install.DEFAULT_CLI_PKG}=={target_version}',
                    *deps,
                ])

                print('venv install check successful')

        else:
            print('venv not present, cannot check install')

        print()

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
        print(f'Target version: {target_version}')
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

            reco_cmd = ' '.join([
                'curl -LsSf',
                f"'{url}'" if (qu := shlex.quote(url)) == url else qu,
                f'| python3 - --version {shlex.quote(target_version)}',
                *deps,
            ])
            print(f'Recovery command:\n\n{reco_cmd}\n')

            with urllib.request.urlopen(urllib.request.Request(url)) as resp:  # noqa
                install_src = resp.read().decode('utf-8')

        if self.args.dry_run:
            return

        os.execl(
            sys.executable,
            sys.executable,
            '-c', install_src,
            '--version', target_version,
            *deps,
        )


# @omlish-manifest
_CLI_MODULE = CliModule('cli', __name__)


def _main() -> None:
    CliCli()()


if __name__ == '__main__':
    _main()
