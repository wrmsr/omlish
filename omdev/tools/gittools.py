import re
import subprocess

from omlish import argparse as ap
from omlish import logs

from ..cli import CliModule


class Cli(ap.Cli):
    @ap.command()
    def blob_sizes(self) -> None:
        # https://stackoverflow.com/a/42544963
        subprocess.check_call(  # noqa
            "git rev-list --objects --all | "
            "git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | "
            "sed -n 's/^blob //p' | "
            "sort --numeric-sort --key=2",
            shell=True,
        )

    #

    _GITHUB_PAT = re.compile(r'((http(s)?://)?(www\./)?github(\.com)?/)?(?P<user>[^/.]+)/(?P<repo>[^/.]+)(/.*)?')

    @ap.command(
        ap.arg('url'),
        ap.arg('args', nargs=ap.REMAINDER),
    )
    def clone(self) -> None:
        if not (m := self._GITHUB_PAT.fullmatch(self.args.url)):
            subprocess.check_call(['git', 'clone', *self.args.args, self.args.url])
            return

        raise NotImplementedError


# @omlish-manifest
_CLI_MODULE = CliModule('git', __name__)


if __name__ == '__main__':
    logs.configure_standard_logging('INFO')
    Cli()()
