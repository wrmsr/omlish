from omlish.testing.pytest import plugins as ptp  # noqa
from omlish.testing.pytest.inject.harness import harness  # noqa


def pytest_addhooks(pluginmanager):
    ptp.addhooks(pluginmanager)
