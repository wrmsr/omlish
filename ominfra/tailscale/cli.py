import json
import subprocess
import sys
import typing as ta

from omdev.cli import CliModule
from omlish import argparse as ap
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh


@dc.dataclass(frozen=True)
@msh.update_object_metadata(field_naming=msh.Naming.CAMEL, unknown_field='x')
class Status:
    version: str
    backend_state: str

    x: ta.Mapping[str, ta.Any] | None = None


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

    @ap.command(
        ap.arg('name'),
    )
    def ip(self) -> None:
        stdout = subprocess.check_output([
            self.bin(),
            'status',
            '--json',
        ])
        status = msh.unmarshal(json.loads(stdout.decode()), Status)
        print(status)


# @omlish-manifest
_CLI_MODULE = CliModule(['tailscale', 'ts'], __name__)


def _main() -> None:
    Cli()()


if __name__ == '__main__':
    _main()
