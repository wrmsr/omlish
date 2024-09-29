import argparse

from omlish import __about__

from .types import CliModule


def _print_version(args) -> None:
    print(__about__.__version__)


def _print_revision(args) -> None:
    print(__about__.__revision__)


# @omlish-manifest
_CLI_MODULE = CliModule('cli', __name__)


def _main(argv=None) -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_version = subparsers.add_parser('version')
    parser_version.set_defaults(func=_print_version)

    parser_revision = subparsers.add_parser('revision')
    parser_revision.set_defaults(func=_print_revision)

    args = parser.parse_args(argv)
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
