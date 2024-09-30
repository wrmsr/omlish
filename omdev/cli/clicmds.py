import argparse
import inspect
import os
import subprocess
import sys

from omlish import __about__

from . import install
from .types import CliModule


def _print_version(args) -> None:
    print(__about__.__version__)


def _print_revision(args) -> None:
    print(__about__.__revision__)


def _reinstall(args) -> None:
    mod_name = globals()['__spec__'].name
    tool_name = '.'.join([mod_name.partition('.')[0], 'tools', 'piptools'])

    out = subprocess.check_output([
        sys.executable,
        '-m',
        tool_name,
        'list-root-dists',
    ]).decode()

    deps = sorted(
        ({s for l in out.splitlines() if (s := l.strip())} | set(args.extra_deps or []))
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
        '-c',
        install_src,
    )


# @omlish-manifest
_CLI_MODULE = CliModule('cli', __name__)


def _main(argv=None) -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_version = subparsers.add_parser('version')
    parser_version.set_defaults(func=_print_version)

    parser_revision = subparsers.add_parser('revision')
    parser_revision.set_defaults(func=_print_revision)

    parser_reinstall = subparsers.add_parser('reinstall')
    parser_reinstall.add_argument('extra_deps', nargs='*')
    parser_reinstall.set_defaults(func=_reinstall)

    args = parser.parse_args(argv)
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
