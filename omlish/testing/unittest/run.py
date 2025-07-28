# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
https://docs.python.org/3/library/unittest.html#command-line-interface
~ https://github.com/python/cpython/tree/f66c75f11d3aeeb614600251fd5d3fe1a34b5ff1/Lib/unittest

TODO:
 - output only final status line
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
import contextlib
import dataclasses as dc
import importlib.util
import os
import re
import sys
import time
import types
import typing as ta
import unittest
import warnings


Test = ta.Callable[[unittest.TestResult], None]  # ta.TypeAlias


##


class _WritelnDecorator:
    def __init__(self, stream):
        super().__init__()

        self.stream = stream

    def __getattr__(self, attr):
        if attr in ('stream', '__getstate__'):
            raise AttributeError(attr)
        return getattr(self.stream, attr)

    def writeln(self, arg=None):
        if arg:
            self.write(arg)
        self.write('\n')  # text-mode streams translate to \r\n if needed


class TestRunner:
    """
    A test runner class that displays results in textual form.

    It prints out the names of tests as they are run, errors as they occur, and a summary of the results at the end of
    the test run.
    """

    @dc.dataclass(frozen=True)
    class Args:
        descriptions: bool = True
        verbosity: int = 1
        failfast: bool = False
        buffer: bool = False
        warnings: ta.Optional[str] = None
        tb_locals: bool = False
        catchbreak: bool = False

    def __init__(
            self,
            args: Args = Args(),
            *,
            stream: ta.Optional[ta.Any] = None,
    ):
        super().__init__()

        self._args = args

        if stream is None:
            stream = sys.stderr
        self._stream = _WritelnDecorator(stream)

    #

    @contextlib.contextmanager
    def _warnings_context(self) -> ta.Iterator[None]:
        with warnings.catch_warnings():
            w = self._args.warnings

            if w is None and not sys.warnoptions:
                # Even if DeprecationWarnings are ignored by default print them anyway unless other warnings settings
                # are specified by the warnings arg or the -W python flag.
                w = 'default'  # noqa
            else:
                # Here self.warnings is set either to the value passed to the warnings args or to None. If the user
                # didn't pass a value self.warnings will be None. This means that the behavior is unchanged and depends
                # on the values passed to -W.
                w = self._args.warnings  # noqa

            if w:
                # If self.warnings is set, use it to filter all the warnings.
                warnings.simplefilter(w)  # noqa

                # If the filter is 'default' or 'always', special-case the warnings from the deprecated unittest methods
                # to show them no more than once per module, because they can be fairly noisy.  The -Wd and -Wa flags
                # can be used to bypass this only when self.warnings is None.
                if w in ['default', 'always']:
                    warnings.filterwarnings(
                        'module',
                        category=DeprecationWarning,
                        message=r'Please use assert\w+ instead.',
                    )

            yield

    #

    def _make_result(self) -> unittest.TextTestResult:
        return unittest.TextTestResult(
            self._stream,  # type: ignore[arg-type]
            self._args.descriptions,
            self._args.verbosity,
        )

    #

    class _InternalRunTestResult(ta.NamedTuple):
        result: unittest.TextTestResult
        time_taken: float

    def _internal_run_test(self, test: ta.Callable[[unittest.TestResult], None]) -> _InternalRunTestResult:
        result = self._make_result()
        unittest.registerResult(result)
        result.failfast = self._args.failfast
        result.buffer = self._args.buffer
        result.tb_locals = self._args.tb_locals

        #

        if self._args.catchbreak:
            unittest.signals.installHandler()

        with self._warnings_context():
            start_time = time.perf_counter()

            start_test_run = getattr(result, 'startTestRun', None)
            if start_test_run is not None:
                start_test_run()

            try:
                test(result)

            finally:
                stop_test_run = getattr(result, 'stopTestRun', None)
                if stop_test_run is not None:
                    stop_test_run()

            stop_time = time.perf_counter()

        time_taken = stop_time - start_time

        return TestRunner._InternalRunTestResult(
            result,
            time_taken,
        )

    #

    @dc.dataclass(frozen=True)
    class RunResult:
        raw_results: ta.Sequence[unittest.TextTestResult]
        time_taken: float

        num_tests_run: int
        was_successful: bool

        class TestAndReason(ta.NamedTuple):
            test: str
            reason: str

        skipped: ta.Sequence[TestAndReason]
        errors: ta.Sequence[TestAndReason]
        failures: ta.Sequence[TestAndReason]

        unexpected_successes: ta.Sequence[str]

        @classmethod
        def merge(cls, results: ta.Iterable['TestRunner.RunResult']) -> 'TestRunner.RunResult':
            def reduce_attr(fn, a):
                return fn(getattr(r, a) for r in results)

            def merge_list_attr(a):
                return [rr for r in results for rr in getattr(r, a)]

            return cls(
                raw_results=merge_list_attr('raw_results'),
                time_taken=reduce_attr(sum, 'time_taken'),

                num_tests_run=reduce_attr(sum, 'num_tests_run'),
                was_successful=reduce_attr(all, 'was_successful'),

                skipped=merge_list_attr('skipped'),
                errors=merge_list_attr('errors'),
                failures=merge_list_attr('failures'),

                unexpected_successes=merge_list_attr('unexpected_successes'),
            )

    def _build_run_result(self, internal_result: _InternalRunTestResult) -> RunResult:
        result = internal_result.result

        def as_test_and_reasons(l):
            return [
                TestRunner.RunResult.TestAndReason(result.getDescription(t), r)
                for t, r in l
            ]

        return TestRunner.RunResult(
            raw_results=[result],
            time_taken=internal_result.time_taken,

            num_tests_run=result.testsRun,
            was_successful=result.wasSuccessful(),

            skipped=as_test_and_reasons(result.skipped),
            errors=as_test_and_reasons(result.errors),
            failures=as_test_and_reasons(result.failures),

            unexpected_successes=[result.getDescription(t) for t in result.unexpectedSuccesses],
        )

    #

    separator1 = unittest.TextTestResult.separator1
    separator2 = unittest.TextTestResult.separator2

    def run(self, test: Test) -> RunResult:
        result = self._build_run_result(self._internal_run_test(test))

        if self._args.verbosity > 0:
            self._stream.writeln()
            self._stream.flush()

        for t, r in result.errors:
            self._stream.writeln(self.separator1)
            self._stream.writeln(f'ERROR: {t}')
            self._stream.writeln(self.separator2)
            self._stream.writeln(f'{r}')
            self._stream.flush()

        for t, r in result.failures:
            self._stream.writeln(self.separator1)
            self._stream.writeln(f'FAIL: {t}')
            self._stream.writeln(self.separator2)
            self._stream.writeln(f'{r}')
            self._stream.flush()

        if result.unexpected_successes:
            self._stream.writeln(self.separator1)
            for t in result.unexpected_successes:
                self._stream.writeln(f'UNEXPECTED SUCCESS: {t}')
            self._stream.flush()

        self._stream.writeln(self.separator2)

        run = result.num_tests_run

        self._stream.writeln(f'Ran {run:d} test{"s" if run != 1 else ""} in {result.time_taken:.3f}s')
        self._stream.writeln()

        expected_fails = unexpected_successes = skipped = 0
        try:
            expected_fails, unexpected_successes, skipped = \
                map(len, (result.expectedFailures, result.unexpectedSuccesses, result.skipped))  # type: ignore
        except AttributeError:
            pass

        infos = []

        if not result.was_successful:
            self._stream.write('FAILED')
            failed, errored = len(result.failures), len(result.errors)
            if failed:
                infos.append(f'failures={failed:d}')
            if errored:
                infos.append(f'errors={errored:d}')
        else:
            self._stream.write('OK')

        if skipped:
            infos.append(f'skipped={skipped:d}')

        if expected_fails:
            infos.append(f'expected failures={expected_fails:d}')

        if unexpected_successes:
            infos.append(f'unexpected successes={unexpected_successes:d}')

        if infos:
            self._stream.writeln(f' ({", ".join(infos)})')
        else:
            self._stream.write('\n')

        return result


