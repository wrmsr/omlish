from .dev.pytest import plugins


def pytest_addhooks(pluginmanager):
    plugins.addhooks(pluginmanager)
