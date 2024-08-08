"""

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
import typing as ta

import pytest

from .... import lang
from ._registry import register


ALL_BACKENDS_MARK = 'all_async_backends'

KNOWN_BACKENDS = (
    'asyncio',
    'trio',
    # 'trio_asyncio',
)

PARAM_NAME = '__async_backend'


@register
class AsyncsPlugin:
    ASYNC_BACKENDS: ta.ClassVar[ta.Sequence[str]] = [
        *[s for s in KNOWN_BACKENDS if lang.can_import(s)],
    ]

    def pytest_configure(self, config):
        config.addinivalue_line('markers', f'{ALL_BACKENDS_MARK}: marks for all async backends')

    def pytest_generate_tests(self, metafunc):
        if metafunc.definition.get_closest_marker('all_async_backends') is None:
            return

        metafunc.fixturenames.append(PARAM_NAME)
        metafunc.parametrize(PARAM_NAME, self.ASYNC_BACKENDS)

        for c in metafunc._calls:  # noqa
            be = c.params[PARAM_NAME]
            if be == 'trio_asyncio':
                c.marks.append(pytest.Mark('trio', (), {}))
                # c.fixturenames.append('__trio_asyncio_fixture')
                raise NotImplementedError
            else:
                c.marks.append(pytest.Mark(be, (), {}))