##


class TestTargetRunner:
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

    #

    def __init__(
            self,
            args: Args = Args(),
            *,
            module: ta.Union[str, types.ModuleType, None] = None,
            loader: ta.Optional[unittest.loader.TestLoader] = None,
    ) -> None:
        super().__init__()

        self._args = args

        self._module = module
        self._loader = loader

    #

    def create_test(self, target: Target) -> Test:
        loader = self._loader
        if loader is None:
            loader = unittest.loader.TestLoader()

        if self._args.test_name_patterns:
            loader.testNamePatterns = self._args.test_name_patterns  # type: ignore[assignment]

        if isinstance(target, TestTargetRunner.DiscoveryTarget):
            return ta.cast(Test, loader.discover(
                target.start,  # type: ignore[arg-type]
                target.pattern,  # type: ignore[arg-type]
                target.top,
            ))

        module: ta.Any = self._module
        if isinstance(module, str):
            module = __import__(module)
            for part in module.split('.')[1:]:
                module = getattr(module, part)

        if isinstance(target, TestTargetRunner.ModuleTarget):
            return ta.cast(Test, loader.loadTestsFromModule(module))

        elif isinstance(target, TestTargetRunner.NamesTarget):
            return ta.cast(Test, loader.loadTestsFromNames(
                target.test_names,  # type: ignore[arg-type]
                module,
            ))

        else:
            raise TypeError(target)

    #

    def run_test(self, test: Test) -> TestRunner.RunResult:
        runner = TestRunner(TestRunner.Args(
            verbosity=self._args.verbosity,
            failfast=self._args.failfast,
            buffer=self._args.buffer,
            warnings=self._args.warnings,
            tb_locals=self._args.tb_locals,
            catchbreak=self._args.catchbreak,
        ))

        # TODO: if result.testsRun == 0 and len(result.skipped) == 0:
        return runner.run(test)


