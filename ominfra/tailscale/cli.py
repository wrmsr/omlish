import sys

from omdev.cli import CliModule
from omlish import argparse as ap
from omlish import lang


class Cli(ap.Cli):
    @lang.cached_function
    def bin(self) -> str:
        if sys.platform == 'darwin':
            return '/Applications/Tailscale.app/Contents/MacOS/Tailscale'
        else:
            return 'tailscale'

    @ap.command(name='bin')
    def bin_cmd(self) -> None:
        print(self.bin())


# @omlish-manifest
_CLI_MODULE = CliModule(['tailscale', 'ts'], __name__)


def _main() -> None:
    Cli()()


if __name__ == '__main__':
    _main()
