import datetime
import os
import sys
import typing as ta

from omdev.cli import CliModule
from omlish import lang
from omlish.argparse import all as ap
from omlish.formats import json
from omlish.logs import all as logs
from omlish.term.confirm import confirm_action


with lang.auto_proxy_import(globals()):
    import huggingface_hub as hf
    import huggingface_hub.errors  # noqa
    import huggingface_hub.utils  # noqa


log = logs.get_module_logger(globals())


##


def fmt_ts(f: float) -> ta.Any:
    dt = datetime.datetime.fromtimestamp(f)  # noqa
    return dt.isoformat()


class Cli(ap.Cli):
    def _passthrough_args_cmd(
            self,
            exe: str,
            pre_args: ta.Sequence[str] = (),
            post_args: ta.Sequence[str] = (),
    ) -> ta.NoReturn:
        os.execvp(
            exe,
            [
                sys.executable,
                *pre_args,
                *self.unknown_args,
                *self.args.args,
                *post_args,
            ],
        )

    @ap.cmd(
        ap.arg('args', nargs=ap.REMAINDER),
        name='cli',
        accepts_unknown=True,
    )
    def cli_cmd(self) -> None:
        self._passthrough_args_cmd(sys.executable, ['-m', 'huggingface_hub.cli.hf'])

    #

    @ap.cmd(
        ap.arg('--dir'),
    )
    def scan(self) -> None:
        hf_cache_info = hf.utils.scan_cache_dir(self.args.dir)

        repo_dcts = [
            {
                'repo_id': repo.repo_id,
                'repo_type': repo.repo_type,

                'repo_path': str(repo.repo_path),

                'size_on_disk': repo.size_on_disk,
                'size_on_disk_str': repo.size_on_disk_str,

                'nb_files': repo.nb_files,

                'revisions': [
                    {
                        'commit_hash': rev.commit_hash,

                        'snapshot_path': str(rev.snapshot_path),

                        'size_on_disk': rev.size_on_disk,

                        'files': [
                            {
                                'file_name': file.file_name,
                                'file_path': str(file.file_path),
                                'blob_path': str(file.blob_path),

                                'size_on_disk': file.size_on_disk,
                                'size_on_disk_str': file.size_on_disk_str,

                                'blob_last_modified': fmt_ts(file.blob_last_modified),
                                'blob_last_modified_str': file.blob_last_modified_str,
                                'blob_last_accessed': fmt_ts(file.blob_last_accessed),
                                'blob_last_accessed_str': file.blob_last_accessed_str,
                            }
                            for file in sorted(rev.files, key=lambda file: file.blob_last_accessed)
                        ],

                        'refs': sorted(rev.refs),

                        'last_modified': fmt_ts(rev.last_modified),
                        'last_modified_str': rev.last_modified_str,

                    }
                    for rev in sorted(repo.revisions, key=lambda rev: rev.last_modified)
                ],

                'last_modified': fmt_ts(repo.last_modified),
                'last_modified_str': repo.last_modified_str,
                'last_accessed': fmt_ts(repo.last_accessed),
                'last_accessed_str': repo.last_accessed_str,

                'refs': sorted(repo.refs),
            }
            for repo in sorted(hf_cache_info.repos, key=lambda repo: repo.last_accessed)
        ]

        print(json.dumps_pretty(repo_dcts))

    @ap.cmd(
        ap.arg('--dir'),
    )
    def list(self) -> None:
        hf_cache_info = hf.utils.scan_cache_dir(self.args.dir)

        repos = [
            repo
            for repo in hf_cache_info.repos
            if repo.repo_type == 'model'
            and repo.nb_files
        ]

        repo_dcts = [
            {
                'repo_id': repo.repo_id,
                'repo_type': repo.repo_type,

                'repo_path': str(repo.repo_path),

                'size_on_disk': repo.size_on_disk,
                'size_on_disk_str': repo.size_on_disk_str,

                'nb_files': repo.nb_files,

                'last_modified': fmt_ts(repo.last_modified),
                'last_modified_str': repo.last_modified_str,
                'last_accessed': fmt_ts(repo.last_accessed),
                'last_accessed_str': repo.last_accessed_str,
            }
            for repo in sorted(repos, key=lambda repo: repo.last_accessed)
        ]

        print(json.dumps_pretty(repo_dcts))

    @ap.cmd(
        ap.arg('key', action='append'),
        ap.arg('--dir'),
        ap.arg('--dry-run', action='store_true'),
        ap.arg('--no-confirm', action='store_true'),
    )
    def rm(self) -> None:
        if not self.args.key:
            raise ValueError('key is required')

        hf_cache_info = hf.utils.scan_cache_dir(self.args.dir)

        repos_by_id = {repo.repo_id: repo for repo in hf_cache_info.repos}
        repos_by_rev = {rev.commit_hash: repo for repo in hf_cache_info.repos for rev in repo.revisions}

        rm_revs: dict[str, None] = {}

        for key in self.args.key:
            if key in repos_by_id:
                rm_revs.update({rev.commit_hash: None for rev in repos_by_id[key].revisions})
            elif key in repos_by_rev:
                rm_revs.update({key: None})
            else:
                raise ValueError(f'key {key} not found')

        for rm_rev in rm_revs:
            rm_repo = repos_by_rev[rm_rev]

            if not self.args.no_confirm:
                if not confirm_action(f'Delete {rm_repo.repo_id}@{rm_rev}?'):
                    return

            if not self.args.dry_run:
                strategy = hf_cache_info.delete_revisions(rm_rev)
                strategy.execute()


##


def _main() -> None:
    logs.configure_standard_logging('INFO')
    Cli()()


# @omlish-manifest
_CLI_MODULE = CliModule('hf', __name__)


if __name__ == '__main__':
    _main()
