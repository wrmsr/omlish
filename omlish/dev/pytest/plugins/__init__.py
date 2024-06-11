from . import (  # noqa
    logging,
    pycharm,
    repeat,
    skips,
    spacing,
)
from ._registry import ALL
from ._registry import register


def addhooks(pluginmanager):
    present_types = {type(p) for p in pluginmanager.get_plugins()}

    for plugin in ALL:
        if plugin not in present_types:
            pluginmanager.register(plugin())
