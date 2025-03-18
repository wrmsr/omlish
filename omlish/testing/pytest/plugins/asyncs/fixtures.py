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
import collections.abc
import contextlib
import contextvars
import inspect
import typing as ta

from _pytest.outcomes import Skipped  # noqa
from _pytest.outcomes import XFailed  # noqa

from ..... import check
from ..... import lang
from .backends.base import AsyncsBackend
from .utils import is_coroutine_function


if ta.TYPE_CHECKING:
    import anyio.abc
else:
    anyio = lang.proxy_import('anyio', extras=['abc'])


##


CANARY: contextvars.ContextVar[ta.Any] = contextvars.ContextVar('pytest-omlish-asyncs canary')


class NURSERY_FIXTURE_PLACEHOLDER:  # noqa
    pass


##


class AsyncsTestContext:
    def __init__(self, backend: AsyncsBackend) -> None:
        super().__init__()

        self.backend = backend

        self.crashed = False

        # This holds cancel scopes for whatever setup steps are currently running -- initially it's the fixtures that
        # are in the middle of evaluating themselves, and then once fixtures are set up it's the test itself. Basically,
        # at any given moment, it's the stuff we need to cancel if we want to start tearing down our fixture DAG.
        self.active_cancel_scopes: set[anyio.CancelScope] = set()

        self.fixtures_with_errors: set[AsyncsFixture] = set()
        self.fixtures_with_cancel: set[AsyncsFixture] = set()

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


##


class AsyncsFixture:
    """
    Represent a fixture that need to be run in a async context to be resolved.

    The name is actually a misnomer, because we use it to represent the actual test itself as well, since the
    test is basically just a fixture with no dependents and no teardown.
    """

    def __init__(
            self,
            name: str,
            func: ta.Callable,
            pytest_kwargs: ta.Mapping[str, ta.Any],
            *,
            is_test: bool = False,
    ) -> None:
        super().__init__()

        self.name = name
        self._func = func
        self._pytest_kwargs = pytest_kwargs
        self._is_test = is_test
        self._teardown_done = anyio.Event()

        # These attrs are all accessed from other objects: Downstream users read this value.
        self.fixture_value: ta.Any = None

        # This event notifies downstream users that we're done setting up. Invariant: if this is set, then either
        # fixture_value is usable *or* test_ctx.crashed is True.
        self.setup_done = anyio.Event()

        # Downstream users *modify* this value, by adding their _teardown_done events to it, so we know who we need to
        # wait for before tearing down.
        self.user_done_events: set[anyio.Event] = set()

    def register_and_collect_dependencies(self) -> set['AsyncsFixture']:
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
    async def _fixture_manager(self, test_ctx: AsyncsTestContext) -> ta.AsyncIterator['anyio.abc.TaskGroup']:
        __tracebackhide__ = True

        try:
            async with anyio.create_task_group() as nursery_fixture:
                try:
                    yield nursery_fixture
                finally:
                    nursery_fixture.cancel_scope.cancel()

        except BaseException as exc:  # noqa
            test_ctx.crash(self, exc)

        finally:
            self.setup_done.set()
            self._teardown_done.set()

    async def run(
            self,
            test_ctx: AsyncsTestContext,
            contextvars_ctx: contextvars.Context,
    ) -> None:
        __tracebackhide__ = True

        await test_ctx.backend.install_context(contextvars_ctx)

        # Check that it worked, since technically trio doesn't *guarantee* that sleep(0) will actually yield.
        check.equal(CANARY.get(), 'in correct context')

        # This 'with' block handles the nursery fixture lifetime, the teardown_done event, and crashing the context if
        # there's an unhandled exception.
        async with self._fixture_manager(test_ctx) as nursery_fixture:
            # Resolve our kwargs
            resolved_kwargs: dict = {}
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
            # - it should get thrown back into the fixture generator, but pytest fixture generators don't work that way:
            #   https://github.com/python-trio/pytest-trio/issues/55
            # And besides, we can't start tearing down until all our users have finished.
            #
            # So if we get an exception here, we crash the context (which cancels the test and starts the cleanup
            # process), save any exception that *isn't* Cancelled (because if its Cancelled then we can't route it to
            # the right place, and anyway the teardown code will get it again if it matters), and then use a shield to
            # keep waiting for the teardown to finish without having to worry about cancellation.
            yield_outcome: lang.Outcome = lang.Value(None)
            try:
                for event in self.user_done_events:
                    await event.wait()

            except BaseException as exc:  # noqa
                check.isinstance(exc, anyio.get_cancelled_exc_class())
                yield_outcome = lang.Error(exc)
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
                    raise RuntimeError('too many yields in fixture')

            elif isinstance(func_value, collections.abc.Generator):
                try:
                    yield_outcome.send(func_value)
                except StopIteration:
                    pass
                else:
                    raise RuntimeError('too many yields in fixture')


##


def is_asyncs_fixture(
        func: ta.Callable,
        coerce_async: bool,
        kwargs: ta.Mapping[str, ta.Any],
) -> bool:
    if coerce_async and (is_coroutine_function(func) or inspect.isasyncgenfunction(func)):
        return True

    if any(isinstance(value, AsyncsFixture) for value in kwargs.values()):
        return True

    return False
