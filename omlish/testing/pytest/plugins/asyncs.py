# Portions based on pytest-trio, licensed under the MIT license, duplicated below.
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

==

_pytest:
https://github.com/pytest-dev/pytest/blob/ef9b8f9d748b6f50eab5d43e32d93008f7880899/src/_pytest/python.py#L155
"async def function and no async plugin installed (see warnings)"

pytest_trio:
https://github.com/python-trio/pytest-trio/blob/f03160aa1dd355a12d39fa21f4aee4e1239efea3/pytest_trio/plugin.py
 - pytest_addoption
 - pytest_configure
 - pytest_collection_modifyitems
 - pytest_runtest_call @(hookwrapper=True)
 - pytest_fixture_setup

pytest_asyncio:
https://github.com/pytest-dev/pytest-asyncio/blob/f45aa18cf3eeeb94075de16a1d797858facab863/pytest_asyncio/plugin.py
 - pytest_addoption
 - pytest_configure
 - pytest_pycollect_makeitem_preprocess_async_fixtures @(specname="pytest_pycollect_makeitem", tryfirst=True)
 - pytest_pycollect_makeitem_convert_async_functions_to_subclass @(specname="pytest_pycollect_makeitem", hookwrapper=True)
 - pytest_generate_tests @(tryfirst=True)
 - pytest_runtest_setup(item: pytest.Item) -> None:
 - pytest_pyfunc_call @(tryfirst=True, hookwrapper=True)
 - pytest_collectstart @()
 - pytest_report_header @(tryfirst=True)
 - pytest_fixture_setup @(hookwrapper=True)

anyio.pytest_plugin:
https://github.com/agronholm/anyio/blob/8907964926a24461840eee0925d3f355e729f15d/src/anyio/pytest_plugin.py
 - pytest_configure
 - pytest_pycollect_makeitem @(tryfirst=True)
 - pytest_pyfunc_call @(tryfirst=True)
 - pytest_fixture_setup

