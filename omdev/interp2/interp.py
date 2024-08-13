#!/usr/bin/env python3
# @omdev-amalg ../scripts/interp2.py
"""
TODO:
 - partial best-matches - '3.12'
 - https://github.com/asdf-vm/asdf support (instead of pyenv) ?
"""
# ruff: noqa: UP007
import argparse
import typing as ta

from ..amalg.std.logs import configure_standard_logging
from ..amalg.std.runtime import check_runtime_version
from .providers.system import SystemInterpProvider


def _resolve_cmd(args) -> None:
    for i in SystemInterpProvider().installed_versions():
        print(i)


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
    configure_standard_logging()

    parser = _build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
