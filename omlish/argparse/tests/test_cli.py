# ruff: noqa: PT009
# @omlish-lite
import unittest

from .. import cli


class JunkCli(cli.ArgparseCli):
    num_runs = 0

    @cli.argparse_cmd(
        cli.argparse_arg('foo', metavar='foo'),
        cli.argparse_arg('--bar', dest='bar', action='store_true'),
    )
    def run(self) -> None:
        self.num_runs += 1


class TestCli(unittest.TestCase):
    def test_cli(self):
        cli = JunkCli(['run', 'xyz'])
        self.assertEqual(cli.num_runs, 0)
        cli()
        self.assertEqual(cli.num_runs, 1)
