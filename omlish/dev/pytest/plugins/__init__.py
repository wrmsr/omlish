from . import pycharm  # noqa
from ._registry import ALL


def addhooks(pluginmanager):
    for plugin in ALL:
        pluginmanager.register(plugin())
