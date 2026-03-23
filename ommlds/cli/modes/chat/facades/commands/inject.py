from omlish import inject as inj
from omlish import lang

from .configs import CommandsConfig
from .injection import commands


with lang.auto_proxy_import(globals()):
    from . import manager as _manager
    from . import permissions as _permissions
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

    for cmd_cls in [
        _simple.EchoCommand,
        _simple.QuitCommand,
        _permissions.PermissionsCommand,
    ]:
        els.extend([
            inj.bind(cmd_cls, singleton=True),
            commands().bind_item(to_key=cmd_cls),
        ])

    #

    return inj.as_elements(*els)
