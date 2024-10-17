import os
import re
import subprocess
import urllib.parse

from omlish import argparse as ap
from omlish import check
from omlish import logs

from ..cli import CliModule


def rev_parse(rev: str) -> str:
    return subprocess.check_output(['git', 'rev-parse', rev]).decode().strip()


def get_first_commit_of_day(rev: str) -> str | None:
    commit_date = subprocess.check_output([
        'git', 'show', '-s', '--format=%ci', rev,
    ]).decode().strip().split(' ')[0]

    first_commit = subprocess.check_output([
        'git', 'rev-list', '--reverse', '--max-parents=1',
        '--since', f'{commit_date} 00:00:00',
        '--until', f'{commit_date} 23:59:59',
        rev,
    ]).decode().strip().splitlines()

    # Return the first commit (if there is any)
    if first_commit:
        return first_commit[0]
    else:
        return None


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
        out_dir: str

        if (m := self._GITHUB_PAT.fullmatch(self.args.repo)):
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

            out_dir = os.path.join(user, repo)

        else:
            parsed = urllib.parse.urlparse(self.args.repo)
            out_dir = parsed.path.split('/')[-1]

            subprocess.check_call([
                'git',
                'clone',
                *self.unknown_args,
                *self.args.args,
                self.args.repo,
            ])

        print(out_dir)

    @ap.command(
        ap.arg('rev', default='HEAD'),
        ap.arg('-g', '--github', action='store_true'),
    )
    def recap(self) -> None:
        rev = rev_parse(self.args.rev)
        first_rev = check.not_none(get_first_commit_of_day(rev))
        base_rev = rev_parse(f'{first_rev}~1')

        print(base_rev)


# @omlish-manifest
_CLI_MODULE = CliModule('git', __name__)


if __name__ == '__main__':
    logs.configure_standard_logging('INFO')
    Cli()()
