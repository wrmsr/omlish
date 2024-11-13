import os
import re
import subprocess
import typing as ta
import urllib.parse

from omlish import argparse as ap
from omlish import check
from omlish import logs
from omlish.formats import json

from ..cli import CliModule
from ..git import GitStatusLine
from ..git import get_git_status


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
        # And expected usage is `cd $(om git clone foo/bar)` and an empty cd arg will return to the previous directory,
        # so always output at least a . so it'll cd to the current dir at least lol - it still runs even if the proc
        # fails.
        out_dir = '.'
        try:
            if (m := self._GITHUB_PAT.fullmatch(self.args.repo)):
                user = m.group('user')
                repo = m.group('repo')

                os.makedirs(user, 0o755, exist_ok=True)

                subprocess.check_call([
                    'git',
                    'clone',
                    *self.unknown_args,
                    *self.args.args,
                    f'git@github.com:{user}/{repo}.git',
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

        finally:
            print(out_dir)

    @ap.command(
        ap.arg('rev', nargs='?', default='HEAD'),
        ap.arg('-d', '--diff', action='store_true'),
        ap.arg('-s', '--diff-stat', action='store_true'),
        ap.arg('-g', '--github', action='store_true'),
    )
    def recap(self) -> None:
        rev = rev_parse(self.args.rev)
        day_rev = check.not_none(get_first_commit_of_day(rev))
        base_rev = rev_parse(f'{day_rev}~1')

        if self.args.diff or self.args.diff_stat:
            os.execvp('git', ['git', 'diff', *(['--stat'] if self.args.diff_stat else []), base_rev, rev])

        elif self.args.github:
            rm_url = subprocess.check_output(['git', 'remote', 'get-url', 'origin']).decode('utf-8').strip()
            pu = urllib.parse.urlparse(rm_url)
            check.equal(pu.scheme, 'https')
            check.equal(pu.hostname, 'github.com')
            _, user, repo, *_ = pu.path.split('/')
            gh_url = f'https://github.com/{user}/{repo}/compare/{base_rev}...{rev}#files_bucket'
            print(gh_url)

        else:
            print(base_rev)

    @ap.command(
        ap.arg('-v', '--verbose', action='store_true'),
    )
    def status(self) -> None:
        st = get_git_status()

        def gsl_dct(gsl: GitStatusLine) -> ta.Mapping[str, ta.Any]:
            return {
                'x': gsl.x.name,
                'y': gsl.y.name,
                'a': gsl.a,
                **({'b': gsl.b} if gsl.b is not None else {}),
            }

        def gsl_dct_lst(gsls: ta.Iterable[GitStatusLine]) -> ta.Sequence[ta.Mapping[str, ta.Any]]:
            return [gsl_dct(gsl) for gsl in sorted(gsls, key=lambda gsl: gsl.a)]

        if self.args.verbose:
            dct = {
                'by_x': {x.name: gsl_dct_lst(lst) for x, lst in st.by_x.items()},
                'by_y': {y.name: gsl_dct_lst(lst) for y, lst in st.by_x.items()},

                'by_a': {a: gsl_dct(gsl) for a, gsl in sorted(st.by_a.items(), key=lambda t: t[0])},
                'by_b': {b: gsl_dct(gsl) for b, gsl in sorted(st.by_b.items(), key=lambda t: t[0])},

                'has_unmerged': st.has_unmerged,
                'has_staged': st.has_staged,
                'has_dirty': st.has_dirty,
            }

            print(json.dumps_pretty(dct))

        else:
            print(json.dumps_pretty([gsl_dct(gsl) for gsl in st]))

    @ap.command(
        ap.arg('-m', '--message', default='--'),
        aliases=['acp'],
    )
    def add_commit_push(self) -> None:
        st = get_git_status()

        if st.has_dirty:
            subprocess.check_call(['git', 'add', '.'])

        if st.has_staged or st.has_dirty:
            subprocess.check_call(['git', 'commit', '-m', self.args.message])

        subprocess.check_call(['git', 'push'])


# @omlish-manifest
_CLI_MODULE = CliModule('git', __name__)


if __name__ == '__main__':
    logs.configure_standard_logging('INFO')
    Cli()()
