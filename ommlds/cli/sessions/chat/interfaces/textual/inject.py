"""
FIXME:
 - too lazy to lazy import guts like every other proper inject module lol >_<
"""
import asyncio
import contextlib

from omlish import inject as inj
from omlish import lang

from ...drivers.events.injection import event_callbacks
from ..base import ChatInterface
from .configs import TextualInterfaceConfig


with lang.auto_proxy_import(globals()):
    from omdev.tui import textual as tx

    from ...drivers.tools import confirmation as _tools_confirmation
    from ...facades import ui as _facades_ui
    from . import app as _app
    from . import facades as _facades
    from . import interface as _interface
    from . import tools as _tools


##


def bind_textual(cfg: TextualInterfaceConfig = TextualInterfaceConfig()) -> inj.Elements:
    els: list[inj.Elemental] = [
        inj.bind(ChatInterface, to_ctor=_interface.TextualChatInterface, singleton=True),
    ]

    #

    els.extend([
        inj.bind(_app.ChatApp, singleton=True),
        inj.bind_async_late(_app.ChatApp, _app.ChatAppGetter),
    ])

    #

    els.extend([
        inj.bind(_app.ChatEventQueue, to_const=asyncio.Queue()),

        event_callbacks().bind_item(to_fn=inj.target(eq=_app.ChatEventQueue)(lambda eq: lambda ev: eq.put(ev))),
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
                to_ctor=_tools.ChatAppToolExecutionConfirmation,
                singleton=True,
            ))

    #

    els.extend([
        inj.bind(tx.DevtoolsConfig(port=41932)),  # FIXME: lol

        inj.bind(
            tx.DevtoolsManager,
            singleton=True,
            to_async_fn=inj.make_async_managed_provider(
                tx.DevtoolsManager,
                contextlib.aclosing,
            ),
        ),

        inj.bind(
            tx.DevtoolsSetup,
            to_async_fn=inj.target(mgr=tx.DevtoolsManager)(lambda mgr: mgr.get_setup()),
            singleton=True,
        ),
    ])

    #

    els.extend([
        inj.bind(_facades.ChatAppUiMessageDisplayer, singleton=True),
        inj.bind(_facades_ui.UiMessageDisplayer, to_key=_facades.ChatAppUiMessageDisplayer),
    ])

    #

    return inj.as_elements(*els)