"""  # noqa
import collections.abc
import contextlib
import contextvars
import functools
import inspect
import sys
import typing as ta
import warnings

import pytest

import trio

import outcome

from _pytest.outcomes import Skipped  # noqa
from _pytest.outcomes import XFailed  # noqa

from .... import lang
from .... import check
from ....asyncs import trio_asyncio as trai
from ....diag import pydevd as pdu
from ._registry import register


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


canary = contextvars.ContextVar("pytest-omlish-asyncs canary")


class NURSERY_FIXTURE_PLACEHOLDER:
    pass


class AsyncsTestContext:
    def __init__(self) -> None:
        super().__init__()

        self.crashed = False

        # This holds cancel scopes for whatever setup steps are currently running -- initially it's the fixtures that
        # are in the middle of evaluating themselves, and then once fixtures are set up it's the test itself. Basically,
        # at any given moment, it's the stuff we need to cancel if we want to start tearing down our fixture DAG.
        self.active_cancel_scopes: set[anyio.CancelScope] = set()

        self.fixtures_with_errors = set()
        self.fixtures_with_cancel = set()

        self.error_list: list[BaseException] = []

    def crash(self, fixture: 'AsyncsFixture', exc: BaseException | None) -> None:
        if exc is None:
            self.fixtures_with_cancel.add(fixture)
        else:
            self.error_list.append(exc)
            self.fixtures_with_errors.add(fixture)

        self.crashed = True

        for cscope in self.active_cancel_scopes:
            cscope.cancel()


class AsyncsFixture:
    """
    Represent a fixture that need to be run in a async context to be resolved.

    The name is actually a misnomer, because we use it to represent the actual test itself as well, since the
    test is basically just a fixture with no dependents and no teardown.
    """

    def __init__(
            self,
            name: str,
            func,
            pytest_kwargs,
            is_test=False,
    ):
        super().__init__()

        self.name = name
        self._func = func
        self._pytest_kwargs = pytest_kwargs
        self._is_test = is_test
        self._teardown_done = anyio.Event()

        # These attrs are all accessed from other objects: Downstream users read this value.
        self.fixture_value = None

        # This event notifies downstream users that we're done setting up. Invariant: if this is set, then either
        # fixture_value is usable *or* test_ctx.crashed is True.
        self.setup_done = anyio.Event()

        # Downstream users *modify* this value, by adding their _teardown_done events to it, so we know who we need to
        # wait for before tearing down.
        self.user_done_events = set()

    def register_and_collect_dependencies(self):
        # Returns the set of all AsyncsFixtures that this fixture depends on, directly or indirectly, and sets up all
        # their user_done_events.
        deps = set()
        deps.add(self)
        for value in self._pytest_kwargs.values():
            if isinstance(value, AsyncsFixture):
                value.user_done_events.add(self._teardown_done)
                deps.update(value.register_and_collect_dependencies())
        return deps

    @contextlib.asynccontextmanager
    async def _fixture_manager(self, test_ctx):
        __tracebackhide__ = True

        try:
            async with anyio.create_task_group() as nursery_fixture:
                try:
                    yield nursery_fixture
                finally:
                    nursery_fixture.cancel_scope.cancel()

        except BaseException as exc:
            test_ctx.crash(self, exc)

        finally:
            self.setup_done.set()
            self._teardown_done.set()

    async def run(self, test_ctx, contextvars_ctx):
        __tracebackhide__ = True

        # This is a gross hack. I guess Trio should provide a context= argument to start_soon/start?
        task = trio.lowlevel.current_task()
        check.not_in(canary, task.context)
        task.context = contextvars_ctx

        # Force a yield so we pick up the new context
        await trio.sleep(0)

        # Check that it worked, since technically trio doesn't *guarantee* that sleep(0) will actually yield.
        check.equal(canary.get(), "in correct context")

        # This 'with' block handles the nursery fixture lifetime, the teardown_done event, and crashing the context if
        # there's an unhandled exception.
        async with self._fixture_manager(test_ctx) as nursery_fixture:
            # Resolve our kwargs
            resolved_kwargs = {}
            for name, value in self._pytest_kwargs.items():
                if isinstance(value, AsyncsFixture):
                    await value.setup_done.wait()
                    if value.fixture_value is NURSERY_FIXTURE_PLACEHOLDER:
                        resolved_kwargs[name] = nursery_fixture
                    else:
                        resolved_kwargs[name] = value.fixture_value
                else:
                    resolved_kwargs[name] = value

            # If something's already crashed before we're ready to start, then there's no point in even setting up.
            if test_ctx.crashed:
                return

            # Run actual fixture setup step. If another fixture crashes while we're in the middle of setting up, we want
            # to be cancelled immediately, so we'll save an encompassing cancel scope where self._crash can find it.
            test_ctx.active_cancel_scopes.add(nursery_fixture.cancel_scope)
            if self._is_test:
                # Tests are exactly like fixtures, except that they to be
                # regular async functions.
                check.state(not self.user_done_events)
                func_value = None
                check.state(not test_ctx.crashed)
                await self._func(**resolved_kwargs)

            else:
                func_value = self._func(**resolved_kwargs)
                if isinstance(func_value, collections.abc.Coroutine):
                    self.fixture_value = await func_value
                elif inspect.isasyncgen(func_value):
                    self.fixture_value = await func_value.asend(None)
                elif isinstance(func_value, collections.abc.Generator):
                    self.fixture_value = func_value.send(None)
                else:
                    # Regular synchronous function
                    self.fixture_value = func_value

            # Now that we're done setting up, we don't want crashes to cancel us immediately; instead we want them to
            # cancel our downstream dependents, and then eventually let us clean up normally. So remove this from the
            # set of cancel scopes affected by self._crash.
            test_ctx.active_cancel_scopes.remove(nursery_fixture.cancel_scope)

            # self.fixture_value is ready, so notify users that they can continue. (Or, maybe we crashed and were
            # cancelled, in which case our users will check test_ctx.crashed and immediately exit, which is fine too.)
            self.setup_done.set()

            # Wait for users to be finished.
            #
            # At this point we're in a very strange state: if the fixture yielded inside a nursery or cancel scope, then
            # we are still "inside" that scope even though its with block is not on the stack. In particular this means
            # that if they get cancelled, then our waiting might get a Cancelled error, that we cannot really deal with
            # – it should get thrown back into the fixture generator, but pytest fixture generators don't work that way:
            #   https://github.com/python-trio/pytest-trio/issues/55
            # And besides, we can't start tearing down until all our users have finished.
            #
            # So if we get an exception here, we crash the context (which cancels the test and starts the cleanup
            # process), save any exception that *isn't* Cancelled (because if its Cancelled then we can't route it to
            # the right place, and anyway the teardown code will get it again if it matters), and then use a shield to
            # keep waiting for the teardown to finish without having to worry about cancellation.
            yield_outcome = outcome.Value(None)
            try:
                for event in self.user_done_events:
                    await event.wait()

            except BaseException as exc:
                check.isinstance(exc, anyio.get_cancelled_exc_class())
                yield_outcome = outcome.Error(exc)
                test_ctx.crash(self, None)
                with anyio.CancelScope(shield=True):
                    for event in self.user_done_events:
                        await event.wait()

            # Do our teardown
            if inspect.isasyncgen(func_value):
                try:
                    await yield_outcome.asend(func_value)
                except StopAsyncIteration:
                    pass
                else:
                    raise RuntimeError("too many yields in fixture")

            elif isinstance(func_value, collections.abc.Generator):
                try:
                    yield_outcome.send(func_value)
                except StopIteration:
                    pass
                else:
                    raise RuntimeError("too many yields in fixture")


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
            contextvars_ctx.run(canary.set, "in correct context")

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
