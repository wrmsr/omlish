"""
TODO:
 - allow manually specifying manifest packages
 - omlish.bootstrap always
 - https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#creating-executable-scripts
 - https://packaging.python.org/en/latest/specifications/entry-points/#entry-points
"""
import argparse
import functools
import os
import runpy
import sys

from omlish import check

from ..manifests.load import ManifestLoader
from .types import CliModule


def _main() -> None:
    cms: list[CliModule] = []

    ldr = ManifestLoader.from_entry_point(globals())

    pkgs = ldr.discover()
    if not pkgs:
        pkgs = []
        for n in os.listdir(os.getcwd()):
            if os.path.isdir(n) and os.path.exists(os.path.join(n, '__init__.py')):
                pkgs.append(n)

    for m in ldr.load(*pkgs, only=[CliModule]):
        cms.append(check.isinstance(m.value, CliModule))

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    def run(cm: CliModule) -> None:
        sys.argv = [cm.cmd_name, *(args.args or ())]
        runpy._run_module_as_main(cm.mod_name)  # type: ignore  # noqa

    seen: set[str] = set()
    for cm in cms:
        if cm.cmd_name in seen:
            raise NameError(cm)

        cmd_parser = subparsers.add_parser(cm.cmd_name)
        cmd_parser.add_argument('args', nargs=argparse.REMAINDER)
        cmd_parser.set_defaults(func=functools.partial(run, cm))

    args = parser.parse_args()
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func()


if __name__ == '__main__':
    _main()
