"""
TODO:
 - https://github.com/vegardit/bash-funk/blob/main/docs/git.md
"""
import os
import re
import subprocess
import typing as ta
import urllib.parse

from omlish import check
from omlish import lang
from omlish.argparse import all as ap
from omlish.formats import json
from omlish.logs import all as logs

from ..cli import CliModule
from ..git.status import GitStatusItem
from ..git.status import get_git_status


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
    @ap.cmd()
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

    @ap.cmd()
    def commits_by_date(self) -> None:
        subprocess.check_call(['git log --date=short --pretty=format:%ad | sort | uniq -c'], shell=True)  # noqa

    #

    _GITHUB_PAT = re.compile(r'((http(s)?://)?(www\./)?github(\.com)?/)?(?P<user>[^/.]+)/(?P<repo>[^/.]+)(/.*)?')

    @ap.cmd(
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

    @ap.cmd(
        ap.arg('rev', nargs='?', default='HEAD'),
        ap.arg('-d', '--diff', action='store_true'),
        ap.arg('-s', '--stat', action='store_true'),
        ap.arg('-g', '--github', action='store_true'),
        ap.arg('-o', '--open', action='store_true'),
    )
    def recap(self) -> None:
        rev = rev_parse(self.args.rev)
        day_rev = check.not_none(get_first_commit_of_day(rev))
        base_rev = rev_parse(f'{day_rev}~1')

        if self.args.diff or self.args.stat:
            os.execvp('git', ['git', 'diff', *(['--stat'] if self.args.stat else []), base_rev, rev])

        elif self.args.github or self.args.open:
            rm_url = subprocess.check_output(['git', 'remote', 'get-url', 'origin']).decode('utf-8').strip()

            if rm_url.startswith(git_pfx := 'git@github.com:'):
                s = rm_url[len(git_pfx):]
                s = s.removesuffix('.git')
                user, repo = s.split('/')

            else:
                pu = urllib.parse.urlparse(rm_url)
                check.equal(pu.scheme, 'https')
                check.equal(pu.hostname, 'github.com')
                _, user, repo, *_ = pu.path.split('/')

            gh_url = f'https://github.com/{user}/{repo}/compare/{base_rev}...{rev}#files_bucket'

            if self.args.open:
                subprocess.check_call(['open', gh_url])
            else:
                print(gh_url)

        else:
            print(base_rev)

    @ap.cmd(
        ap.arg('dir', nargs='?'),
        ap.arg('-v', '--verbose', action='store_true'),
    )
    def status(self) -> None:
        st = get_git_status(cwd=self.args.dir)

        def gsi_dct(gsi: GitStatusItem) -> ta.Mapping[str, ta.Any]:
            return {
                'x': gsi.x.name.lower(),
                'y': gsi.y.name.lower(),
                'a': gsi.a,
                **({'b': gsi.b} if gsi.b is not None else {}),
            }

        def gsi_dct_lst(gsis: ta.Iterable[GitStatusItem]) -> ta.Sequence[ta.Mapping[str, ta.Any]]:
            return [gsi_dct(gsi) for gsi in sorted(gsis, key=lambda gsi: gsi.a)]

        if self.args.verbose:
            dct = {
                'by_x': {x.name.lower(): gsi_dct_lst(lst) for x, lst in st.by_x.items()},
                'by_y': {y.name.lower(): gsi_dct_lst(lst) for y, lst in st.by_x.items()},

                'by_a': {a: gsi_dct(gsi) for a, gsi in sorted(st.by_a.items(), key=lambda t: t[0])},
                'by_b': {b: gsi_dct(gsi) for b, gsi in sorted(st.by_b.items(), key=lambda t: t[0])},

                'has_unmerged': st.has_unmerged,
                'has_staged': st.has_staged,
                'has_dirty': st.has_dirty,
            }

            print(json.dumps_pretty(dct))

        else:
            print(json.dumps_pretty([gsi_dct(gsi) for gsi in st]))

    # Lazy helpers

    @ap.cmd(
        ap.arg('-m', '--message', nargs='?'),
        ap.arg('--time-fmt', default='%Y-%m-%dT%H:%M:%SZ'),
        ap.arg('dir', nargs='*'),
        aliases=['acp'],
    )
    def add_commit_push(self) -> None:
        def run(cwd: str | None) -> None:
            st = get_git_status(cwd=cwd)

            if st.has_dirty:
                subprocess.check_call(['git', 'add', '.'], cwd=cwd)

            if st.has_staged or st.has_dirty:
                if self.args.message is not None:
                    msg = self.args.message
                else:
                    msg = lang.utcnow().strftime(self.args.time_fmt)
                subprocess.check_call(['git', 'commit', '-m', msg], cwd=cwd)

            subprocess.check_call(['git', 'push'], cwd=cwd)

        if not self.args.dir:
            run(None)
        else:
            for d in self.args.dir:
                run(d)

    @ap.cmd(
        ap.arg('dir', nargs='*'),
        aliases=['psu'],
    )
    def pull_submodule_update(self) -> None:
        def run(cwd: str | None) -> None:
            subprocess.check_call(['git', 'pull'], cwd=cwd)
            subprocess.check_call(['git', 'submodule', 'update'], cwd=cwd)

        if not self.args.dir:
            run(None)
        else:
            for d in self.args.dir:
                run(d)


# @omlish-manifest
_CLI_MODULE = CliModule('git', __name__)


if __name__ == '__main__':
    logs.configure_standard_logging('INFO')
    Cli()()
