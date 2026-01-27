# ruff: noqa: N802 N803 UP006 UP007 UP045
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
import contextvars
import inspect
import typing as ta
import unittest
import warnings

from ...lite.check import check


##


class IsolatedAsyncTestCaseAsyncRunner(abc.ABC):
    def setup(self) -> None:
        pass

    @abc.abstractmethod
    def run(self, obj: ta.Any, *, context: ta.Optional[contextvars.Context] = None) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def close(self) -> None:
        raise NotImplementedError


class IsolatedAsyncTestCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)

        self._asyncRunner: ta.Optional[IsolatedAsyncTestCaseAsyncRunner] = None
        self._asyncTestContext = contextvars.copy_context()

    async def asyncSetUp(self):
        pass

    async def asyncTearDown(self):
        pass

    def addAsyncCleanup(self, func, /, *args, **kwargs):
        # A trivial trampoline to addCleanup() the function exists because it has a different semantics and signature:
        # addCleanup() accepts regular functions but addAsyncCleanup() accepts coroutines
        #
        # We intentionally don't add inspect.iscoroutinefunction() check for func argument because there is no way to
        # check for async function reliably:
        # 1. It can be "async def func()" itself
        # 2. Class can implement "async def __call__()" method
        # 3. Regular "def func()" that returns awaitable object
        self.addCleanup(*(func, *args), **kwargs)

    async def enterAsyncContext(self, cm):
        """
        Enters the supplied asynchronous context manager.

        If successful, also adds its __aexit__ method as a cleanup function and returns the result of the __aenter__
        method.
        """

        # We look up the special methods on the type to match the with statement.
        cls = type(cm)
        try:
            enter = cls.__aenter__
            exit = cls.__aexit__  # noqa
        except AttributeError:
            raise TypeError(
                f"'{cls.__module__}.{cls.__qualname__}' object does not support the asynchronous context manager "
                f"protocol",
            ) from None
        result = await enter(cm)
        self.addAsyncCleanup(exit, cm, None, None, None)
        return result

    def _callSetUp(self):
        # Force loop to be initialized and set as the current loop so that setUp functions can use get_event_loop() and
        # get the correct loop instance.
        check.not_none(self._asyncRunner).setup()
        self._asyncTestContext.run(self.setUp)
        self._callAsync(self.asyncSetUp)

    def _callTestMethod(self, method):
        if self._callMaybeAsync(method) is not None:
            warnings.warn(
                f'It is deprecated to return a value that is not None from a test case ({method})',
                DeprecationWarning,
                stacklevel=4,
            )

    def _callTearDown(self):
        self._callAsync(self.asyncTearDown)
        self._asyncTestContext.run(self.tearDown)

    def _callCleanup(self, function, *args, **kwargs):
        self._callMaybeAsync(function, *args, **kwargs)

    def _callAsync(self, func, /, *args, **kwargs):
        runner = check.not_none(self._asyncRunner)
        check.state(inspect.iscoroutinefunction(func))
        return runner.run(
            func(*args, **kwargs),
            context=self._asyncTestContext,
        )

    def _callMaybeAsync(self, func, /, *args, **kwargs):
        runner = check.not_none(self._asyncRunner)
        if inspect.iscoroutinefunction(func):
            return runner.run(
                func(*args, **kwargs),
                context=self._asyncTestContext,
            )
        else:
            return self._asyncTestContext.run(func, *args, **kwargs)

    def _createAsyncRunner(self):
        raise NotImplementedError

    def _setupAsyncRunner(self):
        check.none(self._asyncRunner)
        runner = self._createAsyncRunner()
        self._asyncRunner = runner

    def _tearDownAsyncRunner(self):
        runner = check.not_none(self._asyncRunner)
        runner.close()

    def run(self, result=None):
        self._setupAsyncRunner()
        try:
            return super().run(result)
        finally:
            self._tearDownAsyncRunner()

    def debug(self):
        self._setupAsyncRunner()
        super().debug()
        self._tearDownAsyncRunner()

    def __del__(self):
        if self._asyncRunner is not None:
            self._tearDownAsyncRunner()


##


class AsyncioIsolatedAsyncTestCaseAsyncRunner(IsolatedAsyncTestCaseAsyncRunner):
    def __init__(self, *, loop_factory=None):
        import asyncio
        self._runner = asyncio.Runner(debug=True, loop_factory=loop_factory)

    def setup(self) -> None:
        self._runner.get_loop()

    def run(self, obj: ta.Any, *, context: ta.Optional[contextvars.Context] = None) -> ta.Any:
        return self._runner.run(obj, context=context)

    def close(self) -> None:
        self._runner.close()


class AsyncioIsolatedAsyncTestCase(IsolatedAsyncTestCase):
    def _createAsyncRunner(self):
        return AsyncioIsolatedAsyncTestCaseAsyncRunner()


##


class AnyioIsolatedAsyncTestCaseAsyncRunner(IsolatedAsyncTestCaseAsyncRunner):
    def __init__(self, **kwargs):
        import anyio.from_thread
        self._cm = anyio.from_thread.start_blocking_portal(**kwargs)
        self._portal = self._cm.__enter__()

    def run(self, obj: ta.Any, *, context: ta.Optional[contextvars.Context] = None) -> ta.Any:
        if context is not None:
            return context.run(self._portal.call, obj)
        else:
            return self._portal.call(obj)

    def close(self) -> None:
        self._cm.__exit__(None, None, None)


class AnyioIsolatedAsyncTestCase(IsolatedAsyncTestCase):
    def _createAsyncRunner(self):
        return AnyioIsolatedAsyncTestCaseAsyncRunner()
