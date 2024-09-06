from omlish.testing.pytest import plugins as ptp


def pytest_addhooks(pluginmanager):
    ptp.add_hooks(pluginmanager)
