from omlish.testing import pytest as ptu


def pytest_addhooks(pluginmanager):
    ptu.plugins.addhooks(pluginmanager)
