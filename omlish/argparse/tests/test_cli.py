# ruff: noqa: PT009
# @omlish-lite
import unittest

from .. import cli


##


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
        c = JunkCli(['run', 'xyz'])
        self.assertEqual(c.num_runs, 0)
        c()
        self.assertEqual(c.num_runs, 1)


##


class ClassVarCli(cli.ArgparseCli):
    _foo = cli.argparse_arg('--foo')

    @cli.argparse_cmd(
        cli.argparse_arg('--bar'),
    )
    def baz(self) -> None:
        pass


class TestClassVar(unittest.TestCase):
    def test_cli(self):
        c = ClassVarCli(['--foo', 'foo!', 'baz', '--bar', 'bar!'])
        print(c._args)  # noqa
