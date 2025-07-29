# ruff: noqa: UP006 UP007 UP045
"""
https://docs.python.org/3/library/unittest.html#command-line-interface
~ https://github.com/python/cpython/tree/f66c75f11d3aeeb614600251fd5d3fe1a34b5ff1/Lib/unittest
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
import contextlib
import dataclasses as dc
import sys
import time
import typing as ta
import unittest
import warnings

from .types import UnittestTest


##


class UnittestTestRunner:
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
        self._stream = UnittestTestRunner._WritelnDecorator(stream)

    #

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

        return UnittestTestRunner._InternalRunTestResult(
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

        expected_failures: ta.Sequence[TestAndReason]
        unexpected_successes: ta.Sequence[str]

        @classmethod
        def merge(cls, results: ta.Iterable['UnittestTestRunner.RunResult']) -> 'UnittestTestRunner.RunResult':
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

                expected_failures=merge_list_attr('expected_failures'),
                unexpected_successes=merge_list_attr('unexpected_successes'),
            )

    def _build_run_result(self, internal_result: _InternalRunTestResult) -> RunResult:
        result = internal_result.result

        def as_test_and_reasons(l):
            return [
                UnittestTestRunner.RunResult.TestAndReason(result.getDescription(t), r)
                for t, r in l
            ]

        return UnittestTestRunner.RunResult(
            raw_results=[result],
            time_taken=internal_result.time_taken,

            num_tests_run=result.testsRun,
            was_successful=result.wasSuccessful(),

            skipped=as_test_and_reasons(result.skipped),
            errors=as_test_and_reasons(result.errors),
            failures=as_test_and_reasons(result.failures),

            expected_failures=as_test_and_reasons(result.expectedFailures),
            unexpected_successes=[result.getDescription(t) for t in result.unexpectedSuccesses],
        )

    #

    def run(self, test: UnittestTest) -> RunResult:
        return self._build_run_result(self._internal_run_test(test))

    def run_many(self, tests: ta.Iterable[UnittestTest]) -> RunResult:
        return UnittestTestRunner.RunResult.merge([self.run(t) for t in tests])

    #

    separator1 = unittest.TextTestResult.separator1
    separator2 = unittest.TextTestResult.separator2

    def print(self, result: RunResult) -> None:
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

        self._stream.writeln(
            f'Ran {result.num_tests_run:d} '
            f'test{"s" if result.num_tests_run != 1 else ""} '
            f'in {result.time_taken:.3f}s',
        )
        self._stream.writeln()

        expected_fails = len(result.expected_failures)
        unexpected_successes = len(result.unexpected_successes)
        skipped = len(result.skipped)

        infos: ta.List[str] = []

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
