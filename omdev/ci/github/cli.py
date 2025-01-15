# ruff: noqa: UP006 UP007
# @omlish-lite
"""
See:
 - https://docs.github.com/en/rest/actions/cache?apiVersion=2022-11-28
"""
from omlish.argparse.cli import ArgparseCli
from omlish.argparse.cli import argparse_arg
from omlish.argparse.cli import argparse_cmd


class GithubCli(ArgparseCli):
    @argparse_cmd(
        argparse_arg('repository-id'),
    )
    def list_cache_entries(self) -> None:
        raise NotImplementedError


def _main() -> None:
    GithubCli().cli_run_and_exit()


if __name__ == '__main__':
    _main()
