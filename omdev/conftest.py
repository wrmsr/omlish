from omcore.testing.pytest import plugins as ptp
from omcore.testing.pytest.inject.harness import harness  # noqa


def pytest_addhooks(pluginmanager):
    ptp.add_hooks(pluginmanager)
