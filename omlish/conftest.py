from .testing.pytest import plugins as ptp  # noqa
from .testing.pytest.inject.harness import harness  # noqa


def pytest_addhooks(pluginmanager):
    ptp.addhooks(pluginmanager)
