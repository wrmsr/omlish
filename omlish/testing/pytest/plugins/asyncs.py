import inspect

import pytest

from .... import lang
from ._registry import register


KNOWN_BACKENDS = (
    'asyncio',
    'trio',
)

PARAM_NAME = '__async_backend'


@register
class AsyncsPlugin:
    async_backends = [
        *[s for s in KNOWN_BACKENDS if lang.can_import(s)],
    ]

    def pytest_configure(self, config):
        config.addinivalue_line('markers', 'all_async_backends: marks for all async backends')

    @pytest.hookimpl(tryfirst=True)
    def pytest_pycollect_makeitem(self, collector, name, obj) -> None:
        # ~> https://github.com/agronholm/anyio/blob/f8f269699795373057ac7b0153ec1a217d94461a/src/anyio/pytest_plugin.py#L91  # noqa
        if collector.istestfunction(obj, name) and inspect.iscoroutinefunction(obj):
            if (
                    collector.get_closest_marker('all_async_backends') is not None or
                    any(marker.name == 'all_async_backends' for marker in getattr(obj, 'pytestmark', ()))
            ):
                pytest.mark.anyio()(obj)
                pytest.mark.usefixtures("anyio_backend")(obj)
                pytest.mark.parametrize('anyio_backend', self.async_backends)(obj)
