# ruff: noqa: UP006 UP007 UP045
# @omlish-precheck-allow-any-unicode
"""
TODO:
 - Handle:
  Your branch and 'origin/main' have diverged,
  and have 2691 and 2708 different commits each, respectively.
    (use "git pull" if you want to integrate the remote branch with yours)
  hint: You have divergent branches and need to specify how to reconcile them.
  hint: You can do so by running one of the following commands sometime before
  hint: your next pull:
  hint:
  hint:   git config pull.rebase false  # merge
  hint:   git config pull.rebase true   # rebase
  hint:   git config pull.ff only       # fast-forward only
  hint:
  hint: You can replace "git config" with "git config --global" to set a default
  hint: preference for all repositories. You can also pass --rebase, --no-rebase,
  hint: or --ff-only on the command line to override the configured default per
  hint: invocation.
  fatal: Need to specify how to reconcile divergent branches.
"""
import dataclasses as dc
import os
import shutil
import tempfile
import typing as ta
import urllib.parse

from omlish import cached
from omlish import check
from omlish import lang
from omlish.argparse import all as ap
from omlish.configs.processing.merging import merge_configs
from omlish.formats import json
from omlish.formats import yaml
from omlish.logs import all as logs
from omlish.subprocesses.sync import subprocesses

from ...git.status import GitStatusItem
from ...git.status import get_git_status
from ...home.paths import get_home_paths
from ...home.shadow import get_shadow_configs
from . import consts
from .cloning import GithubCloneTarget
from .cloning import OtherCloneTarget
from .cloning import parse_clone_target
from .messages import GitMessageGenerator
from .messages import TimestampGitMessageGenerator
from .messages import load_message_generator_manifests
from .messages import load_message_generator_manifests_map


if ta.TYPE_CHECKING:
    from omlish import marshal as msh
else:
    msh = lang.proxy_import('omlish.marshal')


log = logs.get_module_logger(globals())


##


def rev_parse(rev: str) -> str:
    return subprocesses.check_output('git', 'rev-parse', rev).decode().strip()


def get_first_commit_of_day(rev: str) -> str | None:
    commit_date = subprocesses.check_output(
        'git', 'show', '-s', '--format=%ci', rev,
    ).decode().strip().split(' ')[0]

    first_commit = subprocesses.check_output(
        'git', 'rev-list', '--reverse', '--max-parents=1',
        '--since', f'{commit_date} 00:00:00',
        '--until', f'{commit_date} 23:59:59',
        rev,
    ).decode().strip().splitlines()

    # Return the first commit (if there is any)
    if first_commit:
        return first_commit[0]
    else:
        return None


