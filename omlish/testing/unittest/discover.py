# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
https://docs.python.org/3/library/unittest.html#command-line-interface

https://github.com/python/cpython/tree/f66c75f11d3aeeb614600251fd5d3fe1a34b5ff1/Lib/unittest
"""
# PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# --------------------------------------------
#
# 1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and the Individual or Organization
# ("Licensee") accessing and otherwise using this software ("Python") in source or binary form and its associated
# documentation.
#
# 2. Subject to the terms and conditions of this License Agreement, PSF hereby grants Licensee a nonexclusive,
# royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative
# works, distribute, and otherwise use Python alone or in any derivative version, provided, however, that PSF's License
# Agreement and PSF's notice of copyright, i.e., "Copyright (c) 2001-2024 Python Software Foundation; All Rights
# Reserved" are retained in Python alone or in any derivative version prepared by Licensee.
#
# 3. In the event Licensee prepares a derivative work that is based on or incorporates Python or any part thereof, and
# wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include in
# any such work a brief summary of the changes made to Python.
#
# 4. PSF is making Python available to Licensee on an "AS IS" basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES,
# EXPRESS OR IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY
# OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY THIRD PARTY
# RIGHTS.
#
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL
# DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE THEREOF, EVEN IF
# ADVISED OF THE POSSIBILITY THEREOF.
#
# 6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.
#
# 7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint
# venture between PSF and Licensee.  This License Agreement does not grant permission to use PSF trademarks or trade
# name in a trademark sense to endorse or promote products or services of Licensee, or any third party.
#
# 8. By copying, installing or otherwise using Python, Licensee agrees to be bound by the terms and conditions of this
# License Agreement.
import abc
import argparse
import dataclasses as dc
import os
import sys
import types
import typing as ta
import unittest


##


def _convert_name(name: str) -> str:
    # on Linux / Mac OS X 'foo.PY' is not importable, but on Windows it is. Simpler to do a case insensitive match a
    # better check would be to check that the name is a valid Python module name.
    if not (os.path.isfile(name) and name.lower().endswith('.py')):
        return name

    if os.path.isabs(name):
        rel_path = os.path.relpath(name, os.getcwd())
        if os.path.isabs(rel_path) or rel_path.startswith(os.pardir):
            return name
        name = rel_path

    # on Windows both '\' and '/' are used as path separators. Better to replace both than rely on os.path.sep
    return os.path.normpath(name)[:-3].replace('\\', '.').replace('/', '.')


def _convert_names(names: ta.Iterable[str]) -> ta.List[str]:
    return [_convert_name(name) for name in names]


def _convert_select_pattern(pattern: str) -> str:
    if '*' not in pattern:
        pattern = f'*{pattern}*'
    return pattern


def _get_attr_dict(obj: ta.Optional[ta.Any], *attrs: str) -> ta.Dict[str, ta.Any]:
    if obj is None:
        return {}

    return {
        a: v
        for a in attrs
        if (v := getattr(obj, a, None)) is not None
    }


##


class TestProgramRunner:
    class Target(abc.ABC):  # noqa
        pass

    class ModuleTarget(Target):
        pass

    @dc.dataclass(frozen=True)
    class NamesTarget(Target):
        test_names: ta.Optional[ta.Sequence[str]] = None

    @dc.dataclass(frozen=True)
    class DiscoveryTarget(Target):
        start: ta.Optional[str] = None
        pattern: ta.Optional[str] = None
        top: ta.Optional[str] = None

    #

    @dc.dataclass(frozen=True)
    class Args:
        test_name_patterns: ta.Optional[ta.Sequence[str]] = None

        verbosity: int = 1
        failfast: bool = False
        catchbreak: bool = False
        buffer: bool = False
        warnings: ta.Optional[str] = None
        tb_locals: bool = False
        durations: ta.Optional[int] = None

    #

    def __init__(
            self,
            args: Args = Args(),
            *,
            module: ta.Union[str, types.ModuleType, None] = None,
            loader: ta.Optional[unittest.loader.TestLoader] = None,
            runner: ta.Union[unittest.TextTestRunner, ta.Type[unittest.TextTestRunner], None] = None,
    ) -> None:
        super().__init__()

        self._args = args

        self._module = module

        if loader is None:
            loader = unittest.loader.TestLoader()
        self._loader = loader

        if runner is None:
            runner = unittest.runner.TextTestRunner
        self._runner = runner

    #

    def create_suite(self, target: Target) -> ta.Any:
        if self._args.test_name_patterns:
            self._loader.testNamePatterns = self._args.test_name_patterns  # type: ignore[assignment]

        if isinstance(target, TestProgramRunner.DiscoveryTarget):
            return self._loader.discover(
                target.start,  # type: ignore[arg-type]
                target.pattern,  # type: ignore[arg-type]
                target.top,
            )

        module: ta.Any = self._module
        if isinstance(module, str):
            module = __import__(module)
            for part in module.split('.')[1:]:
                module = getattr(module, part)

        if isinstance(target, TestProgramRunner.ModuleTarget):
            return self._loader.loadTestsFromModule(module)

        elif isinstance(target, TestProgramRunner.NamesTarget):
            return self._loader.loadTestsFromNames(
                target.test_names,  # type: ignore[arg-type]
                module,
            )

        else:
            raise TypeError(target)

    #

    def run_suite(self, suite: ta.Any) -> ta.Any:
        if self._args.catchbreak:
            unittest.signals.installHandler()

        warnings: ta.Optional[str]
        if self._args.warnings is None and not sys.warnoptions:
            # even if DeprecationWarnings are ignored by default print them anyway unless other warnings settings are
            # specified by the warnings arg or the -W python flag
            warnings = 'default'
        else:
            # here self.warnings is set either to the value passed to the warnings args or to None.
            # If the user didn't pass a value self.warnings will be None. This means that the behavior is unchanged and
            # depends on the values passed to -W.
            warnings = self._args.warnings

        runner: ta.Any = self._runner
        if isinstance(runner, type):
            try:
                try:
                    runner = runner(
                        verbosity=self._args.verbosity,
                        failfast=self._args.failfast,
                        buffer=self._args.buffer,
                        warnings=warnings,
                        tb_locals=self._args.tb_locals,
                        durations=self._args.durations,
                    )

                except TypeError:
                    # didn't accept the tb_locals or durations argument
                    runner = runner(
                        verbosity=self._args.verbosity,
                        failfast=self._args.failfast,
                        buffer=self._args.buffer,
                        warnings=warnings,
                    )

            except TypeError:
                # didn't accept the verbosity, buffer or failfast arguments
                runner = runner()

        # TODO: if result.testsRun == 0 and len(result.skipped) == 0:
        return runner.run(suite)


##


class TestDiscoveryCli:
    def __init__(self) -> None:
        super().__init__()

        self._parser = self._get_arg_parser()

    #

    DEFAULT_DISCOVERY_START = '.'
    DEFAULT_DISCOVERY_PATTERN = 'test*.py'

    def _get_arg_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(add_help=False)

        parser.add_argument(
            '-v',
            '--verbose',
            dest='verbosity',
            action='store_const',
            const=2,
            help='Verbose output',
        )

        parser.add_argument(
            '-q',
            '--quiet',
            dest='verbosity',
            action='store_const',
            const=0,
            help='Quiet output',
        )

        parser.add_argument(
            '--locals',
            dest='tb_locals',
            action='store_true',
            help='Show local variables in tracebacks',
        )

        parser.add_argument(
            '--durations',
            dest='durations',
            type=int,
            default=None,
            metavar='N',
            help='Show the N slowest test cases (N=0 for all)',
        )

        parser.add_argument(
            '-f',
            '--failfast',
            dest='failfast',
            action='store_true',
            help='Stop on first fail or error',
        )

        parser.add_argument(
            '-c',
            '--catch',
            dest='catchbreak',
            action='store_true',
            help='Catch Ctrl-C and display results so far',
        )

        parser.add_argument(
            '-b',
            '--buffer',
            dest='buffer',
            action='store_true',
            help='Buffer stdout and stderr during tests',
        )

        parser.add_argument(
            '-k',
            dest='test_name_patterns',
            action='append',
            type=_convert_select_pattern,
            help='Only run tests which match the given substring',
        )

        #

        parser.epilog = (
            'For test discovery all test modules must be importable from the top level directory of the project.'
        )

        parser.add_argument(
            '-s',
            '--start-directory',
            default=self.DEFAULT_DISCOVERY_START,
            dest='start',
            help="Directory to start discovery ('.' default)",
        )

        parser.add_argument(
            '-p',
            '--pattern',
            default=self.DEFAULT_DISCOVERY_PATTERN,
            dest='pattern',
            help="Pattern to match tests ('test*.py' default)",
        )

        parser.add_argument(
            '-t',
            '--top-level-directory',
            dest='top',
            help='Top level directory of project (defaults to start directory)',
        )

        for arg in ('start', 'pattern', 'top'):
            parser.add_argument(
                arg,
                nargs='?',
                default=argparse.SUPPRESS,
                help=argparse.SUPPRESS,
            )

        return parser

    #

    @dc.dataclass(frozen=True)
    class ParsedArgs:
        args: ta.Optional[argparse.Namespace]
        test_names: ta.Optional[ta.Sequence[str]] = None
        module: ta.Union[str, types.ModuleType, None] = None

    def parse_args(self, argv: ta.Sequence[str]) -> ParsedArgs:
        args = self._parser.parse_args(argv)
        return self.ParsedArgs(args)

    #

    NO_TESTS_EXITCODE = 5

    def run_tests(
            self,
            args: ParsedArgs,
            *,
            exit: bool = False,  # noqa
    ) -> None:
        target: TestProgramRunner.Target = TestProgramRunner.DiscoveryTarget(**_get_attr_dict(
            args.args,
            'start',
            'pattern',
            'top',
        ))

        run_args = TestProgramRunner.Args(**_get_attr_dict(
            args.args,
            'test_name_patterns',
            'verbosity',
            'failfast',
            'catchbreak',
            'buffer',
            'warnings',
            'tb_locals',
            'durations',
        ))

        tpr = TestProgramRunner(
            run_args,
        )

        suite = tpr.create_suite(target)
        result = tpr.run_suite(suite)
        if exit:
            if result.testsRun == 0 and len(result.skipped) == 0:
                sys.exit(self.NO_TESTS_EXITCODE)
            elif result.wasSuccessful():
                sys.exit(0)
            else:
                sys.exit(1)


##


def _main() -> None:
    cli = TestDiscoveryCli()
    args = cli.parse_args(sys.argv[1:])
    cli.run_tests(args, exit=True)


if __name__ == '__main__':
    _main()
