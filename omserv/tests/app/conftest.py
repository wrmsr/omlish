from omlish.testing.pytest import plugins as ptp
from omlish.testing.pytest.inject.harness import harness  # noqa


def pytest_addhooks(pluginmanager):
    ptp.add_hooks(pluginmanager)
