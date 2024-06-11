from .dev import pytest as ptu  # noqa
from .inject.dev import pytest as pti  # noqa


def pytest_addhooks(pluginmanager):
    ptu.plugins.addhooks(pluginmanager)
