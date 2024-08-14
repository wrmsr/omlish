#!/usr/bin/env python3
# @omdev-amalg ../scripts/interp2.py
"""
TODO:
 - partial best-matches - '3.12'
 - https://github.com/asdf-vm/asdf support (instead of pyenv) ?
"""
# ruff: noqa: UP007
import argparse
import collections
import typing as ta

from ..amalg.std.logs import configure_standard_logging
from ..amalg.std.runtime import check_runtime_version
from .providers.base import InterpProvider
from .providers.base import RunningInterpProvider
from .providers.pyenv import PyenvInterpProvider
from .providers.system import SystemInterpProvider
from .providers.types import InterpSpecifier


class Resolver:
    def __init__(
            self,
            providers: ta.Sequence[ta.Tuple[str, InterpProvider]],
    ) -> None:
        super().__init__()
        self._providers: ta.Mapping[str, InterpProvider] = collections.OrderedDict(providers)

    def list(self, spec: InterpSpecifier) -> None:
        print('installed:')
        for n, p in self._providers.items():
            lst = [
                si
                for si in p.get_installed_versions(spec)
                if spec.contains(si)
            ]
            if lst:
                print(f'  {n}')
                for si in lst:
                    print(f'    {si}')

        print()

        print('installable:')
        for n, p in self._providers.items():
            lst = [
                si
                for si in p.get_installable_versions(spec)
                if spec.contains(si)
            ]
            if lst:
                print(f'  {n}')
                for si in lst:
                    print(f'    {si}')


def _resolve_cmd(args) -> None:
    r = Resolver([
        ('running', RunningInterpProvider()),
        ('pyenv', PyenvInterpProvider()),
        ('system', SystemInterpProvider()),
    ])

    s = InterpSpecifier.parse(args.version)

    r.list(s)


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
