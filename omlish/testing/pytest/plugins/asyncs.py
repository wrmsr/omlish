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
                # ~> https://github.com/agronholm/anyio/blob/f8f269699795373057ac7b0153ec1a217d94461a/src/anyio/pytest_plugin.py#L91  # noqa
                c.marks.extend([
                    pytest.Mark('anyio', (), {}),
                    pytest.Mark('usefixtures', ('anyio_backend',), {}),
                    pytest.Mark('anyio_backend', ('asyncio',), {}),
                ])
            else:
                c.marks.append(pytest.Mark(be, (), {}))
