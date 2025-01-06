# Based on pytest-trio, licensed under the MIT license, duplicated below.
#
#  https://github.com/python-trio/pytest-trio/tree/cd6cc14b061d34f35980e38c44052108ed5402d1
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
TODO:
 - auto drain_asyncio
"""
import contextvars
import functools
import inspect
import sys
import typing as ta
import warnings

import pytest

import trio

from _pytest.outcomes import Skipped  # noqa
from _pytest.outcomes import XFailed  # noqa

from ..... import lang
from .....diag import pydevd as pdu
from .._registry import register
from .fixtures import AsyncsFixture
from .fixtures import AsyncsTestContext
from .fixtures import CANARY


if ta.TYPE_CHECKING:
    import anyio
    import trio_asyncio
else:
    anyio = lang.proxy_import('anyio')
    trio_asyncio = lang.proxy_import('trio_asyncio')


##


ASYNCS_MARK = 'asyncs'

KNOWN_BACKENDS = (
    'asyncio',
    'trio',
    'trio_asyncio',
)

PARAM_NAME = '__async_backend'


def iscoroutinefunction(func: ta.Any) -> bool:
    return inspect.iscoroutinefunction(func) or getattr(func, '_is_coroutine', False)


def is_async_function(func: ta.Any) -> bool:
    return iscoroutinefunction(func) or inspect.isasyncgenfunction(func)


##



def _trio_test(fn):
    from trio.abc import Clock
    from trio.abc import Instrument

    @functools.wraps(fn)
    def wrapper(**kwargs):
        __tracebackhide__ = True

        clocks = {k: c for k, c in kwargs.items() if isinstance(c, Clock)}
        if not clocks:
            clock = None
        elif len(clocks) == 1:
            clock = list(clocks.values())[0]
        else:
            raise ValueError(f"Expected at most one Clock in kwargs, got {clocks!r}")

        instruments = [i for i in kwargs.values() if isinstance(i, Instrument)]

        try:
            return trio.run(
                functools.partial(fn, **kwargs),
                clock=clock,
                instruments=instruments,
            )

        except BaseExceptionGroup as eg:
            queue = [eg]
            leaves = []

            while queue:
                ex = queue.pop()
                if isinstance(ex, BaseExceptionGroup):
                    queue.extend(ex.exceptions)
                else:
                    leaves.append(ex)

            if len(leaves) == 1:
                if isinstance(leaves[0], XFailed):
                    pytest.xfail()
                if isinstance(leaves[0], Skipped):
                    pytest.skip()

            # Since our leaf exceptions don't consist of exactly one 'magic' skipped or xfailed exception, re-raise the
            # whole group.
            raise

    return wrapper


##


def _is_asyncs_fixture(func, coerce_async, kwargs):
    if coerce_async and (iscoroutinefunction(func) or inspect.isasyncgenfunction(func)):
        return True

    if any(isinstance(value, AsyncsFixture) for value in kwargs.values()):
        return True

    return False


def handle_fixture(fixturedef, request):
    is_asyncs_test = request.node.get_closest_marker(ASYNCS_MARK) is not None

    kwargs = {name: request.getfixturevalue(name) for name in fixturedef.argnames}

    if _is_asyncs_fixture(fixturedef.func, is_asyncs_test, kwargs):
        if request.scope != "function":
            raise RuntimeError("Asyncs fixtures must be function-scope")

        if not is_asyncs_test:
            raise RuntimeError("Asyncs fixtures can only be used by Asyncs tests")

        fixture = AsyncsFixture(
            "<fixture {!r}>".format(fixturedef.argname),
            fixturedef.func,
            kwargs,
        )

        fixturedef.cached_result = (fixture, request.param_index, None)

        return fixture


###


@register
class AsyncsPlugin:
    ASYNC_BACKENDS: ta.ClassVar[ta.Sequence[str]] = [
        *[s for s in KNOWN_BACKENDS if lang.can_import(s)],
    ]

    def pytest_cmdline_main(self, config):
        if (aio_plugin := sys.modules.get('pytest_asyncio.plugin')):
            # warnings.filterwarnings is clobbered by pytest using warnings.catch_warnings
            def aio_plugin_warn(message, *args, **kwargs):
                if (
                        isinstance(message, pytest.PytestDeprecationWarning) and
                        message.args[0].startswith('The configuration option "asyncio_default_fixture_loop_scope" is unset.')  # noqa
                ):
                    return
                warnings.warn(message, *args, **kwargs)

            aio_plugin.warnings = lang.proxy_import('warnings')  # type: ignore
            aio_plugin.warnings.warn = aio_plugin_warn  # type: ignore

    def pytest_configure(self, config):
        config.addinivalue_line('markers', f'{ASYNCS_MARK}: marks for all async backends')

    def pytest_generate_tests(self, metafunc):
        if (m := metafunc.definition.get_closest_marker(ASYNCS_MARK)) is not None:
            if m.args:
                bes = m.args
            else:
                bes = self.ASYNC_BACKENDS
        else:
            return

        if 'trio_asyncio' in bes:
            # NOTE: Importing it here is apparently necessary to get its patching working - otherwise fails later with
            # `no running event loop` in anyio._backends._asyncio and such.
            import trio_asyncio  # noqa

        if pdu.is_present():
            pdu.patch_for_trio_asyncio()

        metafunc.fixturenames.append(PARAM_NAME)
        metafunc.parametrize(PARAM_NAME, bes)

    def pytest_fixture_setup(self, fixturedef, request):
        return handle_fixture(fixturedef, request)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call(self, item):
        if (m := item.get_closest_marker(ASYNCS_MARK)) is None:
            if is_async_function(item.obj):
                from _pytest.unittest import UnitTestCase  # noqa
                if isinstance(item.parent, UnitTestCase):
                    # unittest handles these itself.
                    pass
                else:
                    raise Exception(f'{item.nodeid}: async def function and no async plugin specified')

            yield
            return

        be = item.callspec.params[PARAM_NAME]

        if be == 'asyncio':
            item.obj = self._asyncio_test_runner_factory(item)
        elif be == 'trio':
            item.obj = self._trio_test_runner_factory(item)
        elif be == 'trio_asyncio':
            item.obj = self._trio_asyncio_test_runner_factory(item)
        else:
            raise ValueError(be)

        yield

        # bes = [be for be in self.ASYNC_BACKENDS if item.get_closest_marker(be) is not None]
        # if len(bes) > 1 and set(bes) != {'trio', 'trio_asyncio'}:
        #     raise Exception(f'{item.nodeid}: multiple async backends specified: {bes}')
        # elif is_async_function(item.obj) and not bes:
        #     from _pytest.unittest import UnitTestCase  # noqa
        #     if isinstance(item.parent, UnitTestCase):
        #         # unittest handles these itself.
        #         pass
        #     else:
        #         raise Exception(f'{item.nodeid}: async def function and no async plugin specified')
        #
        # if 'trio_asyncio' in bes:
        #     obj = item.obj
        #
        #     @functools.wraps(obj)
        #     @trai.with_trio_asyncio_loop(wait=True)
        #     async def run(*args, **kwargs):
        #         await trio_asyncio.aio_as_trio(obj)(*args, **kwargs)
        #
        #     item.obj = run
        #
        # yield

    def _asyncio_test_runner_factory(self, item, testfunc=None):
        raise NotImplementedError

    def _trio_test_runner_factory(self, item, testfunc=None):
        if not testfunc:
            testfunc = item.obj

        if not iscoroutinefunction(testfunc):
            pytest.fail("test function `%r` is marked trio but is not async" % item)

        @_trio_test
        async def _bootstrap_fixtures_and_run_test(**kwargs):
            __tracebackhide__ = True

            test_ctx = AsyncsTestContext()
            test = AsyncsFixture(
                "<test {!r}>".format(testfunc.__name__),
                testfunc,
                kwargs,
                is_test=True,
            )

            contextvars_ctx = contextvars.copy_context()
            contextvars_ctx.run(CANARY.set, "in correct context")

            async with anyio.create_task_group() as nursery:
                for fixture in test.register_and_collect_dependencies():
                    nursery.start_soon(
                        fixture.run,
                        test_ctx,
                        contextvars_ctx,
                        name=fixture.name,
                    )

            silent_cancellers = test_ctx.fixtures_with_cancel - test_ctx.fixtures_with_errors

            if silent_cancellers:
                for fixture in silent_cancellers:
                    test_ctx.error_list.append(
                        RuntimeError("{} cancelled the test but didn't " "raise an error".format(fixture.name)),
                    )

            if len(test_ctx.error_list) == 1:
                raise test_ctx.error_list[0]
            elif test_ctx.error_list:
                raise BaseExceptionGroup("errors in async test and trio fixtures", test_ctx.error_list)

        return _bootstrap_fixtures_and_run_test

    def _trio_asyncio_test_runner_factory(self, item, testfunc=None):
        raise NotImplementedError
