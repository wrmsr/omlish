#!/usr/bin/env python3
# @omdev-amalg ../scripts/interp.py
# ruff: noqa: UP007
"""
TODO:
 - partial best-matches - '3.12'
 - https://github.com/asdf-vm/asdf support (instead of pyenv) ?
 - colon sep provider name prefix - pyenv:3.12
"""
import argparse
import typing as ta

from omlish.lite.check import check_not_none
from omlish.lite.logs import configure_standard_logging
from omlish.lite.runtime import check_runtime_version

from .resolvers import DEFAULT_INTERP_RESOLVER
from .types import InterpSpecifier


def _list_cmd(args) -> None:
    r = DEFAULT_INTERP_RESOLVER
    s = InterpSpecifier.parse(args.version)
    r.list(s)


def _resolve_cmd(args) -> None:
    r = DEFAULT_INTERP_RESOLVER
    s = InterpSpecifier.parse(args.version)
    print(check_not_none(r.resolve(s)).exe)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    parser_list = subparsers.add_parser('list')
    parser_list.add_argument('version')
    parser_list.add_argument('--debug', action='store_true')
    parser_list.set_defaults(func=_list_cmd)

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
