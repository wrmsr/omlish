from .dev import pytest as ptu  # noqa
from .inject.dev import pytest as pti  # noqa
from .inject.dev.pytest.harness import harness  # noqa


def pytest_addhooks(pluginmanager):
    ptu.plugins.addhooks(pluginmanager)
