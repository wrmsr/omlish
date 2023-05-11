from omlish.dev.pytest import plugins  # noqa


def pytest_addhooks(pluginmanager):
    plugins.addhooks(pluginmanager)
