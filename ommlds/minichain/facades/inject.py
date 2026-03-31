from omlish import inject as inj
from omlish import lang

from .configs import FacadeConfig


with lang.auto_proxy_import(globals()):
    from . import impl as _impl
    from . import input as _input
    from . import types as _types
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

    els.extend([
        inj.bind_async_late(_input.UserInputSender, _input.UserInputSenderGetter),
    ])

    #

    els.extend([
        inj.bind(_impl.FacadeImpl, singleton=True),
        inj.bind(_types.Facade, to_key=_impl.FacadeImpl),
    ])

    #

    els.append(inj.bind(_ui.UiQuitSignal(_ui.raise_system_exit_ui_quit_signal)))

    #

    return inj.as_elements(*els)
