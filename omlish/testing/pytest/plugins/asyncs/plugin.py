"""
TODO:
 - auto drain_asyncio
"""
import contextvars
import functools
import sys
import typing as ta
import warnings

import pytest
from _pytest.outcomes import Skipped  # noqa
from _pytest.outcomes import XFailed  # noqa

from ..... import check
from ..... import lang
from .._registry import register
from .backends import ASYNC_BACKENDS
from .backends import AsyncsBackend
from .consts import ASYNCS_MARK
from .consts import PARAM_NAME
from .fixtures import CANARY
from .fixtures import AsyncsFixture
from .fixtures import AsyncsTestContext
from .fixtures import is_asyncs_fixture
from .utils import is_async_function
from .utils import is_coroutine_function


if ta.TYPE_CHECKING:
    import anyio
else:
    anyio = lang.proxy_import('anyio')


##


@register
class AsyncsPlugin:
    def __init__(self, backends: ta.Collection[type[AsyncsBackend]] | None = None) -> None:
        super().__init__()

        if backends is None:
            backends = ASYNC_BACKENDS

        bd: dict[str, AsyncsBackend] = {}
        for bc in backends:
            be = bc()
            bn = be.name
            check.not_in(bn, bd)
            bd[bn] = be
        self._backends = bd

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
            aio_plugin.warnings.warn = aio_plugin_warn

    def pytest_configure(self, config):
        config.addinivalue_line('markers', f'{ASYNCS_MARK}: marks for all async backends')

    def pytest_generate_tests(self, metafunc):
        if (m := metafunc.definition.get_closest_marker(ASYNCS_MARK)) is not None:
            if m.args:
                bns = m.args
            else:
                bns = list(self._backends)
        else:
            return

        for bn in bns:
            be = self._backends[bn]
            if be.is_available():
                be.prepare_for_metafunc(metafunc)

        metafunc.fixturenames.append(PARAM_NAME)
        metafunc.parametrize(PARAM_NAME, bns)

    def pytest_fixture_setup(self, fixturedef, request):
        is_asyncs_test = request.node.get_closest_marker(ASYNCS_MARK) is not None

        kwargs = {name: request.getfixturevalue(name) for name in fixturedef.argnames}

        if not is_asyncs_fixture(fixturedef.func, is_asyncs_test, kwargs):
            return None

        if request.scope != 'function':
            raise RuntimeError('Asyncs fixtures must be function-scope')

        if not is_asyncs_test:
            raise RuntimeError('Asyncs fixtures can only be used by Asyncs tests')

        fixture = AsyncsFixture(
            '<fixture {!r}>'.format(fixturedef.argname),  # noqa
            fixturedef.func,
            kwargs,
        )

        fixturedef.cached_result = (fixture, request.param_index, None)

        return fixture

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call(self, item):
        if (m := item.get_closest_marker(ASYNCS_MARK)) is None:  # noqa
            if is_async_function(item.obj):
                from _pytest.unittest import UnitTestCase  # noqa
                if isinstance(item.parent, UnitTestCase):
                    # unittest handles these itself.
                    pass
                else:
                    raise Exception(f'{item.nodeid}: async def function and no async plugin specified')

            yield
            return

        bn = item.callspec.params[PARAM_NAME]
        be = self._backends[bn]

        item.obj = self.test_runner_factory(be, item)

        yield

    def test_runner_factory(self, backend: AsyncsBackend, item, testfunc=None):
        if not testfunc:
            testfunc = item.obj

        if not is_coroutine_function(testfunc):
            pytest.fail(f'test function `{item!r}` is marked asyncs but is not async')

        if not backend.is_available():
            pytest.skip(f'backend `{backend.name}` is unavailable')

        @backend.wrap_runner
        async def _bootstrap_fixtures_and_run_test(**kwargs):
            __tracebackhide__ = True

            test_ctx = AsyncsTestContext(backend)
            test = AsyncsFixture(
                '<test {!r}>'.format(testfunc.__name__),  # noqa
                testfunc,
                kwargs,
                is_test=True,
            )

            contextvars_ctx = contextvars.copy_context()
            contextvars_ctx.run(CANARY.set, 'in correct context')

            async with anyio.create_task_group() as nursery:
                for fixture in test.register_and_collect_dependencies():
                    contextvars_ctx.run(
                        functools.partial(
                            nursery.start_soon,
                            fixture.run,
                            test_ctx,
                            contextvars_ctx,
                            name=fixture.name,
                        ),
                    )

            silent_cancellers = test_ctx.fixtures_with_cancel - test_ctx.fixtures_with_errors

            if silent_cancellers:
                for fixture in silent_cancellers:
                    test_ctx.error_list.append(
                        RuntimeError(f"{fixture.name} cancelled the test but didn't raise an error"),
                    )

            if len(test_ctx.error_list) == 1:
                raise test_ctx.error_list[0]
            elif test_ctx.error_list:
                raise BaseExceptionGroup('errors in async test and async fixtures', test_ctx.error_list)

        return _bootstrap_fixtures_and_run_test
