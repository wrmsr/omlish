"""

pytest_trio:
https://github.com/python-trio/pytest-trio/blob/f03160aa1dd355a12d39fa21f4aee4e1239efea3/pytest_trio/plugin.py
 - def pytest_addoption(parser):
 - def pytest_configure(config):
 - @pytest.hookimpl(hookwrapper=True)
   def pytest_runtest_call(item):
 - def pytest_fixture_setup(fixturedef, request):
 - def pytest_collection_modifyitems(config, items):

pytest_asyncio:
https://github.com/pytest-dev/pytest-asyncio/blob/f45aa18cf3eeeb94075de16a1d797858facab863/pytest_asyncio/plugin.py
 - def pytest_addoption(parser: Parser, pluginmanager: PytestPluginManager) -> None:
 - def pytest_configure(config: Config) -> None:
 - @pytest.hookimpl(tryfirst=True)
   def pytest_report_header(config: Config) -> List[str]:
 - @pytest.hookimpl(specname="pytest_pycollect_makeitem", tryfirst=True)
   def pytest_pycollect_makeitem_preprocess_async_fixtures(
       collector: Union[pytest.Module, pytest.Class], name: str, obj: object
   ) -> Union[
       pytest.Item, pytest.Collector, List[Union[pytest.Item, pytest.Collector]], None
   ]:
 - @pytest.hookimpl(specname="pytest_pycollect_makeitem", hookwrapper=True)
   def pytest_pycollect_makeitem_convert_async_functions_to_subclass(
       collector: Union[pytest.Module, pytest.Class], name: str, obj: object
   ) -> Generator[None, Any, None]:
 - @pytest.hookimpl
   def pytest_collectstart(collector: pytest.Collector) -> None:
 - @pytest.hookimpl(tryfirst=True)
 - def pytest_generate_tests(metafunc: Metafunc) -> None:
 - @pytest.hookimpl(hookwrapper=True)
   def pytest_fixture_setup(
 -     fixturedef: FixtureDef,
 - ) -> Generator[None, Any, None]:
 - @pytest.hookimpl(tryfirst=True, hookwrapper=True)
   def pytest_pyfunc_call(pyfuncitem: Function) -> Optional[object]:
 - def pytest_runtest_setup(item: pytest.Item) -> None:

anyio.pytest_plugin:
https://github.com/agronholm/anyio/blob/8907964926a24461840eee0925d3f355e729f15d/src/anyio/pytest_plugin.py
 - def pytest_configure(config: Any) -> None:
 - def pytest_fixture_setup(fixturedef: Any, request: Any) -> None:
 - @pytest.hookimpl(tryfirst=True)
   def pytest_pycollect_makeitem(collector: Any, name: Any, obj: Any) -> None:
 - @pytest.hookimpl(tryfirst=True)
   def pytest_pyfunc_call(pyfuncitem: Any) -> bool | None:

"""
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
