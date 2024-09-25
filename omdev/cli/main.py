"""
TODO:
 - allow manually specifying manifest packages
 - https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#creating-executable-scripts
 - https://packaging.python.org/en/latest/specifications/entry-points/#entry-points
"""
import argparse
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

    dct: dict[str, CliModule] = {}
    for cm in cms:
        if cm.cmd_name in dct:
            raise NameError(cm)
        dct[cm.cmd_name] = cm

    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', nargs='?', choices=dct.keys())
    parser.add_argument('args', nargs=argparse.REMAINDER)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return

    cm = dct[args.cmd]
    sys.argv = [cm.cmd_name, *(args.args or ())]
    runpy._run_module_as_main(cm.mod_name)  # type: ignore  # noqa


if __name__ == '__main__':
    _main()
