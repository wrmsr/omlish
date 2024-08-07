from ._registry import register


PARAM_NAME = '__async_backend'


@register
class AsyncsPlugin:

    def pytest_configure(self, config):
        config.addinivalue_line('markers', 'all_async_backends: marks for all async backends')

    def pytest_generate_tests(self, metafunc):
        if metafunc.definition.get_closest_marker('all_async_backends') is None:
            return

        metafunc.fixturenames.append(PARAM_NAME)
        metafunc.parametrize(PARAM_NAME, ['asyncio', 'trio'])
