from omlish import inject as inj
from omlish import lang

from .configs import CommandsConfig
from .injection import commands


with lang.auto_proxy_import(globals()):
    from . import manager as _manager
    from . import simple as _simple


##


def bind_commands(cfg: CommandsConfig = CommandsConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(commands().bind_items_provider(singleton=True))

    #

    els.extend([
        inj.bind(_manager.CommandsManager, singleton=True),
    ])

    #

    els.extend([
        inj.bind(_simple.EchoCommand, singleton=True),
        commands().bind_item(to_key=_simple.EchoCommand),

        inj.bind(_simple.QuitCommand, singleton=True),
        commands().bind_item(to_key=_simple.QuitCommand),
    ])

    #

    return inj.as_elements(*els)
