import inspect
import typing as ta

import pytest

from .... import lang
from ._registry import register


ALL_BACKENDS_MARK = 'all_async_backends'

KNOWN_BACKENDS = (
    'asyncio',
    'trio',
    'trio_asyncio',
)

PARAM_NAME = '__async_backend'


@register
class AsyncsPlugin:
    ASYNC_BACKENDS: ta.ClassVar[ta.Sequence[str]] = [
        *[s for s in KNOWN_BACKENDS if lang.can_import(s)],
    ]

    def pytest_configure(self, config):
        config.addinivalue_line('markers', f'{ALL_BACKENDS_MARK}: marks for all async backends')

    @pytest.hookimpl(tryfirst=True)
    def pytest_pycollect_makeitem(self, collector, name, obj) -> None:
        # ~> https://github.com/agronholm/anyio/blob/f8f269699795373057ac7b0153ec1a217d94461a/src/anyio/pytest_plugin.py#L91  # noqa
        if collector.istestfunction(obj, name) and inspect.iscoroutinefunction(obj):
            if (
                    collector.get_closest_marker(ALL_BACKENDS_MARK) is not None or
                    any(marker.name == ALL_BACKENDS_MARK for marker in getattr(obj, 'pytestmark', ()))
            ):
                # anyio apparently spins up trio_asyncio for asyncio tests, which means the real asyncio backend just
                # isn't tested. It'd be nice to test trio_asyncio too.
                # pytest.mark.anyio()(obj)
                # pytest.mark.usefixtures('anyio_backend')(obj)
                # pytest.mark.parametrize('anyio_backend', self.ASYNC_BACKENDS)(obj)
                pass

    def pytest_generate_tests(self, metafunc):
        if metafunc.definition.get_closest_marker('all_async_backends') is None:
            return

        metafunc.fixturenames.append(PARAM_NAME)
        metafunc.parametrize(PARAM_NAME, self.ASYNC_BACKENDS)

        for c in metafunc._calls:  # noqa
            c.marks.append(pytest.Mark(c.params[PARAM_NAME], (), {}))

        print(metafunc)
