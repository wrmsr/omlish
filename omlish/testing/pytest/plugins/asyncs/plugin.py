"""
TODO:
 - auto drain_asyncio
"""
import sys
import typing as ta
import warnings

import pytest
from _pytest.outcomes import Skipped  # noqa
from _pytest.outcomes import XFailed  # noqa

from ..... import lang
from .....diag import pydevd as pdu
from .._registry import register
from .consts import ASYNCS_MARK
from .consts import KNOWN_BACKENDS
from .consts import PARAM_NAME
from .fixtures import AsyncsFixture
from .fixtures import is_asyncs_fixture
from .trio import trio_test_runner_factory
from .utils import is_async_function


##


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

        be = item.callspec.params[PARAM_NAME]

        if be == 'asyncio':
            raise NotImplementedError
        elif be == 'trio':
            item.obj = trio_test_runner_factory(item)
        elif be == 'trio_asyncio':
            raise NotImplementedError
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
