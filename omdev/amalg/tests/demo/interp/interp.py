#!/usr/bin/env python3
"""
TODO:
 - install (git clone) pyenv
 - https://github.com/asdf-vm/asdf support (instead of pyenv)
 - free-threading https://github.com/pyenv/pyenv/commit/d660c5a84f6b03a94961eb0e49adb2b25cd091b1
"""
import argparse
import sys
import typing as ta

from ....std.logging import setup_standard_logging
from ....std.runtime import check_runtime_version
from .resolvers import LinuxResolver
from .resolvers import MacResolver


def _resolve_cmd(args) -> None:
    if sys.platform == 'darwin':
        resolver_cls = MacResolver
    elif sys.platform in ['linux', 'linux2']:
        resolver_cls = LinuxResolver
    else:
        raise OSError(f'Unsupported platform: {sys.platform}')

    resolver = resolver_cls(
        args.version,
        debug=args.debug,
    )

    resolved = resolver.resolve()
    if resolved is None:
        raise RuntimeError(f'Failed to resolve python version: {args.version}')
    print(resolved)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    parser_resolve = subparsers.add_parser('resolve')
    parser_resolve.add_argument('version')
    parser_resolve.add_argument('--debug', action='store_true')
    parser_resolve.set_defaults(func=_resolve_cmd)

    return parser


def _main(argv: ta.Optional[ta.Sequence[str]] = None) -> None:
    check_runtime_version()
    setup_standard_logging()

    parser = _build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
