import shlex

from omcore.argparse import all as ap
from omcore.subprocesses.sync import subprocesses

from ..cli import CliModule


##


class Cli(ap.Cli):
    @ap.cmd(
        ap.arg('l'),
        ap.arg('r'),
    )
    def less(self) -> None:
        subprocesses.check_call(
            f'diff --color=always -y {shlex.quote(self.args.l)} {shlex.quote(self.args.r)} | less -R',
            shell=True,
        )


# @om-manifest
_CLI_MODULE = CliModule('diff', __name__)


if __name__ == '__main__':
    Cli()()
