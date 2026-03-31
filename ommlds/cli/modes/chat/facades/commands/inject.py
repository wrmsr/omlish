from omlish import inject as inj
from omlish import lang

from ...... import minichain as mc
from .configs import CommandsConfig
from .injection import commands


with lang.auto_proxy_import(globals()):
    from . import manager as _manager
    from . import permissions as _permissions
    from . import send as _send
    from . import simple as _simple
    from . import tools as _tools


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
        _permissions.PermissionsCommand,
        _send.SendCommand,
        _simple.EchoCommand,
        _simple.QuitCommand,
        _tools.ToolsCommand,
    ]:
        els.extend([
            inj.bind(cmd_cls, singleton=True),
            commands().bind_item(to_key=cmd_cls),
        ])

    #

    if aex := cfg.autoexec:
        async def run_autoexec_commands(cm: _manager.CommandsManager) -> None:
            for cmd in aex:
                await cm.run_command_text(cmd.removeprefix('/'))

        els.append(
            mc.drivers.injection.phase_callbacks().bind_item(to_fn=inj.target(
                cm=_manager.CommandsManager,
            )(lambda cm: mc.drivers.PhaseCallback(mc.drivers.Phase.STARTED, lambda: run_autoexec_commands(cm)))),  # noqa
        )

    #

    return inj.as_elements(*els)
