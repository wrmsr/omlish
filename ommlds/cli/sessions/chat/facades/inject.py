from omlish import inject as inj
from omlish import lang

from .configs import FacadeConfig


with lang.auto_proxy_import(globals()):
    from . import facade as _facade
    from . import ui as _ui
    from .commands import inject as _commands


##


def bind_facade(cfg: FacadeConfig = FacadeConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        _commands.bind_commands(cfg.commands),
    ])

    #

    els.append(inj.bind(_facade.ChatFacade, singleton=True))

    #

    els.append(inj.bind(_ui.UiQuitSignal(_ui.raise_system_exit_ui_quit_signal)))

    #

    return inj.as_elements(*els)
