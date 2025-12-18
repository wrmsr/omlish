"""
FIXME:
 - too lazy to lazy import guts like every other proper inject module lol >_<
"""
import asyncio

from omlish import inject as inj
from omlish import lang

from ...drivers.events.injection import event_callbacks
from ..base import ChatInterface
from ..configs import InterfaceConfig


with lang.auto_proxy_import(globals()):
    from ...drivers.tools import confirmation as _tools_confirmation
    from . import app as _app
    from . import interface as _interface
    from . import tools as _tools


##


def bind_textual(cfg: InterfaceConfig = InterfaceConfig()) -> inj.Elements:
    els: list[inj.Elemental] = [
        inj.bind(ChatInterface, to_ctor=_interface.TextualChatInterface, singleton=True),
    ]

    #

    els.extend([
        inj.bind(_app.ChatApp, singleton=True),

        inj.bind_late(_app.ChatApp, _app.ChatAppGetter),
    ])

    #

    els.extend([
        inj.bind(_app.ChatDriverEventQueue, to_const=asyncio.Queue()),

        event_callbacks().bind_item(to_fn=inj.KwargsTarget.of(
            lambda eq: lambda ev: eq.put(ev),
            eq=_app.ChatDriverEventQueue,
        )),
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

    return inj.as_elements(*els)
