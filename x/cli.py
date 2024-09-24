"""
TODO:
 - omlish.bootstrap always
 - https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#creating-executable-scripts
"""
import argparse
import dataclasses as dc
import functools
import runpy

from omdev.manifests import ManifestLoader
from omlish import check


@dc.dataclass(frozen=True)
class CliModule:
    cmd_name: str
    mod_name: str


def _main() -> None:
    cms: list[CliModule] = []

    ldr = ManifestLoader.from_entry_point(__name__, __spec__)  # noqa
    for m in ldr.load('x', only=[CliModule]):
        cms.append(check.isinstance(m.value, CliModule))

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    def run(cm: CliModule) -> None:
        runpy._run_module_as_main(cm.mod_name)  # type: ignore  # noqa

    seen: set[str] = set()
    for m in cms:
        if m.cmd_name in seen:
            raise NameError(m)

        cmd_parser = subparsers.add_parser(m.cmd_name)
        cmd_parser.add_argument('args', nargs=argparse.REMAINDER)
        cmd_parser.set_defaults(func=functools.partial(run, m))

    args = parser.parse_args()
    args.func()


if __name__ == '__main__':
    _main()