class Cli(ap.Cli):
    @dc.dataclass(frozen=True, kw_only=True)
    class Config:
        default_message_generator: str | None = None

    _config_file_path_arg: ta.Optional[str] = ap.arg_('-c', '--config-file-path', nargs='?')

    @cached.function
    def config_file_path(self) -> str:
        if (arg := self._config_file_path_arg) is not None:
            return os.path.expanduser(arg)
        else:
            return os.path.join(get_home_paths().config_dir, 'tools', 'git.yml')

    @cached.function
    def load_home_config_content(self) -> ta.Any:
        try:
            with open(self.config_file_path()) as f:
                buf = f.read()
        except FileNotFoundError:
            return dc.asdict(self.Config())  # noqa

        return yaml.safe_load(buf) or {}

    class _NOT_SET(lang.Marker):  # noqa
        pass

    def load_config(self, path: str | type[_NOT_SET] | None = _NOT_SET) -> Config:
        dct = self.load_home_config_content() or {}

        if path is not self._NOT_SET:
            if path is None:
                path = os.getcwd()
            shadow_cfg = get_shadow_configs().get_shadow_config(check.isinstance(path, str)) or {}
            dct = merge_configs(dct, shadow_cfg.get('git', {}))

        return msh.unmarshal(dct, self.Config)

    @ap.cmd(
        ap.arg('dir', nargs='?'),
    )
    def print_cfg(self) -> None:
        cfg = self.load_config(self._args.dir)
        print(yaml.dump(msh.marshal(cfg)))

    #

    _time_fmt: str = ap.arg_('--time-fmt', default=consts.DEFAULT_TIME_FMT)

    # Commands

    @ap.cmd()
    def blob_sizes(self) -> None:
        # https://stackoverflow.com/a/42544963
        subprocesses.check_call(  # noqa
            "git rev-list --objects --all | "
            "git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | "
            "sed -n 's/^blob //p' | "
            "sort --numeric-sort --key=2",
            shell=True,
        )

    #

    @ap.cmd()
    def commits_by_date(self) -> None:
        subprocesses.check_call('git log --date=short --pretty=format:%ad | sort | uniq -c', shell=True)  # noqa

    #

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
            ct = parse_clone_target(self.args.repo)
            if isinstance(ct, GithubCloneTarget):
                os.makedirs(ct.user, 0o755, exist_ok=True)

                subprocesses.check_call(
                    'git',
                    'clone',
                    *self.unknown_args,
                    *self.args.args,
                    ct.render(),
                    os.path.join(ct.user, ct.repo),
                )

                out_dir = os.path.join(ct.user, ct.repo)

            elif isinstance(ct, OtherCloneTarget):
                parsed = urllib.parse.urlparse(ct.s)
                out_dir = parsed.path.split('/')[-1]

                subprocesses.check_call(
                    'git',
                    'clone',
                    *self.unknown_args,
                    *self.args.args,
                    ct.render(),
                )

            else:
                raise TypeError(ct)

        finally:
            print(out_dir)

    #

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
            rm_url = subprocesses.check_output('git', 'remote', 'get-url', 'origin').decode('utf-8').strip()

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
                subprocesses.check_call('open', gh_url)
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
        ap.arg('-g', '--message-generator', nargs='?'),
        ap.arg('dir', nargs='*'),
        aliases=['gcm'],
    )
    def generate_commit_message(self) -> None:
        def run(cwd: str | None) -> None:
            st = get_git_status(cwd=cwd)

            if not (st.has_staged or st.has_dirty):
                return

            mg_cls: type[GitMessageGenerator] = TimestampGitMessageGenerator
            if (mg_name := self.args.message_generator) is None:
                mg_name = self.load_config(cwd).default_message_generator
            if mg_name is not None:
                mg_cls = load_message_generator_manifests_map()[mg_name].load_cls()
            mg = mg_cls()

            mgr = mg.generate_commit_message(GitMessageGenerator.GenerateCommitMessageArgs(
                cwd=cwd,
                time_fmt=self._time_fmt,
            ))
            print(mgr.msg)

        if not self.args.dir:
            run(None)
        else:
            for d in self.args.dir:
                run(d)

    @ap.cmd(
        ap.arg('-m', '--message', nargs='?'),
        ap.arg('-g', '--message-generator', nargs='?'),
        ap.arg('--dry-run', action='store_true'),
        ap.arg('-y', '--no-confirmation', action='store_true'),
        ap.arg('-r', '--repository'),
        ap.arg('dir', nargs='*'),
        aliases=['acp'],
    )
    def add_commit_push(self) -> None:
        def run(cwd: str | None) -> None:
            def check_call(*cmd: str) -> None:
                if self.args.dry_run:
                    print(cmd)
                else:
                    subprocesses.check_call(*cmd, cwd=cwd)

            st = get_git_status(cwd=cwd)

            if st.has_dirty:
                check_call('git', 'add', '.')

            if st.has_staged or st.has_dirty:
                if self.args.message is not None:
                    msg = self.args.message

                else:
                    mg_cls: type[GitMessageGenerator] = TimestampGitMessageGenerator
                    if (mg_name := self.args.message_generator) is None:
                        mg_name = self.load_config(cwd).default_message_generator
                    if mg_name is not None:
                        mg_cls = load_message_generator_manifests_map()[mg_name].load_cls()
                    mg = mg_cls()

                    mgr = mg.generate_commit_message(GitMessageGenerator.GenerateCommitMessageArgs(
                        cwd=cwd,
                        time_fmt=self._time_fmt,
                    ))
                    if mgr.confirm and not self._args.no_confirmation:
                        print(mgr.msg)
                        input()
                    msg = mgr.msg

                check_call('git', 'commit', '-m', msg)

            check_call('git', 'push', *([self.args.repository] if self.args.repository is not None else []))

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
            subprocesses.check_call('git', 'pull', cwd=cwd)
            subprocesses.check_call('git', 'submodule', 'update', cwd=cwd)

        if not self.args.dir:
            run(None)
        else:
            for d in self.args.dir:
                run(d)

    @ap.cmd(
        ap.arg('dir', nargs='*'),
        ap.arg('-x', '--on-error-resume-next', action='store_true'),
        aliases=['usb'],
    )
    def update_submodule_branches(self) -> None:
        def run_submodule(submodule: str, cwd: str | None) -> None:
            log.info('Updating submodule %s', submodule)

            submodule_path = submodule if cwd is None else os.path.join(cwd, submodule)

            # Get the HEAD branch from origin
            remote_show = subprocesses.check_output(
                'git', 'remote', 'show', 'origin',
                cwd=submodule_path,
            ).decode()
            head_branch: str | None = None
            for line in remote_show.splitlines():
                line = line.strip()
                if line.startswith('HEAD branch:'):
                    head_branch = line.split(':')[1].strip()
                    break

            if not head_branch:
                log.warning('Could not determine HEAD branch for submodule %s', submodule)
                return

            subprocesses.check_call('git', 'checkout', head_branch, cwd=submodule_path)
            subprocesses.check_call('git', 'pull', cwd=submodule_path)

        failed: set[str] = set()

        def run(cwd: str | None) -> None:
            submodules = subprocesses.check_output(
                'git', 'submodule', 'foreach', '-q', 'echo $name',
                cwd=cwd,
            ).decode().strip().splitlines()

            for submodule in sorted(submodules):
                try:
                    run_submodule(submodule, cwd)

                except Exception:  # noqa
                    failed.add(submodule)

                    if self.args.on_error_resume_next:
                        log.exception('Failed to update submodule %s', submodule)
                    else:
                        raise

            if failed:
                log.error(
                    'The following submodules failed to update:\n%s',
                    '\n'.join([f'  {f}' for f in failed]),
                )

        if not self.args.dir:
            run(None)
        else:
            for d in self.args.dir:
                run(d)

    #

    @ap.cmd()
    def list_message_generators(self) -> None:
        for mgm in load_message_generator_manifests():
            print(mgm.name)

    #

    BUILTIN_COMMIT_MESSAGES: ta.Mapping[str, str] = {
        'tableflip': '(╯°□°)╯︵ ┻━┻',
        'tableunflip': '┬─┬ノ(º _ ºノ)',
        'shrug': r'¯\_(ツ)_/¯',
    }

    @ap.cmd(
        ap.arg('-M', '--builtin-message', nargs='?'),
        accepts_unknown=True,
    )
    def commit(self) -> None:
        args: list[str] = []

        if (bim := self.args.builtin_message) is not None:
            args.extend(['-m', self.BUILTIN_COMMIT_MESSAGES[bim]])

        subprocesses.check_call(
            'git',
            'commit',
            *args,
            *self.unknown_args,
        )

    #

    @ap.cmd(
        ap.arg('repo'),
        ap.arg('args', nargs=ap.REMAINDER),
        accepts_unknown=True,
    )
    def anon_clone(self) -> None:
        cwd = os.getcwd()

        # As with the clone command, we always print a cd-able path to stdout, even on failure.
        out_dir = '.'
        try:
            tmp_dir = tempfile.mkdtemp()
            try:
                ct = parse_clone_target(self.args.repo)

                subprocesses.check_call(
                    'git',
                    'clone',
                    *self.unknown_args,
                    *self.args.args,
                    ct.render(),
                    cwd=tmp_dir,
                )

                repo_dir_name = check.single(os.listdir(tmp_dir))
                repo_dir = os.path.join(tmp_dir, repo_dir_name)
                check.state(os.path.isdir(repo_dir))

                git_dir = os.path.join(repo_dir, '.git')
                check.state(os.path.isdir(git_dir))
                shutil.rmtree(git_dir)

                shutil.move(repo_dir, cwd)

                out_dir = repo_dir_name

            finally:
                shutil.rmtree(tmp_dir)

        finally:
            print(out_dir)


##


def _main() -> None:
    logs.configure_standard_logging('INFO')
    Cli()()


if __name__ == '__main__':
    _main()
