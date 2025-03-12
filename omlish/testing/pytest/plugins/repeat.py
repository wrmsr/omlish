from ._registry import register


PARAM_NAME = '__repeat'


@register
class RepeatPlugin:
    def pytest_addoption(self, parser):
        parser.addoption('--repeat', action='store', type=int, help='Number of times to repeat each test')

    def pytest_generate_tests(self, metafunc):
        if metafunc.config.option.repeat is None:
            return

        n = metafunc.config.option.repeat
        metafunc.fixturenames.append(PARAM_NAME)
        metafunc.parametrize(PARAM_NAME, range(n))
