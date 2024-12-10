# ruff: noqa: PT009
# @omlish-lite
import unittest

from .. import cli


class JunkCli(cli.Cli):
    num_runs = 0

    @cli.command(
        cli.arg('foo', metavar='foo'),
        cli.arg('--bar', dest='bar', action='store_true'),
    )
    def run(self) -> None:
        self.num_runs += 1


class TestCli(unittest.TestCase):
    def test_cli(self):
        cli = JunkCli(['run', 'xyz'])
        self.assertEqual(cli.num_runs, 0)
        cli()
        self.assertEqual(cli.num_runs, 1)
