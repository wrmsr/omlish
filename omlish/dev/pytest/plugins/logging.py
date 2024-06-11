from .... import logs
from ._registry import register


@register
class LoggingPlugin:

    def pytest_addoption(self, parser):
        parser.addoption('--log', action='store', help='Configures logging with given log level')

    def pytest_configure(self, config):
        if config.option.log is not None:
            logs.configure_standard_logging(config.option.log.upper())
