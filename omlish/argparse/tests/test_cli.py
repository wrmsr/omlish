# ruff: noqa: PT009
# @omlish-lite
import argparse
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


##


class FormatHelpCli(cli.ArgparseCli):
    _baz = cli.argparse_arg('--baz')

    @cli.argparse_cmd(
        cli.argparse_arg('qux'),
    )
    def foo(self):
        pass

    @cli.argparse_cmd()
    def bar(self):
        pass


class FooHelpFormatter(argparse.HelpFormatter):
    def add_argument(self, action):
        if not (
                isinstance(action, argparse._SubParsersAction) and  # noqa
                action.help is not argparse.SUPPRESS
        ):
            super().add_argument(action)
            return

        s1 = 's1:' + self._format_action_invocation(action)
        action_length = len(s1) + self._current_indent
        self._action_max_length = max(self._action_max_length, action_length)

        # add the item to the list
        def f():
            s2 = 's2:' + self._format_action(action)
            return s2

        self._add_item(f, [])

    def _metavar_formatter(self, action, default_metavar):
        return super()._metavar_formatter(action, default_metavar)  # noqa


class TestFormatHelp(unittest.TestCase):
    def test_cli(self):
        p = FormatHelpCli.get_parser()
        p.formatter_class = FooHelpFormatter
        print(p.format_help())
