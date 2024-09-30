import os
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

    @ap.command()
    def commits_by_date(self) -> None:
        subprocess.check_call(['git log --date=short --pretty=format:%ad | sort | uniq -c'], shell=True)  # noqa

    #

    _GITHUB_PAT = re.compile(r'((http(s)?://)?(www\./)?github(\.com)?/)?(?P<user>[^/.]+)/(?P<repo>[^/.]+)(/.*)?')

    @ap.command(
        ap.arg('repo'),
        ap.arg('args', nargs=ap.REMAINDER),
        accepts_unknown=True,
    )
    def clone(self) -> None:
        if not (m := self._GITHUB_PAT.fullmatch(self.args.repo)):
            subprocess.check_call([
                'git',
                'clone',
                *self.unknown_args,
                *self.args.args,
                self.args.repo,
            ])
            return

        user = m.group('user')
        repo = m.group('repo')

        os.makedirs(user, 0o755, exist_ok=True)

        subprocess.check_call([
            'git',
            'clone',
            *self.unknown_args,
            *self.args.args,
            f'https://github.com/{user}/{repo}.git',
            os.path.join(user, repo),
        ])


# @omlish-manifest
_CLI_MODULE = CliModule('git', __name__)


if __name__ == '__main__':
    logs.configure_standard_logging('INFO')
    Cli()()
