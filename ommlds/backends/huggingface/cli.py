import datetime
import os
import sys
import typing as ta

from omdev.cli import CliModule
from omlish import lang
from omlish.argparse import all as ap
from omlish.formats import json
from omlish.logs import all as logs


with lang.auto_proxy_import(globals()):
    import huggingface_hub as hf
    import huggingface_hub.errors  # noqa
    import huggingface_hub.utils  # noqa


log = logs.get_module_logger(globals())


##


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
    def scan_cache(self) -> None:
        hf_cache_info = hf.utils.scan_cache_dir(self.args.dir)

        def fmt_ts(f: float) -> ta.Any:
            dt = datetime.datetime.fromtimestamp(f)  # noqa
            return dt.isoformat()

        repos = [
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

                                'blob_last_accessed': fmt_ts(file.blob_last_accessed),
                                'blob_last_accessed_str': file.blob_last_accessed_str,
                                'blob_last_modified': fmt_ts(file.blob_last_modified),
                                'blob_last_modified_str': file.blob_last_modified_str,
                            }
                            for file in sorted(rev.files, key=lambda file: file.blob_last_accessed)
                        ],

                        'refs': sorted(rev.refs),

                        'last_modified': fmt_ts(rev.last_modified),
                        'last_modified_str': rev.last_modified_str,

                    }
                    for rev in sorted(repo.revisions, key=lambda rev: rev.last_modified)
                ],

                'last_accessed': fmt_ts(repo.last_accessed),
                'last_accessed_str': repo.last_accessed_str,
                'last_modified': fmt_ts(repo.last_modified),
                'last_modified_str': repo.last_modified_str,

                'refs': sorted(repo.refs),
            }
            for repo in sorted(hf_cache_info.repos, key=lambda repo: repo.last_accessed)
        ]

        print(json.dumps_pretty(repos))


##


def _main() -> None:
    logs.configure_standard_logging('INFO')
    Cli()()


# @omlish-manifest
_CLI_MODULE = CliModule('hf', __name__)


if __name__ == '__main__':
    _main()
