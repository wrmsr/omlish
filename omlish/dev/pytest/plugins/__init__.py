from . import logging  # noqa
from . import pycharm  # noqa
from . import repeat  # noqa
from ._registry import ALL


def addhooks(pluginmanager):
    present_types = {type(p) for p in pluginmanager.get_plugins()}

    for plugin in ALL:
        if plugin not in present_types:
            pluginmanager.register(plugin())