##


def _get_attr_dict(obj: ta.Optional[ta.Any], *attrs: str) -> ta.Dict[str, ta.Any]:
    if obj is None:
        return {}

    return {
        a: v
        for a in attrs
        if (v := getattr(obj, a, None)) is not None
    }


class TestRunCli:
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

        def _convert_select_pattern(pattern: str) -> str:
            if '*' not in pattern:
                pattern = f'*{pattern}*'
            return pattern

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

        parser.add_argument(
            'target',
            nargs='*',
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

    IMPORT_PATH_PAT = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*')

    def _build_target(self, name: str, args: ParsedArgs) -> TestTargetRunner.Target:
        is_discovery = False
        if os.path.isdir(name):
            is_discovery = True
        elif self.IMPORT_PATH_PAT.fullmatch(name):
            spec = importlib.util.find_spec(name)
            if spec is not None and spec.submodule_search_locations is not None:  # is a package, not a module
                is_discovery = True

        if not is_discovery:
            return TestTargetRunner.NamesTarget([name])

        else:
            return TestTargetRunner.DiscoveryTarget(
                start=name,
                **_get_attr_dict(
                    args.args,
                    'pattern',
                    'top',
                ),
            )

    #

    NO_TESTS_EXITCODE = 5

    def run_tests(
            self,
            args: ParsedArgs,
            *,
            exit: bool = False,  # noqa
    ) -> None:
        run_args = TestTargetRunner.Args(**_get_attr_dict(
            args.args,
            'test_name_patterns',
            'verbosity',
            'failfast',
            'catchbreak',
            'buffer',
            'warnings',
            'tb_locals',
        ))

        tpr = TestTargetRunner(
            run_args,
        )

        tests_run = 0
        tests_skipped = 0
        was_successful = True

        for target_arg in (args.args.target if args.args is not None else None) or []:  # noqa
            target = self._build_target(target_arg, args)
            test = tpr.create_test(target)
            result = tpr.run_test(test)

            tests_run += result.num_tests_run
            tests_skipped += len(result.skipped)
            was_successful &= result.was_successful

        if exit:
            if tests_run == 0 and tests_skipped == 0:
                sys.exit(self.NO_TESTS_EXITCODE)
            elif was_successful:
                sys.exit(0)
            else:
                sys.exit(1)


##


def _main() -> None:
    cli = TestRunCli()
    args = cli.parse_args(sys.argv[1:])
    cli.run_tests(args, exit=True)


if __name__ == '__main__':
    _main()
