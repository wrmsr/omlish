from ._registry import register


##


@register
class SpacingPlugin:
    def pytest_addoption(self, parser):
        parser.addoption('--newlines-before', action='store', type=int, help='Adds newlines before tests')
        parser.addoption('--newlines-after', action='store', type=int, help='Adds newlines after tests')

    def pytest_runtest_setup(self, item):
        if item.session.config.option.newlines_before:
            for _ in range(item.session.config.option.newlines_before):
                print()

    def pytest_runtest_teardown(self, item):
        if item.session.config.option.newlines_after:
            for _ in range(item.session.config.option.newlines_after):
                print()
