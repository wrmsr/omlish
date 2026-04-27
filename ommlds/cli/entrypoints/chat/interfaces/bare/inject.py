from omlish import inject as inj
from omlish import lang

from ...... import minichain as mc
from ..base import ChatInterface
from .configs import BareInterfaceConfig


with lang.auto_proxy_import(globals()):
    from .....interfaces.bare.inputs import asyncs as _inputs_asyncs
    from .....interfaces.bare.inputs import sync as _inputs_sync
    from . import chat as _chat
    from . import interactive as _interactive
    from . import oneshot as _oneshot
    from . import tools as _tools


##


def bind_bare(cfg: BareInterfaceConfig = BareInterfaceConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    if cfg.interactive:
        els.extend([
            inj.bind(_interactive.InteractiveBareChatInterface, singleton=True),
            inj.bind(ChatInterface, to_key=_interactive.InteractiveBareChatInterface),
        ])

        els.extend([
            inj.bind(_inputs_sync.SyncStringInput, to_const=_inputs_sync.InputSyncStringInput(use_readline=cfg.use_readline)),  # noqa
            inj.bind(_inputs_asyncs.AsyncStringInput, to_ctor=_inputs_asyncs.ThreadAsyncStringInput, singleton=True),
        ])

    else:
        els.extend([
            inj.bind(_oneshot.OneshotBareChatInterface, singleton=True),
            inj.bind(ChatInterface, to_key=_oneshot.OneshotBareChatInterface),
        ])

    #

    if cfg.enable_tools:
        if cfg.dangerous_no_tool_confirmation:
            els.append(inj.bind(
                mc.drivers.ToolPermissionConfirmation,
                to_ctor=mc.drivers.UnsafeAlwaysAllowToolPermissionConfirmation,
                singleton=True,
            ))

        else:
            els.append(inj.bind(
                mc.drivers.ToolPermissionConfirmation,
                to_ctor=_tools.InteractiveToolPermissionConfirmation,
                singleton=True,
            ))

    #

    els.extend([
        inj.bind(_chat.BareUserInputSender, singleton=True),
        inj.bind(mc.facades.UserInputSender, to_key=_chat.BareUserInputSender),
    ])

    #

    els.extend([
        inj.bind(mc.facades.PrintMessageDisplayer, singleton=True),
        inj.bind(mc.facades.UiMessageDisplayer, to_key=mc.facades.PrintMessageDisplayer),
    ])

    #

    return inj.as_elements(*els)
