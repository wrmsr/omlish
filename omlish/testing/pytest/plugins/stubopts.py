from .... import lang
from ._registry import register


##


@register
class StubOptsPlugin:
    def pytest_addoption(self, parser):
        if not lang.can_import('xdist'):
            parser.addoption('--dist', help='Stub option for missing pytest-xdist plugin')
