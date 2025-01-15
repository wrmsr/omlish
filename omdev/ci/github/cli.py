# ruff: noqa: UP006 UP007
# @omlish-lite
"""
See:
 - https://docs.github.com/en/rest/actions/cache?apiVersion=2022-11-28
"""
from omlish.argparse.cli import ArgparseCli
from omlish.argparse.cli import argparse_arg
from omlish.argparse.cli import argparse_cmd

from .cache import GithubV1CacheShellClient


class GithubCli(ArgparseCli):
    @argparse_cmd(
        argparse_arg('key'),
    )
    def get_cache_key(self) -> None:
        shell_client = GithubV1CacheShellClient()
        result = shell_client.run_get(self.args.key)
        print(result)

    @argparse_cmd(
        argparse_arg('repository-id'),
    )
    def list_cache_entries(self) -> None:
        raise NotImplementedError


if __name__ == '__main__':
    def _main() -> None:
        GithubCli().cli_run_and_exit()

    _main()
