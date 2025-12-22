from omlish import inject as inj
from omlish import lang

from ..base import ChatInterface
from .configs import BareInterfaceConfig


with lang.auto_proxy_import(globals()):
    from .....inputs import asyncs as _inputs_asyncs
    from .....inputs import sync as _inputs_sync
    from ...drivers.tools import confirmation as _tools_confirmation
    from ...facades import ui as _facades_ui
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
                _tools_confirmation.ToolExecutionConfirmation,
                to_ctor=_tools_confirmation.UnsafeAlwaysAllowToolExecutionConfirmation,
                singleton=True,
            ))

        else:
            els.append(inj.bind(
                _tools_confirmation.ToolExecutionConfirmation,
                to_ctor=_tools.InteractiveToolExecutionConfirmation,
                singleton=True,
            ))

    #

    els.extend([
        inj.bind(_facades_ui.PrintMessageDisplayer, singleton=True),
        inj.bind(_facades_ui.UiMessageDisplayer, to_key=_facades_ui.PrintMessageDisplayer),
    ])

    #

    return inj.as_elements(*els)
