# ruff: noqa: UP006 UP007
# @omlish-lite
"""
See:
 - https://docs.github.com/en/rest/actions/cache?apiVersion=2022-11-28
"""
import dataclasses as dc

from omlish.argparse.cli import ArgparseCli
from omlish.argparse.cli import argparse_arg
from omlish.argparse.cli import argparse_cmd
from omlish.lite.json import json_dumps_pretty

from .cache import GithubV1CacheShellClient


class GithubCli(ArgparseCli):
    @argparse_cmd(
        argparse_arg('key'),
    )
    def get_cache_entry(self) -> None:
        shell_client = GithubV1CacheShellClient()
        entry = shell_client.run_get_entry(self.args.key)
        if entry is None:
            return
        print(json_dumps_pretty(dc.asdict(entry)))  # noqa

    @argparse_cmd(
        argparse_arg('repository-id'),
    )
    def list_cache_entries(self) -> None:
        raise NotImplementedError


if __name__ == '__main__':
    def _main() -> None:
        GithubCli().cli_run_and_exit()

    _main()
