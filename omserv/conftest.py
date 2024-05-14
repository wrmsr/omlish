from omlish.dev import pytest as ptu


def pytest_addhooks(pluginmanager):
    ptu.plugins.addhooks(pluginmanager)
