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
import functools
import inspect
import typing as ta

import pytest

from .... import lang
from ....diag.pydevd import patch_for_trio_asyncio
from ._registry import register


ALL_BACKENDS_MARK = 'all_asyncs'

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


@register
class AsyncsPlugin:
    ASYNC_BACKENDS: ta.ClassVar[ta.Sequence[str]] = [
        *[s for s in KNOWN_BACKENDS if lang.can_import(s)],
    ]

    def pytest_configure(self, config):
        config.addinivalue_line('markers', f'{ALL_BACKENDS_MARK}: marks for all async backends')
        config.addinivalue_line('markers', 'trio_asyncio: marks for trio_asyncio backend')

    def pytest_generate_tests(self, metafunc):
        if metafunc.definition.get_closest_marker('all_asyncs') is not None:
            bes = self.ASYNC_BACKENDS
        elif metafunc.definition.get_closest_marker('trio_asyncio') is not None:
            bes = ['trio_asyncio']
        else:
            return

        metafunc.fixturenames.append(PARAM_NAME)
        metafunc.parametrize(PARAM_NAME, bes)

        for c in metafunc._calls:  # noqa
            be = c.params[PARAM_NAME]
            if be == 'trio_asyncio':
                patch_for_trio_asyncio()
                c.marks.extend([
                    pytest.mark.trio.mark,
                    pytest.mark.trio_asyncio.mark,
                ])
            else:
                c.marks.append(getattr(pytest.mark, be).mark)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call(self, item):
        bes = [be for be in self.ASYNC_BACKENDS if item.get_closest_marker(be) is not None]
        if len(bes) > 1:
            raise Exception(f'{item.nodeid}: multiple async backends specified: {bes}')
        elif is_async_function(item.obj) and not bes:
            raise Exception(f'{item.nodeid}: async def function and no async plugin specified')

        if 'trio_asyncio' in bes:
            obj = item.obj
            import trio_asyncio

            @functools.wraps(obj)
            async def run(*args, **kwargs):
                async with trio_asyncio.open_loop():
                    await trio_asyncio.aio_as_trio(obj)(*args, **kwargs)

            item.obj = run

        yield
